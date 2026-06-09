from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from .base import WmsPdaBaseController


class WmsPdaHandoverController(WmsPdaBaseController):
    STATE_LABELS = {
        "waiting_handover": "待交接",
        "handover_ing": "交接中",
        "handover_done": "已交接",
        "handover_exception": "交接异常",
    }

    @http.route("/api/pda/wms/v1/handover/orders", type="http", auth="public", methods=["GET"], csrf=False)
    def list_handover_orders(self, **kwargs):
        payload = self._get_payload()
        return self._handle_request(lambda user, wh, token: self._list_orders(user, wh, payload))

    @http.route(
        "/api/pda/wms/v1/handover/orders/<int:order_id>",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_handover_order(self, order_id, **kwargs):
        return self._handle_request(lambda user, wh, token: self._get_order_detail(user, wh, order_id, lock=True))

    @http.route(
        "/api/pda/wms/v1/handover/orders/<int:order_id>/confirm",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def confirm_handover_order(self, order_id, **kwargs):
        return self._handle_request(lambda user, wh, token: self._confirm_order(user, wh, order_id))

    @http.route(
        "/api/pda/wms/v1/handover/orders/<int:order_id>/complete",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def complete_handover_order(self, order_id, **kwargs):
        return self._handle_request(lambda user, wh, token: self._complete_order(user, wh, order_id))

    @http.route(
        "/api/pda/wms/v1/handover/orders/<int:order_id>/prepare-route-batch",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def prepare_route_batch(self, order_id, **kwargs):
        return self._handle_request(lambda user, wh, token: self._prepare_route_batch(user, wh, order_id))

    def _list_orders(self, user, warehouse, payload):
        if not warehouse:
            raise ValidationError("请先选择仓库。")
        offset = int(payload.get("offset") or 0)
        limit = min(int(payload.get("limit") or 20), 100)
        domain = [("warehouse_id", "=", warehouse.id)]
        state = (payload.get("state") or "").strip()
        if state:
            domain.append(("state", "=", state))
        else:
            domain.append(("state", "in", ["waiting_handover", "handover_ing"]))
        Handover = request.env["wms.handover.order"].with_user(user).sudo()
        total = Handover.search_count(domain)
        orders = Handover.search(domain, offset=offset, limit=limit, order="create_date asc, id asc")
        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "records": [self._format_order(order) for order in orders],
        }

    def _get_order_detail(self, user, warehouse, order_id, lock=False):
        handover = self._get_order(user, warehouse, order_id)
        if lock:
            request.env["wms.task.lock"].sudo().acquire(
                handover._name,
                handover.id,
                user.id,
                warehouse_id=warehouse.id if warehouse else False,
            )
        return {"order": self._format_order(handover, include_lock=True)}

    def _confirm_order(self, user, warehouse, order_id):
        handover = self._get_order(user, warehouse, order_id)
        if handover.state == "handover_done":
            return self._error(self.ERR_STATE_CONFLICT, "交接单已完成，不能重复确认。", status=400, tts="交接已完成")
        if handover.state not in ("waiting_handover", "handover_ing"):
            return self._error(self.ERR_STATE_CONFLICT, "当前状态不能确认交接。", status=400, tts="状态不允许")
        request.env["wms.task.lock"].sudo().acquire(
            handover._name,
            handover.id,
            user.id,
            warehouse_id=warehouse.id if warehouse else False,
        )
        if handover.state == "waiting_handover":
            handover.action_start_handover()
        return self._success({"order": self._format_order(handover, include_lock=True)}, tts="开始交接")

    def _complete_order(self, user, warehouse, order_id):
        handover = self._get_order(user, warehouse, order_id)
        if handover.state == "handover_done":
            return {
                "order": self._format_order(handover, include_lock=True),
                "next_step": "dispatch",
            }
        if handover.state not in ("waiting_handover", "handover_ing"):
            return self._error(self.ERR_STATE_CONFLICT, "当前状态不能完成交接。", status=400, tts="状态不允许")
        request.env["wms.task.lock"].sudo().acquire(
            handover._name,
            handover.id,
            user.id,
            warehouse_id=warehouse.id if warehouse else False,
        )
        handover.action_mark_done()
        request.env["wms.task.lock"].sudo().release(handover._name, handover.id, user_id=user.id)
        return self._success(
            {
                "order": self._format_order(handover),
                "next_step": "dispatch",
            },
            tts="交接完成",
        )

    def _prepare_route_batch(self, user, warehouse, order_id):
        handover = self._get_order(user, warehouse, order_id)
        action = getattr(handover, "action_prepare_route_batch", None)
        if not action:
            return self._error(
                self.ERR_STATE_CONFLICT,
                "当前交接单暂未接入排线批次生成动作。",
                status=400,
            )
        request.env["wms.task.lock"].sudo().acquire(
            handover._name,
            handover.id,
            user.id,
            warehouse_id=warehouse.id if warehouse else False,
        )
        action()
        return self._success(
            {
                "order": self._format_order(handover, include_lock=True),
                "route_batch": self._format_route_batch(handover.route_batch_id),
            },
            tts="排线批次已准备",
        )

    def _get_order(self, user, warehouse, order_id):
        domain = [("id", "=", order_id)]
        if warehouse:
            domain.append(("warehouse_id", "=", warehouse.id))
        handover = request.env["wms.handover.order"].with_user(user).sudo().search(domain, limit=1)
        if not handover:
            raise ValidationError("交接单不存在或不属于当前仓库。")
        return handover

    def _format_order(self, handover, include_lock=False):
        outbound = handover.outbound_task_id
        check_task = self._handover_check_task(handover)
        pick_task = check_task.pick_task_id if check_task and check_task.pick_task_id else self._handover_pick_task(handover)
        waybills = self._related_waybills(handover)
        route_batch = handover.route_batch_id
        driver_profile = handover.driver_profile_id or (route_batch.driver_profile_id if route_batch and "driver_profile_id" in route_batch._fields else False)
        vehicle_profile = handover.vehicle_profile_id or (route_batch.vehicle_profile_id if route_batch and "vehicle_profile_id" in route_batch._fields else False)
        result = {
            "id": handover.id,
            "name": handover.name,
            "state": handover.state,
            "state_label": self.STATE_LABELS.get(handover.state, handover.state),
            "warehouse_id": handover.warehouse_id.id if handover.warehouse_id else False,
            "warehouse_name": handover.warehouse_id.display_name if handover.warehouse_id else "",
            "outbound_task_id": outbound.id if outbound else False,
            "outbound_task_name": outbound.name if outbound else "",
            "partner_id": outbound.store_partner_id.id if outbound and outbound.store_partner_id else False,
            "partner_name": outbound.store_partner_id.display_name if outbound and outbound.store_partner_id else "",
            "check_task_id": check_task.id if check_task else False,
            "check_task_name": check_task.name if check_task else "",
            "pick_task_id": pick_task.id if pick_task else False,
            "pick_task_name": pick_task.name if pick_task else "",
            "waybill_ids": waybills.ids,
            "waybill_names": waybills.mapped("name"),
            "waybills": [self._format_waybill(waybill) for waybill in waybills],
            "route_batch_id": route_batch.id if route_batch else False,
            "route_batch_name": route_batch.display_name if route_batch else "",
            "route_batch": self._format_route_batch(route_batch),
            "driver_profile_id": driver_profile.id if driver_profile else False,
            "driver_profile_name": driver_profile.display_name if driver_profile else "",
            "vehicle_profile_id": vehicle_profile.id if vehicle_profile else False,
            "vehicle_profile_name": vehicle_profile.display_name if vehicle_profile else "",
            "weight_total": handover.weight_total,
            "volume_total": handover.volume_total,
            "note": handover.note or "",
            "create_date": handover.create_date,
        }
        if include_lock:
            result["locked_by"] = request.env["wms.task.lock"].sudo().get_lock_holder(handover._name, handover.id)
        return result

    def _handover_check_task(self, handover):
        outbound = handover.outbound_task_id
        if not outbound:
            return request.env["wms.check.task"]
        return outbound.check_task_ids.sorted(key=lambda task: task.id, reverse=True)[:1]

    def _handover_pick_task(self, handover):
        outbound = handover.outbound_task_id
        if not outbound:
            return request.env["wms.pick.task"]
        return outbound.pick_task_ids.sorted(key=lambda task: task.id, reverse=True)[:1]

    def _related_waybills(self, handover):
        Waybill = request.env["logistics.dispatch.waybill"].sudo()
        waybills = Waybill.browse()
        if "tms.dispatch.order" in request.env:
            dispatch_orders = request.env["tms.dispatch.order"].sudo().search([("handover_order_id", "=", handover.id)])
            waybills |= dispatch_orders.mapped("driver_task_ids.waybill_id")
        route_batch = handover.route_batch_id
        if route_batch and "stop_line_ids" in route_batch._fields:
            waybill_names = [name for name in route_batch.stop_line_ids.mapped("waybill_no") if name]
            if waybill_names:
                waybills |= Waybill.search([("name", "in", waybill_names)])
        outbound = handover.outbound_task_id
        picking = outbound.stock_picking_id if outbound else False
        if picking and "logistics.dispatch.waybill.order.line" in request.env:
            lines = request.env["logistics.dispatch.waybill.order.line"].sudo().search([("stock_picking_id", "=", picking.id)])
            waybills |= lines.mapped("waybill_id")
        return waybills

    def _format_waybill(self, waybill):
        partner = waybill.partner_id or waybill.customer_id or waybill.store_id
        return {
            "id": waybill.id,
            "name": waybill.name,
            "state": waybill.state,
            "partner_id": partner.id if partner else False,
            "partner_name": partner.display_name if partner else "",
        }

    def _format_route_batch(self, route_batch):
        if not route_batch:
            return {}
        return {
            "id": route_batch.id,
            "name": route_batch.display_name,
            "batch_no": route_batch.batch_no if "batch_no" in route_batch._fields else "",
            "delivery_date": route_batch.delivery_date if "delivery_date" in route_batch._fields else False,
        }
