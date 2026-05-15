from odoo import fields, models


class B2bCatalogScope(models.Model):
    _name = "b2b.catalog.scope"
    _description = "B2B 可见范围"
    _order = "id desc"

    name = fields.Char(string="规则名称", required=True)
    partner_id = fields.Many2one("res.partner", string="客户/门店")
    scope_type = fields.Selection(
        [("include", "可见"), ("exclude", "不可见")],
        string="范围类型", required=True, default="include",
    )
    product_ids = fields.Many2many("product.template", string="商品")
    product_category_ids = fields.Many2many("product.category", string="商品分类")
    is_active = fields.Boolean(string="启用", default=True)
