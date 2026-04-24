from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    organization_name = fields.Char(string="所属组织", size=64)
    vehicle_status = fields.Char(string="车辆状态", size=32)
    vehicle_type_name = fields.Char(string="车辆类型", size=64)
    brand_name = fields.Char(string="品牌", size=64)
    model_name = fields.Char(string="车型", size=64)
    energy_type = fields.Char(string="能源类型", size=32)
    logistics_vehicle_profile_count = fields.Integer(
        string="车辆画像数",
        compute="_compute_logistics_vehicle_profile_count",
    )

    @api.depends("license_plate", "name")
    def _compute_logistics_vehicle_profile_count(self):
        profile_model = self.env["logistics.vehicle.profile"].sudo()
        for record in self:
            record.logistics_vehicle_profile_count = profile_model.search_count([("vehicle_id", "=", record.id)])

    def action_open_or_create_vehicle_profile(self):
        self.ensure_one()
        profile = self.env["logistics.vehicle.profile"].sudo().search([("vehicle_id", "=", self.id)], limit=1)
        if not profile:
            profile = self.env["logistics.vehicle.profile"].sudo().create(
                {
                    "vehicle_id": self.id,
                    "internal_vehicle_code": self.name or self.license_plate or "",
                }
            )

        action = self.env["ir.actions.actions"]._for_xml_id("logistics_base.action_logistics_vehicle_profile")
        action["res_id"] = profile.id
        action["views"] = [(self.env.ref("logistics_base.view_logistics_vehicle_profile_form").id, "form")]
        action["view_mode"] = "form"
        action["target"] = "current"
        action["context"] = {"default_vehicle_id": self.id}
        return action
