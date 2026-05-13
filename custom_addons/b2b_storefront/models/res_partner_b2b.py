from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_b2b_customer = fields.Boolean(string="B2B 客户")
    is_b2b_store = fields.Boolean(string="B2B 门店")
    b2b_enabled = fields.Boolean(string="启用 B2B")
    b2b_payment_method_default = fields.Selection(
        [("credit", "账期"), ("transfer", "线下转账"), ("cod", "货到付款")],
        string="默认付款方式",
    )
    b2b_default_store_id = fields.Many2one("res.partner", string="默认收货门店")
