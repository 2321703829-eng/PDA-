from odoo import api, fields, models


class LogisticsDispatchWaybillStop(models.Model):
    _name = "logistics.dispatch.waybill.stop"
    _description = "Waybill Stop"
    _order = "stop_seq asc, id asc"
    _rec_name = "display_name"

    _sql_constraints = [
        (
            "uniq_logistics_dispatch_waybill_stop_seq",
            "unique(waybill_id, stop_seq)",
            "Each stop sequence must be unique within the same waybill.",
        ),
    ]

    waybill_id = fields.Many2one(
        "logistics.dispatch.waybill",
        string="Waybill",
        required=True,
        ondelete="cascade",
        index=True,
    )
    batch_id = fields.Many2one(
        "logistics.dispatch.batch",
        string="Batch",
        related="waybill_id.batch_id",
        store=True,
        readonly=True,
        index=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        related="waybill_id.warehouse_id.company_id",
        store=True,
        readonly=True,
        index=True,
    )
    stop_seq = fields.Integer(string="Stop Sequence", required=True, default=10, index=True)
    partner_id = fields.Many2one(
        "res.partner",
        string="Store",
        domain="[('is_logistics_store', '=', True)]",
        ondelete="set null",
        index=True,
    )
    stock_picking_id = fields.Many2one("stock.picking", string="Stock Picking", ondelete="set null")
    store_name = fields.Char(string="Store Name", required=True)
    address = fields.Char(string="Address")
    lat = fields.Float(string="Latitude", digits=(16, 6))
    lng = fields.Float(string="Longitude", digits=(16, 6))
    contact_name = fields.Char(string="Primary Contact")
    contact_phone = fields.Char(string="Primary Contact Phone")
    contact_list_json = fields.Text(string="Contact List JSON")
    guide_url = fields.Char(string="Guide URL")
    goods_info = fields.Char(string="Goods Info")
    active = fields.Boolean(default=True)
    display_name = fields.Char(string="Display Name", compute="_compute_display_name")

    @api.depends("store_name", "stop_seq", "waybill_id.name")
    def _compute_display_name(self):
        for record in self:
            store_name = record.store_name or "Stop"
            waybill_no = record.waybill_id.name or ""
            record.display_name = f"[{waybill_no}] {record.stop_seq} - {store_name}" if waybill_no else store_name

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        for record in self:
            if not record.partner_id:
                continue
            if not record.store_name:
                record.store_name = record.partner_id.display_name
            if not record.address:
                record.address = (
                    record.partner_id.contact_address
                    or record.partner_id.street
                    or record.partner_id.display_name
                )
            if not record.contact_name:
                record.contact_name = record.partner_id.name
            if not record.contact_phone:
                record.contact_phone = record.partner_id.phone or record.partner_id.mobile
            if "partner_latitude" in record.partner_id._fields and not record.lat:
                record.lat = record.partner_id.partner_latitude
            if "partner_longitude" in record.partner_id._fields and not record.lng:
                record.lng = record.partner_id.partner_longitude
