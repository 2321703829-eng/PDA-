from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # ERP 经营字段
    delivery_deadline = fields.Date(string="要求送达日")
    is_urgent = fields.Boolean(string="加急订单")
    batch_ref = fields.Char(string="批次参考号", index=True)
    store_count = fields.Integer(string="门店数", compute="_compute_store_count", store=True)
    delivery_note = fields.Text(string="配送备注")
    # 状态摘要
    wms_status = fields.Selection(
        [("pending", "待出库"), ("picking", "拣货中"), ("ready", "待发运"), ("done", "已出库")],
        string="仓库状态", default="pending",
    )
    tms_status = fields.Selection(
        [("pending", "待排线"), ("dispatched", "已派车"), ("in_transit", "在途"),
         ("signed", "已签收"), ("exception", "异常")],
        string="配送状态", default="pending",
    )

    def _compute_store_count(self):
        for order in self:
            order.store_count = len(order.order_line.mapped("store_id"))


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    store_id = fields.Many2one("res.partner", string="门店",
        domain=[("is_store", "=", True)])
    logistics_category = fields.Selection(related="product_id.logistics_category", store=True)
