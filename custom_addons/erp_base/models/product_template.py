from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # 箱规
    case_qty = fields.Float(
        string="箱装数量",
        help="每箱多少个基础单位",
    )
    case_uom_id = fields.Many2one(
        "uom.uom",
        string="箱单位",
        help="箱对应的计量单位，例如 '箱 / 件 / 包'",
    )

    # 物流辅助
    volume_m3 = fields.Float(
        string="体积 (m³)",
        help="单品体积，用于装车方数估算",
    )
    weight_kg = fields.Float(
        string="重量 (kg)",
        help="单品毛重",
    )

    # 经营辅助
    min_order_qty = fields.Float(
        string="最小起订量",
        default=1.0,
    )
    logistics_category = fields.Selection(
        [
            ("normal", "普通品"),
            ("fragile", "易碎品"),
            ("cold_chain", "冷链品"),
            ("hazardous", "危险品"),
        ],
        string="物流分类",
        default="normal",
    )
    is_active_sale = fields.Boolean(
        string="可销售",
        default=True,
        help="取消勾选后不显示在销售可选商品中",
    )
