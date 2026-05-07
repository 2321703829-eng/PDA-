from odoo import fields, models


class LogisticsWaybillStop(models.Model):
    _name = "logistics.waybill.stop"
    _description = "Waybill Stop"
    _order = "stop_seq asc, id asc"

    _sql_constraints = [
        (
            "uniq_waybill_stop_seq",
            "unique(waybill_no, stop_seq)",
            "Each waybill stop sequence must be unique.",
        ),
    ]

    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    waybill_no = fields.Char(required=True, index=True)
    batch_no = fields.Char(index=True)
    stop_seq = fields.Integer(required=True, index=True)
    store_name = fields.Char(required=True)
    address = fields.Char()
    lat = fields.Float(string="Latitude", digits=(16, 6))
    lng = fields.Float(string="Longitude", digits=(16, 6))
    contact_name = fields.Char()
    contact_phone = fields.Char()
    contact_list_json = fields.Text()
    guide_url = fields.Char()
    goods_info = fields.Text()
    driver_name = fields.Char()
    vehicle_no = fields.Char()
    partner_id = fields.Many2one("res.partner", string="Store / Contact", index=True)
    stock_picking_id = fields.Many2one(
        "stock.picking",
        string="Related Odoo Delivery Record",
        index=True,
    )
