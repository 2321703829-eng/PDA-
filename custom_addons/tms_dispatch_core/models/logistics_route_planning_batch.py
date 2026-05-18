from odoo import fields, models

from .selection_options import TMS_ROUTE_STATUS_SELECTION


class LogisticsRoutePlanningBatch(models.Model):
    _inherit = "logistics.route.planning.batch"

    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", ondelete="set null", index=True)
    driver_profile_id = fields.Many2one("logistics.driver.profile", string="Driver Profile", ondelete="set null")
    vehicle_profile_id = fields.Many2one("logistics.vehicle.profile", string="Vehicle Profile", ondelete="set null")
    route_status = fields.Selection(
        selection=TMS_ROUTE_STATUS_SELECTION,
        string="Route Status",
        default="waiting_route",
        required=True,
    )
    handover_order_count = fields.Integer(string="Handover Orders", compute="_compute_tms_link_counts")
    dispatch_order_count = fields.Integer(string="Dispatch Orders", compute="_compute_tms_link_counts")
    driver_task_count = fields.Integer(string="Driver Tasks", compute="_compute_tms_link_counts")

    def _compute_tms_link_counts(self):
        handover_model = self.env["wms.handover.order"]
        dispatch_model = self.env["tms.dispatch.order"]
        for record in self:
            handovers = handover_model.search([("route_batch_id", "=", record.id)])
            dispatch_orders = dispatch_model.search([("route_batch_id", "=", record.id)])
            record.handover_order_count = len(handovers)
            record.dispatch_order_count = len(dispatch_orders)
            record.driver_task_count = len(dispatch_orders.mapped("driver_task_ids"))

    def action_open_handover_orders(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Related Handover Orders",
            "res_model": "wms.handover.order",
            "view_mode": "list,form",
            "domain": [("route_batch_id", "=", self.id)],
        }

    def action_open_dispatch_orders(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Related Dispatch Orders",
            "res_model": "tms.dispatch.order",
            "view_mode": "list,form",
            "domain": [("route_batch_id", "=", self.id)],
        }

    def action_open_driver_tasks(self):
        self.ensure_one()
        dispatch_orders = self.env["tms.dispatch.order"].search([("route_batch_id", "=", self.id)])
        return {
            "type": "ir.actions.act_window",
            "name": "Related Driver Tasks",
            "res_model": "tms.driver.task",
            "view_mode": "list,form",
            "domain": [("dispatch_order_id", "in", dispatch_orders.ids)],
        }

    def action_open_route_map(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": "/tms/route/%s/map" % self.id,
            "target": "self",
        }
