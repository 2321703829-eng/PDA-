from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_b2b_visible = fields.Boolean(string="B2B 可见", default=True)
    b2b_sort_no = fields.Integer(string="B2B 排序", default=10)
    b2b_min_qty = fields.Float(string="B2B 起订量", default=1.0)
    b2b_saleable_desc = fields.Text(string="B2B 可销售说明")
