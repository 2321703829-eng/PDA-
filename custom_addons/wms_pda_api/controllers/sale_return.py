from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from .base import WmsPdaBaseController


class WmsPdaSaleReturnController(WmsPdaBaseController):
    STATE_LABELS = {
        "waiting_receipt": "待收货",
        "receiving": "收货中",
        "received": "已收货",
        "receipt_exception": "收货异常",
    }
    QUALITY_LABELS = {
        "good": "完好",
        "damaged": "损坏",
        "expired": "过期",
        "other": "其他",
    }

    @http.route("/api/pda/wms/v1/sale-return/tasks", type="http", auth="public", methods=["GET"], csrf=False)
    def list_sale_return_tasks(self, **kwargs):
        payload = self._get_payload()
        return self._handle_request(lambda user, wh, token: self._sale_return_list_tasks(user, wh, payload))

    @http.route(
        "/api/pda/wms/v1/sale-return/tasks/<int:task_id>/confirm-line",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def confirm_sale_return_line(self, task_id, **kwargs):
        payload = self._get_payload()
        return self._handle_idempotent_request(payload, lambda user, wh, token: self._sale_return_confirm_line(user, wh, task_id, payload))

    @http.route(
        "/api/pda/wms/v1/sale-return/tasks/<int:task_id>/complete",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def complete_sale_return_task(self, task_id, **kwargs):
        payload = self._get_payload()
        return self._handle_idempotent_request(payload, lambda user, wh, token: self._sale_return_complete_task(user, wh, task_id, payload))

    def _sale_return_list_tasks(self, user, warehouse, payload):
        self._sale_return_require_warehouse(warehouse)
        offset = int(payload.get("offset") or 0)
        limit = min(int(payload.get("limit") or 20), 100)
        state = (payload.get("state") or "").strip()
        domain = [("warehouse_id", "=", warehouse.id), ("stock_picking_id.erp_source_type", "=", "sale_return")]
        if state:
            domain.append(("state", "=", state))
        else:
            domain.append(("state", "in", ["waiting_receipt", "receiving"]))
        Task = request.env["wms.receipt.task"].with_user(user).sudo()
        total = Task.search_count(domain)
        tasks = Task.search(domain, offset=offset, limit=limit, order="scheduled_date asc, id asc")
        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "records": [self._sale_return_format_task(task, include_progress=True) for task in tasks],
        }

    def _sale_return_confirm_line(self, user, warehouse, task_id, payload):
        task = self._sale_return_get_task(user, warehouse, task_id)
        if task.state == "received":
            return self._error(self.ERR_STATE_CONFLICT, "退货入库任务已完成，不能重复确认。", status=400, tts="任务已完成")
        if task.state not in ("waiting_receipt", "receiving"):
            return self._error(self.ERR_STATE_CONFLICT, "当前状态不能确认退货收货。", status=400, tts="状态不允许")
        request.env["wms.task.lock"].sudo().acquire(
            task._name,
            task.id,
            user.id,
            warehouse_id=warehouse.id if warehouse else False,
        )
        move = self._sale_return_get_move(task, payload)
        done_qty = self._sale_return_float_payload(payload, "done_qty")
        if done_qty < 0:
            raise ValidationError("实收数量不能小于 0。")
        demand_qty = move.product_uom_qty or 0.0
        if demand_qty and done_qty > demand_qty:
            return self._error(self.ERR_QTY_EXCEED, "实收数量不能超过应收数量。", status=400, tts="数量超出")
        barcode = (payload.get("barcode") or payload.get("product_barcode") or "").strip()
        if barcode and not self._sale_return_product_matches_barcode(move.product_id, barcode):
            return self._error(self.ERR_BARCODE_UNKNOWN, "扫描商品与当前行不一致。", status=400, tts="商品不匹配")
        quality_state = (payload.get("quality_state") or "good").strip()
        if quality_state not in self.QUALITY_LABELS:
            quality_state = "other"
        if task.state == "waiting_receipt":
            task.action_start_receipt()
        self._sale_return_write_done_qty(move, done_qty)
        self._sale_return_write_quality_state(move, quality_state)
        remaining_lines = len([item for item in self._sale_return_task_moves(task) if self._sale_return_read_done_qty(item) <= 0])
        return self._success(
            {
                "move_id": move.id,
                "product_name": move.product_id.display_name,
                "done_qty": done_qty,
                "quality_state": quality_state,
                "quality_label": self.QUALITY_LABELS.get(quality_state, quality_state),
                "remaining_lines": remaining_lines,
                "task": self._sale_return_format_task(task, include_progress=True),
            },
            tts=f"{move.product_id.display_name}{done_qty:g}件，品质{self.QUALITY_LABELS.get(quality_state, quality_state)}",
        )

    def _sale_return_complete_task(self, user, warehouse, task_id, payload):
        task = self._sale_return_get_task(user, warehouse, task_id)
        if task.state == "received":
            return {
                "task_state": task.state,
                "putaway_task_ids": task.putaway_task_ids.ids,
                "recovery_status": self._sale_return_recovery_status(task),
            }
        if task.state not in ("waiting_receipt", "receiving"):
            return self._error(self.ERR_STATE_CONFLICT, "当前状态不能完成退货入库。", status=400, tts="状态不允许")
        self._sale_return_save_photos(task, payload.get("photo_urls") or [], user)
        task.action_mark_received()
        self._sale_return_mark_sale_return_recovered(task)
        request.env["wms.task.lock"].sudo().release(task._name, task.id, user_id=user.id)
        return self._success(
            {
                "task_state": task.state,
                "putaway_task_ids": task.putaway_task_ids.ids,
                "recovery_status": self._sale_return_recovery_status(task),
                "task": self._sale_return_format_task(task, include_progress=True),
            },
            tts="退货入库完成",
        )

    def _sale_return_get_task(self, user, warehouse, task_id):
        domain = [
            ("id", "=", task_id),
            ("stock_picking_id.erp_source_type", "=", "sale_return"),
        ]
        if warehouse:
            domain.append(("warehouse_id", "=", warehouse.id))
        task = request.env["wms.receipt.task"].with_user(user).sudo().search(domain, limit=1)
        if not task:
            raise ValidationError("退货入库任务不存在或不属于当前仓库。")
        return task

    def _sale_return_get_move(self, task, payload):
        move_id = int(payload.get("move_id") or payload.get("line_id") or 0)
        moves = self._sale_return_task_moves(task)
        if move_id:
            move = moves.filtered(lambda record: record.id == move_id)[:1]
            if move:
                return move
            raise ValidationError("退货入库明细不存在。")
        barcode = (payload.get("barcode") or payload.get("product_barcode") or "").strip()
        if not barcode:
            raise ValidationError("请传入明细或商品条码。")
        matched = moves.filtered(lambda record: self._sale_return_product_matches_barcode(record.product_id, barcode))[:1]
        if not matched:
            raise ValidationError("未找到匹配的退货商品明细。")
        return matched

    def _sale_return_task_moves(self, task):
        picking = task.stock_picking_id
        if not picking:
            return request.env["stock.move"]
        moves = getattr(picking, "move_ids_without_package", False) or picking.move_ids
        return moves.filtered(lambda move: move.product_id)

    def _sale_return_format_task(self, task, include_progress=False):
        picking = task.stock_picking_id
        sale_return = picking.sale_return_id if picking and "sale_return_id" in picking._fields else False
        result = {
            "id": task.id,
            "name": task.name,
            "state": task.state,
            "state_label": self.STATE_LABELS.get(task.state, task.state),
            "picking_id": picking.id if picking else False,
            "picking_name": picking.name if picking else "",
            "sale_return_id": sale_return.id if sale_return else False,
            "sale_return_name": sale_return.name if sale_return else "",
            "partner_id": task.partner_id.id if task.partner_id else False,
            "partner_name": task.partner_id.display_name if task.partner_id else "",
            "warehouse_id": task.warehouse_id.id if task.warehouse_id else False,
            "warehouse_name": task.warehouse_id.display_name if task.warehouse_id else "",
            "source_type": "sale_return",
            "scheduled_date": task.scheduled_date,
        }
        if include_progress:
            moves = self._sale_return_task_moves(task)
            result.update(
                {
                    "line_count": len(moves),
                    "done_line_count": len(moves.filtered(lambda move: self._sale_return_read_done_qty(move) > 0)),
                    "demand_qty": sum(moves.mapped("product_uom_qty")),
                    "done_qty": sum(self._sale_return_read_done_qty(move) for move in moves),
                    "lines": [self._sale_return_format_move(move) for move in moves],
                }
            )
        return result

    def _sale_return_format_move(self, move):
        product = move.product_id
        return {
            "id": move.id,
            "product_id": product.id,
            "product_name": product.display_name,
            "default_code": product.default_code or "",
            "barcode": product.barcode or "",
            "demand_qty": move.product_uom_qty or 0.0,
            "done_qty": self._sale_return_read_done_qty(move),
            "quality_state": self._sale_return_read_quality_state(move),
            "uom": move.product_uom.name if move.product_uom else "",
            "state": move.state,
        }

    def _sale_return_mark_sale_return_recovered(self, task):
        picking = task.stock_picking_id
        if not picking:
            return
        vals = {}
        if "recovery_status" in picking._fields:
            vals["recovery_status"] = "recovered"
        if vals:
            picking.write(vals)
        if "sale_return_id" in picking._fields and picking.sale_return_id and "state" in picking.sale_return_id._fields:
            picking.sale_return_id.write({"state": "received"})

    def _sale_return_recovery_status(self, task):
        picking = task.stock_picking_id
        if picking and "recovery_status" in picking._fields:
            return picking.recovery_status or ""
        return ""

    def _sale_return_save_photos(self, task, photo_urls, user):
        if not photo_urls:
            return
        if not isinstance(photo_urls, list):
            photo_urls = [photo_urls]
        Photo = request.env["wms.task.photo"].sudo()
        for url in photo_urls:
            if not url:
                continue
            Photo.create(
                {
                    "task_model": task._name,
                    "task_id": task.id,
                    "photo_url": url,
                    "operator_id": user.id,
                    "warehouse_id": task.warehouse_id.id if task.warehouse_id else False,
                }
            )

    def _sale_return_read_done_qty(self, move):
        if "quantity" in move._fields:
            return move.quantity or 0.0
        if "quantity_done" in move._fields:
            return move.quantity_done or 0.0
        return 0.0

    def _sale_return_write_done_qty(self, move, qty):
        if "quantity" in move._fields:
            move.write({"quantity": qty})
            return
        if "quantity_done" in move._fields:
            move.write({"quantity_done": qty})
            return
        raise ValidationError("当前库存明细没有可写入的实收数量字段。")

    def _sale_return_write_quality_state(self, move, quality_state):
        if "quality_state" in move._fields:
            move.write({"quality_state": quality_state})
        elif "pda_quality_state" in move._fields:
            move.write({"pda_quality_state": quality_state})

    def _sale_return_read_quality_state(self, move):
        if "quality_state" in move._fields:
            return move.quality_state or ""
        if "pda_quality_state" in move._fields:
            return move.pda_quality_state or ""
        return ""

    def _sale_return_float_payload(self, payload, key):
        value = payload.get(key)
        if value in (None, ""):
            raise ValidationError("请填写实收数量。")
        return float(value)

    def _sale_return_require_warehouse(self, warehouse):
        if not warehouse:
            raise ValidationError("请先选择仓库。")

    def _sale_return_product_matches_barcode(self, product, barcode):
        return barcode in {product.barcode, product.default_code, product.product_tmpl_id.default_code}
