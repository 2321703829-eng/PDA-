from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from .base import WmsPdaBaseController


class WmsPdaPickController(WmsPdaBaseController):
    STATE_LABELS = {
        "waiting_pick": "待拣货",
        "picking": "拣货中",
        "picked": "已拣货",
        "pick_exception": "拣货异常",
    }

    @http.route("/api/pda/wms/v1/pick/tasks", type="http", auth="public", methods=["GET"], csrf=False)
    def list_pick_tasks(self, **kwargs):
        payload = self._get_payload()
        return self._handle_request(lambda user, wh, token: self._pick_list_tasks(user, wh, payload))

    @http.route(
        "/api/pda/wms/v1/pick/tasks/<int:task_id>/lines",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_pick_task_lines(self, task_id, **kwargs):
        return self._handle_request(lambda user, wh, token: self._pick_get_lines(user, wh, task_id, lock=True))

    @http.route(
        "/api/pda/wms/v1/pick/tasks/<int:task_id>/confirm-line",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def confirm_pick_line(self, task_id, **kwargs):
        payload = self._get_payload()
        return self._handle_idempotent_request(payload, lambda user, wh, token: self._pick_confirm_line(user, wh, task_id, payload))

    @http.route(
        "/api/pda/wms/v1/pick/tasks/<int:task_id>/complete",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def complete_pick_task(self, task_id, **kwargs):
        payload = self._get_payload()
        return self._handle_idempotent_request(payload, lambda user, wh, token: self._pick_complete_task(user, wh, task_id, payload))

    @http.route(
        "/api/pda/wms/v1/pick/tasks/<int:task_id>/summary",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_pick_summary(self, task_id, **kwargs):
        return self._handle_request(lambda user, wh, token: self._pick_summary_response(user, wh, task_id))

    def _pick_list_tasks(self, user, warehouse, payload):
        if not warehouse:
            raise ValidationError("请先选择仓库。")
        offset = int(payload.get("offset") or 0)
        limit = min(int(payload.get("limit") or 20), 100)
        domain = [("warehouse_id", "=", warehouse.id), ("state", "in", ["waiting_pick", "picking"])]
        Task = request.env["wms.pick.task"].with_user(user).sudo()
        total = Task.search_count(domain)
        tasks = Task.search(domain, offset=offset, limit=limit, order="create_date asc, id asc")
        return {"total": total, "records": [self._pick_format_task(task) for task in tasks]}

    def _pick_get_lines(self, user, warehouse, task_id, lock=False):
        task = self._pick_get_task(user, warehouse, task_id)
        if task.state == "waiting_pick":
            task.action_start_pick()
        if lock:
            request.env["wms.task.lock"].sudo().acquire(
                task._name,
                task.id,
                user.id,
                warehouse_id=warehouse.id if warehouse else False,
            )
        return {
            "task": self._pick_format_task(task, include_lock=True),
            "lines": [self._pick_format_line(line, idx + 1) for idx, line in enumerate(self._pick_ordered_lines(task))],
            "progress": self._pick_progress(task),
        }

    def _pick_confirm_line(self, user, warehouse, task_id, payload):
        task = self._pick_get_task(user, warehouse, task_id)
        if task.state == "picked":
            return self._error(self.ERR_STATE_CONFLICT, "拣货任务已完成，不能重复确认。", status=400, tts="任务已完成")
        request.env["wms.task.lock"].sudo().acquire(
            task._name,
            task.id,
            user.id,
            warehouse_id=warehouse.id if warehouse else False,
        )
        if task.state == "waiting_pick":
            task.action_start_pick()
        line = self._pick_get_line(task, payload)
        product_barcode = (payload.get("product_barcode") or payload.get("barcode") or "").strip()
        location_barcode = (payload.get("location_barcode") or "").strip()
        done_qty = self._pick_float_payload(payload, "done_qty")
        if done_qty <= 0:
            raise ValidationError("拣货数量必须大于 0。")
        if product_barcode and not self._pick_product_matches_barcode(line.product_id, product_barcode):
            return self._error(self.ERR_BARCODE_UNKNOWN, "扫描商品与当前拣货行不一致。", status=400, tts="商品不匹配")
        if location_barcode and line.source_location_id and line.source_location_id.barcode != location_barcode:
            return self._error(self.ERR_STATE_CONFLICT, "扫描库位与当前拣货行不一致。", status=400, tts="库位不匹配")
        line.write({"done_qty": done_qty})
        status = "full"
        if done_qty < line.demand_qty:
            status = "partial"
        elif done_qty > line.demand_qty:
            status = "over"
        next_line = self._pick_next_line(task)
        return self._success(
            {
                "line_id": line.id,
                "product_name": line.product_id.display_name,
                "done_qty": done_qty,
                "demand_qty": line.demand_qty,
                "status": status,
                "next_line": self._pick_format_next_line(next_line) if next_line else {},
            },
            tts=self._pick_pick_tts(line, next_line),
        )

    def _pick_complete_task(self, user, warehouse, task_id, payload):
        task = self._pick_get_task(user, warehouse, task_id)
        if task.state == "picked":
            return {"task_state": task.state, "summary": self._pick_completion_summary(task), "next_step": "check"}
        if task.state not in ("waiting_pick", "picking"):
            return self._error(self.ERR_STATE_CONFLICT, "当前状态不能完成拣货。", status=400, tts="状态不允许")
        self._pick_sync_lines_to_stock_moves(task)
        task.action_mark_picked()
        self._pick_validate_picking(task)
        self._pick_save_photos(task, user, warehouse, payload)
        request.env["wms.task.lock"].sudo().release(task._name, task.id, user_id=user.id)
        return self._success(
            {"task_state": task.state, "summary": self._pick_completion_summary(task), "next_step": "check"},
            tts="拣货完成，等待复核",
        )

    def _pick_summary_response(self, user, warehouse, task_id):
        task = self._pick_get_task(user, warehouse, task_id)
        return {
            "task_id": task.id,
            "state": task.state,
            "progress": self._pick_progress(task),
            "exceptions": [],
        }

    def _pick_get_task(self, user, warehouse, task_id):
        domain = [("id", "=", task_id)]
        if warehouse:
            domain.append(("warehouse_id", "=", warehouse.id))
        task = request.env["wms.pick.task"].with_user(user).sudo().search(domain, limit=1)
        if not task:
            raise ValidationError("拣货任务不存在或不属于当前仓库。")
        return task

    def _pick_get_line(self, task, payload):
        line_id = int(payload.get("line_id") or 0)
        if line_id:
            line = task.line_ids.filtered(lambda item: item.id == line_id)[:1]
            if line:
                return line
            raise ValidationError("拣货明细不存在。")
        barcode = (payload.get("product_barcode") or payload.get("barcode") or "").strip()
        if not barcode:
            raise ValidationError("请传入拣货明细或商品条码。")
        line = task.line_ids.filtered(lambda item: self._pick_product_matches_barcode(item.product_id, barcode))[:1]
        if not line:
            raise ValidationError("未找到匹配的拣货明细。")
        return line

    def _pick_ordered_lines(self, task):
        return task.line_ids.sorted(key=lambda line: self._pick_line_sort_key(line))

    def _pick_line_sort_key(self, line):
        if "path_seq" in line._fields:
            return (line.path_seq or 0, line.id)
        return (line.source_location_id.id or 0, line.id)

    def _pick_format_task(self, task, include_lock=False):
        picking = task.outbound_task_id.stock_picking_id
        result = {
            "id": task.id,
            "name": task.name,
            "state": task.state,
            "state_label": self.STATE_LABELS.get(task.state, task.state),
            "outbound_task_id": task.outbound_task_id.id,
            "outbound_task_name": task.outbound_task_id.name,
            "picking_id": picking.id if picking else False,
            "picking_name": picking.name if picking else "",
            "partner_id": task.store_partner_id.id if task.store_partner_id else False,
            "partner_name": task.store_partner_id.display_name if task.store_partner_id else "",
            "line_count": len(task.line_ids),
            "product_summary": self._pick_product_summary(task.line_ids),
            "source_location": self._pick_first_source_location(task),
            "total_demand_qty": sum(task.line_ids.mapped("demand_qty")),
            "done_qty": sum(task.line_ids.mapped("done_qty")),
            "create_date": task.create_date,
        }
        if include_lock:
            result["locked_by"] = request.env["wms.task.lock"].sudo().get_lock_holder(task._name, task.id)
        return result

    def _pick_product_summary(self, lines):
        products = lines.mapped("product_id")
        if not products:
            return ""
        first_name = products[:1].display_name
        return first_name if len(products) == 1 else f"{first_name} 等{len(products)}种商品"

    def _pick_first_source_location(self, task):
        line = self._pick_ordered_lines(task)[:1]
        return line.source_location_id.display_name if line and line.source_location_id else ""

    def _pick_format_line(self, line, seq=0):
        product = line.product_id
        return {
            "line_id": line.id,
            "seq": seq,
            "product_id": product.id,
            "product_name": product.display_name,
            "barcode": product.barcode or "",
            "default_code": product.default_code or "",
            "spec": getattr(product.product_tmpl_id, "specification", "") or "",
            "uom": product.uom_id.name or "",
            "demand_qty": line.demand_qty,
            "done_qty": line.done_qty,
            "source_location": line.source_location_id.display_name if line.source_location_id else "",
            "source_location_barcode": line.source_location_id.barcode if line.source_location_id else "",
            "path_seq": self._pick_line_sort_key(line)[0],
        }

    def _pick_format_next_line(self, line):
        return {
            "line_id": line.id,
            "product_name": line.product_id.display_name,
            "source_location": line.source_location_id.display_name if line.source_location_id else "",
            "demand_qty": line.demand_qty,
        }

    def _pick_next_line(self, task):
        return self._pick_ordered_lines(task).filtered(lambda line: line.done_qty < line.demand_qty)[:1]

    def _pick_progress(self, task):
        lines = task.line_ids
        total_lines = len(lines)
        completed_lines = len(lines.filtered(lambda line: line.done_qty >= line.demand_qty and line.demand_qty > 0))
        total_demand_qty = sum(lines.mapped("demand_qty"))
        total_done_qty = sum(lines.mapped("done_qty"))
        return {
            "total_lines": total_lines,
            "completed_lines": completed_lines,
            "pending_lines": max(total_lines - completed_lines, 0),
            "total_demand_qty": total_demand_qty,
            "total_done_qty": total_done_qty,
            "completion_pct": round(total_done_qty / total_demand_qty * 100, 2) if total_demand_qty else 0.0,
        }

    def _pick_completion_summary(self, task):
        lines = task.line_ids
        return {
            "total_lines": len(lines),
            "total_done_qty": sum(lines.mapped("done_qty")),
            "short_lines": len(lines.filtered(lambda line: line.done_qty < line.demand_qty)),
        }

    def _pick_sync_lines_to_stock_moves(self, task):
        picking = task.outbound_task_id.stock_picking_id
        if not picking:
            return
        for line in task.line_ids:
            move = picking.move_ids.filtered(
                lambda item: item.product_id.id == line.product_id.id
                and (not line.source_location_id or item.location_id.id == line.source_location_id.id)
            )[:1]
            if move:
                self._pick_write_done_qty(move, line.done_qty)

    def _pick_validate_picking(self, task):
        picking = task.outbound_task_id.stock_picking_id
        if not picking or picking.state == "done":
            return
        if hasattr(picking, "action_assign"):
            picking.action_assign()
        if hasattr(picking, "button_validate"):
            picking.button_validate()

    def _pick_save_photos(self, task, user, warehouse, payload):
        for url in payload.get("photo_urls") or []:
            request.env["wms.task.photo"].sudo().create(
                {
                    "task_model": task._name,
                    "task_id": task.id,
                    "photo_url": url,
                    "operator_id": user.id,
                    "warehouse_id": warehouse.id if warehouse else False,
                    "device_id": (payload.get("device_id") or "").strip(),
                    "gps": (payload.get("gps") or "").strip(),
                    "note": (payload.get("note") or "").strip(),
                }
            )

    def _pick_write_done_qty(self, move, qty):
        if "quantity" in move._fields:
            move.write({"quantity": qty})
            return
        if "quantity_done" in move._fields:
            move.write({"quantity_done": qty})

    def _pick_float_payload(self, payload, key):
        value = payload.get(key)
        if value in (None, ""):
            raise ValidationError("请填写拣货数量。")
        return float(value)

    def _pick_product_matches_barcode(self, product, barcode):
        return barcode in {product.barcode, product.default_code, product.product_tmpl_id.default_code}

    def _pick_pick_tts(self, line, next_line):
        current = f"{line.product_id.display_name}{line.done_qty:g}{line.product_id.uom_id.name or ''}"
        if not next_line:
            return f"{current}，拣货完成"
        next_text = f"下一个，{next_line.source_location_id.display_name if next_line.source_location_id else ''}，{next_line.product_id.display_name}{next_line.demand_qty:g}{next_line.product_id.uom_id.name or ''}"
        return f"{current}，{next_text}"
