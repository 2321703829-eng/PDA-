from odoo import _, fields, models


class LogisticsStoreProfile(models.Model):
    _inherit = "logistics.store.profile"

    dispatch_priority = fields.Integer(string="Dispatch Priority", default=0)
    default_route_code = fields.Char(string="Default Route Code")
    default_vehicle_type = fields.Char(string="Default Vehicle Type")
    default_delivery_order = fields.Integer(string="Default Delivery Order", default=0)
    driver_task_count = fields.Integer(
        string="Driver Task Count",
        compute="_compute_tms_counts",
    )
    related_waybill_count = fields.Integer(
        string="Related Waybill Count",
        compute="_compute_tms_counts",
    )

    def _compute_tms_counts(self):
        task_model = self.env["tms.driver.task"]
        waybill_model = self.env["logistics.dispatch.waybill"]
        for record in self:
            record.driver_task_count = task_model.search_count([("store_profile_id", "=", record.id)])
            partner_id = record.partner_id.id
            if partner_id:
                record.related_waybill_count = waybill_model.search_count(
                    ["|", ("partner_id", "=", partner_id), ("store_id", "=", partner_id)]
                )
            else:
                record.related_waybill_count = 0

    def action_open_driver_tasks(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Driver Tasks"),
            "res_model": "tms.driver.task",
            "view_mode": "list,form",
            "domain": [("store_profile_id", "=", self.id)],
        }

    def action_open_related_waybills(self):
        self.ensure_one()
        partner_id = self.partner_id.id
        return {
            "type": "ir.actions.act_window",
            "name": _("Related Waybills"),
            "res_model": "logistics.dispatch.waybill",
            "view_mode": "list,form",
            "domain": ["|", ("partner_id", "=", partner_id), ("store_id", "=", partner_id)],
        }
