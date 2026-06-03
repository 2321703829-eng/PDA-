from odoo import _, fields, models


class LogisticsDispatchWaybill(models.Model):
    _inherit = "logistics.dispatch.waybill"

    wms_handover_order_count = fields.Integer(string="Handover Orders", compute="_compute_wms_tms_link_counts")
    wms_outbound_task_count = fields.Integer(string="Outbound Tasks", compute="_compute_wms_tms_link_counts")

    def _compute_wms_tms_link_counts(self):
        super_compute = getattr(super(), "_compute_wms_tms_link_counts", None)
        if super_compute:
            super_compute()
        for record in self:
            driver_tasks = self.env["tms.driver.task"].search([("waybill_id", "=", record.id)])
            dispatch_orders = driver_tasks.mapped("dispatch_order_id")
            handovers = dispatch_orders.mapped("handover_order_id")
            outbounds = handovers.mapped("outbound_task_id")
            record.wms_handover_order_count = len(handovers)
            record.wms_outbound_task_count = len(outbounds)

    def action_open_related_handover_orders(self):
        self.ensure_one()
        driver_tasks = self.env["tms.driver.task"].search([("waybill_id", "=", self.id)])
        handover_ids = driver_tasks.mapped("dispatch_order_id.handover_order_id").ids
        return {
            "type": "ir.actions.act_window",
            "name": _("Related Handover Orders"),
            "res_model": "wms.handover.order",
            "view_mode": "list,form",
            "domain": [("id", "in", handover_ids)],
        }

    def action_open_related_outbound_tasks(self):
        self.ensure_one()
        driver_tasks = self.env["tms.driver.task"].search([("waybill_id", "=", self.id)])
        outbound_ids = driver_tasks.mapped("dispatch_order_id.handover_order_id.outbound_task_id").ids
        return {
            "type": "ir.actions.act_window",
            "name": _("Related Outbound Tasks"),
            "res_model": "wms.outbound.task",
            "view_mode": "list,form",
            "domain": [("id", "in", outbound_ids)],
        }
