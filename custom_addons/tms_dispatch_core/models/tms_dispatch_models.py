from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .selection_options import (
    TMS_DISPATCH_STATUS_SELECTION,
    TMS_DRIVER_NODE_STATUS_SELECTION,
    TMS_EXCEPTION_TYPE_SELECTION,
    TMS_FREIGHT_FEE_TYPE_SELECTION,
)


class TmsDispatchMixin(models.AbstractModel):
    _name = "tms.dispatch.mixin"
    _description = "TMS Dispatch Mixin"

    @api.model
    def _next_sequence(self, code, fallback):
        return self.env["ir.sequence"].next_by_code(code) or fallback


class TmsDispatchOrder(models.Model):
    _name = "tms.dispatch.order"
    _description = "TMS Dispatch Order"
    _inherit = ["mail.thread", "mail.activity.mixin", "tms.dispatch.mixin"]
    _order = "id desc"

    name = fields.Char(string="Dispatch No", required=True, copy=False, tracking=True, default=lambda self: self._next_sequence("tms.dispatch.order", "TMS-DSP-NEW"))
    state = fields.Selection(
        selection=TMS_DISPATCH_STATUS_SELECTION,
        string="Status",
        default="waiting_dispatch",
        required=True,
        tracking=True,
    )
    route_batch_id = fields.Many2one("logistics.route.planning.batch", string="Route Batch", required=True, ondelete="restrict", index=True)
    handover_order_id = fields.Many2one("wms.handover.order", string="Handover Order", ondelete="set null", index=True)
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", ondelete="set null", index=True)
    driver_profile_id = fields.Many2one("logistics.driver.profile", string="Driver Profile", ondelete="set null")
    vehicle_profile_id = fields.Many2one("logistics.vehicle.profile", string="Vehicle Profile", ondelete="set null")
    driver_task_ids = fields.One2many("tms.driver.task", "dispatch_order_id", string="Driver Tasks")
    freight_fee_line_ids = fields.One2many("tms.freight.fee.line", "dispatch_order_id", string="Freight Fee Lines")
    note = fields.Text(string="Note")
    driver_task_count = fields.Integer(string="Driver Task Count", compute="_compute_counts")
    signoff_receipt_count = fields.Integer(string="Signoff Count", compute="_compute_counts")
    exception_count = fields.Integer(string="Exception Count", compute="_compute_counts")
    freight_fee_total = fields.Float(string="Freight Total", compute="_compute_counts", digits=(16, 2))
    departed_task_count = fields.Integer(string="Departed Tasks", compute="_compute_counts")
    in_transit_task_count = fields.Integer(string="In Transit Tasks", compute="_compute_counts")
    signed_task_count = fields.Integer(string="Signed Tasks", compute="_compute_counts")

    @api.depends("driver_task_ids.state", "driver_task_ids", "freight_fee_line_ids.amount")
    def _compute_counts(self):
        for record in self:
            record.driver_task_count = len(record.driver_task_ids)
            record.signoff_receipt_count = self.env["tms.signoff.receipt"].search_count([("driver_task_id", "in", record.driver_task_ids.ids)])
            record.exception_count = self.env["tms.delivery.exception"].search_count([("driver_task_id", "in", record.driver_task_ids.ids)])
            record.freight_fee_total = sum(record.freight_fee_line_ids.mapped("amount"))
            record.departed_task_count = len(record.driver_task_ids.filtered(lambda task: task.state == "departed"))
            record.in_transit_task_count = len(record.driver_task_ids.filtered(lambda task: task.state in ("in_transit", "arrived_store")))
            record.signed_task_count = len(record.driver_task_ids.filtered(lambda task: task.state in ("signed_full", "signed_partial")))

    @api.model
    def create_from_handover(self, handover_order):
        dispatch_order = self.search([("handover_order_id", "=", handover_order.id)], limit=1)
        if dispatch_order:
            return dispatch_order
        route_batch = handover_order.route_batch_id
        if not route_batch:
            route_batch = self.env["logistics.route.planning.batch"].search(
                [("warehouse_id", "=", handover_order.warehouse_id.id)],
                order="delivery_date desc, id desc",
                limit=1,
            )
        if not route_batch:
            raise ValidationError(_("A route batch is required before creating a dispatch order."))
        dispatch_order = self.create({
            "handover_order_id": handover_order.id,
            "route_batch_id": route_batch.id,
            "warehouse_id": handover_order.warehouse_id.id,
            "driver_profile_id": handover_order.driver_profile_id.id or route_batch.driver_profile_id.id,
            "vehicle_profile_id": handover_order.vehicle_profile_id.id or route_batch.vehicle_profile_id.id,
            "note": handover_order.note,
        })
        return dispatch_order

    def _prepare_driver_task_vals(self, stop_line):
        waybill = self.env["logistics.dispatch.waybill"].search([("name", "=", stop_line.waybill_no)], limit=1)
        if not waybill:
            raise ValidationError(
                _(
                    "Cannot create driver task because route stop %(stop)s is not linked to an existing waybill %(waybill)s."
                )
                % {
                    "stop": stop_line.display_name or stop_line.store_name or stop_line.id,
                    "waybill": stop_line.waybill_no or "/",
                }
            )
        partner = waybill.partner_id or waybill.store_id or waybill.customer_id
        store_profile = self.env["logistics.store.profile"].search([("partner_id", "=", partner.id)], limit=1) if partner else False
        return {
            "dispatch_order_id": self.id,
            "waybill_id": waybill.id,
            "store_profile_id": store_profile.id if store_profile else False,
            "note": stop_line.address_detail or stop_line.store_name,
        }

    def _sync_state_from_tasks(self):
        for record in self:
            states = set(record.driver_task_ids.mapped("state"))
            if not states:
                continue
            if "delivery_exception" in states:
                record.state = "delivery_exception"
            elif states <= {"signed_full"}:
                record.state = "signed_full"
            elif "signed_partial" in states or ("signed_full" in states and len(states) > 1):
                record.state = "signed_partial"
            elif "arrived_store" in states:
                record.state = "arrived_store"
            elif "in_transit" in states:
                record.state = "in_transit"
            elif "departed" in states:
                record.state = "departed"
            else:
                record.state = "dispatched"

    def action_dispatch(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条派车单记录"),
                    "type": "warning",
                },
            }
        for record in self:
            if not record.driver_task_ids:
                stop_lines = record.route_batch_id.stop_line_ids.sorted(key=lambda line: (line.stop_seq, line.id))
                if not stop_lines:
                    return {
                        "type": "ir.actions.client",
                        "tag": "display_notification",
                        "params": {
                            "title": _("提示"),
                            "message": _("排线批次 %s 没有停靠点，无法生成司机任务") % record.route_batch_id.display_name,
                            "type": "warning",
                            "sticky": True,
                        },
                    }
                for stop_line in stop_lines:
                    record.env["tms.driver.task"].create(record._prepare_driver_task_vals(stop_line))
            record.write({"state": "dispatched"})
            if "core.operation.audit.log" in self.env.registry:
                self.env["core.operation.audit.log"].log_action(
                    business_domain="tms",
                    action_code="dispatch_order_dispatch",
                    record=record,
                    note=_("Dispatch order dispatched."),
                    payload={"driver_task_count": record.driver_task_count},
                    related_record=record.route_batch_id,
                )
        return True

    def action_depart(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条派车单记录"),
                    "type": "warning",
                },
            }
        for record in self:
            record.write({"state": "departed"})
            for driver_task in record.driver_task_ids:
                driver_task.action_arrive_warehouse()
                driver_task.action_start_delivery()
            if "core.operation.audit.log" in self.env.registry:
                self.env["core.operation.audit.log"].log_action(
                    business_domain="tms",
                    action_code="dispatch_order_depart",
                    record=record,
                    note=_("Dispatch order departed from warehouse."),
                    payload={"driver_task_count": record.driver_task_count},
                )
        return True

    def action_generate_freight_lines(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条派车单记录"),
                    "type": "warning",
                },
            }
        for record in self:
            if not record.freight_fee_line_ids:
                for driver_task in record.driver_task_ids:
                    record.env["tms.freight.fee.line"].create(
                        {
                            "dispatch_order_id": record.id,
                            "fee_type": "stop_fee",
                            "amount": 1.0,
                            "partner_id": driver_task.store_profile_id.partner_id.id or driver_task.waybill_id.partner_id.id,
                            "note": _("Auto-generated from driver task %s") % driver_task.name,
                        }
                    )
            exceptions = self.env["tms.delivery.exception"].search([("driver_task_id", "in", record.driver_task_ids.ids)])
            existing_deduction_notes = set(record.freight_fee_line_ids.filtered(lambda l: l.fee_type == "deduction_fee").mapped("note"))
            for exception in exceptions:
                note = _("Exception deduction source: %s") % exception.name
                if note in existing_deduction_notes:
                    continue
                record.env["tms.freight.fee.line"].create(
                    {
                        "dispatch_order_id": record.id,
                        "fee_type": "deduction_fee",
                        "amount": abs(exception.amount or 0.0),
                        "partner_id": exception.waybill_id.partner_id.id,
                        "note": note,
                    }
                )
            self.env["core.operation.audit.log"].log_action(
                business_domain="tms",
                action_code="dispatch_order_generate_freight_lines",
                record=record,
                note=_("Freight fee lines generated or refreshed."),
                payload={"freight_fee_total": record.freight_fee_total},
            )
        return True

    def action_open_related_waybills(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条派车单记录"),
                    "type": "warning",
                },
            }
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Related Waybills"),
            "res_model": "logistics.dispatch.waybill",
            "view_mode": "list,form",
            "domain": [("id", "in", self.driver_task_ids.mapped("waybill_id").ids)],
        }

    def action_open_freight_lines(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条派车单记录"),
                    "type": "warning",
                },
            }
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Freight Fee Lines"),
            "res_model": "tms.freight.fee.line",
            "view_mode": "list,form",
            "domain": [("dispatch_order_id", "=", self.id)],
        }

    def action_open_record(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条派车单记录"),
                    "type": "warning",
                },
            }
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Dispatch Order"),
            "res_model": "tms.dispatch.order",
            "view_mode": "form",
            "res_id": self.id,
        }

    def action_open_operation_logs(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条派车单记录"),
                    "type": "warning",
                },
            }
        self.ensure_one()
        return self.env["core.operation.audit.log"].action_open_logs_for_record(self)


