from odoo import fields, models

from odoo.addons.logistics_base.models.selection_options import DRIVER_DISPATCH_STATUS_SELECTION


class LogisticsDriverProfile(models.Model):
    _inherit = "logistics.driver.profile"

    dispatch_status = fields.Selection(
        selection=DRIVER_DISPATCH_STATUS_SELECTION,
        string="Dispatch Status",
        default="idle",
    )
    home_warehouse_id = fields.Many2one("stock.warehouse", string="Home Warehouse", ondelete="set null")
