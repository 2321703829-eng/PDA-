from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LogisticsDispatchWaybillCustomerGoodsLine(models.Model):
    @api.model
    def get_import_templates(self):
        return [
            {
                "label": self.env._("下载货物明细模板"),
                "template": "/logistics_dispatch/static/src/import_templates/logistics_dispatch_waybill_customer_goods_line_import_template.csv",
            }
        ]

    _name = "logistics.dispatch.waybill.customer.goods.line"
    _description = "运单客户货物明细"
    _order = "sequence, id"

    sequence = fields.Integer(string="排序", default=10)
    customer_line_id = fields.Many2one(
        "logistics.dispatch.waybill.customer.line",
        string="客户明细",
        required=True,
        ondelete="cascade",
        index=True,
    )
    waybill_no = fields.Char(
        string="杩愬崟鍙凤紙瀵煎叆瀵煎嚭锛?,
        compute="_compute_waybill_no",
        inverse="_inverse_waybill_no",
    )
    waybill_id = fields.Many2one(
        "logistics.dispatch.waybill",
        string="运单",
        related="customer_line_id.waybill_id",
        store=True,
        readonly=True,
    )
    customer_id = fields.Many2one(
        "res.partner",
        string="客户",
        related="customer_line_id.customer_id",
        store=True,
        readonly=True,
    )
    customer_no = fields.Char(
        string="客户编号",
        related="customer_line_id.customer_no",
        store=True,
        readonly=True,
    )
    goods_code = fields.Char(string="货物编码")
    goods_name = fields.Char(string="货物名称", required=True)
    specification = fields.Char(string="规格")
    quantity = fields.Float(string="数量", required=True, default=1.0)
    package_count = fields.Integer(string="件数", default=0)
    uom_name = fields.Char(string="单位")
    weight = fields.Float(string="重量")
    volume = fields.Float(string="体积")
    temperature_zone = fields.Selection(
        [
            ("ambient", "常温"),
            ("chilled", "冷藏"),
            ("frozen", "冷冻"),
            ("other", "其他"),
        ],
        string="温层",
        default="ambient",
    )
    package_type = fields.Char(string="包装类型")
    remark = fields.Text(string="货物备注")

    @api.constrains("quantity", "package_count", "weight", "volume")
    def _check_non_negative_values(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError("货物数量必须大于 0。")
            if record.package_count < 0:
                raise ValidationError("货物件数不能小于 0。")
            if record.weight < 0 or record.volume < 0:
                raise ValidationError("货物重量和体积不能为负数。")
