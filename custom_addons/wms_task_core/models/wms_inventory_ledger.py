from odoo import fields, models


class WmsInventoryLedger(models.Model):
    _name = "wms.inventory.ledger"
    _description = "WMS Inventory Ledger"
    _auto = False
    _order = "id desc"

    company_id = fields.Many2one("res.company", string="Company")
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse")
    location_id = fields.Many2one("stock.location", string="Location")
    product_id = fields.Many2one("product.product", string="Product")
    product_tmpl_id = fields.Many2one("product.template", string="Product Template")
    product_uom_id = fields.Many2one("uom.uom", string="UoM")
    lot_id = fields.Many2one("stock.lot", string="Lot")
    quantity_on_hand = fields.Float(string="Quantity On Hand", digits=(16, 4))
    reserved_quantity = fields.Float(string="Reserved Quantity", digits=(16, 4))
    available_quantity = fields.Float(string="Available Quantity", digits=(16, 4))
    quant_count = fields.Integer(string="Quant Count")
    last_count_date = fields.Date(string="Last Count Date")
