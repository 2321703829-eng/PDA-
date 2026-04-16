from odoo import _, api, fields, models


class LogisticsDispatchWaybill(models.Model):
    _name = "logistics.dispatch.waybill"
    _description = "Dispatch Waybill"
    _order = "delivery_date desc, id desc"
    _rec_name = "name"

    name = fields.Char(string="Waybill No", required=True, copy=False, default="New", index=True)
    delivery_date = fields.Date(string="Delivery Date", default=fields.Date.context_today)
    store_id = fields.Many2one(
        "res.partner",
        string="Store",
        domain="[('is_logistics_store', '=', True)]",
    )
    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        domain="[('is_logistics_customer', '=', True)]",
    )
    batch_id = fields.Many2one("logistics.dispatch.batch", string="Batch", ondelete="set null")
    wave_id = fields.Many2one(
        "logistics.dispatch.wave",
        string="Wave",
        related="batch_id.wave_id",
        store=True,
        readonly=True,
    )
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse")
    vehicle_id = fields.Many2one(
        "fleet.vehicle",
        string="Vehicle",
        related="batch_id.vehicle_id",
        store=True,
        readonly=True,
    )
    driver_employee_id = fields.Many2one(
        "hr.employee",
        string="Driver",
        related="batch_id.driver_employee_id",
        store=True,
        readonly=True,
    )
    route_seq = fields.Integer(string="Route Sequence", default=10)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("ready", "Ready"),
            ("in_transit", "In Transit"),
            ("arrived", "Arrived"),
            ("signed", "Signed"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        required=True,
    )
    arrive_trace_status = fields.Selection(
        [("pending", "Pending"), ("partial", "Partial"), ("done", "Done")],
        string="Arrival Trace",
        default="pending",
    )
    signoff_trace_status = fields.Selection(
        [("pending", "Pending"), ("partial", "Partial"), ("done", "Done")],
        string="Signoff Trace",
        default="pending",
    )
    exception_status = fields.Selection(
        [
            ("none", "No Exception"),
            ("open", "Open"),
            ("processing", "Processing"),
            ("closed", "Closed"),
        ],
        string="Exception Status",
        default="none",
        required=True,
    )
    evidence_status = fields.Selection(
        [("missing", "Missing"), ("partial", "Partial"), ("complete", "Complete")],
        string="Evidence Status",
        default="missing",
        required=True,
    )
    risk_level = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        string="Risk Level",
        default="low",
    )
    latest_trace_time = fields.Datetime(string="Latest Trace Time")
    latest_trace_type = fields.Char(string="Latest Trace Type")
    latest_trace_summary = fields.Char(string="Latest Trace Summary")
    trace_count = fields.Integer(string="Trace Count", default=0)
    evidence_count = fields.Integer(string="Evidence Count", default=0)
    open_exception_count = fields.Integer(string="Open Exception Count", default=0)
    order_line_ids = fields.One2many(
        "logistics.dispatch.waybill.order.line",
        "waybill_id",
        string="Order Lines",
    )
    stop_ids = fields.One2many(
        "logistics.dispatch.waybill.stop",
        "waybill_id",
        string="Stops",
    )
    order_line_count = fields.Integer(
        string="Order Line Count",
        compute="_compute_order_line_count",
        store=True,
    )
    stop_count = fields.Integer(
        string="Stop Count",
        compute="_compute_stop_count",
        store=True,
    )
    remark = fields.Text(string="Remark")

    @api.depends("order_line_ids")
    def _compute_order_line_count(self):
        for record in self:
            record.order_line_count = len(record.order_line_ids)

    @api.depends("stop_ids")
    def _compute_stop_count(self):
        for record in self:
            record.stop_count = len(record.stop_ids)

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
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("logistics.dispatch.waybill") or "New"
        return super().create(vals_list)

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
            "name": _("Waybill Order Lines"),
            "res_model": "logistics.dispatch.waybill.order.line",
            "view_mode": "list,form",
            "domain": [("waybill_id", "=", self.id)],
            "context": {"default_waybill_id": self.id},
        }

    def action_open_stops(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Waybill Stops"),
            "res_model": "logistics.dispatch.waybill.stop",
            "view_mode": "list,form",
            "domain": [("waybill_id", "=", self.id)],
            "context": {"default_waybill_id": self.id},
        }