class TmsDriverTask(models.Model):
    _name = "tms.driver.task"
    _description = "TMS Driver Task"
    _inherit = ["mail.thread", "mail.activity.mixin", "tms.dispatch.mixin"]
    _order = "id desc"

    name = fields.Char(string="Task No", required=True, copy=False, tracking=True, default=lambda self: self._next_sequence("tms.driver.task", "TMS-DRV-NEW"))
    state = fields.Selection(
        selection=TMS_DISPATCH_STATUS_SELECTION,
        string="Status",
        default="waiting_dispatch",
        required=True,
        tracking=True,
    )
    dispatch_order_id = fields.Many2one("tms.dispatch.order", string="Dispatch Order", required=True, ondelete="cascade", index=True)
    waybill_id = fields.Many2one("logistics.dispatch.waybill", string="Waybill", ondelete="set null", index=True)
    store_profile_id = fields.Many2one("logistics.store.profile", string="Store Profile", ondelete="set null", index=True)
    node_ids = fields.One2many("tms.driver.task.node", "driver_task_id", string="Task Nodes")
    note = fields.Text(string="Note")
    latest_node_state = fields.Selection(selection=TMS_DRIVER_NODE_STATUS_SELECTION, string="Latest Node", compute="_compute_latest_node")
    latest_node_time = fields.Datetime(string="Latest Node Time", compute="_compute_latest_node")
    node_count = fields.Integer(string="Node Count", compute="_compute_latest_node")
    latest_longitude = fields.Float(string="Latest Longitude", compute="_compute_latest_node", digits=(16, 8))
    latest_latitude = fields.Float(string="Latest Latitude", compute="_compute_latest_node", digits=(16, 8))
    signoff_receipt_count = fields.Integer(string="Signoff Count", compute="_compute_related_counts")
    exception_count = fields.Integer(string="Exception Count", compute="_compute_related_counts")

    @api.depends("node_ids.event_time", "node_ids.state")
    def _compute_latest_node(self):
        for record in self:
            latest = record.node_ids.sorted(key=lambda node: (node.event_time or fields.Datetime.now(), node.id))[-1:] if record.node_ids else self.env["tms.driver.task.node"]
            latest_node = latest[0] if latest else False
            record.latest_node_state = latest_node.state if latest_node else False
            record.latest_node_time = latest_node.event_time if latest_node else False
            record.latest_longitude = latest_node.longitude if latest_node else 0.0
            record.latest_latitude = latest_node.latitude if latest_node else 0.0
            record.node_count = len(record.node_ids)

    @api.depends("dispatch_order_id", "state")
    def _compute_related_counts(self):
        for record in self:
            record.signoff_receipt_count = self.env["tms.signoff.receipt"].search_count([("driver_task_id", "=", record.id)])
            record.exception_count = self.env["tms.delivery.exception"].search_count([("driver_task_id", "=", record.id)])

    def _log_node(self, node_state, note=None):
        for record in self:
            self.env["tms.driver.task.node"].create({
                "driver_task_id": record.id,
                "state": node_state,
                "note": note or record.note,
            })

    def action_arrive_warehouse(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条司机任务记录"),
                    "type": "warning",
                },
            }
        self._log_node("driver_arrived_warehouse", note=_("Driver arrived at warehouse."))
        for record in self:
            self.env["core.operation.audit.log"].log_action(
                business_domain="tms",
                action_code="driver_task_arrive_warehouse",
                record=record,
                note=_("Driver arrived at warehouse."),
            )
        return True

    def action_start_delivery(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条司机任务记录"),
                    "type": "warning",
                },
            }
        allowed = self.filtered(lambda t: t.state not in ("signed_full", "signed_partial", "delivery_exception"))
        if not allowed:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("所选任务已签收或异常，无法重新开始配送"),
                    "type": "warning",
                },
            }
        allowed.write({"state": "in_transit"})
        allowed._log_node("departed", note=_("Vehicle departed from warehouse."))
        allowed._log_node("in_transit", note=_("Vehicle is in transit."))
        allowed.mapped("dispatch_order_id")._sync_state_from_tasks()
        for record in allowed:
            self.env["core.operation.audit.log"].log_action(
                business_domain="tms",
                action_code="driver_task_start_delivery",
                record=record,
                note=_("Driver task delivery started."),
                related_record=record.dispatch_order_id,
            )
        return True

    def action_arrive_store(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条司机任务记录"),
                    "type": "warning",
                },
            }
        allowed = self.filtered(lambda t: t.state in ("in_transit", "departed"))
        if not allowed:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("所选任务尚未开始配送，无法标记到店"),
                    "type": "warning",
                },
            }
        allowed.write({"state": "arrived_store"})
        allowed._log_node("arrived_store")
        allowed.mapped("dispatch_order_id")._sync_state_from_tasks()
        for record in allowed:
            self.env["core.operation.audit.log"].log_action(
                business_domain="tms",
                action_code="driver_task_arrive_store",
                record=record,
                note=_("Driver arrived at store."),
            )
        return True

    def action_mark_delivering(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条司机任务记录"),
                    "type": "warning",
                },
            }
        self._log_node("delivering", note=_("Driver is delivering at store."))
        for record in self:
            self.env["core.operation.audit.log"].log_action(
                business_domain="tms",
                action_code="driver_task_mark_delivering",
                record=record,
                note=_("Driver marked delivering at store."),
            )
        return True

    def action_log_in_transit(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条司机任务记录"),
                    "type": "warning",
                },
            }
        self.write({"state": "in_transit"})
        self._log_node("in_transit", note=_("In-transit checkpoint updated."))
        self.dispatch_order_id._sync_state_from_tasks()
        for record in self:
            self.env["core.operation.audit.log"].log_action(
                business_domain="tms",
                action_code="driver_task_update_transit",
                record=record,
                note=_("In-transit checkpoint updated."),
                payload={
                    "latest_node_state": record.latest_node_state,
                    "latest_longitude": record.latest_longitude,
                    "latest_latitude": record.latest_latitude,
                },
            )
        return True

    def action_create_signoff_receipt(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条司机任务记录"),
                    "type": "warning",
                },
            }
        self.ensure_one()
        receipt = self.env["tms.signoff.receipt"].search([("driver_task_id", "=", self.id)], limit=1)
        if not receipt:
            receipt = self.env["tms.signoff.receipt"].create({
                "driver_task_id": self.id,
                "signed_qty": self.waybill_id.total_goods_qty or 0.0,
                "signer_name": self.store_profile_id.customer_name or self.store_profile_id.partner_id.name,
                "note": self.note,
            })
            self.env["core.operation.audit.log"].log_action(
                business_domain="tms",
                action_code="driver_task_create_signoff",
                record=self,
                note=_("Signoff receipt created from driver task."),
                related_record=receipt,
            )
        return receipt.action_open_record()

    def action_create_exception(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条司机任务记录"),
                    "type": "warning",
                },
            }
        self.ensure_one()
        exception = self.env["tms.delivery.exception"].create({
            "driver_task_id": self.id,
            "waybill_id": self.waybill_id.id,
            "exception_type": "delay",
            "note": self.note,
        })
        self.write({"state": "delivery_exception"})
        self.dispatch_order_id._sync_state_from_tasks()
        self.env["core.operation.audit.log"].log_action(
            business_domain="tms",
            action_code="driver_task_create_exception",
            record=self,
            action_result="failed",
            note=_("Delivery exception created from driver task."),
            exception_state=exception.exception_type,
            related_record=exception,
        )
        return exception.action_open_record()

    def action_mark_signed_full(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条司机任务记录"),
                    "type": "warning",
                },
            }
        allowed = self.filtered(lambda t: t.state == "arrived_store")
        if not allowed:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("所选任务尚未到店，无法全签"),
                    "type": "warning",
                },
            }
        allowed.write({"state": "signed_full"})
        allowed._log_node("delivering", note=_("Signoff completed in full."))
        allowed.mapped("dispatch_order_id")._sync_state_from_tasks()
        for record in allowed:
            self.env["core.operation.audit.log"].log_action(
                business_domain="tms",
                action_code="driver_task_signed_full",
                record=record,
                note=_("Driver task signed off in full."),
            )
        return True

    def action_mark_signed_partial(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条司机任务记录"),
                    "type": "warning",
                },
            }
        allowed = self.filtered(lambda t: t.state == "arrived_store")
        if not allowed:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("所选任务尚未到店，无法部分签收"),
                    "type": "warning",
                },
            }
        allowed.write({"state": "signed_partial"})
        allowed._log_node("delivering", note=_("Signoff completed partially."))
        allowed.mapped("dispatch_order_id")._sync_state_from_tasks()
        for record in allowed:
            self.env["core.operation.audit.log"].log_action(
                business_domain="tms",
                action_code="driver_task_signed_partial",
                record=record,
                note=_("Driver task signed off partially."),
            )
        return True

    def action_open_signoff_receipts(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条司机任务记录"),
                    "type": "warning",
                },
            }
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Signoff Receipts"),
            "res_model": "tms.signoff.receipt",
            "view_mode": "list,form",
            "domain": [("driver_task_id", "=", self.id)],
        }

    def action_open_delivery_exceptions(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条司机任务记录"),
                    "type": "warning",
                },
            }
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Delivery Exceptions"),
            "res_model": "tms.delivery.exception",
            "view_mode": "list,form",
            "domain": [("driver_task_id", "=", self.id)],
        }

    def action_open_waybill(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条司机任务记录"),
                    "type": "warning",
                },
            }
        self.ensure_one()
        if not self.waybill_id:
            raise ValidationError(_("Waybill is not available for this driver task."))
        return {
            "type": "ir.actions.act_window",
            "name": _("Waybill"),
            "res_model": "logistics.dispatch.waybill",
            "view_mode": "form",
            "res_id": self.waybill_id.id,
        }

    def action_open_record(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条司机任务记录"),
                    "type": "warning",
                },
            }
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Driver Task"),
            "res_model": "tms.driver.task",
            "view_mode": "form",
            "res_id": self.id,
        }

    def action_open_operation_logs(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条司机任务记录"),
                    "type": "warning",
                },
            }
        self.ensure_one()
        return self.env["core.operation.audit.log"].action_open_logs_for_record(self)


