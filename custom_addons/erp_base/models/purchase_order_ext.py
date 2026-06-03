from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    expected_arrival = fields.Date(string="预计到货日")
    batch_ref = fields.Char(string="批次参考号", index=True)
    receiving_status = fields.Selection(
        [("pending", "待收货"), ("partial", "部分收货"), ("received", "已收货"),
         ("exception", "收货异常")],
        string="收货状态", default="pending",
    )
    warehouse_id = fields.Many2one("stock.warehouse", string="目标仓库")
    logistics_note = fields.Text(string="物流备注")


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    expected_qty = fields.Float(string="预期收货数量")
    received_qty = fields.Float(string="实际收货数量")
