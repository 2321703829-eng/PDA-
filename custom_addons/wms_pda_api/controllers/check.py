from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from .base import WmsPdaBaseController


class WmsPdaCheckController(WmsPdaBaseController):
    STATE_LABELS = {
        "waiting_check": "待复核",
        "checking": "复核中",
        "checked": "已复核",
        "check_exception": "复核异常",
    }

    @http.route("/api/pda/wms/v1/check/tasks", type="http", auth="public", methods=["GET"], csrf=False)
    def list_check_tasks(self, **kwargs):
        payload = self._get_payload()
        return self._handle_request(lambda user, wh, token: self._list_tasks(user, wh, payload))

    @http.route(
        "/api/pda/wms/v1/check/tasks/<int:task_id>/lines",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_check_task_lines(self, task_id, **kwargs):
        return self._handle_request(lambda user, wh, token: self._get_lines(user, wh, task_id, lock=True))

    @http.route(
        "/api/pda/wms/v1/check/tasks/<int:task_id>/confirm-line",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def confirm_check_line(self, task_id, **kwargs):
        payload = self._get_payload()
        return self._handle_idempotent_request(payload, lambda user, wh, token: self._confirm_line(user, wh, task_id, payload))

    @http.route(
        "/api/pda/wms/v1/check/tasks/<int:task_id>/complete",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def complete_check_task(self, task_id, **kwargs):
        payload = self._get_payload()
        return self._handle_idempotent_request(payload, lambda user, wh, token: self._complete_task(user, wh, task_id, payload))

    @http.route(
        "/api/pda/wms/v1/check/tasks/<int:task_id>/summary",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_check_summary(self, task_id, **kwargs):
        return self._handle_request(lambda user, wh, token: self._summary_response(user, wh, task_id))

    def _list_tasks(self, user, warehouse, payload):
        if not warehouse:
            raise ValidationError("请先选择仓库。")
        offset = int(payload.get("offset") or 0)
        limit = min(int(payload.get("limit") or 20), 100)
        domain = [("warehouse_id", "=", warehouse.id), ("state", "in", ["waiting_check", "checking"])]
        Task = request.env["wms.check.task"].with_user(user).sudo()
        total = Task.search_count(domain)
        tasks = Task.search(domain, offset=offset, limit=limit, order="create_date asc, id asc")
        return {"total": total, "records": [self._format_task(task) for task in tasks]}

    def _get_lines(self, user, warehouse, task_id, lock=False):
        task = self._get_task(user, warehouse, task_id)
        if task.state == "waiting_check":
            task.action_start_check()
        if lock:
            request.env["wms.task.lock"].sudo().acquire(
                task._name,
                task.id,
                user.id,
                warehouse_id=warehouse.id if warehouse else False,
            )
        lines = self._ensure_check_lines(task)
        return {
            "task": self._format_task(task, include_lock=True),
            "lines": [self._format_line(line, idx + 1) for idx, line in enumerate(lines)],
            "progress": self._progress(task),
        }

    def _confirm_line(self, user, warehouse, task_id, payload):
        task = self._get_task(user, warehouse, task_id)
        if task.state == "checked":
            return self._error(self.ERR_STATE_CONFLICT, "复核任务已完成，不能重复确认。", status=400, tts="任务已完成")
        if task.state == "waiting_check":
            task.action_start_check()
        request.env["wms.task.lock"].sudo().acquire(
            task._name,
            task.id,
            user.id,
            warehouse_id=warehouse.id if warehouse else False,
        )
        line = self._get_check_line(task, payload)
        barcode = (payload.get("product_barcode") or payload.get("barcode") or "").strip()
        checked_qty = self._float_payload(payload, "checked_qty", fallback_key="done_qty")
        if checked_qty <= 0:
            raise ValidationError("复核数量必须大于 0。")
        if barcode and not self._product_matches_barcode(line.product_id, barcode):
            return self._error(self.ERR_BARCODE_UNKNOWN, "扫描商品与当前复核行不一致。", status=400, tts="商品不匹配")
        state = self._line_state(checked_qty, line.picked_qty)
        line.write({"checked_qty": checked_qty, "state": state})
        next_line = self._next_line(task)
        return self._success(
            {
                "line_id": line.id,
                "pick_line_id": line.pick_line_id.id if line.pick_line_id else False,
                "product_name": line.product_id.display_name,
                "checked_qty": checked_qty,
                "picked_qty": line.picked_qty,
                "status": state,
                "next_line": self._format_next_line(next_line) if next_line else {},
            },
            tts=self._check_tts(line, next_line),
        )

    def _complete_task(self, user, warehouse, task_id, payload):
        task = self._get_task(user, warehouse, task_id)
        if task.state == "checked":
            return {"task_state": task.state, "summary": self._completion_summary(task), "next_step": "handover"}
        if task.state not in ("waiting_check", "checking"):
            return self._error(self.ERR_STATE_CONFLICT, "当前状态不能完成复核。", status=400, tts="状态不允许")
        self._ensure_check_lines(task)
        task.action_mark_checked()
        self._save_photos(task, user, warehouse, payload)
        request.env["wms.task.lock"].sudo().release(task._name, task.id, user_id=user.id)
        return self._success(
            {
                "task_state": task.state,
                "summary": self._completion_summary(task),
                "handover_order_ids": task.outbound_task_id.handover_order_ids.ids if task.outbound_task_id else [],
                "next_step": "handover",
            },
            tts="复核完成，等待交接",
        )

    def _summary_response(self, user, warehouse, task_id):
        task = self._get_task(user, warehouse, task_id)
        self._ensure_check_lines(task)
        return {"task_id": task.id, "state": task.state, "progress": self._progress(task), "exceptions": []}

    def _get_task(self, user, warehouse, task_id):
        domain = [("id", "=", task_id)]
        if warehouse:
            domain.append(("warehouse_id", "=", warehouse.id))
        task = request.env["wms.check.task"].with_user(user).sudo().search(domain, limit=1)
        if not task:
            raise ValidationError("复核任务不存在或不属于当前仓库。")
        return task

    def _ensure_check_lines(self, task):
        CheckLine = request.env["wms.pda.check.line"].sudo()
        existing = CheckLine.search([("task_id", "=", task.id)])
        existing_pick_line_ids = set(existing.mapped("pick_line_id").ids)
        commands = []
        for pick_line in task.pick_task_id.line_ids:
            if pick_line.id in existing_pick_line_ids:
                continue
            commands.append(
                {
                    "task_id": task.id,
                    "pick_line_id": pick_line.id,
                    "product_id": pick_line.product_id.id,
                    "source_location_id": pick_line.source_location_id.id,
                    "demand_qty": pick_line.demand_qty,
                    "picked_qty": pick_line.done_qty,
                    "checked_qty": 0.0,
                    "state": "waiting",
                }
            )
        if commands:
            CheckLine.create(commands)
        return CheckLine.search([("task_id", "=", task.id)], order="id asc")

    def _get_check_line(self, task, payload):
        self._ensure_check_lines(task)
        line_id = int(payload.get("line_id") or payload.get("check_line_id") or 0)
        pick_line_id = int(payload.get("pick_line_id") or 0)
        lines = request.env["wms.pda.check.line"].sudo().search([("task_id", "=", task.id)])
        if line_id:
            line = lines.filtered(lambda item: item.id == line_id)[:1]
            if line:
                return line
            raise ValidationError("复核明细不存在。")
        if pick_line_id:
            line = lines.filtered(lambda item: item.pick_line_id.id == pick_line_id)[:1]
            if line:
                return line
            raise ValidationError("复核明细不存在。")
        barcode = (payload.get("product_barcode") or payload.get("barcode") or "").strip()
        if not barcode:
            raise ValidationError("请传入复核明细或商品条码。")
        line = lines.filtered(lambda item: self._product_matches_barcode(item.product_id, barcode))[:1]
        if not line:
            raise ValidationError("未找到匹配的复核明细。")
        return line

    def _format_task(self, task, include_lock=False):
        picking = task.outbound_task_id.stock_picking_id if task.outbound_task_id else False
        result = {
            "id": task.id,
            "name": task.name,
            "state": task.state,
            "state_label": self.STATE_LABELS.get(task.state, task.state),
            "outbound_task_id": task.outbound_task_id.id if task.outbound_task_id else False,
            "outbound_task_name": task.outbound_task_id.name if task.outbound_task_id else "",
            "pick_task_id": task.pick_task_id.id if task.pick_task_id else False,
            "pick_task_name": task.pick_task_id.name if task.pick_task_id else "",
            "picking_id": picking.id if picking else False,
            "picking_name": picking.name if picking else "",
            "partner_id": task.outbound_task_id.store_partner_id.id if task.outbound_task_id.store_partner_id else False,
            "partner_name": task.outbound_task_id.store_partner_id.display_name if task.outbound_task_id.store_partner_id else "",
            "line_count": len(task.pick_task_id.line_ids),
            "total_picked_qty": sum(task.pick_task_id.line_ids.mapped("done_qty")),
            "create_date": task.create_date,
        }
        if include_lock:
            result["locked_by"] = request.env["wms.task.lock"].sudo().get_lock_holder(task._name, task.id)
        return result

    def _format_line(self, line, seq=0):
        product = line.product_id
        return {
            "line_id": line.id,
            "pick_line_id": line.pick_line_id.id if line.pick_line_id else False,
            "seq": seq,
            "product_id": product.id,
            "product_name": product.display_name,
            "barcode": product.barcode or "",
            "default_code": product.default_code or "",
            "spec": getattr(product.product_tmpl_id, "specification", "") or "",
            "uom": product.uom_id.name or "",
            "demand_qty": line.demand_qty,
            "picked_qty": line.picked_qty,
            "checked_qty": line.checked_qty,
            "state": line.state,
            "source_location": line.source_location_id.display_name if line.source_location_id else "",
            "source_location_barcode": line.source_location_id.barcode if line.source_location_id else "",
        }

    def _format_next_line(self, line):
        return {
            "line_id": line.id,
            "product_name": line.product_id.display_name,
            "picked_qty": line.picked_qty,
            "source_location": line.source_location_id.display_name if line.source_location_id else "",
        }

    def _next_line(self, task):
        lines = request.env["wms.pda.check.line"].sudo().search([("task_id", "=", task.id)], order="id asc")
        return lines.filtered(lambda line: line.state in ("waiting", "partial"))[:1]

    def _progress(self, task):
        lines = self._ensure_check_lines(task)
        total_lines = len(lines)
        completed_lines = len(lines.filtered(lambda line: line.state in ("full", "over")))
        total_picked_qty = sum(lines.mapped("picked_qty"))
        total_checked_qty = sum(lines.mapped("checked_qty"))
        return {
            "total_lines": total_lines,
            "completed_lines": completed_lines,
            "pending_lines": max(total_lines - completed_lines, 0),
            "total_picked_qty": total_picked_qty,
            "total_checked_qty": total_checked_qty,
            "completion_pct": round(total_checked_qty / total_picked_qty * 100, 2) if total_picked_qty else 0.0,
        }

    def _completion_summary(self, task):
        lines = self._ensure_check_lines(task)
        return {
            "total_lines": len(lines),
            "total_checked_qty": sum(lines.mapped("checked_qty")),
            "diff_lines": len(lines.filtered(lambda line: line.checked_qty != line.picked_qty)),
        }

    def _save_photos(self, task, user, warehouse, payload):
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

    def _float_payload(self, payload, key, fallback_key=False):
        value = payload.get(key)
        if value in (None, "") and fallback_key:
            value = payload.get(fallback_key)
        if value in (None, ""):
            raise ValidationError("请填写复核数量。")
        return float(value)

    def _line_state(self, checked_qty, picked_qty):
        if checked_qty == picked_qty:
            return "full"
        if checked_qty < picked_qty:
            return "partial"
        return "over"

    def _product_matches_barcode(self, product, barcode):
        return barcode in {product.barcode, product.default_code, product.product_tmpl_id.default_code}

    def _check_tts(self, line, next_line):
        current = f"{line.product_id.display_name}{line.checked_qty:g}{line.product_id.uom_id.name or ''}"
        if not next_line:
            return f"{current}，复核完成"
        next_text = f"下一个，{next_line.product_id.display_name}{next_line.picked_qty:g}{next_line.product_id.uom_id.name or ''}"
        return f"{current}，{next_text}"
