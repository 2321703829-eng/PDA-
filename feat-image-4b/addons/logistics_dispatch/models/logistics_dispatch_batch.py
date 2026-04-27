from odoo import _, api, fields, models


class LogisticsDispatchBatch(models.Model):
    _name = "logistics.dispatch.batch"
    _description = "Dispatch Batch"
    _order = "planned_depart_time desc, id desc"

    name = fields.Char(string="Batch No", required=True, copy=False, default="New", index=True)
    stock_picking_batch_id = fields.Many2one(
        "stock.picking.batch",
        string="Odoo Batch",
        ondelete="set null",
        help="Reuse Odoo's native batch as the execution base instead of building a parallel batch master table.",
    )
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
            if vals.get("stock_picking_batch_id") and vals.get("name", "New") == "New":
                stock_batch = self.env["stock.picking.batch"].browse(vals["stock_picking_batch_id"])
                if stock_batch.exists():
                    vals["name"] = stock_batch.name
                    if not vals.get("planned_depart_time"):
                        vals["planned_depart_time"] = stock_batch.scheduled_date
                    if not vals.get("warehouse_id") and stock_batch.picking_ids:
                        warehouse = stock_batch.picking_ids[:1].picking_type_id.warehouse_id
                        if warehouse:
                            vals["warehouse_id"] = warehouse.id
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("logistics.dispatch.batch") or "New"
        return super().create(vals_list)

