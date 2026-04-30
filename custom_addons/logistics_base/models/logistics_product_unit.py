from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LogisticsProductUnit(models.Model):
    _name = "logistics.product.unit"
    _description = "商品规格"
    _table = "logistics_product_unit"
    _rec_name = "display_name"

    _uniq_product_unit_spec = models.Constraint(
        "unique(product_tmpl_id, spec_desc, sale_unit_name)",
        "同一商品、规格和销售单位组合必须唯一。",
    )

    company_id = fields.Many2one("res.company", string="公司", default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one("res.currency", string="币种", related="company_id.currency_id", store=True)
    product_tmpl_id = fields.Many2one(
        "product.template",
        string="商品本体",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sku_code = fields.Char(string="SKU 编号", size=64)
    spec_desc = fields.Char(string="规格描述", size=64, required=True)
    full_category_name = fields.Char(string="全级分类", size=128)
    unit_name = fields.Char(string="单位名", size=32, required=True)
    sale_unit_name = fields.Char(string="销售单位", size=32, required=True, index=True)
    convert_to_base = fields.Float(string="换算系数", digits=(16, 4), default=0.0)
    barcode = fields.Char(string="条码", size=64)
    standard_price = fields.Monetary(string="标准价", currency_field="currency_id", default=0.0)
    purchase_price = fields.Monetary(string="采购价", currency_field="currency_id", default=0.0)
    retail_price = fields.Monetary(string="零售价", currency_field="currency_id", default=0.0)
    sale_tax_rate = fields.Float(string="税率", digits=(8, 4), default=0.0)
    length_cm = fields.Float(string="长(cm)", digits=(16, 4), default=0.0)
    width_cm = fields.Float(string="宽(cm)", digits=(16, 4), default=0.0)
    height_cm = fields.Float(string="高(cm)", digits=(16, 4), default=0.0)
    weight = fields.Float(string="重量", digits=(16, 6), default=0.0)
    small_unit_weight = fields.Float(string="小单位重量", digits=(16, 6), default=0.0)
    middle_unit_weight = fields.Float(string="中单位重量", digits=(16, 6), default=0.0)
    volume = fields.Float(string="体积", digits=(16, 6), default=0.0)
    small_unit_volume = fields.Float(string="小单位体积", digits=(16, 6), default=0.0)
    middle_unit_volume = fields.Float(string="中单位体积", digits=(16, 6), default=0.0)
    volume_unit_large = fields.Char(string="大单位体积量纲", size=32)
    small_unit_qty = fields.Float(string="小单位数量", digits=(16, 4), default=0.0)
    middle_unit_qty = fields.Float(string="中单位数量", digits=(16, 4), default=0.0)
    gross_weight_unit_large = fields.Char(string="大单位重量量纲", size=32)
    large_unit_qty = fields.Float(string="大单位数量", digits=(16, 4), default=0.0)
    brand_owner_name = fields.Char(string="品牌方", size=64)
    default_vendor_name = fields.Char(string="默认供应商", size=64)
    buyer_name = fields.Char(string="采购员", size=64)
    min_order_qty = fields.Float(string="起订量", digits=(16, 4), default=0.0)
    can_press_stock = fields.Boolean(string="可压货", default=False)
    unit_remark = fields.Text(string="备注")
    display_name = fields.Char(string="显示名称", compute="_compute_display_name", store=True)

    @api.depends("product_tmpl_id.name", "spec_desc", "unit_name", "sale_unit_name")
    def _compute_display_name(self):
        for record in self:
            unit_label = record.unit_name or record.sale_unit_name or ""
            parts = [record.product_tmpl_id.name or "", record.spec_desc or "", unit_label]
            record.display_name = " / ".join(part for part in parts if part)

    @api.constrains(
        "convert_to_base",
        "sale_tax_rate",
        "standard_price",
        "purchase_price",
        "retail_price",
        "length_cm",
        "width_cm",
        "height_cm",
        "weight",
        "small_unit_weight",
        "middle_unit_weight",
        "small_unit_qty",
        "middle_unit_qty",
        "volume",
        "small_unit_volume",
        "middle_unit_volume",
        "large_unit_qty",
        "min_order_qty",
    )
    def _check_non_negative_values(self):
        numeric_fields = (
            "convert_to_base",
            "sale_tax_rate",
            "standard_price",
            "purchase_price",
            "retail_price",
            "length_cm",
            "width_cm",
            "height_cm",
            "weight",
            "small_unit_weight",
            "middle_unit_weight",
            "small_unit_qty",
            "middle_unit_qty",
            "volume",
            "small_unit_volume",
            "middle_unit_volume",
            "large_unit_qty",
            "min_order_qty",
        )
        for record in self:
            for field_name in numeric_fields:
                if record[field_name] < 0:
                    raise ValidationError(f"{self._fields[field_name].string}不能小于 0。")
