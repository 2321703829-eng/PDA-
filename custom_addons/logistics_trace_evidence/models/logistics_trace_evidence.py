from odoo import api, fields, models


class LogisticsTraceEvidence(models.Model):
    _name = "logistics.trace.evidence"
    _description = "Logistics Trace Evidence"
    _order = "uploaded_at desc, sequence asc, id desc"
    _rec_name = "name"

    STATE_SELECTION = [
        ("available", "Available"),
        ("missing", "Missing"),
    ]

    name = fields.Char(string="Evidence", required=True, copy=False, default="New")
    trace_event_id = fields.Many2one(
        "logistics.trace.event",
        string="Trace Event",
        required=True,
        ondelete="cascade",
        index=True,
    )
    waybill_id = fields.Many2one(
        "logistics.dispatch.waybill",
        string="Waybill",
        related="trace_event_id.waybill_id",
        store=True,
        readonly=True,
        index=True,
    )
    batch_id = fields.Many2one(
        "logistics.dispatch.batch",
        string="Batch",
        related="trace_event_id.batch_id",
        store=True,
        readonly=True,
        index=True,
    )
    image_access_key = fields.Char(string="Image Access Key", index=True)
    preview_url = fields.Char(string="Preview URL")
    full_url = fields.Char(string="Full URL")
    uploaded_at = fields.Datetime(
        string="Uploaded At",
        required=True,
        default=fields.Datetime.now,
        index=True,
    )
    uploader_id = fields.Many2one(
        "res.users",
        string="Uploader",
        default=lambda self: self.env.user,
    )
    uploader_name = fields.Char(
        string="Uploader Name",
        compute="_compute_uploader_name",
        store=True,
    )
    remark = fields.Char(string="Remark")
    is_exception_related = fields.Boolean(
        string="Exception Related",
        compute="_compute_exception_flags",
        store=True,
    )
    sequence = fields.Integer(string="Sequence", default=10)
    state = fields.Selection(
        STATE_SELECTION,
        string="State",
        required=True,
        default="available",
    )

    @api.depends("uploader_id")
    def _compute_uploader_name(self):
        for record in self:
            record.uploader_name = record.uploader_id.name or ""

    @api.depends("trace_event_id.is_exception")
    def _compute_exception_flags(self):
        for record in self:
            record.is_exception_related = bool(record.trace_event_id.is_exception)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self._build_evidence_name(vals)
        return super().create(vals_list)

    def _build_evidence_name(self, vals):
        uploaded_at = vals.get("uploaded_at")
        uploaded_dt = fields.Datetime.to_datetime(uploaded_at) if uploaded_at else fields.Datetime.now()
        return f"Evidence - {fields.Datetime.to_string(uploaded_dt)}"
