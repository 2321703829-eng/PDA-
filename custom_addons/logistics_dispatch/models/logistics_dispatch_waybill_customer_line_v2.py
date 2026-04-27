from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LogisticsDispatchWaybillCustomerLine(models.Model):
    _name = "logistics.dispatch.waybill.customer.line"
    _description = "运单配送节点明细"
    _order = "sequence, id"

    _uniq_waybill_customer_line_no = models.Constraint(
        "unique(waybill_id, customer_line_no)",
        "同一运单下的配送节点编号必须唯一。",
    )

    @api.model
    def get_import_templates(self):
        return [
            {
                "label": self.env._("下载标准模板（英文列头）"),
                "template": "/api/admin/logistics/imports/waybill-standard/template/download?template_code=TSL-IMPORT-WAYBILL-V3&template_version=v3&template_locale=en_US",
            },
            {
                "label": self.env._("下载标准模板（中文列头）"),
                "template": "/api/admin/logistics/imports/waybill-standard/template/download?template_code=TSL-IMPORT-WAYBILL-V3&template_version=v3&template_locale=zh_CN",
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
    waybill_no = fields.Char(string="运单号（导入导出）", compute="_compute_waybill_no", inverse="_inverse_waybill_no")
    customer_line_no = fields.Char(string="配送节点编号", size=64, index=True, copy=False)

    partner_id = fields.Many2one(
        "res.partner",
        string="客户",
        domain="[('is_logistics_partner', '=', True)]",
        ondelete="set null",
        index=True,
    )
    partner_no = fields.Char(string="客户号", compute="_compute_partner_fields", inverse="_inverse_partner_no")
    partner_name = fields.Char(string="客户名称", compute="_compute_partner_fields", inverse="_inverse_partner_name")

    # 兼容字段：保留底层旧口径，但用户界面不再直接暴露。
    customer_id = fields.Many2one(
        "res.partner",
        string="客户（兼容）",
        domain="[('is_logistics_partner', '=', True)]",
        ondelete="set null",
    )
    customer_no = fields.Char(string="客户号（兼容）", compute="_compute_customer_no", inverse="_inverse_customer_no")
    customer_name = fields.Char(string="客户名称（兼容）", compute="_compute_customer_name", inverse="_inverse_customer_name")
    store_id = fields.Many2one(
        "res.partner",
        string="客户（兼容门店）",
        related="partner_id",
        readonly=True,
        store=True,
    )
    store_no = fields.Char(string="客户号（兼容门店）", compute="_compute_store_no", inverse="_inverse_store_no")
    store_name = fields.Char(string="客户名称（兼容门店）", compute="_compute_store_name", inverse="_inverse_store_name")

    internal_customer_code_snapshot = fields.Char(string="内部客户编号快照", size=64)
    external_customer_code_snapshot = fields.Char(string="外联客户编号快照", size=64)
    customer_name_snapshot = fields.Char(string="客户名称快照", size=128)
    contact_name_snapshot = fields.Char(string="联系人快照", size=64)
    contact_phone_snapshot = fields.Char(string="电话快照", size=32)
    address_full_snapshot = fields.Text(string="地址快照")
    longitude_snapshot = fields.Float(string="经度快照", digits=(10, 7))
    latitude_snapshot = fields.Float(string="纬度快照", digits=(10, 7))
    address_region_json_snapshot = fields.Json(string="结构化地址快照")
    stop_seq_in_waybill = fields.Integer(string="运单内顺序", default=0, index=True)
    signoff_requirement_snapshot = fields.Char(string="签收要求快照", size=128)
    delivery_access_flags_snapshot = fields.Char(string="可达性快照", size=128)
    upstairs_floor_count_snapshot = fields.Integer(string="上楼层数快照", default=0)
    basement_height_limit_text_snapshot = fields.Text(string="地库限高快照")
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

    @api.depends("customer_id.external_customer_code", "customer_id.logistics_customer_code", "customer_id.logistics_store_code")
    def _compute_customer_no(self):
        for record in self:
            record.customer_no = (
                record.customer_id.external_customer_code
                or record.customer_id.logistics_customer_code
                or record.customer_id.logistics_store_code
                or ""
            )

    @api.depends("customer_id.name")
    def _compute_customer_name(self):
        for record in self:
            record.customer_name = record.customer_id.name or ""

    @api.depends("partner_id.external_customer_code", "partner_id.logistics_customer_code", "partner_id.logistics_store_code")
    def _compute_store_no(self):
        for record in self:
            record.store_no = record.partner_id.external_customer_code or record.partner_id.logistics_customer_code or record.partner_id.logistics_store_code or ""

    @api.depends("partner_id.name")
    def _compute_store_name(self):
        for record in self:
            record.store_name = record.partner_id.name or ""

    @api.depends(
        "partner_id",
        "partner_id.external_customer_code",
        "partner_id.internal_customer_code",
        "partner_id.logistics_customer_code",
        "partner_id.name",
        "customer_id",
    )
    def _compute_partner_fields(self):
        for record in self:
            partner = record.partner_id or record.customer_id
            record.partner_no = (
                partner.external_customer_code
                or partner.internal_customer_code
                or partner.logistics_customer_code
                or partner.logistics_store_code
                or ""
            )
            record.partner_name = partner.name or ""

    @api.depends("goods_line_ids", "goods_line_ids.quantity", "goods_line_ids.package_count", "goods_line_ids.weight", "goods_line_ids.volume")
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
            partner = self._resolve_partner_by_code(customer_no) if customer_no else False
            record._apply_partner_link(partner)

    def _inverse_customer_name(self):
        for record in self:
            customer_name = (record.customer_name or "").strip()
            partner = self._resolve_partner_by_name(customer_name) if customer_name else False
            record._apply_partner_link(partner)

    def _inverse_store_no(self):
        for record in self:
            store_no = (record.store_no or "").strip()
            partner = self._resolve_partner_by_code(store_no) if store_no else False
            record._apply_partner_link(partner)

    def _inverse_store_name(self):
        for record in self:
            store_name = (record.store_name or "").strip()
            partner = self._resolve_partner_by_name(store_name) if store_name else False
            record._apply_partner_link(partner)

    def _inverse_partner_no(self):
        for record in self:
            partner_no = (record.partner_no or "").strip()
            partner = self._resolve_partner_by_code(partner_no) if partner_no else False
            record._apply_partner_link(partner)

    def _inverse_partner_name(self):
        for record in self:
            partner_name = (record.partner_name or "").strip()
            partner = self._resolve_partner_by_name(partner_name) if partner_name else False
            record._apply_partner_link(partner)

    def _apply_partner_link(self, partner):
        for record in self:
            record.partner_id = partner or False
            record.customer_id = partner or False

    @api.model
    def _ensure_unique_record(self, records, field_label, value):
        if not records:
            raise ValidationError(f"未找到“{field_label} = {value}”对应的记录。")
        if len(records) > 1:
            raise ValidationError(f"“{field_label} = {value}”匹配到多条记录，请先去重。")
        return records

    @api.model
    def _resolve_partner_by_code(self, code):
        partners = self.env["res.partner"].search(
            [
                ("is_logistics_partner", "=", True),
                "|",
                "|",
                "|",
                ("external_customer_code", "=", code),
                ("internal_customer_code", "=", code),
                ("logistics_customer_code", "=", code),
                ("logistics_store_code", "=", code),
            ],
            limit=2,
        )
        return self._ensure_unique_record(partners, "客户号", code)

    @api.model
    def _resolve_partner_by_name(self, name):
        partners = self.env["res.partner"].search(
            [("name", "=", name), ("is_logistics_partner", "=", True)],
            limit=2,
        )
        return self._ensure_unique_record(partners, "客户名称", name)

    @api.model
    def _resolve_waybill_by_no(self, waybill_no):
        waybills = self.env["logistics.dispatch.waybill"].search([("name", "=", waybill_no)], limit=2)
        return self._ensure_unique_record(waybills, "运单号", waybill_no)

    @api.model
    def _generate_customer_line_no(self, waybill_id):
        prefix = self.env["logistics.dispatch.waybill"].browse(waybill_id).name or "WB"
        line_no = self.search_count([("waybill_id", "=", waybill_id)]) + 1
        return f"{prefix}-CL-{line_no:03d}"

    @api.model
    def _build_partner_snapshot_vals(self, normalized_vals):
        partner = self.env["res.partner"].browse(normalized_vals.get("partner_id"))
        return {
            "internal_customer_code_snapshot": partner.internal_customer_code or False,
            "external_customer_code_snapshot": partner.external_customer_code or False,
            "customer_name_snapshot": partner.name or False,
            "contact_name_snapshot": partner.contact_name or False,
            "contact_phone_snapshot": partner.contact_phone or False,
            "address_full_snapshot": partner.address_full or False,
            "longitude_snapshot": partner.partner_longitude or False,
            "latitude_snapshot": partner.partner_latitude or False,
            "address_region_json_snapshot": partner.address_region_json or False,
            "signoff_requirement_snapshot": partner.default_signoff_requirement or False,
            "delivery_access_flags_snapshot": partner.delivery_access_flags or False,
            "upstairs_floor_count_snapshot": partner.upstairs_floor_count or 0,
            "basement_height_limit_text_snapshot": partner.basement_height_limit_text or False,
        }

    @api.model
    def _normalize_partner_vals(self, vals):
        normalized_vals = dict(vals)
        partner = False
        partner_fields = {
            "partner_id",
            "customer_id",
            "partner_no",
            "customer_no",
            "store_no",
            "partner_name",
            "customer_name",
            "store_name",
        }
        partner_supplied = any(field_name in normalized_vals for field_name in partner_fields)

        if "partner_id" in normalized_vals:
            partner = self.env["res.partner"].browse(normalized_vals["partner_id"]) if normalized_vals["partner_id"] else False
        elif "customer_id" in normalized_vals and normalized_vals["customer_id"]:
            partner = self.env["res.partner"].browse(normalized_vals["customer_id"])
        elif "partner_no" in normalized_vals:
            partner_no = (normalized_vals.pop("partner_no") or "").strip()
            partner = self._resolve_partner_by_code(partner_no) if partner_no else False
        elif "customer_no" in normalized_vals:
            customer_no = (normalized_vals.pop("customer_no") or "").strip()
            partner = self._resolve_partner_by_code(customer_no) if customer_no else False
        elif "store_no" in normalized_vals:
            store_no = (normalized_vals.pop("store_no") or "").strip()
            partner = self._resolve_partner_by_code(store_no) if store_no else False
        elif "partner_name" in normalized_vals:
            partner_name = (normalized_vals.pop("partner_name") or "").strip()
            partner = self._resolve_partner_by_name(partner_name) if partner_name else False
        elif "customer_name" in normalized_vals:
            customer_name = (normalized_vals.pop("customer_name") or "").strip()
            partner = self._resolve_partner_by_name(customer_name) if customer_name else False
        elif "store_name" in normalized_vals:
            store_name = (normalized_vals.pop("store_name") or "").strip()
            partner = self._resolve_partner_by_name(store_name) if store_name else False

        if "waybill_no" in normalized_vals and "waybill_id" not in normalized_vals:
            waybill_no = (normalized_vals.pop("waybill_no") or "").strip()
            normalized_vals["waybill_id"] = self._resolve_waybill_by_no(waybill_no).id if waybill_no else False

        if partner_supplied:
            partner_id = partner.id if partner else False
            normalized_vals["partner_id"] = partner_id
            normalized_vals["customer_id"] = partner_id

        if not normalized_vals.get("customer_line_no") and normalized_vals.get("waybill_id"):
            normalized_vals["customer_line_no"] = self._generate_customer_line_no(normalized_vals["waybill_id"])

        if partner_supplied:
            for field_name, field_value in self._build_partner_snapshot_vals(normalized_vals).items():
                normalized_vals.setdefault(field_name, field_value)
        return normalized_vals

    @api.model_create_multi
    def create(self, vals_list):
        normalized_vals_list = [self._normalize_partner_vals(vals) for vals in vals_list]
        return super().create(normalized_vals_list)

    def write(self, vals):
        normalized_vals = self._normalize_partner_vals(vals)
        return super().write(normalized_vals)

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        for record in self:
            record._apply_partner_link(record.partner_id)
