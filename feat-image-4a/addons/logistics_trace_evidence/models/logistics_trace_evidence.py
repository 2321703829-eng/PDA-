from odoo import api, fields, models
from odoo.exceptions import UserError

from ..services.image_storage_service import LogisticsEvidenceImageStorage


class LogisticsTraceEvidence(models.Model):
    _name = "logistics.trace.evidence"
    _description = "Logistics Trace Evidence"
    _order = "sequence, id"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    state = fields.Selection(
        [
            ("new", "New"),
            ("ok", "OK"),
            ("bad", "Bad"),
            ("del", "Deleted"),
        ],
        default="new",
        required=True,
    )
    evidence_type = fields.Selection(
        [
            ("image", "Image"),
            ("sign", "Sign"),
            ("file", "File"),
            ("video", "Video"),
            ("other", "Other"),
        ],
        default="image",
        required=True,
    )
    trace_id = fields.Many2one(
        "logistics.trace.event",
        required=True,
        ondelete="cascade",
        index=True,
    )
    biz_type = fields.Selection(
        related="trace_id.biz_type",
        store=True,
        index=True,
    )
    batch_no = fields.Char(
        related="trace_id.batch_no",
        store=True,
        index=True,
    )
    waybill_no = fields.Char(
        related="trace_id.waybill_no",
        store=True,
        index=True,
    )
    company_id = fields.Many2one(
        "res.company",
        related="trace_id.company_id",
        store=True,
        index=True,
    )
    remark = fields.Text()
    image_ids = fields.One2many(
        "logistics.trace.evidence.image",
        "evidence_id",
        string="Images",
    )
    image_count = fields.Integer(compute="_compute_image_count")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name"):
                vals["name"] = self.env["ir.sequence"].next_by_code("logistics.trace.evidence") or "EV"
        return super().create(vals_list)

    @api.depends("image_ids")
    def _compute_image_count(self):
        for record in self:
            record.image_count = len(record.image_ids)

    def action_mark_ok(self):
        self.write({"state": "ok"})

    def action_mark_bad(self):
        self.write({"state": "bad"})

    def action_mark_deleted(self):
        self.write({"state": "del"})

    def action_open_upload_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Upload Evidence Image",
            "res_model": "logistics.trace.evidence.upload.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_evidence_id": self.id,
            },
        }

    def action_sync_all_image_meta(self):
        for record in self:
            record.image_ids.action_sync_image_meta()

    def action_open_images(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Evidence Images",
            "res_model": "logistics.trace.evidence.image",
            "view_mode": "list,form",
            "domain": [("evidence_id", "=", self.id)],
            "context": {
                "default_evidence_id": self.id,
            },
        }

    def register_uploaded_image(self, image_payload):
        self.ensure_one()
        return self.env["logistics.trace.evidence.image"].create(
            {
                "evidence_id": self.id,
                "image_access_key": image_payload["image_access_key"],
                "source_filename": image_payload.get("original_file_name") or image_payload.get("file_name"),
                "stored_file_name": image_payload.get("file_name"),
                "file_ext": image_payload.get("file_ext"),
                "mime_type": image_payload.get("content_type"),
                "file_size": image_payload.get("content_length"),
                "storage_provider": image_payload.get("storage_provider"),
                "storage_bucket": image_payload.get("storage_bucket"),
                "storage_relative_path": image_payload.get("storage_relative_path"),
                "storage_status": image_payload.get("storage_status"),
                "captured_at": fields.Datetime.now(),
            }
        )


class LogisticsTraceEvidenceImage(models.Model):
    _name = "logistics.trace.evidence.image"
    _description = "Logistics Trace Evidence Image"
    _order = "sequence, id"
    _sql_constraints = [
        (
            "uniq_logistics_trace_evidence_image_access_key",
            "unique(image_access_key)",
            "Image access key must be unique.",
        ),
    ]

    evidence_id = fields.Many2one(
        "logistics.trace.evidence",
        required=True,
        ondelete="cascade",
        index=True,
    )
    biz_type = fields.Selection(
        related="evidence_id.biz_type",
        store=True,
        index=True,
    )
    batch_no = fields.Char(
        related="evidence_id.batch_no",
        store=True,
        index=True,
    )
    waybill_no = fields.Char(
        related="evidence_id.waybill_no",
        store=True,
        index=True,
    )
    sequence = fields.Integer(default=10)
    image_access_key = fields.Char(required=True, index=True)
    source_filename = fields.Char()
    stored_file_name = fields.Char()
    file_ext = fields.Char()
    mime_type = fields.Char()
    file_size = fields.Integer()
    storage_provider = fields.Selection(
        [
            ("local", "Local Storage"),
            ("minio", "MinIO"),
            ("s3", "Amazon S3"),
            ("oss", "Alibaba OSS"),
        ],
        default="local",
    )
    captured_at = fields.Datetime()
    storage_bucket = fields.Char()
    storage_relative_path = fields.Char()
    storage_status = fields.Char()
    preview_url = fields.Char(compute="_compute_urls")
    download_url = fields.Char(compute="_compute_urls")
    remark = fields.Char()

    @api.depends("image_access_key")
    def _compute_urls(self):
        storage = LogisticsEvidenceImageStorage(self.env)
        for record in self:
            if record.image_access_key:
                record.preview_url = storage.build_preview_url(record.image_access_key)
                record.download_url = storage.build_download_url(record.image_access_key)
            else:
                record.preview_url = False
                record.download_url = False

    def action_sync_image_meta(self):
        storage = LogisticsEvidenceImageStorage(self.env)
        for record in self:
            if not record.image_access_key:
                continue
            meta = storage.sync_image_meta(record)
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

    def action_open_download(self):
        self.ensure_one()
        if not self.download_url:
            raise UserError("Download URL is not available because the image storage is not configured.")
        return {
            "type": "ir.actions.act_url",
            "url": self.download_url,
            "target": "new",
        }
