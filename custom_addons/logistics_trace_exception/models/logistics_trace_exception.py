from odoo import _, api, fields, models


class LogisticsTraceException(models.Model):
    _name = "logistics.trace.exception"
    _description = "Logistics Trace Exception"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "report_time desc, id desc"
    _rec_name = "name"

    EXCEPTION_TYPE_SELECTION = [
        ("delay", "Delay"),
        ("damage", "Damage"),
        ("missing", "Missing"),
        ("rejected", "Rejected"),
        ("store_closed", "Store Closed"),
        ("signoff_problem", "Signoff Problem"),
        ("evidence_missing", "Evidence Missing"),
        ("other", "Other"),
    ]

    SEVERITY_SELECTION = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    STATE_SELECTION = [
        ("draft", "Draft"),
        ("open", "Open"),
        ("processing", "Processing"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
        ("cancelled", "Cancelled"),
    ]

    name = fields.Char(string="Exception No", required=True, copy=False, default="New", tracking=True)
    exception_type = fields.Selection(
        EXCEPTION_TYPE_SELECTION,
        string="Exception Type",
        required=True,
        tracking=True,
    )
    severity_level = fields.Selection(
        SEVERITY_SELECTION,
        string="Severity",
        required=True,
        default="medium",
        tracking=True,
    )
    state = fields.Selection(
        STATE_SELECTION,
        string="State",
        required=True,
        default="open",
        tracking=True,
    )
    waybill_id = fields.Many2one(
        "logistics.dispatch.waybill",
        string="Waybill",
        ondelete="cascade",
        index=True,
        tracking=True,
    )
    batch_id = fields.Many2one(
        "logistics.dispatch.batch",
        string="Batch",
        ondelete="set null",
        index=True,
        tracking=True,
    )
    trace_event_id = fields.Many2one(
        "logistics.trace.event",
        string="Trace Event",
        ondelete="set null",
        index=True,
        tracking=True,
    )
    report_time = fields.Datetime(
        string="Report Time",
        required=True,
        default=fields.Datetime.now,
        index=True,
        tracking=True,
    )
    reporter_user_id = fields.Many2one(
        "res.users",
        string="Reported By",
        default=lambda self: self.env.user,
        tracking=True,
    )
    reporter_user_name = fields.Char(
        string="Reporter Name",
        compute="_compute_reporter_user_name",
        store=True,
    )
    process_owner_id = fields.Many2one(
        "hr.employee",
        string="Process Owner",
        tracking=True,
    )
    process_owner_name = fields.Char(
        string="Process Owner Name",
        compute="_compute_process_owner_name",
        store=True,
    )
    description = fields.Text(string="Description", tracking=True)
    close_summary = fields.Text(string="Close Summary")
    closed_time = fields.Datetime(string="Closed Time")
    is_overdue = fields.Boolean(
        string="Overdue",
        compute="_compute_is_overdue",
        store=True,
    )
    remark = fields.Text(string="Remark")
    process_log_ids = fields.One2many(
        "logistics.trace.exception.process.log",
        "exception_id",
        string="Process Logs",
    )
    evidence_count = fields.Integer(
        string="Evidence Count",
        compute="_compute_evidence_count",
        store=True,
        readonly=True,
    )

    @api.depends("reporter_user_id")
    def _compute_reporter_user_name(self):
        for record in self:
            record.reporter_user_name = record.reporter_user_id.name or ""

    @api.depends("process_owner_id")
    def _compute_process_owner_name(self):
        for record in self:
            record.process_owner_name = record.process_owner_id.name or ""

    @api.depends("trace_event_id.evidence_count")
    def _compute_evidence_count(self):
        for record in self:
            record.evidence_count = record.trace_event_id.evidence_count or 0

    @api.depends("state", "report_time")
    def _compute_is_overdue(self):
        now = fields.Datetime.now()
        for record in self:
            record.is_overdue = (
                record.state in ("open", "processing")
                and bool(record.report_time)
                and (now - record.report_time).days >= 1
            )

    @api.onchange("trace_event_id")
    def _onchange_trace_event_id(self):
        for record in self:
            if record.trace_event_id:
                if not record.waybill_id:
                    record.waybill_id = record.trace_event_id.waybill_id
                if not record.batch_id:
                    record.batch_id = record.trace_event_id.batch_id

    @api.onchange("waybill_id")
    def _onchange_waybill_id(self):
        for record in self:
            if record.waybill_id and not record.batch_id:
                record.batch_id = record.waybill_id.batch_id

    @api.model_create_multi
    def create(self, vals_list):
        records = self.browse()
        for vals in vals_list:
            if vals.get("trace_event_id") and not vals.get("waybill_id"):
                trace_event = self.env["logistics.trace.event"].browse(vals["trace_event_id"])
                vals["waybill_id"] = trace_event.waybill_id.id
                vals["batch_id"] = vals.get("batch_id") or trace_event.batch_id.id
            elif vals.get("waybill_id") and not vals.get("batch_id"):
                waybill = self.env["logistics.dispatch.waybill"].browse(vals["waybill_id"])
                vals["batch_id"] = waybill.batch_id.id
            if vals.get("name", "New") == "New":
                vals["name"] = self._build_exception_name(vals)
        records = super().create(vals_list)
        records._create_process_logs("create", from_state=False)
        return records

    def write(self, vals):
        previous_states = {record.id: record.state for record in self}
        result = super().write(vals)
        if "state" in vals or "remark" in vals or "close_summary" in vals:
            for record in self:
                from_state = previous_states.get(record.id)
                to_state = record.state
                if from_state != to_state:
                    record._create_process_logs(
                        "state_change",
                        from_state=from_state,
                        to_state=to_state,
                        note=vals.get("close_summary") or vals.get("remark") or "",
                    )
        if "state" in vals:
            for record in self.filtered(lambda rec: rec.state in ("closed", "cancelled")):
                if not record.closed_time:
                    record.closed_time = fields.Datetime.now()
        return result

    def _build_exception_name(self, vals):
        exception_type = vals.get("exception_type") or "other"
        report_time = vals.get("report_time")
        report_dt = fields.Datetime.to_datetime(report_time) if report_time else fields.Datetime.now()
        return f"EXC-{exception_type.upper()}-{report_dt.strftime('%Y%m%d%H%M%S')}"

    def _create_process_logs(self, action_type, from_state=False, to_state=False, note=""):
        log_model = self.env["logistics.trace.exception.process.log"]
        values_list = []
        for record in self:
            values_list.append(
                {
                    "exception_id": record.id,
                    "action_type": action_type,
                    "operator_id": self.env.user.id,
                    "from_state": from_state or False,
                    "to_state": to_state or record.state,
                    "note": note or "",
                }
            )
        if values_list:
            log_model.create(values_list)

    def action_mark_processing(self):
        self.write({"state": "processing"})

    def action_mark_resolved(self):
        self.write({"state": "resolved"})

    def action_mark_closed(self):
        self.write({"state": "closed", "closed_time": fields.Datetime.now()})

    def action_open_waybill(self):
        self.ensure_one()
        if not self.waybill_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": _("Waybill"),
            "res_model": "logistics.dispatch.waybill",
            "view_mode": "form",
            "res_id": self.waybill_id.id,
        }

    def action_open_trace_event(self):
        self.ensure_one()
        if not self.trace_event_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": _("Trace Event"),
            "res_model": "logistics.trace.event",
            "view_mode": "form",
            "res_id": self.trace_event_id.id,
        }

    def action_open_batch(self):
        self.ensure_one()
        if not self.batch_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": _("Batch"),
            "res_model": "logistics.dispatch.batch",
            "view_mode": "form",
            "res_id": self.batch_id.id,
        }

    def action_open_evidence(self):
        self.ensure_one()
        if not self.trace_event_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": _("Evidence"),
            "res_model": "logistics.trace.evidence",
            "view_mode": "list,form",
            "domain": [("trace_event_id", "=", self.trace_event_id.id)],
            "context": {
                "default_trace_event_id": self.trace_event_id.id,
                "default_waybill_id": self.waybill_id.id,
                "default_batch_id": self.batch_id.id,
            },
        }
