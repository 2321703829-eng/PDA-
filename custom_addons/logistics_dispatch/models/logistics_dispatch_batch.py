from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LogisticsDispatchBatch(models.Model):
    _name = "logistics.dispatch.batch"
    _description = "物流批次"
    _order = "planned_depart_time desc, id desc"

    _uniq_batch_no = models.Constraint(
        "unique(name)",
        "批次号必须唯一。",
    )

    name = fields.Char(string="批次号", required=True, copy=False, default="新建", index=True)
    active = fields.Boolean(default=True, index=True)
    batch_no = fields.Char(
        string="批次号（导入导出）",
        compute="_compute_batch_no",
        inverse="_inverse_batch_no",
    )
    wave_id = fields.Many2one("logistics.dispatch.wave", string="波次", ondelete="cascade", index=True)
    wave_no = fields.Char(
        string="波次号（导入导出）",
        compute="_compute_wave_no",
        inverse="_inverse_wave_no",
    )
    warehouse_id = fields.Many2one("stock.warehouse", string="仓库", required=True)
    vehicle_id = fields.Many2one("fleet.vehicle", string="本次执行车辆", ondelete="restrict", index=True)
    driver_employee_id = fields.Many2one(
        "hr.employee",
        string="本次执行司机",
        domain="[('logistics_role', '=', 'driver')]",
        ondelete="restrict",
        index=True,
    )
    loading_position = fields.Char(string="装车口位")
    planned_depart_time = fields.Datetime(string="计划发车时间")
    actual_depart_time = fields.Datetime(string="实际发车时间")
    state = fields.Selection(
        [
            ("draft", "草稿"),
            ("ready", "待执行"),
            ("loading", "装车中"),
            ("in_transit", "运输中"),
            ("done", "已完成"),
            ("cancelled", "已取消"),
        ],
        string="状态",
        default="draft",
        required=True,
    )
    route_summary = fields.Char(string="路线摘要")
    warehouse_name_snapshot = fields.Char(string="仓库快照", size=64)
    route_name_snapshot = fields.Char(string="路线快照", size=64)
    driver_name_snapshot = fields.Char(string="司机快照", size=64)
    driver_phone_snapshot = fields.Char(string="司机电话快照", size=32)
    waybill_ids = fields.One2many("logistics.dispatch.waybill", "batch_id", string="运单")
    total_waybill_count = fields.Integer(string="运单数", compute="_compute_counts", store=True)
    finished_waybill_count = fields.Integer(string="已完成运单数", compute="_compute_counts", store=True)
    exception_waybill_count = fields.Integer(string="异常运单数", compute="_compute_counts", store=True)
    remark = fields.Text(string="备注")

    @api.depends("name")
    def _compute_batch_no(self):
        for record in self:
            record.batch_no = record.name or ""

    @api.depends("wave_id.name")
    def _compute_wave_no(self):
        for record in self:
            record.wave_no = record.wave_id.name or ""

    def _inverse_batch_no(self):
        for record in self:
            record.name = (record.batch_no or "").strip() or record.name or "新建"

    def _inverse_wave_no(self):
        for record in self:
            wave_no = (record.wave_no or "").strip()
            record.wave_id = self._resolve_wave_by_no(wave_no) if wave_no else False

    @api.model
    def _resolve_wave_by_no(self, wave_no):
        waves = self.env["logistics.dispatch.wave"].search([("name", "=", wave_no)], limit=2)
        if not waves:
            raise ValidationError(f"未找到波次号“{wave_no}”对应的波次记录。")
        if len(waves) > 1:
            raise ValidationError(f"波次号“{wave_no}”匹配到多条波次记录，请先去重。")
        return waves

    @api.model
    def _normalize_wave_vals(self, vals):
        normalized_vals = dict(vals)
        if "wave_no" in normalized_vals and not normalized_vals.get("wave_id"):
            wave_no = (normalized_vals.pop("wave_no") or "").strip()
            normalized_vals["wave_id"] = self._resolve_wave_by_no(wave_no).id if wave_no else False

        wave_id = normalized_vals.get("wave_id")
        if wave_id and not normalized_vals.get("warehouse_id"):
            wave = self.env["logistics.dispatch.wave"].browse(wave_id)
            normalized_vals["warehouse_id"] = wave.warehouse_id.id
        return normalized_vals

    @api.model
    def _build_snapshot_vals(self, normalized_vals):
        warehouse = self.env["stock.warehouse"].browse(normalized_vals.get("warehouse_id"))
        driver = self.env["hr.employee"].browse(normalized_vals.get("driver_employee_id")).sudo()
        return {
            "warehouse_name_snapshot": warehouse.name or False,
            "route_name_snapshot": normalized_vals.get("route_name_snapshot") or normalized_vals.get("route_summary") or False,
            "driver_name_snapshot": driver.name or False,
            "driver_phone_snapshot": driver.work_phone or driver.mobile_phone or False,
        }

    @api.constrains("wave_id", "warehouse_id")
    def _check_wave_warehouse_consistency(self):
        for record in self:
            if record.wave_id and record.warehouse_id and record.wave_id.warehouse_id != record.warehouse_id:
                raise ValidationError("批次仓库必须与所属波次仓库一致。")

    @api.depends("waybill_ids", "waybill_ids.state", "waybill_ids.exception_status")
    def _compute_counts(self):
        for record in self:
            record.total_waybill_count = len(record.waybill_ids)
            record.finished_waybill_count = len(record.waybill_ids.filtered(lambda waybill: waybill.state == "done"))
            record.exception_waybill_count = len(
                record.waybill_ids.filtered(lambda waybill: waybill.exception_status in ("open", "processing"))
            )

    @api.model_create_multi
    def create(self, vals_list):
        normalized_vals_list = []
        for vals in vals_list:
            normalized_vals = self._normalize_wave_vals(vals)
            if "batch_no" in normalized_vals:
                normalized_vals["name"] = (
                    (normalized_vals.pop("batch_no") or "").strip() or normalized_vals.get("name") or "新建"
                )
            if normalized_vals.get("name", "新建") in ("New", "新建"):
                normalized_vals["name"] = self.env["ir.sequence"].next_by_code("logistics.dispatch.batch") or "新建"
            for field_name, field_value in self._build_snapshot_vals(normalized_vals).items():
                normalized_vals.setdefault(field_name, field_value)
            normalized_vals_list.append(normalized_vals)
        return super().create(normalized_vals_list)

    def write(self, vals):
        normalized_vals = self._normalize_wave_vals(vals)
        if "batch_no" in normalized_vals:
            batch_no = (normalized_vals.pop("batch_no") or "").strip()
            if batch_no:
                normalized_vals["name"] = batch_no
        if any(field_name in normalized_vals for field_name in ("wave_id", "warehouse_id", "driver_employee_id", "route_summary")):
            for field_name, field_value in self._build_snapshot_vals(normalized_vals).items():
                normalized_vals.setdefault(field_name, field_value)
        return super().write(normalized_vals)

    def _logistics_delete_related(self, model_name, domain):
        if model_name not in self.env.registry:
            return
        records = self.env[model_name].sudo().search(domain)
        if not records:
            return
        if hasattr(records, "action_logistics_delete"):
            records.action_logistics_delete()
            return
        records.unlink()

    def action_logistics_delete(self):
        batch_ids = self.ids
        self._logistics_delete_related(
            "logistics.trace.exception",
            [("batch_id", "in", batch_ids), ("waybill_id", "=", False)],
        )
        self._logistics_delete_related(
            "logistics.trace.evidence",
            [("batch_id", "in", batch_ids), ("waybill_id", "=", False)],
        )
        self._logistics_delete_related(
            "logistics.trace.event",
            [("batch_id", "in", batch_ids), ("waybill_id", "=", False)],
        )
        self.waybill_ids.action_logistics_delete()
        self.unlink()
        return True

    def action_logistics_archive(self):
        return self.action_logistics_delete()
