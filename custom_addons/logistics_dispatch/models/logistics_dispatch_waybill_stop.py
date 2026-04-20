import json

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

    @api.model
    def _legacy_stop_table_exists(self):
        self.env.cr.execute("SELECT to_regclass('public.logistics_waybill_stop')")
        row = self.env.cr.fetchone()
        return bool(row and row[0])

    def _legacy_stop_keys(self):
        keys = []
        for record in self:
            waybill_no = record.waybill_id.name or ""
            if waybill_no and record.stop_seq:
                keys.append((waybill_no, record.stop_seq))
        return keys

    def _legacy_contact_list_json(self):
        self.ensure_one()
        if self.contact_list_json:
            try:
                raw = json.loads(self.contact_list_json)
                if isinstance(raw, list):
                    return json.dumps(raw, ensure_ascii=False)
            except json.JSONDecodeError:
                pass
        if self.contact_name or self.contact_phone:
            return json.dumps(
                [{"name": self.contact_name or "", "phone": self.contact_phone or ""}],
                ensure_ascii=False,
            )
        return json.dumps([], ensure_ascii=False)

    def _resolve_legacy_company_id(self):
        self.ensure_one()
        company = (
            self.company_id
            or self.waybill_id.warehouse_id.company_id
            or self.batch_id.warehouse_id.company_id
            or self.env.company
        )
        return company.id or None

    def _legacy_stop_vals(self):
        self.ensure_one()
        return {
            "company_id": self._resolve_legacy_company_id(),
            "stop_seq": self.stop_seq,
            "partner_id": self.partner_id.id or None,
            "stock_picking_id": self.stock_picking_id.id or None,
            "waybill_no": self.waybill_id.name or None,
            "batch_no": self.batch_id.name or None,
            "store_name": self.store_name or None,
            "address": self.address or None,
            "contact_name": self.contact_name or None,
            "contact_phone": self.contact_phone or None,
            "guide_url": self.guide_url or None,
            "driver_name": self.waybill_id.driver_employee_id.name or None,
            "vehicle_no": self.waybill_id.vehicle_id.license_plate or None,
            "contact_list_json": self._legacy_contact_list_json(),
            "goods_info": self.goods_info or None,
            "lat": self.lat if self.lat or self.lat == 0 else None,
            "lng": self.lng if self.lng or self.lng == 0 else None,
            "active": self.active,
            "create_uid": self.env.uid,
            "write_uid": self.env.uid,
        }

    @api.model
    def _delete_legacy_stop_rows(self, keys):
        if not keys or not self._legacy_stop_table_exists():
            return
        for waybill_no, stop_seq in sorted(set(keys)):
            self.env.cr.execute(
                """
                DELETE FROM logistics_waybill_stop
                WHERE waybill_no = %s AND stop_seq = %s
                """,
                (waybill_no, stop_seq),
            )

    def _sync_legacy_stop_rows(self):
        if not self or not self._legacy_stop_table_exists():
            return
        self._delete_legacy_stop_rows(self._legacy_stop_keys())
        for record in self:
            vals = record._legacy_stop_vals()
            if not vals["waybill_no"] or not vals["stop_seq"]:
                continue
            self.env.cr.execute(
                """
                INSERT INTO logistics_waybill_stop (
                    company_id,
                    stop_seq,
                    partner_id,
                    stock_picking_id,
                    create_uid,
                    write_uid,
                    waybill_no,
                    batch_no,
                    store_name,
                    address,
                    contact_name,
                    contact_phone,
                    guide_url,
                    driver_name,
                    vehicle_no,
                    contact_list_json,
                    goods_info,
                    lat,
                    lng,
                    active,
                    create_date,
                    write_date
                ) VALUES (
                    %(company_id)s,
                    %(stop_seq)s,
                    %(partner_id)s,
                    %(stock_picking_id)s,
                    %(create_uid)s,
                    %(write_uid)s,
                    %(waybill_no)s,
                    %(batch_no)s,
                    %(store_name)s,
                    %(address)s,
                    %(contact_name)s,
                    %(contact_phone)s,
                    %(guide_url)s,
                    %(driver_name)s,
                    %(vehicle_no)s,
                    %(contact_list_json)s,
                    %(goods_info)s,
                    %(lat)s,
                    %(lng)s,
                    %(active)s,
                    NOW(),
                    NOW()
                )
                """,
                vals,
            )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._sync_legacy_stop_rows()
        return records

    def write(self, vals):
        legacy_keys = self._legacy_stop_keys()
        result = super().write(vals)
        self._delete_legacy_stop_rows(legacy_keys)
        self._sync_legacy_stop_rows()
        return result

    def unlink(self):
        legacy_keys = self._legacy_stop_keys()
        result = super().unlink()
        self._delete_legacy_stop_rows(legacy_keys)
        return result