class TmsDriverTaskNode(models.Model):
    _name = "tms.driver.task.node"
    _description = "TMS Driver Task Node"
    _order = "event_time asc, id asc"

    driver_task_id = fields.Many2one("tms.driver.task", string="Driver Task", required=True, ondelete="cascade", index=True)
    state = fields.Selection(
        selection=TMS_DRIVER_NODE_STATUS_SELECTION,
        string="Node Type",
        required=True,
    )
    event_time = fields.Datetime(string="Event Time", required=True, default=fields.Datetime.now)
    longitude = fields.Float(string="Longitude", digits=(16, 8))
    latitude = fields.Float(string="Latitude", digits=(16, 8))
    note = fields.Text(string="Note")


class TmsSignoffReceipt(models.Model):
    _name = "tms.signoff.receipt"
    _description = "TMS Signoff Receipt"
    _inherit = ["mail.thread", "mail.activity.mixin", "tms.dispatch.mixin"]
    _order = "id desc"

    name = fields.Char(string="Receipt No", required=True, copy=False, tracking=True, default=lambda self: self._next_sequence("tms.signoff.receipt", "TMS-SGN-NEW"))
    state = fields.Selection(
        selection=TMS_DISPATCH_STATUS_SELECTION,
        string="Status",
        default="waiting_dispatch",
        required=True,
        tracking=True,
    )
    driver_task_id = fields.Many2one("tms.driver.task", string="Driver Task", required=True, ondelete="cascade", index=True)
    signed_at = fields.Datetime(string="Signed At")
    signer_name = fields.Char(string="Signer Name")
    signed_qty = fields.Float(string="Signed Qty", digits=(16, 4), default=0.0)
    photo_count = fields.Integer(string="Photo Count", default=0)
    note = fields.Text(string="Note")

    def action_confirm_signoff(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条签收单记录"),
                    "type": "warning",
                },
            }
        for record in self:
            record.signed_at = record.signed_at or fields.Datetime.now()
            total_qty = record.driver_task_id.waybill_id.total_goods_qty or 0.0
            if total_qty and record.signed_qty < total_qty:
                record.write({"state": "signed_partial"})
                record.driver_task_id.action_mark_signed_partial()
            else:
                record.write({"state": "signed_full"})
                record.driver_task_id.action_mark_signed_full()
            self.env["core.operation.audit.log"].log_action(
                business_domain="tms",
                action_code="signoff_receipt_confirm",
                record=record,
                note=_("Signoff receipt confirmed."),
                related_record=record.driver_task_id,
                payload={"signed_qty": record.signed_qty},
            )
        return True

    def action_open_record(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条签收单记录"),
                    "type": "warning",
                },
            }
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Signoff Receipt"),
            "res_model": "tms.signoff.receipt",
            "view_mode": "form",
            "res_id": self.id,
        }


