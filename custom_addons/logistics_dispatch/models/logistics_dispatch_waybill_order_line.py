from odoo import fields, models


class LogisticsDispatchWaybillOrderLine(models.Model):
    _name = "logistics.dispatch.waybill.order.line"
    _description = "Waybill Order Line"
    _order = "id"

    waybill_id = fields.Many2one(
        "logistics.dispatch.waybill",
        string="Waybill",
        required=True,
        ondelete="cascade",
    )
    sale_order_id = fields.Many2one("sale.order", string="Sale Order", ondelete="set null")
    stock_picking_id = fields.Many2one("stock.picking", string="Stock Picking", ondelete="set null")
    external_order_no = fields.Char(string="External Order No", index=True)
    store_id = fields.Many2one(
        "res.partner",
        string="Store",
        domain="[('is_logistics_store', '=', True)]",
    )
    goods_summary = fields.Char(string="Goods Summary")
    qty_summary = fields.Float(string="Quantity", digits="Product Unit of Measure")
    weight_summary = fields.Float(string="Weight")
    volume_summary = fields.Float(string="Volume")
    line_state = fields.Selection(
        [("draft", "Draft"), ("ready", "Ready"), ("done", "Done"), ("cancelled", "Cancelled")],
        string="Line Status",
        default="draft",
        required=True,
    )
