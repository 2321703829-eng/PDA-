from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LogisticsDispatchWaybillCustomerLine(models.Model):
    _name = "logistics.dispatch.waybill.customer.line"
    _description = "运单客户明细"
    _order = "sequence, id"

    @api.model
    def get_import_templates(self):
        return [
            {
                "label": self.env._("下载标准模板（英文列头）"),
                "template": "/api/admin/logistics/imports/waybill-standard/template/download?template_code=TSL-IMPORT-WAYBILL-V2&template_version=v2&template_locale=en_US",
            },
            {
                "label": self.env._("下载标准模板（中文列头）"),
                "template": "/api/admin/logistics/imports/waybill-standard/template/download?template_code=TSL-IMPORT-WAYBILL-V2&template_version=v2&template_locale=zh_CN",
            },
        ]

    sequence = fields.Integer(string="排序", default=10)
    waybill_id = fields.Many2one(
        "logistics.dispatch.waybill",
        string="运单",
        required=True,
        ondelete="cascade",
        index=True,
    )
    waybill_no = fields.Char(
        string="运单号（导入导出）",
        compute="_compute_waybill_no",
        inverse="_inverse_waybill_no",
    )
    customer_id = fields.Many2one(
        "res.partner",
        string="客户",
        domain="[('is_logistics_customer', '=', True)]",
        ondelete="set null",
    )
    customer_no = fields.Char(
        string="客户号",
        compute="_compute_customer_no",
        inverse="_inverse_customer_no",
    )
    customer_name = fields.Char(
        string="客户名称",
        compute="_compute_customer_name",
        inverse="_inverse_customer_name",
    )
    store_id = fields.Many2one(
        "res.partner",
        string="门店",
        domain="[('is_logistics_store', '=', True)]",
        ondelete="set null",
    )
    store_no = fields.Char(
        string="门店号",
        compute="_compute_store_no",
        inverse="_inverse_store_no",
    )
    store_name = fields.Char(
        string="门店名称",
        compute="_compute_store_name",
        inverse="_inverse_store_name",
    )
    delivery_note = fields.Text(string="配送备注")
    signoff_requirement = fields.Char(string="签收要求")
    customer_ref = fields.Char(string="客户外部参考号")
    goods_line_ids = fields.One2many(
        "logistics.dispatch.waybill.customer.goods.line",
        "customer_line_id",
        string="货物明细",
    )
    goods_line_count = fields.Integer(string="货物条数", compute="_compute_totals", store=True)
    total_goods_qty = fields.Float(string="货物总数量", compute="_compute_totals", store=True)
    total_package_count = fields.Integer(string="货物总件数", compute="_compute_totals", store=True)
    total_weight = fields.Float(string="货物总重量", compute="_compute_totals", store=True)
    total_volume = fields.Float(string="货物总体积", compute="_compute_totals", store=True)

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
            record.customer_id = self._resolve_partner_by_name(customer_name, "customer") if customer_name else False

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
            raise ValidationError(f'未找到“{field_label}” = {value} 对应的记录。')
        if len(records) > 1:
            raise ValidationError(f'“{field_label}” = {value} 匹配到多条记录，请先去重。')
        return records

    @api.model
    def _resolve_partner_by_code(self, code, partner_type):
        field_name = "logistics_customer_code" if partner_type == "customer" else "logistics_store_code"
        flag_name = "is_logistics_customer" if partner_type == "customer" else "is_logistics_store"
        label = "客户号" if partner_type == "customer" else "门店号"
        partners = self.env["res.partner"].search([(field_name, "=", code), (flag_name, "=", True)], limit=2)
        return self._ensure_unique_record(partners, label, code)

    @api.model
    def _resolve_partner_by_name(self, name, partner_type):
        flag_name = "is_logistics_customer" if partner_type == "customer" else "is_logistics_store"
        label = "客户名称" if partner_type == "customer" else "门店名称"
        partners = self.env["res.partner"].search([("name", "=", name), (flag_name, "=", True)], limit=2)
        return self._ensure_unique_record(partners, label, name)

    @api.model
    def _resolve_waybill_by_no(self, waybill_no):
        waybills = self.env["logistics.dispatch.waybill"].search([("name", "=", waybill_no)], limit=2)
        return self._ensure_unique_record(waybills, "运单号", waybill_no)

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
