from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LogisticsTraceEvent(models.Model):
    _name = "logistics.trace.event"
    _description = "Logistics Trace Event"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "trace_time desc, id desc"
    _rec_name = "name"

    EVENT_SELECTION = [
        ("arrive_loading_point", "Arrive Loading Point"),
        ("start_loading", "Start Loading"),
        ("finish_loading", "Finish Loading"),
        ("departed", "Departed"),
        ("arrive_store", "Arrive Store"),
        ("deliver_finish", "Deliver Finish"),
        ("signoff", "Signoff"),
        ("exception_report", "Exception Report"),
    ]

    OBJECT_SELECTION = [
        ("batch", "Batch"),
        ("waybill", "Waybill"),
    ]

    SUBMIT_SOURCE_SELECTION = [
        ("manual", "Manual"),
        ("system", "System"),
        ("mobile", "Mobile"),
    ]

    STATE_SELECTION = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("invalid", "Invalid"),
    ]

    name = fields.Char(string="Trace Event", required=True, copy=False, default="New", tracking=True)
    event_type = fields.Selection(EVENT_SELECTION, string="Event Type", required=True, tracking=True)
    object_type = fields.Selection(
        OBJECT_SELECTION,
        string="Object Type",
        required=True,
        default="waybill",
        tracking=True,
    )
    batch_id = fields.Many2one("logistics.dispatch.batch", string="Batch", ondelete="cascade", index=True)
    waybill_id = fields.Many2one(
        "logistics.dispatch.waybill",
        string="Waybill",
        ondelete="cascade",
        index=True,
    )
    trace_time = fields.Datetime(
        string="Trace Time",
        required=True,
        default=fields.Datetime.now,
        tracking=True,
        index=True,
    )
    submit_user_id = fields.Many2one(
        "res.users",
        string="Submitted By",
        default=lambda self: self.env.user,
        tracking=True,
    )
    submit_user_name = fields.Char(
        string="Submit User Name",
        compute="_compute_submit_user_name",
        store=True,
    )
    submit_source = fields.Selection(
        SUBMIT_SOURCE_SELECTION,
        string="Submit Source",
        default="manual",
    )
    location_text = fields.Char(string="Location")
    plate_no = fields.Char(string="Plate No")
    driver_name = fields.Char(string="Driver Name")
    remark = fields.Text(string="Remark", tracking=True)
    evidence_count = fields.Integer(string="Evidence Count", default=0)
    is_exception = fields.Boolean(string="Exception Event", tracking=True)
    source_channel = fields.Char(string="Source Channel")
    source_record_id = fields.Char(string="Source Record ID")
    state = fields.Selection(
        STATE_SELECTION,
        string="State",
        required=True,
        default="submitted",
        tracking=True,
    )

    @api.depends("submit_user_id")
    def _compute_submit_user_name(self):
        for record in self:
            record.submit_user_name = record.submit_user_id.name or ""

    @api.constrains("object_type", "batch_id", "waybill_id")
    def _check_object_link(self):
        for record in self:
            if record.object_type == "batch" and not record.batch_id:
                raise ValidationError("Batch trace events must be linked to a batch.")
            if record.object_type == "waybill" and not record.waybill_id:
                raise ValidationError("Waybill trace events must be linked to a waybill.")

    @api.onchange("waybill_id")
    def _onchange_waybill_id(self):
        for record in self:
            if record.waybill_id:
                record.object_type = "waybill"
                if not record.batch_id:
                    record.batch_id = record.waybill_id.batch_id
                if not record.plate_no and record.waybill_id.vehicle_id:
                    record.plate_no = record.waybill_id.vehicle_id.license_plate
                if not record.driver_name and record.waybill_id.driver_employee_id:
                    record.driver_name = record.waybill_id.driver_employee_id.name

    @api.onchange("batch_id")
    def _onchange_batch_id(self):
        for record in self:
            if record.object_type == "batch" and record.batch_id:
                if not record.plate_no and record.batch_id.vehicle_id:
                    record.plate_no = record.batch_id.vehicle_id.license_plate
                if not record.driver_name and record.batch_id.driver_employee_id:
                    record.driver_name = record.batch_id.driver_employee_id.name

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            waybill_id = vals.get("waybill_id")
            if waybill_id and not vals.get("batch_id"):
                waybill = self.env["logistics.dispatch.waybill"].browse(waybill_id)
                vals["batch_id"] = waybill.batch_id.id
            if vals.get("name", "New") == "New":
                vals["name"] = self._build_event_name(vals)
        return super().create(vals_list)

    def _build_event_name(self, vals):
        event_type = vals.get("event_type") or "trace"
        trace_time = vals.get("trace_time")
        trace_dt = fields.Datetime.to_datetime(trace_time) if trace_time else fields.Datetime.now()
        return f"{event_type.replace('_', ' ').title()} - {fields.Datetime.to_string(trace_dt)}"
