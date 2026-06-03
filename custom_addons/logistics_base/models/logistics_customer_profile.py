from odoo import fields, models


class LogisticsCustomerProfile(models.Model):
    _name = "logistics.customer.profile"
    _description = "客户经营画像（兼容）"
    _table = "logistics_customer_profile"
    _rec_name = "partner_id"

    _uniq_customer_profile_partner = models.Constraint(
        "unique(partner_id)",
        "同一客户主档只能绑定一条客户经营画像。",
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="关联客户主档",
        required=True,
        ondelete="cascade",
        index=True,
    )
    customer_level = fields.Selection(
        related="partner_id.logistics_customer_level",
        string="客户等级",
        store=True,
        readonly=False,
    )
    customer_status = fields.Selection(
        related="partner_id.customer_status",
        string="客户状态",
        store=True,
        readonly=False,
    )
    allow_cash_on_delivery = fields.Boolean(
        related="partner_id.allow_cash_on_delivery",
        string="允许货到付款",
        store=True,
        readonly=False,
    )
    internal_counterparty_flag = fields.Boolean(
        related="partner_id.internal_counterparty_flag",
        string="内部往来单位",
        store=True,
        readonly=False,
    )
    invoice_type = fields.Char(
        related="partner_id.invoice_type",
        string="发票类型",
        store=True,
        readonly=False,
    )
    registered_phone = fields.Char(
        related="partner_id.contact_phone",
        string="注册电话",
        store=True,
        readonly=False,
    )
    registered_address = fields.Text(
        related="partner_id.address_full",
        string="注册地址",
        store=True,
        readonly=False,
    )
    customer_seq_no = fields.Char(
        related="partner_id.logistics_customer_code",
        string="客户序号",
        store=True,
        readonly=False,
    )
