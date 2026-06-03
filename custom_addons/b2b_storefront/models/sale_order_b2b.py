from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    source_channel = fields.Selection(
        [("manual", "手动"), ("import", "导入"), ("b2b", "B2B 商城")],
        string="订单来源", default="manual",
    )
    store_partner_id = fields.Many2one("res.partner", string="收货门店")
    delivery_time_required = fields.Char(string="要求送达时间")
    b2b_submit_user_id = fields.Many2one("res.users", string="B2B 提交人")
    b2b_submit_note = fields.Text(string="订单备注")
    b2b_payment_method = fields.Selection(
        [("credit", "账期"), ("transfer", "线下转账"), ("cod", "货到付款")],
        string="B2B 付款方式",
    )
