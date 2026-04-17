from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LogisticsDispatchBatch(models.Model):
    _name = "logistics.dispatch.batch"
    _description = "物流批次"
    _order = "planned_depart_time desc, id desc"

    name = fields.Char(string="批次号", required=True, copy=False, default="新建", index=True)
    stock_picking_batch_id = fields.Many2one(
        "stock.picking.batch",
        string="Odoo 批次",
        ondelete="set null",
        help="复用 Odoo 原生批处理作为执行基础，避免维护一套平行批次主数据。",
    )
    wave_id = fields.Many2one("logistics.dispatch.wave", string="波次", ondelete="set null")
    batch_no = fields.Char(
        string="批次号（导入导出）",
        compute="_compute_batch_no",
        inverse="_inverse_batch_no",
    )
    wave_no = fields.Char(
        string="波次号（导入导出）",
        compute="_compute_wave_no",
        inverse="_inverse_wave_no",
    )
    warehouse_id = fields.Many2one("stock.warehouse", string="仓库", required=True)
    vehicle_id = fields.Many2one("fleet.vehicle", string="车辆")
    driver_employee_id = fields.Many2one(
        "hr.employee",
        string="司机",
        domain="[('logistics_role', '=', 'driver')]",
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
    waybill_ids = fields.One2many("logistics.dispatch.waybill", "batch_id", string="运单")
    total_waybill_count = fields.Integer(string="运单数", compute="_compute_counts", store=True)
    finished_waybill_count = fields.Integer(
        string="已完成运单数",
        compute="_compute_counts",
        store=True,
    )
    exception_waybill_count = fields.Integer(
        string="异常运单数",
        compute="_compute_counts",
        store=True,
    )
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

    @api.onchange("stock_picking_batch_id")
    def _onchange_stock_picking_batch_id(self):
        for record in self:
            stock_batch = record.stock_picking_batch_id
            if not stock_batch:
                continue
            if not record.name or record.name == "New":
                record.name = stock_batch.name
            if not record.warehouse_id and stock_batch.picking_ids:
                warehouse = stock_batch.picking_ids[:1].picking_type_id.warehouse_id
                if warehouse:
                    record.warehouse_id = warehouse
            if not record.planned_depart_time:
                record.planned_depart_time = stock_batch.scheduled_date

    def action_open_stock_batch(self):
        self.ensure_one()
        if not self.stock_picking_batch_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": _("Odoo Batch"),
            "res_model": "stock.picking.batch",
            "view_mode": "form",
            "res_id": self.stock_picking_batch_id.id,
        }

    @api.depends("waybill_ids", "waybill_ids.state", "waybill_ids.exception_status")
    def _compute_counts(self):
        for record in self:
            record.total_waybill_count = len(record.waybill_ids)
            record.finished_waybill_count = len(record.waybill_ids.filtered(lambda w: w.state == "done"))
            record.exception_waybill_count = len(
                record.waybill_ids.filtered(lambda w: w.exception_status in ("open", "processing"))
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("stock_picking_batch_id") and vals.get("name", "新建") in ("New", "新建"):
                stock_batch = self.env["stock.picking.batch"].browse(vals["stock_picking_batch_id"])
                if stock_batch.exists():
                    vals["name"] = stock_batch.name
                    if not vals.get("planned_depart_time"):
                        vals["planned_depart_time"] = stock_batch.scheduled_date
                    if not vals.get("warehouse_id") and stock_batch.picking_ids:
                        warehouse = stock_batch.picking_ids[:1].picking_type_id.warehouse_id
                        if warehouse:
                            vals["warehouse_id"] = warehouse.id
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

