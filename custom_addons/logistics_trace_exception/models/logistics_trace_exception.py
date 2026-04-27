from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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

    CREATE_ALLOWED_STATES = {"draft", "open"}
    FINAL_STATES = {"closed", "cancelled"}
    ALLOWED_STATE_TRANSITIONS = {
        "draft": {"open", "cancelled"},
        "open": {"processing", "resolved", "cancelled"},
        "processing": {"resolved", "closed", "cancelled"},
        "resolved": {"processing", "closed", "cancelled"},
        "closed": set(),
        "cancelled": set(),
    }

    name = fields.Char(string="Exception No", required=True, copy=False, default="New", tracking=True)
    exception_no = fields.Char(
        string="Exception No (Import/Export)",
        compute="_compute_exception_no",
        inverse="_inverse_exception_no",
    )
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
    waybill_no = fields.Char(
        string="Waybill No (Import/Export)",
        compute="_compute_waybill_no",
        inverse="_inverse_waybill_no",
    )
    batch_id = fields.Many2one(
        "logistics.dispatch.batch",
        string="Batch",
        ondelete="set null",
        index=True,
        tracking=True,
    )
    batch_no = fields.Char(
        string="Batch No (Import/Export)",
        compute="_compute_batch_no",
        inverse="_inverse_batch_no",
    )
    trace_event_id = fields.Many2one(
        "logistics.trace.event",
        string="Trace Event",
        ondelete="set null",
        index=True,
        tracking=True,
    )
    trace_event_name = fields.Char(
        string="Trace Event (Import/Export)",
        compute="_compute_trace_event_name",
        inverse="_inverse_trace_event_name",
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
        string="Reporter",
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
        inverse="_inverse_process_owner_name",
    )
    description = fields.Text(string="Description", tracking=True)
    close_summary = fields.Text(string="Close Summary")
    closed_time = fields.Datetime(string="Closed Time")
    is_overdue = fields.Boolean(
        string="Is Overdue",
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

    @api.depends("name")
    def _compute_exception_no(self):
        for record in self:
            record.exception_no = record.name or ""

    @api.depends("waybill_id.name")
    def _compute_waybill_no(self):
        for record in self:
            record.waybill_no = record.waybill_id.name or ""

    @api.depends("batch_id.name")
    def _compute_batch_no(self):
        for record in self:
            record.batch_no = record.batch_id.name or ""

    @api.depends("trace_event_id.name")
    def _compute_trace_event_name(self):
        for record in self:
            record.trace_event_name = record.trace_event_id.name or ""

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

    def _inverse_exception_no(self):
        for record in self:
            record.name = (record.exception_no or "").strip() or record.name or "New"

    def _inverse_waybill_no(self):
        for record in self:
            waybill_no = (record.waybill_no or "").strip()
            record.waybill_id = self._resolve_waybill_by_no(waybill_no) if waybill_no else False

    def _inverse_batch_no(self):
        for record in self:
            batch_no = (record.batch_no or "").strip()
            record.batch_id = self._resolve_batch_by_no(batch_no) if batch_no else False

    def _inverse_trace_event_name(self):
        for record in self:
            trace_event_name = (record.trace_event_name or "").strip()
            record.trace_event_id = (
                self._resolve_trace_event_by_name(trace_event_name) if trace_event_name else False
            )

    def _inverse_process_owner_name(self):
        for record in self:
            process_owner_name = (record.process_owner_name or "").strip()
            record.process_owner_id = (
                self._resolve_employee_by_name(process_owner_name) if process_owner_name else False
            )

    @api.model
    def _ensure_unique_record(self, records, field_label, value):
        if not records:
            raise ValidationError(_("%s '%s' was not found.") % (field_label, value))
        if len(records) > 1:
            raise ValidationError(_("%s '%s' matched multiple records.") % (field_label, value))
        return records

    @api.model
    def _resolve_waybill_by_no(self, waybill_no):
        waybills = self.env["logistics.dispatch.waybill"].search([("name", "=", waybill_no)], limit=2)
        return self._ensure_unique_record(waybills, "Waybill", waybill_no)

    @api.model
    def _resolve_batch_by_no(self, batch_no):
        batches = self.env["logistics.dispatch.batch"].search([("name", "=", batch_no)], limit=2)
        return self._ensure_unique_record(batches, "Batch", batch_no)

    @api.model
    def _resolve_trace_event_by_name(self, trace_event_name):
        events = self.env["logistics.trace.event"].search([("name", "=", trace_event_name)], limit=2)
        return self._ensure_unique_record(events, "Trace event", trace_event_name)

    @api.model
    def _resolve_employee_by_name(self, employee_name):
        employees = self.env["hr.employee"].search([("name", "=", employee_name)], limit=2)
        return self._ensure_unique_record(employees, "Employee", employee_name)

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

    @api.model
    def _normalize_reference_vals(self, vals):
        vals = dict(vals)
        if "exception_no" in vals:
            vals["name"] = (vals.pop("exception_no") or "").strip() or vals.get("name") or "New"
        if "waybill_no" in vals and not vals.get("waybill_id"):
            waybill_no = (vals.pop("waybill_no") or "").strip()
            vals["waybill_id"] = self._resolve_waybill_by_no(waybill_no).id if waybill_no else False
        if "batch_no" in vals and not vals.get("batch_id"):
            batch_no = (vals.pop("batch_no") or "").strip()
            vals["batch_id"] = self._resolve_batch_by_no(batch_no).id if batch_no else False
        if "trace_event_name" in vals and not vals.get("trace_event_id"):
            trace_event_name = (vals.pop("trace_event_name") or "").strip()
            vals["trace_event_id"] = (
                self._resolve_trace_event_by_name(trace_event_name).id if trace_event_name else False
            )
        if "process_owner_name" in vals and not vals.get("process_owner_id"):
            process_owner_name = (vals.pop("process_owner_name") or "").strip()
            vals["process_owner_id"] = (
                self._resolve_employee_by_name(process_owner_name).id if process_owner_name else False
            )
        return vals

    @api.model
    def _build_audit_note(self, vals):
        note_parts = []
        if "remark" in vals:
            remark = (vals.get("remark") or "").strip()
            note_parts.append(f"remark: {remark}" if remark else "remark cleared")
        if "close_summary" in vals:
            close_summary = (vals.get("close_summary") or "").strip()
            note_parts.append(
                f"close_summary: {close_summary}" if close_summary else "close_summary cleared"
            )
        return "; ".join(note_parts)

    @api.model
    def _validate_create_vals(self, vals):
        state = vals.get("state") or "open"
        if state not in self.CREATE_ALLOWED_STATES:
            raise ValidationError(_("New exceptions can only start in draft or open state."))
        if "closed_time" in vals:
            raise ValidationError(_("closed_time is managed by exception state transitions."))

    def _ensure_state_transition_allowed(self, target_state, previous_states):
        if not target_state:
            return
        for record in self:
            current_state = previous_states.get(record.id, record.state)
            if current_state == target_state:
                continue
            allowed_states = self.ALLOWED_STATE_TRANSITIONS.get(current_state, set())
            if target_state not in allowed_states:
                raise ValidationError(
                    _("State transition %s -> %s is not allowed.")
                    % (current_state, target_state)
                )

    def _ensure_final_state_requirements(self, target_state, vals):
        if target_state not in self.FINAL_STATES:
            return
        for record in self:
            close_summary = (
                vals.get("close_summary") if "close_summary" in vals else record.close_summary
            ) or ""
            if not close_summary.strip():
                raise ValidationError(
                    _("close_summary is required before closing or cancelling.")
                )

    @api.model_create_multi
    def create(self, vals_list):
        normalized_vals_list = []
        for raw_vals in vals_list:
            vals = self._normalize_reference_vals(raw_vals)
            if vals.get("trace_event_id") and not vals.get("waybill_id"):
                trace_event = self.env["logistics.trace.event"].browse(vals["trace_event_id"])
                vals["waybill_id"] = trace_event.waybill_id.id
                vals["batch_id"] = vals.get("batch_id") or trace_event.batch_id.id
            elif vals.get("waybill_id") and not vals.get("batch_id"):
                waybill = self.env["logistics.dispatch.waybill"].browse(vals["waybill_id"])
                vals["batch_id"] = waybill.batch_id.id
            if vals.get("name", "New") in ("New", "新建"):
                vals["name"] = self._build_exception_name(vals)
            self._validate_create_vals(vals)
            normalized_vals_list.append(vals)
        records = super().create(normalized_vals_list)
        records._create_process_logs("create", from_state=False)
        return records

    def write(self, vals):
        vals = self._normalize_reference_vals(vals)
        previous_states = {record.id: record.state for record in self}
        previous_notes = {
            record.id: {
                "remark": record.remark or "",
                "close_summary": record.close_summary or "",
            }
            for record in self
        }
        target_state = vals.get("state")
        if target_state:
            self._ensure_state_transition_allowed(target_state, previous_states)
            self._ensure_final_state_requirements(target_state, vals)
            if target_state in self.FINAL_STATES and not vals.get("closed_time"):
                vals["closed_time"] = fields.Datetime.now()
        elif "closed_time" in vals:
            raise ValidationError(_("closed_time is managed by exception state transitions."))

        audit_note = self._build_audit_note(vals)
        result = super().write(vals)

        state_changed_records = self.filtered(
            lambda record: previous_states.get(record.id) != record.state
        )
        if state_changed_records:
            state_changed_records._create_process_logs(
                "state_change",
                note=audit_note,
                previous_states=previous_states,
            )

        note_changed_records = self.filtered(
            lambda record: previous_states.get(record.id) == record.state
            and (
                ("remark" in vals and previous_notes[record.id]["remark"] != (record.remark or ""))
                or (
                    "close_summary" in vals
                    and previous_notes[record.id]["close_summary"] != (record.close_summary or "")
                )
            )
        )
        if note_changed_records:
            note_changed_records._create_process_logs(
                "note",
                note=audit_note,
                previous_states=previous_states,
            )
        return result

    def _build_exception_name(self, vals):
        exception_type = vals.get("exception_type") or "other"
        report_time = vals.get("report_time")
        report_dt = fields.Datetime.to_datetime(report_time) if report_time else fields.Datetime.now()
        return f"EXC-{exception_type.upper()}-{report_dt.strftime('%Y%m%d%H%M%S')}"

    def _create_process_logs(
        self,
        action_type,
        from_state=False,
        to_state=False,
        note="",
        previous_states=None,
    ):
        log_model = self.env["logistics.trace.exception.process.log"].sudo()
        values_list = []
        for record in self:
            values_list.append(
                {
                    "exception_id": record.id,
                    "action_type": action_type,
                    "operator_id": self.env.user.id,
                    "from_state": (
                        previous_states.get(record.id)
                        if previous_states and record.id in previous_states
                        else from_state or False
                    ),
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
        self.write({"state": "closed"})

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
