from odoo import fields, models

from .selection_options import WMS_CHECK_TASK_STATUS_SELECTION, WMS_PICK_TASK_STATUS_SELECTION


class StockMove(models.Model):
    _inherit = "stock.move"

    store_partner_id = fields.Many2one(
        "res.partner",
        string="Store Partner",
        index=True,
    )
    wms_pick_status = fields.Selection(
        selection=WMS_PICK_TASK_STATUS_SELECTION,
        string="WMS Pick Status",
    )
    wms_check_status = fields.Selection(
        selection=WMS_CHECK_TASK_STATUS_SELECTION,
        string="WMS Check Status",
    )
