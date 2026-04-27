from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.logistics_base.models.selection_options import CUSTOMER_STATUS_SELECTION


class ResPartner(models.Model):
    _inherit = "res.partner"

    _uniq_logistics_customer_code = models.Constraint(
        "unique(logistics_customer_code)",
        "Unique logistics customer code is required.",
    )
    _uniq_logistics_store_code = models.Constraint(
        "unique(logistics_store_code)",
        "Unique logistics store code is required.",
    )
    _uniq_internal_customer_code = models.Constraint(
        "unique(internal_customer_code)",
        "Unique internal customer code is required.",
    )

    _uniq_external_customer_code = models.Constraint(
        "unique(external_customer_code)",
        "外联客户编号必须唯一。",
    )

    is_logistics_customer = fields.Boolean(
        string="物流客户",
        help="兼容字段：是否纳入物流客户管理。",
    )
    is_logistics_store = fields.Boolean(
        string="物流门店",
        help="兼容字段：是否纳入物流门店或收货点管理。",
    )
    is_logistics_partner = fields.Boolean(
        string="物流客户",
        compute="_compute_is_logistics_partner",
        inverse="_inverse_is_logistics_partner",
        store=True,
        readonly=False,
        help="单对象口径：客户与门店视为同一业务对象时，统一使用该标记。",
    )
    logistics_customer_code = fields.Char(
        string="客户号",
        index=True,
        copy=False,
    )
    logistics_store_code = fields.Char(
        string="门店号",
        index=True,
        copy=False,
    )
    logistics_customer_level = fields.Selection(
        selection=[
            ("standard", "标准"),
            ("vip", "VIP"),
            ("strategic", "战略"),
        ],
        string="客户等级",
    )
    logistics_customer_status = fields.Selection(
        selection=[
            ("active", "启用"),
            ("inactive", "停用"),
            ("paused", "暂停"),
        ],
        string="客户状态（兼容）",
        default="active",
    )
    logistics_store_status = fields.Selection(
        selection=[
            ("active", "启用"),
            ("inactive", "停用"),
        ],
        string="门店状态（兼容）",
        default="active",
    )
    logistics_delivery_time_window = fields.Char(string="配送时间窗")
    logistics_unload_requirement = fields.Text(string="卸货要求")
    logistics_need_sign_receipt = fields.Boolean(string="需要签收回执", default=False)
    logistics_service_note = fields.Text(string="服务备注")
    logistics_internal_reference = fields.Char(
        string="内部参考号",
        index=True,
        copy=False,
    )

    internal_customer_code = fields.Char(string="系统内部客户编号", size=64)
    external_customer_code = fields.Char(string="外联客户编号", size=64, index=True)
    customer_name = fields.Char(
        string="统一客户名称",
        related="name",
        readonly=False,
        store=True,
    )
    contact_name = fields.Char(string="默认联系人", size=64)
    contact_phone = fields.Char(string="默认联系电话", size=32)
    address_full = fields.Text(string="默认地址")
    address_region_json = fields.Json(string="结构化地址")
    organization_name = fields.Char(string="组织归属", size=64)
    channel_name = fields.Char(string="渠道", size=64)
    department_name = fields.Char(string="部门", size=64)
    salesperson_name = fields.Char(string="业务员", size=64)
    customer_status = fields.Selection(
        selection=CUSTOMER_STATUS_SELECTION,
        string="经营状态",
        default="normal",
        index=True,
    )

    # 统一画像字段：经营画像
    allow_cash_on_delivery = fields.Boolean(string="允许货到付款", default=False, index=True)
    internal_counterparty_flag = fields.Boolean(string="内部往来单位", default=False, index=True)
    invoice_type = fields.Char(string="发票类型", size=64)

    # 统一画像字段：配送画像
    delivery_window_text = fields.Text(string="配送时间窗摘要")
    receive_start_time = fields.Char(string="开始收货时间", size=16, default="")
    receive_end_time = fields.Char(string="截止收货时间", size=16, default="")
    receive_time_slots_text = fields.Text(string="收货时间段", default="")
    no_receive_time_slots_text = fields.Text(string="不收货时间段", default="")
    delivery_week_flags = fields.Char(string="周维度配送周期", size=64, default="")
    default_signoff_requirement = fields.Char(string="默认签收要求", size=128)
    delivery_access_flags = fields.Char(string="配送可达性编码串", size=128, default="")
    illegal_parking_flag = fields.Boolean(string="违停", default=False)
    free_parking_minutes = fields.Integer(string="免费停车时长", default=0)
    parking_fee_per_hour = fields.Float(string="停车费/小时", default=0.0)
    parking_location_text = fields.Text(string="停车位置", default="")
    parking_mode_text = fields.Text(string="停车方式", default="")
    unload_entrance_text = fields.Text(string="卸货入口", default="")
    unload_location_text = fields.Text(string="卸货位置", default="")
    upstairs_floor_count = fields.Integer(string="上楼层数", default=0)
    basement_height_limit_text = fields.Text(string="地库限高", default="")
    route_preference = fields.Char(string="线路偏好", size=64)
    warehouse_preference = fields.Char(string="仓库偏好", size=64)

    logistics_profile_count = fields.Integer(
        string="物流客户画像数",
        compute="_compute_logistics_profile_counts",
    )
    logistics_customer_profile_count = fields.Integer(
        string="客户经营画像数",
        compute="_compute_logistics_profile_counts",
    )
    logistics_store_profile_count = fields.Integer(
        string="门店配送画像数",
        compute="_compute_logistics_profile_counts",
    )

    @api.depends("is_logistics_customer", "is_logistics_store")
    def _compute_is_logistics_partner(self):
        for record in self:
            record.is_logistics_partner = bool(record.is_logistics_customer or record.is_logistics_store)

    def _inverse_is_logistics_partner(self):
        for record in self:
            partner_flag = bool(record.is_logistics_partner)
            record.is_logistics_customer = partner_flag
            record.is_logistics_store = partner_flag

    @api.depends("is_logistics_partner")
    def _compute_logistics_profile_counts(self):
        for record in self:
            record.logistics_profile_count = 1 if record.is_logistics_partner else 0
            record.logistics_customer_profile_count = 1 if record.is_logistics_partner else 0
            record.logistics_store_profile_count = 1 if record.is_logistics_partner else 0

    @api.model
    def _normalize_logistics_partner_vals(self, vals):
        normalized_vals = dict(vals)

        if "is_logistics_partner" in normalized_vals:
            partner_flag = bool(normalized_vals["is_logistics_partner"])
            normalized_vals["is_logistics_customer"] = partner_flag
            normalized_vals["is_logistics_store"] = partner_flag
        elif "is_logistics_customer" in normalized_vals or "is_logistics_store" in normalized_vals:
            partner_flag = bool(normalized_vals.get("is_logistics_customer")) or bool(normalized_vals.get("is_logistics_store"))
            normalized_vals["is_logistics_customer"] = partner_flag
            normalized_vals["is_logistics_store"] = partner_flag

        for field_name in (
            "logistics_customer_code",
            "logistics_store_code",
            "internal_customer_code",
            "external_customer_code",
        ):
            if field_name in normalized_vals:
                normalized_vals[field_name] = (normalized_vals.get(field_name) or "").strip() or False

        customer_code = normalized_vals.get("logistics_customer_code")
        store_code = normalized_vals.get("logistics_store_code")
        if customer_code and store_code and customer_code != store_code:
            raise ValidationError(_("logistics_customer_code and logistics_store_code must stay consistent under the unified partner model."))

        unified_code = customer_code or store_code or False
        if unified_code:
            normalized_vals["logistics_customer_code"] = unified_code
            normalized_vals["logistics_store_code"] = unified_code

        return normalized_vals

    @api.model_create_multi
    def create(self, vals_list):
        return super().create([self._normalize_logistics_partner_vals(vals) for vals in vals_list])

    def write(self, vals):
        return super().write(self._normalize_logistics_partner_vals(vals))

    def action_open_or_create_logistics_profile(self):
        self.ensure_one()
        if not self.is_logistics_partner:
            raise ValidationError(_("Only logistics customers can open a logistics profile."))

        action = self.env["ir.actions.actions"]._for_xml_id("logistics_base.action_logistics_partner_profile")
        action["res_id"] = self.id
        action["views"] = [(self.env.ref("logistics_base.view_res_partner_logistics_profile_form").id, "form")]
        action["view_mode"] = "form"
        action["target"] = "current"
        action["context"] = {
            "default_is_logistics_partner": True,
            "default_is_logistics_customer": True,
            "default_is_logistics_store": True,
        }
        return action

    def action_open_or_create_customer_profile(self):
        return self.action_open_or_create_logistics_profile()

    def action_open_or_create_store_profile(self):
        return self.action_open_or_create_logistics_profile()
