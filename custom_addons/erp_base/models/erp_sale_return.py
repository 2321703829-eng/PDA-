from odoo import fields, models


class ErpSaleReturn(models.Model):
    _name = "erp.sale.return"
    _description = "销售退货单"
    _order = "return_date desc, id desc"

    name = fields.Char(string="退货单号", required=True)
    sale_order_id = fields.Many2one("sale.order", string="原销售订单")
    partner_id = fields.Many2one("res.partner", string="客户", required=True)
    return_date = fields.Date(string="退货日期", default=fields.Date.context_today)
    return_reason = fields.Selection(
        [("damage", "破损"), ("shortage", "短少"), ("wrong_item", "错货"),
         ("quality", "质量问题"), ("customer_reject", "客户拒收"),
         ("other", "其他")],
        string="退货原因", required=True,
    )
    state = fields.Selection(
        [("draft", "草稿"), ("confirmed", "已确认"), ("received", "已收货"),
         ("refunded", "已退款"), ("cancelled", "已取消")],
        string="状态", default="draft",
    )
    amount_total = fields.Float(string="退货金额")
    picking_ids = fields.Many2many("stock.picking", string="关联入库单")
    refund_invoice_id = fields.Many2one("account.move", string="退款凭证")
    note = fields.Text(string="备注")
