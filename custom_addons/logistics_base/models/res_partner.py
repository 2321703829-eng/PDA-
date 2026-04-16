from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_logistics_customer = fields.Boolean(
        string="物流客户",
        help="标记该联系人是否按物流客户管理。",
    )
    is_logistics_store = fields.Boolean(
        string="物流门店",
        help="标记该联系人是否按物流门店或收货点管理。",
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
        string="客户状态",
        default="active",
    )
    logistics_store_status = fields.Selection(
        selection=[
            ("active", "启用"),
            ("inactive", "停用"),
        ],
        string="门店状态",
        default="active",
    )
    logistics_delivery_time_window = fields.Char(
        string="配送时间窗",
    )
    logistics_unload_requirement = fields.Text(
        string="卸货要求",
    )
    logistics_need_sign_receipt = fields.Boolean(
        string="需要签收回执",
        default=False,
    )
    logistics_service_note = fields.Text(
        string="服务备注",
    )
    logistics_internal_reference = fields.Char(
        string="内部参考号",
        index=True,
        copy=False,
    )
