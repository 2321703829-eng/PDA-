from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LogisticsDispatchWaybill(models.Model):
    @api.model
    def get_import_templates(self):
        return [
            {
                "label": _("下载标准模板（英文列头）"),
                "template": "/api/admin/logistics/imports/waybill-standard/template/download?template_code=TSL-IMPORT-WAYBILL-V2&template_version=v2&template_locale=en_US",
            },
            {
                "label": _("下载标准模板（中文列头）"),
                "template": "/api/admin/logistics/imports/waybill-standard/template/download?template_code=TSL-IMPORT-WAYBILL-V2&template_version=v2&template_locale=zh_CN",
            },
        ]

    _name = "logistics.dispatch.waybill"
    _description = "物流运单"
    _order = "delivery_date desc, id desc"
    _rec_name = "name"

    name = fields.Char(string="运单号", required=True, copy=False, default="新建", index=True)
    waybill_no = fields.Char(
        string="运单号（导入导出）",
        compute="_compute_waybill_no",
        inverse="_inverse_waybill_no",
    )
    delivery_date = fields.Date(string="配送日期", default=fields.Date.context_today)
    store_id = fields.Many2one(
        "res.partner",
        string="门店",
        domain="[('is_logistics_store', '=', True)]",
    )
    store_no = fields.Char(
        string="门店号（导入导出）",
        compute="_compute_store_no",
        inverse="_inverse_store_no",
    )
    store_name = fields.Char(
        string="门店名称（导入导出）",
        compute="_compute_store_name",
        inverse="_inverse_store_name",
    )
    customer_id = fields.Many2one(
        "res.partner",
        string="客户",
        domain="[('is_logistics_customer', '=', True)]",
    )
    customer_no = fields.Char(
        string="客户号（导入导出）",
        compute="_compute_customer_no",
        inverse="_inverse_customer_no",
    )
    customer_name = fields.Char(
        string="客户名称（导入导出）",
        compute="_compute_customer_name",
        inverse="_inverse_customer_name",
    )
    batch_id = fields.Many2one("logistics.dispatch.batch", string="批次", ondelete="set null")
    batch_no = fields.Char(
        string="批次号（导入导出）",
        compute="_compute_batch_no",
        inverse="_inverse_batch_no",
    )
    wave_id = fields.Many2one(
        "logistics.dispatch.wave",
        string="波次",
        related="batch_id.wave_id",
        store=True,
        readonly=True,
    )
    warehouse_id = fields.Many2one("stock.warehouse", string="仓库")
    vehicle_id = fields.Many2one(
        "fleet.vehicle",
        string="车辆",
        related="batch_id.vehicle_id",
        store=True,
        readonly=True,
    )
    driver_employee_id = fields.Many2one(
        "hr.employee",
        string="司机",
        related="batch_id.driver_employee_id",
        store=True,
        readonly=True,
    )
    route_seq = fields.Integer(string="路线顺序", default=10)
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
        [("pending", "待补充"), ("partial", "部分完成"), ("done", "已完成")],
        string="到店留痕",
        default="pending",
    )
    signoff_trace_status = fields.Selection(
        [("pending", "待补充"), ("partial", "部分完成"), ("done", "已完成")],
        string="签收留痕",
        default="pending",
    )
    exception_status = fields.Selection(
        [
            ("none", "无异常"),
            ("open", "待处理"),
            ("processing", "处理中"),
            ("closed", "已关闭"),
        ],
        string="异常状态",
        default="none",
        required=True,
    )
    evidence_status = fields.Selection(
        [("missing", "待补充"), ("partial", "部分齐全"), ("complete", "已齐全")],
        string="证据状态",
        default="missing",
        required=True,
    )
    risk_level = fields.Selection(
        [("low", "低"), ("medium", "中"), ("high", "高")],
        string="风险等级",
        default="low",
    )
    latest_trace_time = fields.Datetime(string="最新留痕时间")
    latest_trace_type = fields.Char(string="最新留痕类型")
    latest_trace_summary = fields.Char(string="最新留痕摘要")
    trace_count = fields.Integer(string="留痕数", default=0)
    evidence_count = fields.Integer(string="证据数", default=0)
    open_exception_count = fields.Integer(string="待处理异常数", default=0)
    order_line_ids = fields.One2many(
        "logistics.dispatch.waybill.order.line",
        "waybill_id",
        string="订单明细",
    )
    customer_line_ids = fields.One2many(
        "logistics.dispatch.waybill.customer.line",
        "waybill_id",
        string="客户明细",
    )
    goods_line_ids = fields.One2many(
        "logistics.dispatch.waybill.customer.goods.line",
        "waybill_id",
        string="货物明细",
    )
    order_line_count = fields.Integer(
        string="明细数",
        compute="_compute_order_line_count",
        store=True,
    )
    customer_line_count = fields.Integer(
        string="客户数",
        compute="_compute_detail_counts",
        store=True,
    )
    goods_line_count = fields.Integer(
        string="货物条数",
        compute="_compute_detail_counts",
        store=True,
    )
    total_goods_qty = fields.Float(
        string="货物总数量",
        compute="_compute_detail_counts",
        store=True,
    )
    total_package_count = fields.Integer(
        string="货物总件数",
        compute="_compute_detail_counts",
        store=True,
    )
    total_goods_weight = fields.Float(
        string="货物总重量",
        compute="_compute_detail_counts",
        store=True,
    )
    total_goods_volume = fields.Float(
        string="货物总体积",
        compute="_compute_detail_counts",
        store=True,
    )
    remark = fields.Text(string="备注")

    @api.depends("name")
    def _compute_waybill_no(self):
        for record in self:
            record.waybill_no = record.name or ""

    @api.depends("batch_id.name")
    def _compute_batch_no(self):
        for record in self:
            record.batch_no = record.batch_id.name or ""

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
            raise ValidationError(f"未找到{field_label}“{value}”对应的记录。")
        if len(records) > 1:
            raise ValidationError(f"{field_label}“{value}”匹配到多条记录，请先去重。")
        return records

    @api.model
    def _resolve_batch_by_no(self, batch_no):
        batches = self.env["logistics.dispatch.batch"].search([("name", "=", batch_no)], limit=2)
        return self._ensure_unique_record(batches, "批次号", batch_no)

    @api.model
    def _resolve_partner_by_code(self, code, partner_type):
        field_name = "logistics_customer_code" if partner_type == "customer" else "logistics_store_code"
        flag_name = "is_logistics_customer" if partner_type == "customer" else "is_logistics_store"
        label = "客户号" if partner_type == "customer" else "门店号"
        partners = self.env["res.partner"].search(
            [(field_name, "=", code), (flag_name, "=", True)],
            limit=2,
        )
        return self._ensure_unique_record(partners, label, code)

    @api.model
    def _resolve_partner_by_name(self, name, partner_type):
        flag_name = "is_logistics_customer" if partner_type == "customer" else "is_logistics_store"
        label = "客户名称" if partner_type == "customer" else "门店名称"
        partners = self.env["res.partner"].search(
            [("name", "=", name), (flag_name, "=", True)],
            limit=2,
        )
        return self._ensure_unique_record(partners, label, name)

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

    @api.onchange("store_id")
    def _onchange_store_id(self):
        for record in self:
            if record.store_id and record.store_id.parent_id and not record.customer_id:
                record.customer_id = record.store_id.parent_id

    @api.onchange("batch_id")
    def _onchange_batch_id(self):
        for record in self:
            if record.batch_id and not record.warehouse_id:
                record.warehouse_id = record.batch_id.warehouse_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "waybill_no" in vals:
                vals["name"] = (vals.pop("waybill_no") or "").strip() or vals.get("name") or "新建"
            if "batch_no" in vals and not vals.get("batch_id"):
                batch_no = (vals.pop("batch_no") or "").strip()
                vals["batch_id"] = self._resolve_batch_by_no(batch_no).id if batch_no else False
            if "customer_no" in vals and not vals.get("customer_id"):
                customer_no = (vals.pop("customer_no") or "").strip()
                vals["customer_id"] = (
                    self._resolve_partner_by_code(customer_no, "customer").id if customer_no else False
                )
            if "customer_name" in vals and not vals.get("customer_id"):
                customer_name = (vals.pop("customer_name") or "").strip()
                vals["customer_id"] = (
                    self._resolve_partner_by_name(customer_name, "customer").id if customer_name else False
                )
            if "store_no" in vals and not vals.get("store_id"):
                store_no = (vals.pop("store_no") or "").strip()
                vals["store_id"] = self._resolve_partner_by_code(store_no, "store").id if store_no else False
            if "store_name" in vals and not vals.get("store_id"):
                store_name = (vals.pop("store_name") or "").strip()
                vals["store_id"] = self._resolve_partner_by_name(store_name, "store").id if store_name else False
            if vals.get("name", "新建") in ("New", "新建"):
                vals["name"] = self.env["ir.sequence"].next_by_code("logistics.dispatch.waybill") or "新建"
        return super().create(vals_list)

    def write(self, vals):
        vals = dict(vals)
        if "waybill_no" in vals:
            waybill_no = (vals.pop("waybill_no") or "").strip()
            if waybill_no:
                vals["name"] = waybill_no
        if "batch_no" in vals and "batch_id" not in vals:
            batch_no = (vals.pop("batch_no") or "").strip()
            vals["batch_id"] = self._resolve_batch_by_no(batch_no).id if batch_no else False
        if "customer_no" in vals and "customer_id" not in vals:
            customer_no = (vals.pop("customer_no") or "").strip()
            vals["customer_id"] = (
                self._resolve_partner_by_code(customer_no, "customer").id if customer_no else False
            )
        if "customer_name" in vals and "customer_id" not in vals:
            customer_name = (vals.pop("customer_name") or "").strip()
            vals["customer_id"] = (
                self._resolve_partner_by_name(customer_name, "customer").id if customer_name else False
            )
        if "store_no" in vals and "store_id" not in vals:
            store_no = (vals.pop("store_no") or "").strip()
            vals["store_id"] = self._resolve_partner_by_code(store_no, "store").id if store_no else False
        if "store_name" in vals and "store_id" not in vals:
            store_name = (vals.pop("store_name") or "").strip()
            vals["store_id"] = self._resolve_partner_by_name(store_name, "store").id if store_name else False
        return super().write(vals)

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
            "name": _("客户明细"),
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
