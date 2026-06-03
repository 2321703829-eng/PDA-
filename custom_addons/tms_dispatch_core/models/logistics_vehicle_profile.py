from odoo import fields, models

from odoo.addons.logistics_base.models.selection_options import VEHICLE_DISPATCH_STATUS_SELECTION


class LogisticsVehicleProfile(models.Model):
    _inherit = "logistics.vehicle.profile"

    dispatch_status = fields.Selection(
        selection=VEHICLE_DISPATCH_STATUS_SELECTION,
        string="Dispatch Status",
        default="idle",
    )
    home_warehouse_id = fields.Many2one("stock.warehouse", string="Home Warehouse", ondelete="set null")
    default_driver_profile_id = fields.Many2one("logistics.driver.profile", string="Default Driver", ondelete="set null")
