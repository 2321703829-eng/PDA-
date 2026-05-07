import base64
from html import escape

from odoo import api, fields, models
from odoo.exceptions import UserError

from ..services.image_storage_service import LogisticsEvidenceImageStorage


class LogisticsTraceEvidence(models.Model):
    _name = "logistics.trace.evidence"
    _description = "Logistics Trace Evidence"
    _order = "uploaded_at desc, sequence asc, id desc"
    _rec_name = "name"
    _uniq_logistics_trace_evidence_trace_request = models.Constraint(
        "unique(trace_event_id, client_request_id)",
        "Client request ID must be unique within the same trace event.",
    )

    STATE_SELECTION = [
        ("available", "Available"),
        ("missing", "Missing"),
    ]

    UPLOAD_ROLE_SELECTION = [
        ("warehouse", "仓库留痕"),
        ("driver", "司机留痕"),
        ("unknown", "未标记"),
    ]

    name = fields.Char(string="Evidence Name", required=True, copy=False, default="New")
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
    image_access_key = fields.Char(string="Cover Image Access Key", index=True)
    preview_url = fields.Char(string="Cover Preview URL")
    full_url = fields.Char(string="Cover Full URL")
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
    upload_role = fields.Selection(
        UPLOAD_ROLE_SELECTION,
        string="留痕端",
        required=True,
        default="unknown",
        index=True,
    )
    trace_event_type = fields.Selection(
        [
            ("arrive_loading_point", "到达装货点"),
            ("start_loading", "开始装车"),
            ("finish_loading", "完成装车"),
            ("departed", "离开门店"),
            ("arrive_store", "到达门店"),
            ("deliver_finish", "交付完成"),
            ("signoff", "完成签收"),
            ("exception_report", "异常上报"),
        ],
        string="留痕事件类型",
        compute="_compute_trace_event_fields",
        store=True,
        readonly=True,
        index=True,
    )
    trace_event_time = fields.Datetime(
        string="留痕时间",
        compute="_compute_trace_event_fields",
        store=True,
        readonly=True,
        index=True,
    )
    trace_event_display_name = fields.Char(
        string="留痕事件",
        compute="_compute_trace_event_fields",
        store=True,
        readonly=True,
    )
    remark = fields.Char(string="Remark")
    client_request_id = fields.Char(string="Client Request ID", index=True)
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
    image_ids = fields.One2many(
        "logistics.trace.evidence.image",
        "evidence_id",
        string="Images",
    )
    image_count = fields.Integer(
        string="Image Count",
        compute="_compute_image_count",
        store=True,
    )
    image_items_json = fields.Json(
        string="Image Items",
        compute="_compute_image_items_json",
    )
    image_preview_html = fields.Html(
        string="证据图片",
        compute="_compute_image_preview_html",
        sanitize=False,
    )

    @api.depends("uploader_id")
    def _compute_uploader_name(self):
        for record in self:
            record.uploader_name = record.uploader_id.name or ""

    @api.depends("trace_event_id.event_type", "trace_event_id.trace_time", "trace_event_id.display_name")
    def _compute_trace_event_fields(self):
        for record in self:
            record.trace_event_type = record.trace_event_id.event_type or False
            record.trace_event_time = record.trace_event_id.trace_time or False
            record.trace_event_display_name = record.trace_event_id.display_name or ""

    @api.depends("trace_event_id.event_type")
    def _compute_exception_flags(self):
        for record in self:
            record.is_exception_related = record.trace_event_id.event_type == "exception_report"

    @api.depends(
        "image_ids",
        "image_ids.sequence",
        "image_ids.storage_status",
        "image_access_key",
        "preview_url",
        "full_url",
    )
    def _compute_image_count(self):
        for record in self:
            if record.image_ids:
                record.image_count = len(record._sorted_image_ids())
            elif record.state != "missing" and (record.image_access_key or record.preview_url or record.full_url):
                record.image_count = 1
            else:
                record.image_count = 0

    @api.depends(
        "image_ids",
        "image_ids.sequence",
        "image_ids.image_access_key",
        "image_ids.preview_url",
        "image_ids.full_url",
        "image_ids.download_url",
        "image_ids.storage_status",
        "image_access_key",
        "preview_url",
        "full_url",
        "name",
        "trace_event_id",
        "trace_event_type",
        "trace_event_time",
        "trace_event_display_name",
        "uploaded_at",
        "uploader_name",
        "remark",
        "is_exception_related",
    )
    def _compute_image_items_json(self):
        for record in self:
            image_records = record._sorted_image_ids()
            if image_records:
                total = len(image_records)
                record.image_items_json = [
                    image_record.to_viewer_item(
                        evidence=record,
                        index=index,
                        total=total,
                    )
                    for index, image_record in enumerate(image_records, start=1)
                ]
            elif record.state != "missing" and (record.image_access_key or record.preview_url or record.full_url):
                record.image_items_json = [record._build_legacy_image_item()]
            else:
                record.image_items_json = []

    @api.depends("image_items_json")
    def _compute_image_preview_html(self):
        for record in self:
            items = record.image_items_json or []
            blocks = []
            overlays = []
            for index, item in enumerate(items, start=1):
                url = (item.get("previewUrl") or item.get("fullUrl") or "").strip()
                if not url:
                    continue
                label = escape(item.get("sourceFilename") or item.get("label") or record.name or "证据图片")
                safe_url = escape(url, quote=True)
                target_id = f"evidence-image-preview-{record.id}-{index}"
                blocks.append(
                    '<a href="#{target_id}" '
                    'style="display:inline-block;margin:0 12px 12px 0;text-decoration:none;">'
                    '<img src="{url}" alt="{label}" '
                    'style="width:148px;height:148px;object-fit:cover;border-radius:8px;'
                    'border:1px solid #d9e2ef;background:#f8fafc;display:block;"/>'
                    '<div style="max-width:148px;margin-top:4px;font-size:12px;color:#526070;'
                    'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{label}</div>'
                    '</a>'.format(target_id=target_id, url=safe_url, label=label)
                )
                overlays.append(
                    '<div id="{target_id}" class="o_logistics_evidence_lightbox">'
                    '<a href="#" class="o_logistics_evidence_lightbox_backdrop" aria-label="关闭"></a>'
                    '<div class="o_logistics_evidence_lightbox_body">'
                    '<a href="#" class="o_logistics_evidence_lightbox_close">关闭</a>'
                    '<img src="{url}" alt="{label}"/>'
                    '</div>'
                    '</div>'.format(target_id=target_id, url=safe_url, label=label)
                )
            record.image_preview_html = (
                '<style>'
                '.o_logistics_evidence_lightbox{display:none;position:fixed;z-index:3000;'
                'left:0;top:0;right:0;bottom:0;background:rgba(15,23,42,.72);'
                'align-items:center;justify-content:center;padding:32px;}'
                '.o_logistics_evidence_lightbox:target{display:flex;}'
                '.o_logistics_evidence_lightbox_backdrop{position:absolute;left:0;top:0;right:0;bottom:0;}'
                '.o_logistics_evidence_lightbox_body{position:relative;z-index:1;max-width:92vw;max-height:88vh;}'
                '.o_logistics_evidence_lightbox_body img{display:block;max-width:92vw;max-height:88vh;'
                'object-fit:contain;border-radius:8px;background:#fff;}'
                '.o_logistics_evidence_lightbox_close{position:absolute;right:10px;top:10px;'
                'padding:6px 12px;border-radius:6px;background:rgba(15,23,42,.78);'
                'color:#fff;text-decoration:none;font-size:13px;}'
                '</style>'
                '<div style="display:flex;flex-wrap:wrap;align-items:flex-start;">'
                + "".join(blocks)
                + "</div>"
                + "".join(overlays)
                if blocks
                else '<span style="color:#8a94a6;">暂无可显示图片</span>'
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("upload_role"):
                vals["upload_role"] = self._resolve_upload_role(vals)
            if vals.get("name", "New") in ("New", "新建"):
                vals["name"] = self._build_evidence_name(vals)
        return super().create(vals_list)

    def _resolve_upload_role(self, vals):
        raw = vals.get("upload_role") or vals.get("uploadRole") or vals.get("uploader_role") or vals.get("role")
        normalized = str(raw or "").strip().lower()
        mapping = {
            "warehouse": "warehouse",
            "store": "warehouse",
            "keeper": "warehouse",
            "driver": "driver",
            "truck_driver": "driver",
            "unknown": "unknown",
        }
        return mapping.get(normalized, "unknown")

    def _build_evidence_name(self, vals):
        uploaded_at = vals.get("uploaded_at")
        uploaded_dt = fields.Datetime.to_datetime(uploaded_at) if uploaded_at else fields.Datetime.now()
        return f"Evidence - {fields.Datetime.to_string(uploaded_dt)}"

    def action_back_to_evidence_list(self):
        self.ensure_one()
        action_xml_id = "logistics_trace_evidence.action_logistics_trace_evidence"
        if self.upload_role == "warehouse":
            action_xml_id = "logistics_trace_evidence.action_logistics_trace_evidence_warehouse"
        elif self.upload_role == "driver":
            action_xml_id = "logistics_trace_evidence.action_logistics_trace_evidence_driver"
        action = self.env["ir.actions.actions"]._for_xml_id(action_xml_id)
        action["target"] = "current"
        return action

    def action_download_images(self):
        self.ensure_one()
        image_records = self._sorted_image_ids()
        if image_records:
            download_url = image_records[0].download_url or image_records[0].full_url or image_records[0].preview_url
        elif self.state != "missing" and (self.full_url or self.preview_url):
            download_url = self.full_url or self.preview_url
        else:
            download_url = False
        if not download_url:
            raise UserError("当前证据没有可下载图片。")
        return {
            "type": "ir.actions.act_url",
            "url": download_url,
            "target": "self",
        }

    def _sorted_image_ids(self):
        return self.image_ids.filtered(lambda rec: rec.storage_status != "deleted").sorted(
            key=lambda rec: (rec.sequence, rec.id)
        )

    def _build_legacy_image_item(self):
        self.ensure_one()
        image_access_key = (self.image_access_key or "").strip()
        preview_url = (self.preview_url or "").strip()
        full_url = (self.full_url or "").strip() or preview_url
        return {
            "key": f"legacy_{self.id}",
            "evidenceId": self.id,
            "evidenceLabel": self.name or f"Evidence {self.id}",
            "imageId": False,
            "imageIndex": 1,
            "imageCountInEvidence": 1,
            "label": self.name or f"Evidence {self.id}",
            "name": self.name or f"Evidence {self.id}",
            "traceEventId": self.trace_event_id.id,
            "traceLabel": self.trace_event_display_name or self.trace_event_id.display_name or "Trace Event",
            "traceEventType": self.trace_event_type or "",
            "traceEventTime": fields.Datetime.to_string(self.trace_event_time) if self.trace_event_time else False,
            "uploadedAt": fields.Datetime.to_string(self.uploaded_at) if self.uploaded_at else False,
            "uploader": self.uploader_name or "",
            "remark": self.remark or "",
            "isExceptionEvidence": bool(self.is_exception_related),
            "hasRelatedException": bool(self.is_exception_related),
            "previewText": self.name or "Evidence Preview",
            "imageAccessKey": image_access_key,
            "previewUrl": preview_url,
            "fullUrl": full_url,
            "downloadUrl": full_url,
        }

    def register_uploaded_image(self, image_payload, *, sequence=None, remark="", content_sha256=False):
        self.ensure_one()
        image_model = self.env["logistics.trace.evidence.image"].sudo()
        image_vals = {
            "evidence_id": self.id,
            "sequence": sequence if sequence is not None else (len(self.image_ids) + 1) * 10,
            "image_access_key": image_payload["image_access_key"],
            "source_filename": image_payload.get("original_file_name") or image_payload.get("file_name"),
            "stored_file_name": image_payload.get("file_name"),
            "file_ext": image_payload.get("file_ext"),
            "mime_type": image_payload.get("content_type"),
            "file_size": image_payload.get("content_length"),
            "storage_provider": image_payload.get("storage_provider") or "local",
            "storage_bucket": image_payload.get("storage_bucket"),
            "storage_relative_path": image_payload.get("storage_relative_path"),
            "storage_status": image_payload.get("storage_status") or "active",
            "captured_at": fields.Datetime.now(),
            "content_sha256": content_sha256 or False,
            "remark": remark or False,
        }
        image_record = image_model.create(image_vals)
        self._sync_legacy_cover_fields(force_clear=True)
        return image_record

    def upload_image_binary(self, *, file_name, content, content_type, sequence=None, remark="", content_sha256=False):
        self.ensure_one()
        storage = LogisticsEvidenceImageStorage(self.env)
        payload = storage.upload_image(
            file_name=file_name,
            content=content,
            content_type=content_type,
        )
        return self.register_uploaded_image(payload, sequence=sequence, remark=remark, content_sha256=content_sha256)

    def _build_attachment_image_payload(self, attachment, *, preferred_key):
        content = base64.b64decode(attachment.datas or b"")
        if not content:
            raise UserError("Legacy evidence attachment is empty.")
        storage = LogisticsEvidenceImageStorage(self.env)
        return storage.import_existing_image(
            image_access_key=preferred_key,
            file_name=attachment.name or preferred_key or "legacy_image.png",
            content=content,
            content_type=attachment.mimetype or "application/octet-stream",
        )

    def _build_legacy_image_payload(self):
        self.ensure_one()
        storage = LogisticsEvidenceImageStorage(self.env)
        attachment = (
            self.env["ir.attachment"]
            .sudo()
            .search(
                [
                    ("res_model", "=", "logistics.trace.evidence"),
                    ("res_id", "=", self.id),
                    ("description", "=", self.image_access_key),
                ],
                order="id asc",
                limit=1,
            )
        )
        if attachment and attachment.datas:
            return self._build_attachment_image_payload(
                attachment,
                preferred_key=self.image_access_key,
            )

        legacy_source = (self.full_url or self.preview_url or "").strip()
        if not legacy_source:
            return False
        legacy_file = storage.read_legacy_image(
            self.name or self.image_access_key or f"legacy_{self.id}",
            self.full_url,
            self.preview_url,
        )
        return storage.import_existing_image(
            image_access_key=self.image_access_key,
            file_name=legacy_file["file_name"],
            content=legacy_file["content"],
            content_type=legacy_file["content_type"],
        )

    def _migrate_legacy_images_to_subtable(self):
        image_model = self.env["logistics.trace.evidence.image"].sudo()
        evidence_records = self.sudo().search(
            [
                ("image_access_key", "!=", False),
                ("image_ids", "=", False),
            ],
            order="id asc",
        )
        for evidence in evidence_records:
            try:
                payload = evidence._build_legacy_image_payload()
            except UserError:
                payload = False
            if not payload:
                continue
            image_model.create(
                {
                    "evidence_id": evidence.id,
                    "sequence": 10,
                    "image_access_key": payload["image_access_key"],
                    "source_filename": payload.get("original_file_name") or payload.get("file_name"),
                    "stored_file_name": payload.get("file_name"),
                    "file_ext": payload.get("file_ext"),
                    "mime_type": payload.get("content_type"),
                    "file_size": payload.get("content_length"),
                    "storage_provider": payload.get("storage_provider") or "local",
                    "storage_bucket": payload.get("storage_bucket"),
                    "storage_relative_path": payload.get("storage_relative_path"),
                    "storage_status": payload.get("storage_status") or "active",
                    "captured_at": evidence.uploaded_at or fields.Datetime.now(),
                    "remark": evidence.remark or False,
                    "legacy_preview_url": evidence.preview_url or False,
                    "legacy_full_url": evidence.full_url or False,
                }
            )
            evidence._sync_legacy_cover_fields(force_clear=True)
        self._refresh_legacy_fallback_state()

    def _refresh_legacy_fallback_state(self):
        evidence_records = self.sudo().search(
            [
                ("image_ids", "=", False),
                "|",
                "|",
                ("image_access_key", "!=", False),
                ("preview_url", "!=", False),
                ("full_url", "!=", False),
            ],
            order="id asc",
        )
        for evidence in evidence_records:
            try:
                payload = evidence._build_legacy_image_payload()
            except UserError:
                payload = False
            target_state = "available" if payload else "missing"
            if evidence.state != target_state:
                evidence.sudo().write({"state": target_state})

    def _sync_legacy_cover_fields(self, *, force_clear=False):
        for record in self:
            cover_image = record._sorted_image_ids()[:1]
            cover_image = cover_image[0] if cover_image else False
            if cover_image:
                values = {
                    "image_access_key": cover_image.image_access_key or False,
                    "preview_url": cover_image.preview_url or False,
                    "full_url": cover_image.full_url or cover_image.preview_url or False,
                }
            elif force_clear:
                values = {
                    "image_access_key": False,
                    "preview_url": False,
                    "full_url": False,
                }
            else:
                continue
            if any(record[field_name] != values[field_name] for field_name in values):
                super(LogisticsTraceEvidence, record.sudo()).write(values)


class LogisticsTraceEvidenceImage(models.Model):
    _name = "logistics.trace.evidence.image"
    _description = "Logistics Trace Evidence Image"
    _order = "sequence asc, id asc"
    _uniq_logistics_trace_evidence_image_access_key = models.Constraint(
        "unique(image_access_key)",
        "Image access key must be unique.",
    )
    _uniq_logistics_trace_evidence_image_hash = models.Constraint(
        "unique(evidence_id, content_sha256)",
        "Image content hash must be unique within the same evidence.",
    )

    evidence_id = fields.Many2one(
        "logistics.trace.evidence",
        string="Evidence",
        required=True,
        ondelete="cascade",
        index=True,
    )
    trace_event_id = fields.Many2one(
        "logistics.trace.event",
        string="Trace Event",
        related="evidence_id.trace_event_id",
        store=True,
        readonly=True,
        index=True,
    )
    waybill_id = fields.Many2one(
        "logistics.dispatch.waybill",
        string="Waybill",
        related="evidence_id.waybill_id",
        store=True,
        readonly=True,
        index=True,
    )
    batch_id = fields.Many2one(
        "logistics.dispatch.batch",
        string="Batch",
        related="evidence_id.batch_id",
        store=True,
        readonly=True,
        index=True,
    )
    upload_role = fields.Selection(
        related="evidence_id.upload_role",
        string="留痕端",
        store=True,
        readonly=True,
        index=True,
    )
    sequence = fields.Integer(string="Sequence", default=10)
    image_access_key = fields.Char(string="Image Access Key", required=True, index=True)
    source_filename = fields.Char(string="Source Filename")
    stored_file_name = fields.Char(string="Stored Filename")
    file_ext = fields.Char(string="File Extension")
    mime_type = fields.Char(string="MIME Type")
    file_size = fields.Integer(string="File Size")
    storage_provider = fields.Selection(
        [
            ("local", "Local Storage"),
            ("legacy_url", "Legacy URL"),
        ],
        string="Storage Provider",
        default="local",
        required=True,
    )
    captured_at = fields.Datetime(string="Captured At")
    storage_bucket = fields.Char(string="Storage Bucket")
    storage_relative_path = fields.Char(string="Storage Relative Path")
    storage_status = fields.Selection(
        [
            ("active", "Active"),
            ("missing", "Missing"),
            ("invalid", "Invalid"),
            ("deleted", "Deleted"),
        ],
        string="Storage Status",
        default="active",
        required=True,
    )
    legacy_preview_url = fields.Char(string="Legacy Preview URL")
    legacy_full_url = fields.Char(string="Legacy Full URL")
    preview_url = fields.Char(string="Preview URL", compute="_compute_urls")
    full_url = fields.Char(string="Full URL", compute="_compute_urls")
    download_url = fields.Char(string="Download URL", compute="_compute_urls")
    remark = fields.Char(string="Remark")
    content_sha256 = fields.Char(string="Content SHA256", index=True)

    @api.depends(
        "image_access_key",
        "storage_provider",
        "legacy_preview_url",
        "legacy_full_url",
    )
    def _compute_urls(self):
        storage = LogisticsEvidenceImageStorage(self.env)
        for record in self:
            if record.storage_provider == "legacy_url":
                record.preview_url = record.legacy_preview_url or record.legacy_full_url or False
                record.full_url = record.legacy_full_url or record.legacy_preview_url or False
                record.download_url = record.full_url or False
            elif record.image_access_key:
                record.preview_url = storage.build_preview_url(record.image_access_key)
                record.full_url = record.preview_url
                record.download_url = storage.build_download_url(record.image_access_key)
            else:
                record.preview_url = False
                record.full_url = False
                record.download_url = False

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.mapped("evidence_id")._sync_legacy_cover_fields(force_clear=True)
        return records

    def write(self, vals):
        result = super().write(vals)
        self.mapped("evidence_id")._sync_legacy_cover_fields(force_clear=True)
        return result

    def unlink(self):
        evidence_records = self.mapped("evidence_id")
        result = super().unlink()
        evidence_records._sync_legacy_cover_fields(force_clear=True)
        return result

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
            raise UserError("Preview URL is not available for this image.")
        return {
            "type": "ir.actions.act_url",
            "url": self.preview_url,
            "target": "new",
        }

    def action_open_download(self):
        self.ensure_one()
        if not self.download_url:
            raise UserError("Download URL is not available for this image.")
        return {
            "type": "ir.actions.act_url",
            "url": self.download_url,
            "target": "new",
        }

    def to_viewer_item(self, *, evidence, index, total):
        self.ensure_one()
        evidence.ensure_one()
        label_suffix = f" #{index}" if total > 1 else ""
        evidence_label = evidence.name or f"Evidence {evidence.id}"
        return {
            "key": f"{self.id}_{self.image_access_key}",
            "evidenceId": evidence.id,
            "evidenceLabel": evidence_label,
            "imageId": self.id,
            "imageIndex": index,
            "imageCountInEvidence": total,
            "label": f"{evidence_label}{label_suffix}",
            "name": f"{evidence_label}{label_suffix}",
            "traceEventId": evidence.trace_event_id.id,
            "traceLabel": evidence.trace_event_display_name or evidence.trace_event_id.display_name or "Trace Event",
            "traceEventType": evidence.trace_event_type or "",
            "traceEventTime": fields.Datetime.to_string(evidence.trace_event_time) if evidence.trace_event_time else False,
            "uploadedAt": fields.Datetime.to_string(evidence.uploaded_at) if evidence.uploaded_at else False,
            "uploader": evidence.uploader_name or "",
            "remark": self.remark or evidence.remark or "",
            "isExceptionEvidence": bool(evidence.is_exception_related),
            "hasRelatedException": bool(evidence.is_exception_related),
            "previewText": evidence_label,
            "imageAccessKey": self.image_access_key or "",
            "previewUrl": self.preview_url or "",
            "fullUrl": self.full_url or self.preview_url or "",
            "downloadUrl": self.download_url or self.full_url or self.preview_url or "",
            "sourceFilename": self.source_filename or self.stored_file_name or "",
            "mimeType": self.mime_type or "",
            "fileSize": self.file_size or 0,
        }
