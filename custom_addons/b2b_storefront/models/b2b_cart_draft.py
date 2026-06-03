from odoo import fields, models


class B2bCartDraft(models.Model):
    _name = "b2b.cart.draft"
    _description = "B2B 购物车草稿"
    _order = "write_date desc"

    partner_id = fields.Many2one("res.partner", string="客户", required=True)
    store_id = fields.Many2one("res.partner", string="收货门店")
    state = fields.Selection(
        [("draft", "草稿"), ("submitted", "已提交"), ("converted", "已转订单")],
        string="状态", default="draft",
    )
    line_ids = fields.One2many("b2b.cart.draft.line", "cart_id", string="明细")
    total_amount = fields.Float(string="合计金额", compute="_compute_total", store=True)
    total_qty = fields.Float(string="合计数量", compute="_compute_total", store=True)

    def _compute_total(self):
        for c in self:
            c.total_qty = sum(l.qty for l in c.line_ids)
            c.total_amount = sum(l.subtotal for l in c.line_ids)


class B2bCartDraftLine(models.Model):
    _name = "b2b.cart.draft.line"
    _description = "B2B 购物车明细"

    cart_id = fields.Many2one("b2b.cart.draft", string="购物车", ondelete="cascade")
    product_id = fields.Many2one("product.template", string="商品", required=True)
    qty = fields.Float(string="数量", default=1.0)
    unit_price = fields.Float(string="单价")
    subtotal = fields.Float(string="小计", compute="_compute_subtotal", store=True)

    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.qty * line.unit_price
