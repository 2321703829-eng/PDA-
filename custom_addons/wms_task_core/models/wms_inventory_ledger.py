from odoo import fields, models


class WmsInventoryLedger(models.Model):
    _name = "wms.inventory.ledger"
    _description = "WMS Inventory Ledger"
    _auto = False
    _order = "event_time desc, id desc"

    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", index=True, ondelete="cascade")
    location_id = fields.Many2one("stock.location", string="Location", index=True, ondelete="set null")
    product_id = fields.Many2one("product.product", string="Product", index=True, ondelete="set null")
    lot_id = fields.Many2one("stock.lot", string="Lot", ondelete="set null")
    event_time = fields.Datetime(string="Event Time", default=fields.Datetime.now, index=True)
    document_no = fields.Char(string="Document No", index=True)
    source_model = fields.Char(string="Source Model")
    source_res_id = fields.Integer(string="Source Record ID")
    movement_type = fields.Selection(
        [
            ("receipt", "Receipt"),
            ("putaway", "Putaway"),
            ("outbound", "Outbound"),
            ("inventory_count", "Inventory Count"),
            ("stock_adjustment", "Stock Adjustment"),
            ("warehouse_return", "Warehouse Return"),
        ],
        string="Movement Type",
    )
    qty_in = fields.Float(string="Qty In", digits=(16, 4), default=0.0)
    qty_out = fields.Float(string="Qty Out", digits=(16, 4), default=0.0)
    qty_balance = fields.Float(string="Qty Balance", digits=(16, 4), default=0.0)
    note = fields.Char(string="Remark")
