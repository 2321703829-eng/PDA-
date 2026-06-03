from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    _uniq_external_product_code = models.Constraint(
        "unique(external_product_code)",
        "外部商品编码必须唯一。",
    )

    internal_product_code = fields.Char(string="内部商品编码", size=64)
    external_product_code = fields.Char(string="外部商品编码", size=64, index=True)
    product_name = fields.Char(string="商品名称", size=128, translate=False)
    brand_name = fields.Char(string="品牌", size=64)
    category_name = fields.Char(string="分类", size=64)
    product_tag = fields.Char(string="商品标签", size=64)
    default_barcode = fields.Char(string="默认条码", size=64)
    base_unit_name = fields.Char(string="基础单位", size=32)
    default_weight = fields.Float(string="默认重量", digits=(16, 6), default=0.0)
    default_volume = fields.Float(string="默认体积", digits=(16, 6), default=0.0)
    delivery_requirement_text = fields.Text(string="配送要求")

    @api.model_create_multi
    def create(self, vals_list):
        normalized_vals_list = []
        for vals in vals_list:
            normalized_vals = dict(vals)
            if normalized_vals.get("product_name") and not normalized_vals.get("name"):
                normalized_vals["name"] = normalized_vals["product_name"]
            elif normalized_vals.get("name") and not normalized_vals.get("product_name"):
                normalized_vals["product_name"] = normalized_vals["name"]
            normalized_vals_list.append(normalized_vals)
        return super().create(normalized_vals_list)

    def write(self, vals):
        normalized_vals = dict(vals)
        if "product_name" in normalized_vals and "name" not in normalized_vals and normalized_vals["product_name"]:
            normalized_vals["name"] = normalized_vals["product_name"]
        elif "name" in normalized_vals and "product_name" not in normalized_vals and normalized_vals["name"]:
            normalized_vals["product_name"] = normalized_vals["name"]
        return super().write(normalized_vals)
