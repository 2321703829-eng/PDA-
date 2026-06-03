from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LogisticsVehicleProfile(models.Model):
    _name = "logistics.vehicle.profile"
    _description = "车辆画像"
    _table = "logistics_vehicle_profile"
    _rec_name = "vehicle_id"

    _uniq_vehicle_profile_vehicle = models.Constraint(
        "unique(vehicle_id)",
        "同一车辆只能绑定一条车辆画像。",
    )

    vehicle_id = fields.Many2one(
        "fleet.vehicle",
        string="关联车辆主档",
        required=True,
        ondelete="cascade",
        index=True,
    )
    internal_vehicle_code = fields.Char(string="车辆编号", size=64)
    factory_date = fields.Date(string="出厂日期")
    purchase_mode = fields.Char(string="购置方式", size=32)
    vehicle_spec = fields.Char(string="规格", size=64)
    color_name = fields.Char(string="颜色", size=64)
    vin_no = fields.Char(string="VIN", size=64)
    engine_no = fields.Char(string="发动机号", size=64)
    approved_load_ton = fields.Float(string="核定载重", digits=(16, 4), default=0.0)
    approved_volume_m3 = fields.Float(string="核定体积", digits=(16, 6), default=0.0)
    standby_site_name = fields.Char(string="常驻站点", size=64)
    operation_type = fields.Char(string="营运类型", size=64)
    driving_license_no = fields.Char(string="行驶证号", size=64)
    transport_license_no = fields.Char(string="道路运输证号", size=64)
    driving_license_register_date = fields.Date(string="行驶证注册日期")
    driving_license_issue_date = fields.Date(string="行驶证发证日期")
    inspection_valid_to = fields.Date(string="检验有效期止")
    transport_license_valid_to = fields.Date(string="道路运输证有效期止")
    annual_check_due_date = fields.Date(string="年审到期日")
    insurance_company_name = fields.Char(string="保险公司", size=64)
    compulsory_policy_no = fields.Char(string="交强险保单号", size=64)
    commercial_policy_no = fields.Char(string="商业险保单号", size=64)
    compulsory_insurance_due_date = fields.Date(string="交强险到期日")
    commercial_insurance_due_date = fields.Date(string="商业险到期日")
    vehicle_vessel_tax_due_date = fields.Date(string="车船税到期日")
    gps_device_no = fields.Char(string="GPS 设备号", size=64)
    etc_no = fields.Char(string="ETC 号", size=64)
    fuel_or_power_card_no = fields.Char(string="油卡/电卡号", size=64)
    major_accident_record_flag = fields.Boolean(string="有重大事故记录", default=False)
    vehicle_remark = fields.Text(string="备注")

    @api.constrains("approved_load_ton", "approved_volume_m3")
    def _check_non_negative_values(self):
        for record in self:
            if record.approved_load_ton < 0 or record.approved_volume_m3 < 0:
                raise ValidationError("核定载重和核定体积不能小于 0。")
