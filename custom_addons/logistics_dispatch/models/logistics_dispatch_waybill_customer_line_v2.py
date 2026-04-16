from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LogisticsDispatchWaybillCustomerLine(models.Model):
    _name = "logistics.dispatch.waybill.customer.line"
    _description = "Waybill Customer Line"
    _order = "sequence, id"

    @api.model
    def get_import_templates(self):
        return [
            {
                "label": self.env._("下载客户明细模板"),
                "template": "/logistics_dispatch/static/src/import_templates/运单客户明细导入模板.csv",
            },
            {
                "label": self.env._("下载货物明细模板"),
                "template": "/logistics_dispatch/static/src/import_templates/运单货物明细导入模板.csv",
            },
        ]

    sequence = fields.Integer(string="Sequence", default=10)
    waybill_id = fields.Many2one(
        "logistics.dispatch.waybill",
        string="Waybill",
        required=True,
        ondelete="cascade",
        index=True,
    )
    waybill_no = fields.Char(
        string="Waybill No (Import/Export)",
        compute="_compute_waybill_no",
        inverse="_inverse_waybill_no",
    )
    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        domain="[('is_logistics_customer', '=', True)]",
        ondelete="set null",
    )
    customer_no = fields.Char(
        string="Customer No",
        compute="_compute_customer_no",
        inverse="_inverse_customer_no",
    )
    customer_name = fields.Char(
        string="Customer Name",
        compute="_compute_customer_name",
        inverse="_inverse_customer_name",
    )
    store_id = fields.Many2one(
        "res.partner",
        string="Store",
        domain="[('is_logistics_store', '=', True)]",
        ondelete="set null",
    )
    store_no = fields.Char(
        string="Store No",
        compute="_compute_store_no",
        inverse="_inverse_store_no",
    )
    store_name = fields.Char(
        string="Store Name",
        compute="_compute_store_name",
        inverse="_inverse_store_name",
    )
    delivery_note = fields.Text(string="Delivery Note")
    signoff_requirement = fields.Char(string="Signoff Requirement")
    goods_line_ids = fields.One2many(
        "logistics.dispatch.waybill.customer.goods.line",
        "customer_line_id",
        string="Goods Lines",
    )
    goods_line_count = fields.Integer(string="Goods Lines", compute="_compute_totals", store=True)
    total_goods_qty = fields.Float(string="Total Goods Qty", compute="_compute_totals", store=True)
    total_package_count = fields.Integer(string="Total Package Count", compute="_compute_totals", store=True)
    total_weight = fields.Float(string="Total Weight", compute="_compute_totals", store=True)
    total_volume = fields.Float(string="Total Volume", compute="_compute_totals", store=True)

    @api.depends("waybill_id.name")
    def _compute_waybill_no(self):
        for record in self:
            record.waybill_no = record.waybill_id.name or ""

    @api.depends("customer_id.logistics_customer_code")
    def _compute_customer_no(self):
        for record in self:
            record.customer_no = record.customer_id.logistics_customer_code or ""

    @api.depends("customer_id.name")
    def _compute_customer_name(self):
        for record in self:
            record.customer_name = record.customer_id.name or ""

    @api.depends("store_id.logistics_store_code")
    def _compute_store_no(self):
        for record in self:
            record.store_no = record.store_id.logistics_store_code or ""

    @api.depends("store_id.name")
    def _compute_store_name(self):
        for record in self:
            record.store_name = record.store_id.name or ""

    @api.depends(
        "goods_line_ids",
        "goods_line_ids.quantity",
        "goods_line_ids.package_count",
        "goods_line_ids.weight",
        "goods_line_ids.volume",
    )
    def _compute_totals(self):
        for record in self:
            record.goods_line_count = len(record.goods_line_ids)
            record.total_goods_qty = sum(record.goods_line_ids.mapped("quantity"))
            record.total_package_count = sum(record.goods_line_ids.mapped("package_count"))
            record.total_weight = sum(record.goods_line_ids.mapped("weight"))
            record.total_volume = sum(record.goods_line_ids.mapped("volume"))

    def _inverse_waybill_no(self):
        for record in self:
            waybill_no = (record.waybill_no or "").strip()
            record.waybill_id = self._resolve_waybill_by_no(waybill_no) if waybill_no else False

    def _inverse_customer_no(self):
        for record in self:
            customer_no = (record.customer_no or "").strip()
            record.customer_id = self._resolve_partner_by_code(customer_no, "customer") if customer_no else False

    def _inverse_customer_name(self):
        for record in self:
            customer_name = (record.customer_name or "").strip()
            record.customer_id = (
                self._resolve_partner_by_name(customer_name, "customer") if customer_name else False
            )

    def _inverse_store_no(self):
        for record in self:
            store_no = (record.store_no or "").strip()
            record.store_id = self._resolve_partner_by_code(store_no, "store") if store_no else False

    def _inverse_store_name(self):
        for record in self:
            store_name = (record.store_name or "").strip()
            record.store_id = self._resolve_partner_by_name(store_name, "store") if store_name else False

    @api.model
    def _ensure_unique_record(self, records, field_label, value):
        if not records:
            raise ValidationError(f'No record found for "{field_label}" = {value}.')
        if len(records) > 1:
            raise ValidationError(f'"{field_label}" = {value} matched multiple records. Please deduplicate first.')
        return records

    @api.model
    def _resolve_partner_by_code(self, code, partner_type):
        field_name = "logistics_customer_code" if partner_type == "customer" else "logistics_store_code"
        flag_name = "is_logistics_customer" if partner_type == "customer" else "is_logistics_store"
        label = "Customer No" if partner_type == "customer" else "Store No"
        partners = self.env["res.partner"].search(
            [(field_name, "=", code), (flag_name, "=", True)],
            limit=2,
        )
        return self._ensure_unique_record(partners, label, code)

    @api.model
    def _resolve_partner_by_name(self, name, partner_type):
        flag_name = "is_logistics_customer" if partner_type == "customer" else "is_logistics_store"
        label = "Customer Name" if partner_type == "customer" else "Store Name"
        partners = self.env["res.partner"].search(
            [("name", "=", name), (flag_name, "=", True)],
            limit=2,
        )
        return self._ensure_unique_record(partners, label, name)

    @api.model
    def _resolve_waybill_by_no(self, waybill_no):
        waybills = self.env["logistics.dispatch.waybill"].search([("name", "=", waybill_no)], limit=2)
        return self._ensure_unique_record(waybills, "Waybill No", waybill_no)

    @api.model_create_multi
    def create(self, vals_list):
        normalized_vals_list = []
        for vals in vals_list:
            normalized_vals = dict(vals)
            if "waybill_no" in normalized_vals and "waybill_id" not in normalized_vals:
                waybill_no = (normalized_vals.pop("waybill_no") or "").strip()
                normalized_vals["waybill_id"] = self._resolve_waybill_by_no(waybill_no).id if waybill_no else False
            normalized_vals_list.append(normalized_vals)
        return super().create(normalized_vals_list)

    def write(self, vals):
        normalized_vals = dict(vals)
        if "waybill_no" in normalized_vals and "waybill_id" not in normalized_vals:
            waybill_no = (normalized_vals.pop("waybill_no") or "").strip()
            normalized_vals["waybill_id"] = self._resolve_waybill_by_no(waybill_no).id if waybill_no else False
        return super().write(normalized_vals)

    @api.onchange("store_id")
    def _onchange_store_id(self):
        for record in self:
            if record.store_id and record.store_id.parent_id and not record.customer_id:
                record.customer_id = record.store_id.parent_id
