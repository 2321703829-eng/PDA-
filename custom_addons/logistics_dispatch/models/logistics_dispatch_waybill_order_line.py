from odoo import fields, models


class LogisticsDispatchWaybillOrderLine(models.Model):
    _name = "logistics.dispatch.waybill.order.line"
    _description = "Waybill Order Line"
    _order = "id"

    waybill_id = fields.Many2one(
        "logistics.dispatch.waybill",
        string="运单",
        required=True,
        ondelete="cascade",
    )
    sale_order_id = fields.Many2one("sale.order", string="销售订单", ondelete="set null")
    stock_picking_id = fields.Many2one("stock.picking", string="出库单", ondelete="set null")
    external_order_no = fields.Char(string="外部单号", index=True)
    store_id = fields.Many2one(
        "res.partner",
        string="门店",
        domain="[('is_logistics_store', '=', True)]",
    )
    goods_summary = fields.Char(string="货物摘要")
    qty_summary = fields.Float(string="数量", digits="Product Unit of Measure")
    weight_summary = fields.Float(string="重量")
    volume_summary = fields.Float(string="体积")
    line_state = fields.Selection(
        [("draft", "草稿"), ("ready", "待执行"), ("done", "已完成"), ("cancelled", "已取消")],
        string="明细状态",
        default="draft",
        required=True,
    )
