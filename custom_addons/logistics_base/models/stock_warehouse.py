from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    logistics_contact_name = fields.Char(
        string="Logistics Contact Name",
    )
    logistics_contact_phone = fields.Char(
        string="Logistics Contact Phone",
    )
    logistics_status_note = fields.Text(
        string="Status Note",
    )
    logistics_operation_note = fields.Text(
        string="Operation Note",
    )
