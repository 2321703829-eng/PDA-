from odoo import _, fields, models


class LogisticsDispatchWaybill(models.Model):
    _inherit = "logistics.dispatch.waybill"

    tms_dispatch_order_count = fields.Integer(string="Dispatch Orders", compute="_compute_tms_link_counts")
    tms_driver_task_count = fields.Integer(string="Driver Tasks", compute="_compute_tms_link_counts")
    tms_signoff_receipt_count = fields.Integer(string="Signoff Receipts", compute="_compute_tms_link_counts")
    tms_exception_count = fields.Integer(string="Delivery Exceptions", compute="_compute_tms_link_counts")

    def _compute_tms_link_counts(self):
        for record in self:
            driver_tasks = self.env["tms.driver.task"].search([("waybill_id", "=", record.id)])
            record.tms_driver_task_count = len(driver_tasks)
            record.tms_dispatch_order_count = len(driver_tasks.mapped("dispatch_order_id"))
            record.tms_signoff_receipt_count = self.env["tms.signoff.receipt"].search_count([("driver_task_id", "in", driver_tasks.ids)])
            record.tms_exception_count = self.env["tms.delivery.exception"].search_count([("driver_task_id", "in", driver_tasks.ids)])

    def action_open_related_dispatch_orders(self):
        self.ensure_one()
        driver_tasks = self.env["tms.driver.task"].search([("waybill_id", "=", self.id)])
        return {
            "type": "ir.actions.act_window",
            "name": _("Related Dispatch Orders"),
            "res_model": "tms.dispatch.order",
            "view_mode": "list,form",
            "domain": [("id", "in", driver_tasks.mapped("dispatch_order_id").ids)],
        }

    def action_open_related_driver_tasks(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Related Driver Tasks"),
            "res_model": "tms.driver.task",
            "view_mode": "list,form",
            "domain": [("waybill_id", "=", self.id)],
        }

    def action_open_related_signoff_receipts(self):
        self.ensure_one()
        driver_tasks = self.env["tms.driver.task"].search([("waybill_id", "=", self.id)])
        return {
            "type": "ir.actions.act_window",
            "name": _("Related Signoff Receipts"),
            "res_model": "tms.signoff.receipt",
            "view_mode": "list,form",
            "domain": [("driver_task_id", "in", driver_tasks.ids)],
        }

    def action_open_related_delivery_exceptions(self):
        self.ensure_one()
        driver_tasks = self.env["tms.driver.task"].search([("waybill_id", "=", self.id)])
        return {
            "type": "ir.actions.act_window",
            "name": _("Related Delivery Exceptions"),
            "res_model": "tms.delivery.exception",
            "view_mode": "list,form",
            "domain": [("driver_task_id", "in", driver_tasks.ids)],
        }
