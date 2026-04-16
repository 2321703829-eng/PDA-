from odoo import api, fields, models
from odoo.exceptions import UserError

from ..services.image_storage_service import LogisticsEvidenceImageStorage


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
    source_filename = fields.Char(string="Source Filename")
    stored_file_name = fields.Char(string="Stored Filename")
    file_ext = fields.Char(string="File Extension")
    mime_type = fields.Char(string="MIME Type")
    file_size = fields.Integer(string="File Size")
    storage_provider = fields.Selection(
        [
            ("local", "Local Storage"),
            ("minio", "MinIO"),
            ("s3", "Amazon S3"),
            ("oss", "Alibaba OSS"),
        ],
        string="Storage Provider",
        default="local",
    )
    storage_bucket = fields.Char(string="Storage Bucket")
    storage_relative_path = fields.Char(string="Storage Relative Path")
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

    def upload_image_binary(self, *, file_name, content, content_type):
        self.ensure_one()
        storage = LogisticsEvidenceImageStorage(self.env)
        payload = storage.upload_image(
            file_name=file_name,
            content=content,
            content_type=content_type,
        )
        values = {
            "image_access_key": payload["image_access_key"],
            "preview_url": storage.build_preview_url(payload["image_access_key"]),
            "full_url": storage.build_full_url(payload["image_access_key"]),
            "source_filename": payload.get("original_file_name") or payload.get("file_name"),
            "stored_file_name": payload.get("file_name"),
            "file_ext": payload.get("file_ext"),
            "mime_type": payload.get("content_type"),
            "file_size": payload.get("content_length"),
            "storage_provider": payload.get("storage_provider"),
            "storage_bucket": payload.get("storage_bucket"),
            "storage_relative_path": payload.get("storage_relative_path"),
            "uploaded_at": fields.Datetime.now(),
        }
        self.write(values)
        if self.state == "missing":
            self.state = "available"
        return self

    def action_sync_storage_meta(self):
        storage = LogisticsEvidenceImageStorage(self.env)
        for record in self:
            if not record.image_access_key:
                continue
            meta = storage.sync_evidence_meta(record)
            record.write(meta)

    def action_open_preview(self):
        self.ensure_one()
        if not self.preview_url:
            raise UserError("Preview URL is not available because the image storage is not configured.")
        return {
            "type": "ir.actions.act_url",
            "url": self.preview_url,
            "target": "new",
        }

    def action_open_full(self):
        self.ensure_one()
        if not self.full_url:
            raise UserError("Full URL is not available because the image storage is not configured.")
        return {
            "type": "ir.actions.act_url",
            "url": self.full_url,
            "target": "new",
        }