class TmsDeliveryException(models.Model):
    _name = "tms.delivery.exception"
    _description = "TMS Delivery Exception"
    _inherit = ["mail.thread", "mail.activity.mixin", "tms.dispatch.mixin"]
    _order = "id desc"

    name = fields.Char(string="Exception No", required=True, copy=False, tracking=True, default=lambda self: self._next_sequence("tms.delivery.exception", "TMS-EXC-NEW"))
    state = fields.Selection(
        selection=TMS_DISPATCH_STATUS_SELECTION,
        string="Status",
        default="delivery_exception",
        required=True,
        tracking=True,
    )
    exception_type = fields.Selection(
        selection=TMS_EXCEPTION_TYPE_SELECTION,
        string="Exception Type",
        required=True,
    )
    driver_task_id = fields.Many2one("tms.driver.task", string="Driver Task", ondelete="set null", index=True)
    waybill_id = fields.Many2one("logistics.dispatch.waybill", string="Waybill", ondelete="set null", index=True)
    amount = fields.Float(string="Settlement Amount", digits=(16, 2), default=0.0)
    note = fields.Text(string="Note")

    def action_open_record(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条配送异常记录"),
                    "type": "warning",
                },
            }
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Delivery Exception"),
            "res_model": "tms.delivery.exception",
            "view_mode": "form",
            "res_id": self.id,
        }


class TmsFreightFeeLine(models.Model):
    _name = "tms.freight.fee.line"
    _description = "TMS Freight Fee Line"
    _order = "id desc"

    dispatch_order_id = fields.Many2one("tms.dispatch.order", string="Dispatch Order", required=True, ondelete="cascade", index=True)
    fee_type = fields.Selection(
        selection=TMS_FREIGHT_FEE_TYPE_SELECTION,
        string="Fee Type",
        required=True,
    )
    amount = fields.Float(string="Amount", digits=(16, 2), default=0.0)
    partner_id = fields.Many2one("res.partner", string="Counterparty", ondelete="set null", index=True)
    note = fields.Text(string="Note")
