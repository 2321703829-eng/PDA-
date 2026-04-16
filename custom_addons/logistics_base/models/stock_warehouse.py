from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    logistics_contact_name = fields.Char(
        string="物流联系人",
    )
    logistics_contact_phone = fields.Char(
        string="物流联系电话",
    )
    logistics_status_note = fields.Text(
        string="状态备注",
    )
    logistics_operation_note = fields.Text(
        string="作业备注",
    )
