from odoo import api, fields, models


class LogisticsDispatchWave(models.Model):
    _name = "logistics.dispatch.wave"
    _description = "物流波次"
    _order = "dispatch_date desc, id desc"

    name = fields.Char(string="波次号", required=True, copy=False, default="New", index=True)
    wave_no = fields.Char(
        string="波次号（导入导出）",
        compute="_compute_wave_no",
        inverse="_inverse_wave_no",
    )
    dispatch_date = fields.Date(
        string="发车日期",
        required=True,
        default=fields.Date.context_today,
    )
    warehouse_id = fields.Many2one("stock.warehouse", string="仓库", required=True)
    planned_depart_time = fields.Datetime(string="计划发车时间")
    state = fields.Selection(
        [
            ("draft", "草稿"),
            ("ready", "待执行"),
            ("in_progress", "执行中"),
            ("done", "已完成"),
            ("cancelled", "已取消"),
        ],
        string="状态",
        default="draft",
        required=True,
    )
    batch_ids = fields.One2many("logistics.dispatch.batch", "wave_id", string="批次")
    total_batch_count = fields.Integer(string="批次数", compute="_compute_counts", store=True)
    total_waybill_count = fields.Integer(string="运单数", compute="_compute_counts", store=True)
    total_order_count = fields.Integer(string="订单明细数", compute="_compute_counts", store=True)
    remark = fields.Text(string="备注")

    @api.depends("name")
    def _compute_wave_no(self):
        for record in self:
            record.wave_no = record.name or ""

    def _inverse_wave_no(self):
        for record in self:
            record.name = (record.wave_no or "").strip() or record.name or "New"

    @api.depends("batch_ids", "batch_ids.total_waybill_count", "batch_ids.waybill_ids.order_line_ids")
    def _compute_counts(self):
        for record in self:
            record.total_batch_count = len(record.batch_ids)
            record.total_waybill_count = sum(record.batch_ids.mapped("total_waybill_count"))
            record.total_order_count = sum(
                len(batch.waybill_ids.mapped("order_line_ids")) for batch in record.batch_ids
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "wave_no" in vals:
                vals["name"] = (vals.pop("wave_no") or "").strip() or vals.get("name") or "New"
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("logistics.dispatch.wave") or "New"
        return super().create(vals_list)

    def write(self, vals):
        vals = dict(vals)
        if "wave_no" in vals:
            wave_no = (vals.pop("wave_no") or "").strip()
            if wave_no:
                vals["name"] = wave_no
        return super().write(vals)

