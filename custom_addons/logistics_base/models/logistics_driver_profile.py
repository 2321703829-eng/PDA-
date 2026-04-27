from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LogisticsDriverProfile(models.Model):
    _name = "logistics.driver.profile"
    _description = "司机画像"
    _table = "logistics_driver_profile"
    _rec_name = "employee_id"

    _uniq_driver_profile_employee = models.Constraint(
        "unique(employee_id)",
        "同一员工只能绑定一条司机画像。",
    )

    employee_id = fields.Many2one(
        "hr.employee",
        string="关联司机主档",
        required=True,
        ondelete="cascade",
        index=True,
    )
    internal_driver_code = fields.Char(
        related="employee_id.logistics_employee_code",
        string="内部司机编号",
        store=True,
        readonly=True,
    )
    driver_name = fields.Char(
        related="employee_id.name",
        string="司机姓名",
        store=True,
        readonly=True,
    )
    driver_phone = fields.Char(
        string="联系电话",
        compute="_compute_driver_phone",
    )
    id_card_no = fields.Char(string="身份证号", size=64)
    driver_license_no = fields.Char(string="驾驶证号", size=64)
    bank_card_no = fields.Char(string="银行卡号", size=64)
    native_place = fields.Char(string="籍贯", size=64)
    ethnicity_name = fields.Char(string="民族", size=64)
    political_status = fields.Char(string="政治面貌", size=64)
    marital_status = fields.Char(string="婚姻状态", size=64)
    military_years_text = fields.Char(string="军龄", size=32)
    driver_license_level = fields.Char(string="驾驶证级别", size=32)
    first_license_date = fields.Date(string="初领证日期")
    driver_license_valid_from = fields.Date(string="驾驶证有效期起")
    driver_license_valid_to = fields.Date(string="驾驶证有效期止")
    wechat_no = fields.Char(string="微信号", size=32)
    contact_phone_1 = fields.Char(string="联系电话1", size=32)
    contact_phone_2 = fields.Char(string="联系电话2", size=32)
    emergency_contact_name = fields.Char(string="紧急联系人", size=64)
    emergency_contact_relation = fields.Char(string="与司机关系", size=64)
    emergency_contact_phone_1 = fields.Char(string="紧急联系电话1", size=32)
    emergency_contact_phone_2 = fields.Char(string="紧急联系电话2", size=32)
    bank_name = fields.Char(string="开户行", size=64)
    contract_start_date = fields.Date(string="合同开始日期")
    contract_end_date = fields.Date(string="合同结束日期")
    health_status_text = fields.Text(string="健康情况")
    violation_record_text = fields.Text(string="违法记录")
    credit_status_text = fields.Text(string="征信状况")
    driver_remark = fields.Text(string="备注")
    current_address = fields.Text(string="详细住址")
    allow_night_shift = fields.Boolean(string="适合夜班", default=False)
    current_residence_region = fields.Char(string="现居住地行政区", size=128)
    major_accident_record_flag = fields.Boolean(string="有重大事故记录", default=False)

    @api.depends("employee_id", "employee_id.mobile_phone", "employee_id.work_phone", "employee_id.private_phone")
    def _compute_driver_phone(self):
        for record in self:
            employee = record.employee_id
            record.driver_phone = (
                getattr(employee, "mobile_phone", False)
                or getattr(employee, "work_phone", False)
                or getattr(employee, "private_phone", False)
                or ""
            )

    @api.constrains("contract_start_date", "contract_end_date", "driver_license_valid_from", "driver_license_valid_to")
    def _check_date_ranges(self):
        for record in self:
            if record.contract_start_date and record.contract_end_date and record.contract_start_date > record.contract_end_date:
                raise ValidationError("合同结束日期不能早于合同开始日期。")
            if (
                record.driver_license_valid_from
                and record.driver_license_valid_to
                and record.driver_license_valid_from > record.driver_license_valid_to
            ):
                raise ValidationError("驾驶证有效期结束日期不能早于开始日期。")
