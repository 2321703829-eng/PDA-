from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LogisticsDispatchWaybill(models.Model):
    _name = "logistics.dispatch.waybill"
    _description = "物流运单"
    _order = "delivery_date desc, id desc"
    _rec_name = "name"

    _uniq_waybill_no = models.Constraint(
        "unique(name)",
        "运单号必须唯一。",
    )

    @api.model
    def get_import_templates(self):
        return [
            {
                "label": _("下载标准模板（英文列头）"),
                "template": "/api/admin/logistics/imports/waybill-standard/template/download?template_code=TSL-IMPORT-WAYBILL-V3&template_version=v3&template_locale=en_US",
            },
            {
                "label": _("下载标准模板（中文列头）"),
                "template": "/api/admin/logistics/imports/waybill-standard/template/download?template_code=TSL-IMPORT-WAYBILL-V3&template_version=v3&template_locale=zh_CN",
            },
        ]

    name = fields.Char(string="运单号", required=True, copy=False, default="新建", index=True)
    waybill_no = fields.Char(string="运单号（导入导出）", compute="_compute_waybill_no", inverse="_inverse_waybill_no")
    waybill_group_no = fields.Char(string="运单分组号", size=64, index=True)
    delivery_date = fields.Date(string="配送日期", default=fields.Date.context_today, index=True)

    partner_id = fields.Many2one(
        "res.partner",
        string="客户",
        store=True,
        domain="[('is_logistics_partner', '=', True)]",
        ondelete="set null",
    )
    partner_no = fields.Char(string="客户号（导入导出）", compute="_compute_partner_fields", inverse="_inverse_partner_no", store=True)
    partner_name = fields.Char(string="客户名称（导入导出）", compute="_compute_partner_fields", inverse="_inverse_partner_name", store=True)

    # 兼容字段：保留底层导入与旧联调口径，但用户界面不再直接暴露。
    store_id = fields.Many2one(
        "res.partner",
        string="客户（兼容门店）",
        domain="[('is_logistics_partner', '=', True)]",
        ondelete="set null",
    )
    store_no = fields.Char(string="客户号（兼容门店）", compute="_compute_store_no", inverse="_inverse_store_no")
    store_name = fields.Char(string="客户名称（兼容门店）", compute="_compute_store_name", inverse="_inverse_store_name")
    customer_id = fields.Many2one(
        "res.partner",
        string="客户（兼容）",
        domain="[('is_logistics_partner', '=', True)]",
        ondelete="set null",
    )
    customer_no = fields.Char(string="客户号（兼容）", compute="_compute_customer_no", inverse="_inverse_customer_no")
    customer_name = fields.Char(
        string="客户名称（兼容）",
        compute="_compute_customer_name",
        inverse="_inverse_customer_name",
    )

    batch_id = fields.Many2one("logistics.dispatch.batch", string="批次", ondelete="cascade", index=True)
    batch_no = fields.Char(string="批次号（导入导出）", compute="_compute_batch_no", inverse="_inverse_batch_no")
    wave_id = fields.Many2one("logistics.dispatch.wave", string="波次", related="batch_id.wave_id", store=True, readonly=True)
    warehouse_id = fields.Many2one("stock.warehouse", string="仓库")
    vehicle_id = fields.Many2one("fleet.vehicle", string="车辆", related="batch_id.vehicle_id", store=True, readonly=True)
    driver_employee_id = fields.Many2one(
        "hr.employee",
        string="司机",
        related="batch_id.driver_employee_id",
        store=True,
        readonly=True,
    )
    organization_name_snapshot = fields.Char(string="组织快照", size=64)
    warehouse_name_snapshot = fields.Char(string="仓库快照", size=64)
    route_name_snapshot = fields.Char(string="线路快照", size=64)
    route_seq = fields.Integer(string="线路顺序", default=10)
    state = fields.Selection(
        [
            ("draft", "草稿"),
            ("ready", "待执行"),
            ("in_transit", "在途"),
            ("arrived", "已到店"),
            ("signed", "已签收"),
            ("done", "已完成"),
            ("cancelled", "已取消"),
        ],
        string="状态",
        default="draft",
        required=True,
    )
    arrive_trace_status = fields.Selection(
        [("pending", "待补全"), ("partial", "部分完成"), ("done", "已完成")],
        string="到店留痕",
        default="pending",
    )
    signoff_trace_status = fields.Selection(
        [("pending", "待补全"), ("partial", "部分完成"), ("done", "已完成")],
        string="签收留痕",
        default="pending",
    )
    exception_status = fields.Selection(
        [("none", "无异常"), ("open", "待处理"), ("processing", "处理中"), ("closed", "已关闭")],
        string="异常状态",
        default="none",
        required=True,
    )
    evidence_status = fields.Selection(
        [("missing", "待补全"), ("partial", "部分齐全"), ("complete", "已齐全")],
        string="证据状态",
        default="missing",
        required=True,
    )
    risk_level = fields.Selection([("low", "低"), ("medium", "中"), ("high", "高")], string="风险等级", default="low")
    latest_trace_time = fields.Datetime(string="最新留痕时间")
    latest_trace_type = fields.Char(string="最新留痕类型")
    latest_trace_summary = fields.Char(string="最新留痕摘要")
    trace_count = fields.Integer(string="留痕数", default=0)
    evidence_count = fields.Integer(string="证据数", default=0)
    open_exception_count = fields.Integer(string="待处理异常数", default=0)
    order_line_ids = fields.One2many("logistics.dispatch.waybill.order.line", "waybill_id", string="订单明细")
    customer_line_ids = fields.One2many("logistics.dispatch.waybill.customer.line", "waybill_id", string="配送节点明细")
    goods_line_ids = fields.One2many("logistics.dispatch.waybill.customer.goods.line", "waybill_id", string="货物明细")
    order_line_count = fields.Integer(string="订单数", compute="_compute_order_line_count", store=True)
    customer_line_count = fields.Integer(string="配送节点数", compute="_compute_detail_counts", store=True)
    goods_line_count = fields.Integer(string="货物条数", compute="_compute_detail_counts", store=True)
    total_goods_qty = fields.Float(string="货物总数量", compute="_compute_detail_counts", store=True)
    total_package_count = fields.Integer(string="货物总件数", compute="_compute_detail_counts", store=True)
    total_goods_weight = fields.Float(string="货物总重量", compute="_compute_detail_counts", store=True)
    total_goods_volume = fields.Float(string="货物总体积", compute="_compute_detail_counts", store=True)
    delivery_remark_snapshot = fields.Text(string="运单备注")
    remark = fields.Text(string="备注")

    @api.depends("name")
    def _compute_waybill_no(self):
        for record in self:
            record.waybill_no = record.name or ""

    @api.depends("batch_id.name")
    def _compute_batch_no(self):
        for record in self:
            record.batch_no = record.batch_id.name or ""

    @api.depends("customer_id.logistics_customer_code", "customer_id.logistics_store_code", "customer_id.external_customer_code")
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

    @api.depends("store_id.logistics_store_code", "store_id.external_customer_code", "store_id.logistics_customer_code")
    def _compute_store_no(self):
        for record in self:
            record.store_no = record.store_id.external_customer_code or record.store_id.logistics_customer_code or record.store_id.logistics_store_code or ""

    @api.depends("store_id.name")
    def _compute_store_name(self):
        for record in self:
            record.store_name = record.store_id.name or ""

    @api.depends(
        "partner_id",
        "partner_id.external_customer_code",
        "partner_id.internal_customer_code",
        "partner_id.logistics_customer_code",
        "partner_id.name",
        "customer_id",
        "store_id",
    )
    def _compute_partner_fields(self):
        for record in self:
            partner = record.partner_id or record.customer_id or record.store_id
            record.partner_no = (
                partner.external_customer_code
                or partner.internal_customer_code
                or partner.logistics_customer_code
                or partner.logistics_store_code
                or ""
            )
            record.partner_name = partner.name or ""

    def _inverse_waybill_no(self):
        for record in self:
            record.name = (record.waybill_no or "").strip() or record.name or "新建"

    def _inverse_batch_no(self):
        for record in self:
            batch_no = (record.batch_no or "").strip()
            record.batch_id = self._resolve_batch_by_no(batch_no) if batch_no else False

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

    def _inverse_partner_id(self):
        for record in self:
            record._apply_partner_link(record.partner_id)

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
        link_vals = self._prepare_partner_link_vals(partner)
        for record in self:
            record.update(link_vals)

    @api.model
    def _prepare_partner_link_vals(self, partner):
        partner_id = partner.id if partner else False
        return {
            "partner_id": partner_id,
            "customer_id": partner_id,
            "store_id": partner_id,
        }

    @api.model
    def _ensure_unique_record(self, records, field_label, value):
        if not records:
            raise ValidationError(f"未找到“{field_label} = {value}”对应的记录。")
        if len(records) > 1:
            raise ValidationError(f"“{field_label} = {value}”匹配到多条记录，请先去重。")
        return records

    @api.model
    def _resolve_batch_by_no(self, batch_no):
        batches = self.env["logistics.dispatch.batch"].search([("name", "=", batch_no)], limit=2)
        return self._ensure_unique_record(batches, "批次号", batch_no)

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
    def _build_snapshot_vals(self, normalized_vals):
        batch = self.env["logistics.dispatch.batch"].browse(normalized_vals.get("batch_id"))
        warehouse = self.env["stock.warehouse"].browse(normalized_vals.get("warehouse_id")) or batch.warehouse_id
        partner = self.env["res.partner"].browse(normalized_vals.get("partner_id"))
        return {
            "organization_name_snapshot": partner.organization_name or batch.wave_id.organization_name_snapshot or warehouse.company_id.name or False,
            "warehouse_name_snapshot": warehouse.name or False,
            "route_name_snapshot": batch.route_name_snapshot or batch.route_summary or False,
            "delivery_remark_snapshot": normalized_vals.get("delivery_remark_snapshot") or normalized_vals.get("remark") or False,
        }

    @api.model
    def _normalize_partner_vals(self, vals):
        normalized_vals = dict(vals)
        partner = False
        partner_fields = {
            "partner_id",
            "customer_id",
            "store_id",
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
        elif "store_id" in normalized_vals and normalized_vals["store_id"]:
            partner = self.env["res.partner"].browse(normalized_vals["store_id"])
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

        if "waybill_no" in normalized_vals:
            normalized_vals["name"] = (normalized_vals.pop("waybill_no") or "").strip() or normalized_vals.get("name") or "新建"
        if "batch_no" in normalized_vals and not normalized_vals.get("batch_id"):
            batch_no = (normalized_vals.pop("batch_no") or "").strip()
            normalized_vals["batch_id"] = self._resolve_batch_by_no(batch_no).id if batch_no else False

        batch_id = normalized_vals.get("batch_id")
        if batch_id and not normalized_vals.get("warehouse_id"):
            batch = self.env["logistics.dispatch.batch"].browse(batch_id)
            normalized_vals["warehouse_id"] = batch.warehouse_id.id

        if partner_supplied:
            normalized_vals.update(self._prepare_partner_link_vals(partner))

        refresh_snapshot = not self.env.context.get("skip_waybill_snapshot_sync") and (
            self.env.context.get("waybill_snapshot_force")
            or any(
                field_name in normalized_vals
                for field_name in (
                    "batch_id",
                    "warehouse_id",
                    "partner_id",
                    "customer_id",
                    "store_id",
                    "remark",
                )
            )
        )
        if refresh_snapshot:
            snapshot_vals = self._build_snapshot_vals(normalized_vals)
            for field_name, field_value in snapshot_vals.items():
                if field_name not in normalized_vals:
                    normalized_vals[field_name] = field_value

        return normalized_vals

    @api.constrains("batch_id", "warehouse_id")
    def _check_batch_warehouse_consistency(self):
        for record in self:
            if record.batch_id and not record.warehouse_id:
                raise ValidationError("Waybill warehouse is required when batch_id is set.")
            if record.batch_id and record.warehouse_id and record.batch_id.warehouse_id != record.warehouse_id:
                raise ValidationError("Waybill warehouse must match its batch warehouse.")

    @api.depends("order_line_ids")
    def _compute_order_line_count(self):
        for record in self:
            record.order_line_count = len(record.order_line_ids)

    @api.depends(
        "customer_line_ids",
        "goods_line_ids",
        "goods_line_ids.quantity",
        "goods_line_ids.package_count",
        "goods_line_ids.weight",
        "goods_line_ids.volume",
    )
    def _compute_detail_counts(self):
        for record in self:
            record.customer_line_count = len(record.customer_line_ids)
            record.goods_line_count = len(record.goods_line_ids)
            record.total_goods_qty = sum(record.goods_line_ids.mapped("quantity"))
            record.total_package_count = sum(record.goods_line_ids.mapped("package_count"))
            record.total_goods_weight = sum(record.goods_line_ids.mapped("weight"))
            record.total_goods_volume = sum(record.goods_line_ids.mapped("volume"))

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        for record in self:
            record._apply_partner_link(record.partner_id)

    @api.onchange("batch_id")
    def _onchange_batch_id(self):
        for record in self:
            if record.batch_id:
                record.warehouse_id = record.batch_id.warehouse_id

    @api.model_create_multi
    def create(self, vals_list):
        normalized_vals_list = []
        for vals in vals_list:
            normalized_vals = self.with_context(waybill_snapshot_force=True)._normalize_partner_vals(vals)
            if normalized_vals.get("name", "新建") in ("New", "新建"):
                normalized_vals["name"] = self.env["ir.sequence"].next_by_code("logistics.dispatch.waybill") or "新建"
            normalized_vals_list.append(normalized_vals)
        return super().create(normalized_vals_list)

    def write(self, vals):
        normalized_vals = self._normalize_partner_vals(vals)
        return super().write(normalized_vals)

    def action_open_batch(self):
        self.ensure_one()
        if not self.batch_id:
            return False
        action = self.env.ref("logistics_dispatch.action_logistics_dispatch_batch").read()[0]
        action["res_id"] = self.batch_id.id
        action["views"] = [(self.env.ref("logistics_dispatch.view_logistics_dispatch_batch_form").id, "form")]
        return action

    def action_open_wave(self):
        self.ensure_one()
        if not self.wave_id:
            return False
        action = self.env.ref("logistics_dispatch.action_logistics_dispatch_wave").read()[0]
        action["res_id"] = self.wave_id.id
        action["views"] = [(self.env.ref("logistics_dispatch.view_logistics_dispatch_wave_form").id, "form")]
        return action

    def action_open_order_lines(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("订单明细"),
            "res_model": "logistics.dispatch.waybill.order.line",
            "view_mode": "list,form",
            "domain": [("waybill_id", "=", self.id)],
            "context": {"default_waybill_id": self.id},
        }

    def action_open_customer_lines(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("配送节点明细"),
            "res_model": "logistics.dispatch.waybill.customer.line",
            "view_mode": "list,form",
            "domain": [("waybill_id", "=", self.id)],
            "context": {"default_waybill_id": self.id},
        }

    def action_open_goods_lines(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("货物明细"),
            "res_model": "logistics.dispatch.waybill.customer.goods.line",
            "view_mode": "list,form",
            "domain": [("waybill_id", "=", self.id)],
            "context": {"default_waybill_id": self.id},
        }
