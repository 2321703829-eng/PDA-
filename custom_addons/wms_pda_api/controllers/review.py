import json

from odoo import fields, http
from odoo.exceptions import AccessError, ValidationError
from odoo.http import Response, request


class WmsPdaReviewController(http.Controller):
    TASK_MODELS = {
        "receipt": ("wms.receipt.task", "收货任务"),
        "putaway": ("wms.putaway.task", "上架任务"),
        "outbound": ("wms.outbound.task", "出库任务"),
        "pick": ("wms.pick.task", "拣货任务"),
        "check": ("wms.check.task", "复核任务"),
        "handover": ("wms.handover.order", "交接单"),
    }
    EXCEPTION_STATES = {
        "receipt": "receipt_exception",
        "putaway": "putaway_exception",
        "outbound": "task_exception",
        "pick": "pick_exception",
        "check": "check_exception",
        "handover": "handover_exception",
    }

    @http.route("/api/admin/wms/review/tasks", type="http", auth="user", methods=["GET"], csrf=False)
    def list_review_tasks(self, **kwargs):
        return self._handle(lambda: self._list_tasks())

    @http.route(
        "/api/admin/wms/review/tasks/<int:task_id>/resolve",
        type="http",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def resolve_review_task(self, task_id, **kwargs):
        return self._handle(lambda: self._resolve_task(task_id))

    def _list_tasks(self):
        self._require_review_permission()
        params = request.params
        task_type = (params.get("task_type") or "").strip()
        offset = max(int(params.get("offset") or 0), 0)
        limit = min(max(int(params.get("limit") or 50), 1), 200)
        records = []
        for code in self._iter_task_codes(task_type):
            model_name, _label = self.TASK_MODELS[code]
            Model = request.env[model_name].sudo()
            if "review_state" not in Model._fields:
                continue
            exception_state = self.EXCEPTION_STATES[code]
            domain = ["|", ("review_state", "=", "pending_review"), ("state", "=", exception_state)]
            for task in Model.search(domain):
                records.append(self._format_task(code, task))
        records.sort(key=lambda item: item.get("submitted_at") or "", reverse=True)
        return {
            "total": len(records),
            "offset": offset,
            "limit": limit,
            "records": records[offset : offset + limit],
        }

    def _resolve_task(self, task_id):
        self._require_review_permission()
        payload = self._get_payload()
        action = (payload.get("action") or "").strip()
        reason = (payload.get("reason") or payload.get("review_note") or "").strip()
        task_type = (payload.get("task_type") or request.params.get("task_type") or "").strip()
        task = self._find_task(task_id, task_type)
        self._apply_adjustment(task, payload)
        task.pda_review_resolve(action, reason)
        return {
            "task_id": task.id,
            "task_type": self._task_code(task._name),
            "task_name": task.display_name,
            "review_state": task.review_state,
            "reviewer": task.review_user_id.display_name if task.review_user_id else "",
            "review_date": task.review_date or fields.Datetime.now(),
        }

    def _apply_adjustment(self, task, payload):
        adjusted_qty = payload.get("adjusted_qty")
        if adjusted_qty in (None, ""):
            return
        line_id = int(payload.get("line_id") or 0)
        move_id = int(payload.get("move_id") or 0)
        qty = float(adjusted_qty)
        if qty < 0:
            raise ValidationError("调整数量不能小于 0。")
        if task._name == "wms.pick.task":
            lines = task.line_ids
            line = lines.filtered(lambda item: item.id == line_id)[:1] if line_id else lines[:1]
            if not line:
                raise ValidationError("未找到可调整的拣货明细。")
            line.write({"done_qty": qty})
        elif task._name == "wms.receipt.task":
            moves = task.stock_picking_id.move_ids_without_package or task.stock_picking_id.move_ids
            move = moves.filtered(lambda item: item.id == move_id)[:1] if move_id else moves[:1]
            if not move:
                raise ValidationError("未找到可调整的收货明细。")
            if "quantity" in move._fields:
                move.write({"quantity": qty})
            elif "quantity_done" in move._fields:
                move.write({"quantity_done": qty})
            else:
                raise ValidationError("当前收货明细没有可调整的实收数量字段。")
        else:
            raise ValidationError("当前任务类型暂不支持直接调整数量。")

    def _find_task(self, task_id, task_type):
        matches = []
        for code in self._iter_task_codes(task_type):
            model_name, _label = self.TASK_MODELS[code]
            task = request.env[model_name].sudo().browse(task_id)
            if task.exists():
                matches.append(task)
        if not matches:
            raise ValidationError("待审核任务不存在。")
        if len(matches) > 1 and not task_type:
            raise ValidationError("任务编号不唯一，请传入 task_type。")
        return matches[0]

    def _format_task(self, code, task):
        picking = self._task_picking(task)
        return {
            "id": task.id,
            "task_type": code,
            "task_type_label": self.TASK_MODELS[code][1],
            "task_name": task.display_name,
            "review_state": task.review_state,
            "exception_note": task.exception_note or task.note or "",
            "operator_name": task.write_uid.display_name if task.write_uid else "",
            "submitted_at": task.write_date,
            "picking_id": picking.id if picking else False,
            "picking_name": picking.name if picking else "",
            "diff_summary": self._diff_summary(task),
        }

    def _diff_summary(self, task):
        if task._name == "wms.pick.task":
            demand = sum(task.line_ids.mapped("demand_qty"))
            done = sum(task.line_ids.mapped("done_qty"))
            return f"需求{demand:g}, 实拣{done:g}, 差{demand - done:g}"
        if task._name == "wms.receipt.task" and task.stock_picking_id:
            moves = task.stock_picking_id.move_ids_without_package or task.stock_picking_id.move_ids
            demand = sum(moves.mapped("product_uom_qty"))
            done = sum(self._read_move_done_qty(move) for move in moves)
            return f"预期{demand:g}, 实收{done:g}, 差{demand - done:g}"
        return ""

    def _read_move_done_qty(self, move):
        if "quantity" in move._fields:
            return move.quantity or 0.0
        if "quantity_done" in move._fields:
            return move.quantity_done or 0.0
        return 0.0

    def _task_picking(self, task):
        if "stock_picking_id" in task._fields and task.stock_picking_id:
            return task.stock_picking_id
        if "outbound_task_id" in task._fields and task.outbound_task_id and task.outbound_task_id.stock_picking_id:
            return task.outbound_task_id.stock_picking_id
        return request.env["stock.picking"]

    def _task_code(self, model_name):
        for code, (name, _label) in self.TASK_MODELS.items():
            if name == model_name:
                return code
        return ""

    def _iter_task_codes(self, task_type):
        if task_type:
            if task_type not in self.TASK_MODELS:
                raise ValidationError("不支持的任务类型。")
            return [task_type]
        return list(self.TASK_MODELS)

    def _require_review_permission(self):
        user = request.env.user
        if not (user.has_group("wms_pda_api.group_pda_admin") or user.has_group("base.group_system")):
            raise AccessError("当前账号没有 PC 审核权限。")

    def _get_payload(self):
        payload = dict(request.params)
        if request.httprequest.mimetype == "application/json":
            body = request.httprequest.get_json(silent=True) or {}
            if isinstance(body, dict):
                payload.update({key: value for key, value in body.items() if value is not None})
        return payload

    def _handle(self, callback):
        try:
            return self._success(callback())
        except AccessError as exc:
            return self._error(1002, str(exc), status=403)
        except (ValidationError, ValueError) as exc:
            return self._error(2001, str(exc), status=400)
        except Exception as exc:
            return self._error(5000, str(exc), status=500)

    def _success(self, data):
        return self._response({"code": 0, "message": "success", "data": data})

    def _error(self, code, message, status=400):
        return self._response({"code": code, "message": message, "data": {}}, status=status)

    def _response(self, payload, status=200):
        return Response(
            json.dumps(payload, ensure_ascii=False, default=str),
            status=status,
            headers=[("Content-Type", "application/json; charset=utf-8")],
        )
