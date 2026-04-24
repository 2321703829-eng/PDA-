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
            ("in_transit", "在途"),
            ("done", "已完成"),
            ("cancelled", "已取消"),
        ],
        string="状态",
        default="draft",
        required=True,
    )
    route_summary = fields.Char(string="路线摘要")
    warehouse_name_snapshot = fields.Char(string="仓库快照", size=64)
    route_name_snapshot = fields.Char(string="线路快照", size=64)
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
        for vals in vals_list:
            if "batch_no" in vals:
                vals["name"] = (vals.pop("batch_no") or "").strip() or vals.get("name") or "新建"
            if "wave_no" in vals and not vals.get("wave_id"):
                wave_no = (vals.pop("wave_no") or "").strip()
                vals["wave_id"] = self._resolve_wave_by_no(wave_no).id if wave_no else False
            if vals.get("name", "新建") in ("New", "新建"):
                vals["name"] = self.env["ir.sequence"].next_by_code("logistics.dispatch.batch") or "新建"
        return super().create(vals_list)

    def write(self, vals):
        vals = dict(vals)
        if "batch_no" in vals:
            batch_no = (vals.pop("batch_no") or "").strip()
            if batch_no:
                vals["name"] = batch_no
        if "wave_no" in vals and "wave_id" not in vals:
            wave_no = (vals.pop("wave_no") or "").strip()
            vals["wave_id"] = self._resolve_wave_by_no(wave_no).id if wave_no else False
        return super().write(vals)
