from odoo import api, fields, models


class LogisticsDispatchBatch(models.Model):
    _name = "logistics.dispatch.batch"
    _description = "Dispatch Batch"
    _order = "planned_depart_time desc, id desc"

    name = fields.Char(string="Batch No", required=True, copy=False, default="New", index=True)
    wave_id = fields.Many2one("logistics.dispatch.wave", string="Wave", ondelete="set null")
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", required=True)
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle")
    driver_employee_id = fields.Many2one(
        "hr.employee",
        string="Driver",
        domain="[('logistics_role', '=', 'driver')]",
    )
    loading_position = fields.Char(string="Loading Position")
    planned_depart_time = fields.Datetime(string="Planned Depart Time")
    actual_depart_time = fields.Datetime(string="Actual Depart Time")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("ready", "Ready"),
            ("loading", "Loading"),
            ("in_transit", "In Transit"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        required=True,
    )
    route_summary = fields.Char(string="Route Summary")
    waybill_ids = fields.One2many("logistics.dispatch.waybill", "batch_id", string="Waybills")
    total_waybill_count = fields.Integer(string="Waybill Count", compute="_compute_counts", store=True)
    finished_waybill_count = fields.Integer(
        string="Finished Waybill Count",
        compute="_compute_counts",
        store=True,
    )
    exception_waybill_count = fields.Integer(
        string="Exception Waybill Count",
        compute="_compute_counts",
        store=True,
    )
    remark = fields.Text(string="Remark")

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
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("logistics.dispatch.batch") or "New"
        return super().create(vals_list)

