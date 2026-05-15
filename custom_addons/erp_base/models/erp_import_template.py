from odoo import fields, models


class ErpImportTemplate(models.Model):
    _name = "erp.import.template"
    _description = "导入导出模板"
    _order = "sequence, name"

    name = fields.Char(string="模板名称", required=True)
    sequence = fields.Integer(string="排序", default=10)
    template_type = fields.Selection(
        [
            ("order_import", "订单导入"),
            ("product_import", "商品导入"),
            ("customer_import", "客户导入"),
            ("supplier_import", "供应商导入"),
            ("order_export", "订单导出"),
            ("product_export", "商品导出"),
            ("report_export", "报表导出"),
            ("other", "其他"),
        ],
        string="模板类型",
        required=True,
    )
    description = fields.Text(string="说明")
    attachment_id = fields.Many2one(
        "ir.attachment", string="模板文件", ondelete="set null"
    )
    is_active = fields.Boolean(string="启用", default=True)
