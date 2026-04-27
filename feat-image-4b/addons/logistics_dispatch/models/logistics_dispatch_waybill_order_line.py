from odoo import api, fields, models
from odoo.exceptions import ValidationError


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

    @api.onchange("sale_order_id")
    def _onchange_sale_order_id(self):
        for record in self:
            sale_order = record.sale_order_id
            if not sale_order:
                continue
            if not record.external_order_no:
                record.external_order_no = sale_order.client_order_ref or sale_order.name
            if not record.store_id:
                record.store_id = sale_order.partner_shipping_id or sale_order.partner_id

    @api.onchange("stock_picking_id")
    def _onchange_stock_picking_id(self):
        for record in self:
            picking = record.stock_picking_id
            if not picking:
                continue
            if not record.store_id:
                record.store_id = picking.partner_id

    @api.constrains("sale_order_id", "stock_picking_id")
    def _check_order_source(self):
        for record in self:
            if not record.sale_order_id and not record.stock_picking_id:
                raise ValidationError("Waybill order line must reference sale.order or stock.picking.")
