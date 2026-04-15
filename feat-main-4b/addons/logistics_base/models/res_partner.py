from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_logistics_customer = fields.Boolean(
        string="Logistics Customer",
        help="Identify partners that should be managed as logistics customers.",
    )
    is_logistics_store = fields.Boolean(
        string="Logistics Store",
        help="Identify partners that should be managed as logistics stores or delivery points.",
    )
    logistics_customer_code = fields.Char(
        string="Customer Code",
        index=True,
        copy=False,
    )
    logistics_store_code = fields.Char(
        string="Store Code",
        index=True,
        copy=False,
    )
    logistics_customer_level = fields.Selection(
        selection=[
            ("standard", "Standard"),
            ("vip", "VIP"),
            ("strategic", "Strategic"),
        ],
        string="Customer Level",
    )
    logistics_customer_status = fields.Selection(
        selection=[
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("paused", "Paused"),
        ],
        string="Customer Status",
        default="active",
    )
    logistics_store_status = fields.Selection(
        selection=[
            ("active", "Active"),
            ("inactive", "Inactive"),
        ],
        string="Store Status",
        default="active",
    )
    logistics_delivery_time_window = fields.Char(
        string="Delivery Time Window",
    )
    logistics_unload_requirement = fields.Text(
        string="Unload Requirement",
    )
    logistics_need_sign_receipt = fields.Boolean(
        string="Need Sign Receipt",
        default=False,
    )
    logistics_service_note = fields.Text(
        string="Service Note",
    )
    logistics_internal_reference = fields.Char(
        string="Internal Reference",
        index=True,
        copy=False,
    )
