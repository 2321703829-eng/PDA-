from odoo import fields, models


class ProductPriceAdjustment(models.Model):
    _name = "product.price.adjustment"
    _description = "价格调整记录"
    _order = "adjustment_date desc, id desc"

    product_id = fields.Many2one(
        "product.template", string="商品", required=True, ondelete="cascade"
    )
    adjustment_date = fields.Date(
        string="调价日期", required=True, default=fields.Date.context_today
    )
    old_price = fields.Float(string="调价前")
    new_price = fields.Float(string="调价后")
    price_type = fields.Selection(
        [
            ("sale", "销售价"),
            ("purchase", "采购成本价"),
            ("customer_level", "客户等级价"),
            ("industry", "行业价"),
        ],
        string="价格类型",
        default="sale",
    )
    reason = fields.Text(string="调价原因")
    user_id = fields.Many2one(
        "res.users", string="操作人", default=lambda self: self.env.user
    )
    state = fields.Selection(
        [("draft", "草稿"), ("confirmed", "已生效"), ("cancelled", "已作废")],
        string="状态",
        default="draft",
    )

    def action_confirm(self):
        # 确认时将新价写入商品
        for rec in self:
            if rec.price_type == "sale":
                rec.product_id.list_price = rec.new_price
            elif rec.price_type == "purchase":
                rec.product_id.standard_price = rec.new_price
            rec.state = "confirmed"
