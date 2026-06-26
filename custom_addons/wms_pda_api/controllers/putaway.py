from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from .base import WmsPdaBaseController


class WmsPdaPutawayController(WmsPdaBaseController):
    STATE_LABELS = {
        "waiting_putaway": "待上架",
        "putaway_ing": "上架中",
        "putaway_done": "已上架",
        "putaway_exception": "上架异常",
    }

    @http.route("/api/pda/wms/v1/putaway/tasks", type="http", auth="public", methods=["GET"], csrf=False)
    def list_putaway_tasks(self, **kwargs):
        payload = self._get_payload()
        return self._handle_request(lambda user, wh, token: self._putaway_list_tasks(user, wh, payload))

    @http.route(
        "/api/pda/wms/v1/putaway/tasks/<int:task_id>/lines",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_putaway_task_lines(self, task_id, **kwargs):
        payload = self._get_payload()
        lock = str(payload.get("lock", "1")).strip().lower() not in ("0", "false", "no")
        return self._handle_request(lambda user, wh, token: self._putaway_get_task_lines(user, wh, task_id, lock=lock))

    @http.route(
        "/api/pda/wms/v1/putaway/tasks/<int:task_id>/confirm",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def confirm_putaway(self, task_id, **kwargs):
        payload = self._get_payload()
        return self._handle_idempotent_request(payload, lambda user, wh, token: self._putaway_confirm_putaway(user, wh, task_id, payload))

    @http.route(
        "/api/pda/wms/v1/putaway/tasks/<int:task_id>/complete",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def complete_putaway(self, task_id, **kwargs):
        payload = self._get_payload()
        return self._handle_idempotent_request(payload, lambda user, wh, token: self._putaway_complete_task(user, wh, task_id))

    def _putaway_list_tasks(self, user, warehouse, payload):
        if not warehouse:
            raise ValidationError("请先选择仓库。")
        offset = int(payload.get("offset") or 0)
        limit = min(int(payload.get("limit") or 20), 100)
        state = (payload.get("state") or payload.get("status") or "waiting").strip()
        states = ["putaway_done"] if state in ("done", "putaway_done") else ["waiting_putaway", "putaway_ing"]
        domain = [("warehouse_id", "=", warehouse.id), ("state", "in", states)]
        Task = request.env["wms.putaway.task"].with_user(user).sudo()
        total = Task.search_count(domain)
        tasks = Task.search(domain, offset=offset, limit=limit, order="id desc")
        return {
            "total": total,
            "records": [self._putaway_format_task(task, include_summary=True) for task in tasks],
        }

    def _putaway_get_task_lines(self, user, warehouse, task_id, lock=False):
        task = self._putaway_get_task(user, warehouse, task_id)
        if lock:
            request.env["wms.task.lock"].sudo().acquire(
                task._name,
                task.id,
                user.id,
                warehouse_id=warehouse.id if warehouse else False,
            )
        return {
            "task": self._putaway_format_task(task, include_summary=True),
            "lines": [self._putaway_format_move(move, task) for move in self._putaway_task_moves(task)],
        }

    def _putaway_confirm_putaway(self, user, warehouse, task_id, payload):
        task = self._putaway_get_task(user, warehouse, task_id)
        if task.state == "putaway_done":
            return self._error(self.ERR_STATE_CONFLICT, "上架任务已完成，不能重复确认。", status=400, tts="任务已完成")
        if task.state not in ("waiting_putaway", "putaway_ing"):
            return self._error(self.ERR_STATE_CONFLICT, "当前状态不能确认上架。", status=400, tts="状态不允许")
        request.env["wms.task.lock"].sudo().acquire(
            task._name,
            task.id,
            user.id,
            warehouse_id=warehouse.id if warehouse else False,
        )
        product_barcode = (payload.get("product_barcode") or payload.get("barcode") or "").strip()
        location_barcode = (payload.get("dest_location_barcode") or payload.get("location_barcode") or "").strip()
        qty = self._putaway_float_payload(payload, "qty")
        if qty <= 0:
            raise ValidationError("上架数量必须大于 0。")
        if not product_barcode:
            raise ValidationError("请扫描商品条码。")
        if not location_barcode:
            raise ValidationError("请扫描目标库位。")
        move = self._putaway_match_source_move(task, product_barcode)
        product = move.product_id
        remaining_qty = self._putaway_remaining_qty(task, product)
        if remaining_qty and qty > remaining_qty:
            return self._error(self.ERR_QTY_EXCEED, "上架数量不能超过待上架数量。", status=400, tts="数量超出")
        dest_location = self._putaway_find_location(warehouse, location_barcode)
        source_location = task.source_location_id or task.stock_picking_id.location_dest_id
        if not source_location:
            raise ValidationError("上架任务缺少来源库位。")
        if task.state == "waiting_putaway":
            task.action_start_putaway()
        internal_move = self._putaway_create_done_internal_move(task, product, qty, source_location, dest_location)
        task.write({"dest_location_id": dest_location.id})
        remaining_products = len(
            [
                source_move
                for source_move in self._putaway_task_moves(task)
                if self._putaway_remaining_qty(task, source_move.product_id) > 0
            ]
        )
        return self._success(
            {
                "product_name": product.display_name,
                "dest_location": dest_location.display_name,
                "qty": qty,
                "move_id": internal_move.id,
                "remaining_products": remaining_products,
            },
            tts=f"{product.display_name}，上架到{dest_location.display_name}，{qty:g}",
        )

    def _putaway_complete_task(self, user, warehouse, task_id):
        task = self._putaway_get_task(user, warehouse, task_id)
        if task.state == "putaway_done":
            summary = self._putaway_summary(task)
            return {"task_state": task.state, "summary": summary}
        if task.state not in ("waiting_putaway", "putaway_ing"):
            return self._error(self.ERR_STATE_CONFLICT, "当前状态不能完成上架。", status=400, tts="状态不允许")
        remaining_moves = [
            source_move
            for source_move in self._putaway_task_moves(task)
            if self._putaway_remaining_qty(task, source_move.product_id) > 0
        ]
        if remaining_moves:
            return self._error(self.ERR_STATE_CONFLICT, "还有商品未上架完成，不能完成上架。", status=400, tts="还有商品未上架")
        task.action_mark_done()
        request.env["wms.task.lock"].sudo().release(task._name, task.id, user_id=user.id)
        return self._success({"task_state": task.state, "summary": self._putaway_summary(task)}, tts="上架完成")

    def _putaway_get_task(self, user, warehouse, task_id):
        domain = [("id", "=", task_id)]
        if warehouse:
            domain.append(("warehouse_id", "=", warehouse.id))
        task = request.env["wms.putaway.task"].with_user(user).sudo().search(domain, limit=1)
        if not task:
            raise ValidationError("上架任务不存在或不属于当前仓库。")
        return task

    def _putaway_task_moves(self, task):
        picking = task.stock_picking_id
        if not picking:
            return request.env["stock.move"]
        moves = getattr(picking, "move_ids_without_package", False) or picking.move_ids
        return moves.filtered(lambda move: move.product_id)

    def _putaway_match_source_move(self, task, barcode):
        moves = self._putaway_task_moves(task)
        matched = moves.filtered(lambda move: self._putaway_product_matches_barcode(move.product_id, barcode))[:1]
        if not matched:
            raise ValidationError("未找到匹配的待上架商品。")
        return matched

    def _putaway_find_location(self, warehouse, barcode):
        domain = [("barcode", "=", barcode)]
        if warehouse:
            domain = [
                ("barcode", "=", barcode),
                "|",
                ("id", "child_of", warehouse.view_location_id.id),
                ("id", "=", warehouse.lot_stock_id.id),
            ]
        location = request.env["stock.location"].sudo().search(domain, limit=1)
        if not location:
            raise ValidationError("目标库位不存在或不属于当前仓库。")
        return location

    def _putaway_create_done_internal_move(self, task, product, qty, source_location, dest_location):
        vals = {
            "product_id": product.id,
            "product_uom_qty": qty,
            "product_uom": product.uom_id.id,
            "location_id": source_location.id,
            "location_dest_id": dest_location.id,
            "origin": task.name,
        }
        if "name" in request.env["stock.move"]._fields:
            vals["name"] = f"??: {task.name} - {product.display_name}"
        if task.stock_picking_id and "company_id" in request.env["stock.move"]._fields:
            vals["company_id"] = task.stock_picking_id.company_id.id
        if task.warehouse_id and getattr(task.warehouse_id, "int_type_id", False):
            vals["picking_type_id"] = task.warehouse_id.int_type_id.id
        move = request.env["stock.move"].sudo().create(vals)
        if hasattr(move, "_action_confirm"):
            move._action_confirm()
        if hasattr(move, "_action_assign"):
            move._action_assign()
        self._putaway_write_done_qty(move, qty)
        if "picked" in move._fields:
            move.write({"picked": True})
        if hasattr(move, "_action_done"):
            move._action_done()
        return move

    def _putaway_format_task(self, task, include_summary=False):
        result = {
            "id": task.id,
            "name": task.name,
            "state": task.state,
            "state_label": self.STATE_LABELS.get(task.state, task.state),
            "receipt_task_id": task.receipt_task_id.id if task.receipt_task_id else False,
            "receipt_task_name": task.receipt_task_id.name if task.receipt_task_id else "",
            "picking_id": task.stock_picking_id.id if task.stock_picking_id else False,
            "picking_name": task.stock_picking_id.name if task.stock_picking_id else "",
            "source_location": task.source_location_id.display_name if task.source_location_id else "",
            "dest_location": task.dest_location_id.display_name if task.dest_location_id else "",
            "source_location_barcode": task.source_location_id.barcode if task.source_location_id else "",
            "dest_location_barcode": task.dest_location_id.barcode if task.dest_location_id else "",
            "create_date": task.create_date,
        }
        if include_summary:
            moves = self._putaway_task_moves(task)
            result.update(
                {
                    "product_summary": self._putaway_product_summary(moves),
                    "total_qty": sum(moves.mapped("product_uom_qty")),
                    "putaway_qty": sum(self._putaway_putaway_qty(task, move.product_id) for move in moves),
                    "lines": [self._putaway_format_move(move, task) for move in moves],
                }
            )
        return result

    def _putaway_format_move(self, move, task):
        product = move.product_id
        putaway_qty = self._putaway_putaway_qty(task, product)
        demand_qty = move.product_uom_qty or 0.0
        return {
            "id": move.id,
            "product_id": product.id,
            "product_name": product.display_name,
            "default_code": product.default_code or "",
            "barcode": product.barcode or "",
            "demand_qty": demand_qty,
            "putaway_qty": putaway_qty,
            "remaining_qty": max(demand_qty - putaway_qty, 0.0),
            "uom": move.product_uom.name if move.product_uom else "",
            "dest_location": task.dest_location_id.display_name if task.dest_location_id else "",
            "dest_location_barcode": task.dest_location_id.barcode if task.dest_location_id else "",
        }

    def _putaway_summary(self, task):
        moves = self._putaway_task_moves(task)
        locations = self._putaway_putaway_moves(task).mapped("location_dest_id")
        return {
            "products_count": len(moves.mapped("product_id")),
            "locations_used": len(locations),
            "total_qty": sum(self._putaway_putaway_qty(task, move.product_id) for move in moves),
        }

    def _putaway_remaining_qty(self, task, product):
        source_move = self._putaway_task_moves(task).filtered(lambda move: move.product_id.id == product.id)[:1]
        return max((source_move.product_uom_qty or 0.0) - self._putaway_putaway_qty(task, product), 0.0)

    def _putaway_putaway_qty(self, task, product):
        moves = self._putaway_putaway_moves(task).filtered(lambda move: move.product_id.id == product.id)
        return sum(self._putaway_read_done_qty(move) or move.product_uom_qty or 0.0 for move in moves)

    def _putaway_putaway_moves(self, task):
        return request.env["stock.move"].sudo().search(
            [
                ("origin", "=", task.name),
                ("state", "=", "done"),
            ]
        )

    def _putaway_read_done_qty(self, move):
        if "quantity" in move._fields:
            return move.quantity or 0.0
        if "quantity_done" in move._fields:
            return move.quantity_done or 0.0
        return 0.0

    def _putaway_write_done_qty(self, move, qty):
        if "quantity" in move._fields:
            move.write({"quantity": qty})
            return
        if "quantity_done" in move._fields:
            move.write({"quantity_done": qty})
            return

    def _putaway_float_payload(self, payload, key):
        value = payload.get(key)
        if value in (None, ""):
            raise ValidationError("请填写上架数量。")
        return float(value)

    def _putaway_product_matches_barcode(self, product, barcode):
        return barcode in {product.barcode, product.default_code, product.product_tmpl_id.default_code}

    def _putaway_product_summary(self, moves):
        products = moves.mapped("product_id")
        if not products:
            return ""
        first_name = products[:1].display_name
        return first_name if len(products) == 1 else f"{first_name} 等{len(products)}种商品"
