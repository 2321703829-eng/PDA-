from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.logistics_base.models.selection_options import LOGISTICS_ROLE_SELECTION


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    logistics_employee_code = fields.Char(string="员工编号", index=True, copy=False)
    logistics_role = fields.Selection(
        selection=LOGISTICS_ROLE_SELECTION,
        string="物流角色",
        default="driver",
    )
    logistics_work_status = fields.Selection(
        selection=[
            ("active", "在岗"),
            ("inactive", "停用"),
            ("leave", "请假"),
        ],
        string="工作状态",
        default="active",
    )
    logistics_service_area = fields.Char(string="服务区域")
    logistics_default_warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="默认仓库",
        ondelete="set null",
    )
    logistics_can_take_order = fields.Boolean(string="可接单", default=False)
    organization_name = fields.Char(string="所属组织", size=64)
    employee_status = fields.Char(string="员工状态", size=32)
    logistics_driver_profile_count = fields.Integer(
        string="司机画像数",
        compute="_compute_logistics_driver_profile_count",
    )

    @api.depends("logistics_role")
    def _compute_logistics_driver_profile_count(self):
        profile_model = self.env["logistics.driver.profile"].sudo()
        for record in self:
            record.logistics_driver_profile_count = profile_model.search_count([("employee_id", "=", record.id)])

    def action_open_or_create_driver_profile(self):
        self.ensure_one()
        if self.logistics_role != "driver":
            raise ValidationError(_("Only employees with logistics role 'driver' can create a driver profile."))

        profile = self.env["logistics.driver.profile"].search([("employee_id", "=", self.id)], limit=1)
        if not profile:
            profile = self.env["logistics.driver.profile"].create(
                {
                    "employee_id": self.id,
                    "current_residence_region": self._get_employee_region_label(),
                }
            )

        action = self.env["ir.actions.actions"]._for_xml_id("logistics_base.action_logistics_driver_profile")
        action["res_id"] = profile.id
        action["views"] = [(self.env.ref("logistics_base.view_logistics_driver_profile_form").id, "form")]
        action["view_mode"] = "form"
        action["target"] = "current"
        action["context"] = {"default_employee_id": self.id}
        return action

    def _get_driver_profile_phone(self):
        self.ensure_one()
        return (
            getattr(self, "mobile_phone", False)
            or getattr(self, "work_phone", False)
            or getattr(self, "private_phone", False)
            or ""
        )

    def _get_employee_region_label(self):
        self.ensure_one()
        private_partner = getattr(self, "private_address_id", False)
        if private_partner and private_partner.state_id:
            return private_partner.state_id.name or ""
        work_contact = getattr(self, "address_id", False)
        if work_contact and work_contact.state_id:
            return work_contact.state_id.name or ""
        return ""
