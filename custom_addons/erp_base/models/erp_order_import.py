from odoo import fields, models


class ErpOrderImport(models.Model):
    _name = "erp.order.import"
    _description = "订单导入批次"
    _order = "create_date desc, id desc"

    name = fields.Char(string="批次名称", required=True, default="新导入")
    import_file = fields.Binary(string="Excel 文件", attachment=True)
    file_name = fields.Char(string="文件名")
    state = fields.Selection(
        [
            ("draft", "待清洗"),
            ("validated", "已校验"),
            ("imported", "已导入"),
            ("error", "异常"),
        ],
        string="状态",
        default="draft",
    )
    total_rows = fields.Integer(string="总行数")
    matched_rows = fields.Integer(string="匹配成功")
    error_rows = fields.Integer(string="异常行数")
    log = fields.Text(string="处理日志")
    order_ids = fields.One2many(
        "erp.order.import.line", "import_id", string="导入明细"
    )


class ErpOrderImportLine(models.Model):
    _name = "erp.order.import.line"
    _description = "订单导入明细"

    import_id = fields.Many2one(
        "erp.order.import", string="导入批次", ondelete="cascade"
    )
    sequence = fields.Integer(string="行号")
    raw_data = fields.Text(string="原始数据")
    customer_name = fields.Char(string="客户名称")
    store_name = fields.Char(string="门店名称")
    product_name = fields.Char(string="商品名称")
    quantity = fields.Float(string="数量")
    match_status = fields.Selection(
        [
            ("pending", "待匹配"),
            ("matched", "已匹配"),
            ("unmatched", "未匹配"),
        ],
        string="匹配状态",
        default="pending",
    )
    partner_id = fields.Many2one("res.partner", string="匹配客户")
    product_id = fields.Many2one("product.product", string="匹配商品")
    error_msg = fields.Text(string="错误信息")
