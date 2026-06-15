from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from .base import WmsPdaBaseController


class WmsPdaReceiptController(WmsPdaBaseController):
    @http.route("/api/pda/wms/v1/receipt/tasks", type="http", auth="public", methods=["GET"], csrf=False)
    def list_receipt_tasks(self, **kwargs):
        payload = self._get_payload()
        return self._handle_request(lambda user, wh, token: self._receipt_list_tasks(user, wh, payload))

    @http.route(
        "/api/pda/wms/v1/receipt/tasks/<int:task_id>/lines",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_receipt_task_lines(self, task_id, **kwargs):
        return self._handle_request(lambda user, wh, token: self._receipt_get_task_lines(user, wh, task_id, lock=True))

    @http.route(
        "/api/pda/wms/v1/receipt/tasks/<int:task_id>/confirm-line",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def confirm_receipt_line(self, task_id, **kwargs):
        payload = self._get_payload()
        return self._handle_idempotent_request(payload, lambda user, wh, token: self._receipt_confirm_line(user, wh, task_id, payload))

    @http.route(
        "/api/pda/wms/v1/receipt/tasks/<int:task_id>/complete",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def complete_receipt_task(self, task_id, **kwargs):
        payload = self._get_payload()
        return self._handle_idempotent_request(payload, lambda user, wh, token: self._receipt_complete_task(user, wh, task_id))

    def _receipt_list_tasks(self, user, warehouse, payload):
        if not warehouse:
            raise ValidationError("请先选择仓库。")
        limit = min(int(payload.get("limit") or 50), 100)
        state = (payload.get("state") or "").strip()
        domain = [("warehouse_id", "=", warehouse.id)]
        if state:
            domain.append(("state", "=", state))
        else:
            domain.append(("state", "in", ["waiting_receipt", "receiving"]))
        tasks = request.env["wms.receipt.task"].with_user(user).sudo().search(domain, limit=limit, order="id desc")
        return {
            "warehouse_id": warehouse.id,
            "tasks": [self._receipt_format_task(task, include_progress=True) for task in tasks],
        }

    def _receipt_get_task_lines(self, user, warehouse, task_id, lock=False):
        task = self._receipt_get_task(user, warehouse, task_id)
        if lock:
            request.env["wms.task.lock"].sudo().acquire(
                task._name,
                task.id,
                user.id,
                warehouse_id=warehouse.id if warehouse else False,
            )
        return {
            "task": self._receipt_format_task(task, include_progress=True),
            "lines": [self._receipt_format_move(move) for move in self._receipt_task_moves(task)],
        }

    def _receipt_confirm_line(self, user, warehouse, task_id, payload):
        task = self._receipt_get_task(user, warehouse, task_id)
        if task.state == "received":
            return self._error(self.ERR_STATE_CONFLICT, "收货任务已完成，不能重复确认。", status=400, tts="任务已完成")
        request.env["wms.task.lock"].sudo().acquire(
            task._name,
            task.id,
            user.id,
            warehouse_id=warehouse.id if warehouse else False,
        )
        move = self._receipt_get_move(task, payload)
        done_qty = self._receipt_float_payload(payload, "done_qty")
        demand_qty = move.product_uom_qty or 0.0
        if done_qty < 0:
            raise ValidationError("实收数量不能小于 0。")
        if demand_qty and done_qty > demand_qty:
            return self._error(self.ERR_QTY_EXCEED, "实收数量不能超过应收数量。", status=400, tts="数量超出")
        barcode = (payload.get("barcode") or payload.get("product_barcode") or "").strip()
        if barcode and not self._receipt_product_matches_barcode(move.product_id, barcode):
            return self._error(self.ERR_BARCODE_UNKNOWN, "扫描商品与当前行不一致。", status=400, tts="商品不匹配")
        if task.state == "waiting_receipt":
            task.action_start_receipt()
        self._receipt_write_done_qty(move, done_qty)
        return {
            "task": self._receipt_format_task(task, include_progress=True),
            "line": self._receipt_format_move(move),
        }

    def _receipt_complete_task(self, user, warehouse, task_id):
        task = self._receipt_get_task(user, warehouse, task_id)
        if task.state == "received":
            return {
                "task": self._receipt_format_task(task, include_progress=True),
                "putaway_task_ids": task.putaway_task_ids.ids,
            }
        if task.state not in ("waiting_receipt", "receiving"):
            return self._error(self.ERR_STATE_CONFLICT, "当前状态不能完成收货。", status=400, tts="状态不允许")
        task.action_mark_received()
        request.env["wms.task.lock"].sudo().release(task._name, task.id, user_id=user.id)
        return self._success(
            {
                "task": self._receipt_format_task(task, include_progress=True),
                "putaway_task_ids": task.putaway_task_ids.ids,
            },
            tts="收货完成",
        )

    def _receipt_get_task(self, user, warehouse, task_id):
        domain = [("id", "=", task_id)]
        if warehouse:
            domain.append(("warehouse_id", "=", warehouse.id))
        task = request.env["wms.receipt.task"].with_user(user).sudo().search(domain, limit=1)
        if not task:
            raise ValidationError("收货任务不存在或不属于当前仓库。")
        return task

    def _receipt_get_move(self, task, payload):
        move_id = int(payload.get("move_id") or payload.get("line_id") or 0)
        moves = self._receipt_task_moves(task)
        if move_id:
            move = moves.filtered(lambda record: record.id == move_id)[:1]
            if move:
                return move
            raise ValidationError("收货明细不存在。")
        barcode = (payload.get("barcode") or payload.get("product_barcode") or "").strip()
        if not barcode:
            raise ValidationError("请传入收货明细或商品条码。")
        matched = moves.filtered(lambda record: self._receipt_product_matches_barcode(record.product_id, barcode))[:1]
        if not matched:
            raise ValidationError("未找到匹配的商品明细。")
        return matched

    def _receipt_task_moves(self, task):
        picking = task.stock_picking_id
        if not picking:
            return request.env["stock.move"]
        moves = getattr(picking, "move_ids_without_package", False) or picking.move_ids
        return moves.filtered(lambda move: move.product_id)

    def _receipt_format_task(self, task, include_progress=False):
        result = {
            "id": task.id,
            "name": task.name,
            "state": task.state,
            "warehouse_id": task.warehouse_id.id,
            "warehouse_name": task.warehouse_id.display_name,
            "picking_id": task.stock_picking_id.id if task.stock_picking_id else False,
            "picking_name": task.stock_picking_id.name if task.stock_picking_id else "",
            "partner_id": task.partner_id.id if task.partner_id else False,
            "partner_name": task.partner_id.display_name if task.partner_id else "",
            "scheduled_date": task.scheduled_date,
        }
        if include_progress:
            moves = self._receipt_task_moves(task)
            done_moves = moves.filtered(lambda move: self._receipt_read_done_qty(move) > 0)
            result.update(
                {
                    "line_count": len(moves),
                    "done_line_count": len(done_moves),
                    "demand_qty": sum(moves.mapped("product_uom_qty")),
                    "done_qty": sum(self._receipt_read_done_qty(move) for move in moves),
                }
            )
        return result

    def _receipt_format_move(self, move):
        product = move.product_id
        return {
            "id": move.id,
            "product_id": product.id,
            "product_name": product.display_name,
            "default_code": product.default_code or "",
            "barcode": product.barcode or "",
            "demand_qty": move.product_uom_qty or 0.0,
            "done_qty": self._receipt_read_done_qty(move),
            "uom": move.product_uom.name if move.product_uom else "",
            "source_location_id": move.location_id.id if move.location_id else False,
            "source_location_name": move.location_id.display_name if move.location_id else "",
            "dest_location_id": move.location_dest_id.id if move.location_dest_id else False,
            "dest_location_name": move.location_dest_id.display_name if move.location_dest_id else "",
            "state": move.state,
        }

    def _receipt_read_done_qty(self, move):
        if "quantity" in move._fields:
            return move.quantity or 0.0
        if "quantity_done" in move._fields:
            return move.quantity_done or 0.0
        return 0.0

    def _receipt_write_done_qty(self, move, qty):
        if "quantity" in move._fields:
            move.write({"quantity": qty})
            return
        if "quantity_done" in move._fields:
            move.write({"quantity_done": qty})
            return
        raise ValidationError("当前库存明细没有可写入的实收数量字段。")

    def _receipt_float_payload(self, payload, key):
        value = payload.get(key)
        if value in (None, ""):
            raise ValidationError("请填写实收数量。")
        return float(value)

    def _receipt_product_matches_barcode(self, product, barcode):
        return barcode in {product.barcode, product.default_code, product.product_tmpl_id.default_code}
