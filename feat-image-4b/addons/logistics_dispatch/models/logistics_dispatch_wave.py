from odoo import api, fields, models


class LogisticsDispatchWave(models.Model):
    _name = "logistics.dispatch.wave"
    _description = "Dispatch Wave"
    _order = "dispatch_date desc, id desc"

    name = fields.Char(string="Wave No", required=True, copy=False, default="New", index=True)
    dispatch_date = fields.Date(
        string="Dispatch Date",
        required=True,
        default=fields.Date.context_today,
    )
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", required=True)
    planned_depart_time = fields.Datetime(string="Planned Depart Time")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("ready", "Ready"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        required=True,
    )
    batch_ids = fields.One2many("logistics.dispatch.batch", "wave_id", string="Batches")
    total_batch_count = fields.Integer(string="Batch Count", compute="_compute_counts", store=True)
    total_waybill_count = fields.Integer(string="Waybill Count", compute="_compute_counts", store=True)
    total_order_count = fields.Integer(string="Order Line Count", compute="_compute_counts", store=True)
    remark = fields.Text(string="Remark")

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
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("logistics.dispatch.wave") or "New"
        return super().create(vals_list)

