import base64
import io
import zipfile
from urllib.parse import quote

from odoo import http
from odoo.exceptions import UserError
from odoo.http import request

from ..services.image_storage_service import LogisticsEvidenceImageStorage
from .image_capability_controller import LogisticsImageCapabilityController


class LogisticsTraceEvidenceImageController(http.Controller):
    @http.route(
        [
            "/logistics_trace/evidence-images/<string:image_access_key>",
            "/<string:lang>/logistics_trace/evidence-images/<string:image_access_key>",
        ],
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_evidence_image(self, image_access_key, lang=None, download=False, **kwargs):
        storage = LogisticsEvidenceImageStorage(request.env)
        image_record = False
        try:
            image_record = (
                request.env["logistics.trace.evidence.image"]
                .sudo()
                .search([("image_access_key", "=", image_access_key)], limit=1)
            )
        except KeyError:
            image_record = False

        try:
            if image_record and image_record.storage_provider == "oss":
                payload = self._read_oss_image(image_record, download=download)
                if not download:
                    return request.redirect(payload["url"], code=302)
            elif image_record:
                payload = storage.read_image(image_record)
            else:
                evidence = (
                    request.env["logistics.trace.evidence"]
                    .sudo()
                    .search([("image_access_key", "=", image_access_key)], limit=1)
                )
                if not evidence:
                    return request.not_found()
                attachment = (
                    request.env["ir.attachment"]
                    .sudo()
                    .search(
                        [
                            ("res_model", "=", "logistics.trace.evidence"),
                            ("res_id", "=", evidence.id),
                            ("description", "=", image_access_key),
                        ],
                        limit=1,
                    )
                )
                if attachment and attachment.datas:
                    content = base64.b64decode(attachment.datas)
                    payload = {
                        "file_name": attachment.name or image_access_key,
                        "content_type": attachment.mimetype or "application/octet-stream",
                        "content_length": len(content),
                        "content": content,
                    }
                else:
                    payload = storage.read_legacy_image(
                        evidence.name or image_access_key,
                        evidence.full_url,
                        evidence.preview_url,
                    )
        except UserError:
            return request.not_found()
        file_name = payload["file_name"]
        disposition = "attachment" if download else "inline"
        encoded_name = quote(file_name)
        headers = [
            ("Content-Type", payload["content_type"]),
            ("Content-Length", str(payload["content_length"])),
            ("Content-Disposition", f"{disposition}; filename*=UTF-8''{encoded_name}"),
        ]
        return request.make_response(payload["content"], headers=headers)

    @http.route(
        [
            "/logistics_trace/waybills/<int:waybill_id>/evidences/download",
            "/<string:lang>/logistics_trace/waybills/<int:waybill_id>/evidences/download",
        ],
        type="http",
        auth="user",
        methods=["GET"],
        csrf=False,
    )
    def download_waybill_evidence_images(self, waybill_id, lang=None, upload_role=None, **kwargs):
        domain = [("waybill_id", "=", waybill_id), ("state", "!=", "missing")]
        if upload_role:
            domain.append(("upload_role", "=", upload_role))

        evidences = (
            request.env["logistics.trace.evidence"]
            .sudo()
            .search(domain, order="uploaded_at desc, sequence asc, id asc")
        )
        if not evidences:
            return request.not_found()

        storage = LogisticsEvidenceImageStorage(request.env)
        zip_entries = []
        used_names = set()
        for evidence in evidences:
            image_records = evidence.image_ids.filtered(
                lambda rec: rec.storage_status != "deleted"
            ).sorted(key=lambda rec: (rec.sequence, rec.id))
            if image_records:
                for image in image_records:
                    try:
                        if image.storage_provider == "oss":
                            payload = self._read_oss_image(image, download=True)
                        else:
                            payload = storage.read_image(image)
                    except UserError:
                        continue
                    archive_name = self._unique_archive_name(
                        payload.get("file_name") or image.image_access_key or "evidence-image",
                        used_names,
                    )
                    zip_entries.append((archive_name, payload["content"]))
            elif evidence.image_access_key or evidence.full_url or evidence.preview_url:
                try:
                    payload = self._read_legacy_evidence_payload(storage, evidence)
                except UserError:
                    continue
                archive_name = self._unique_archive_name(
                    payload.get("file_name") or evidence.image_access_key or evidence.name or "evidence-image",
                    used_names,
                )
                zip_entries.append((archive_name, payload["content"]))

        if not zip_entries:
            return request.not_found()

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
            for archive_name, content in zip_entries:
                archive.writestr(archive_name, content)
        content = buffer.getvalue()

        waybill = request.env["logistics.dispatch.waybill"].sudo().browse(waybill_id)
        file_name = "%s-evidence-images.zip" % (waybill.name or ("waybill-%s" % waybill_id))
        encoded_name = quote(file_name)
        headers = [
            ("Content-Type", "application/zip"),
            ("Content-Length", str(len(content))),
            ("Content-Disposition", f"attachment; filename*=UTF-8''{encoded_name}"),
        ]
        return request.make_response(content, headers=headers)


    def _read_oss_image(self, image_record, *, download):
        signer = LogisticsImageCapabilityController()
        config = request.env["ir.config_parameter"].sudo()
        session = {
            "image_access_key": image_record.image_access_key,
            "bucket": image_record.storage_bucket or (config.get_param("logistics_trace_image_accel.bucket", default="") or "").strip(),
            "endpoint": (config.get_param("logistics_trace_image_accel.endpoint", default="") or "").strip(),
            "object_key": image_record.storage_relative_path or "",
            "mime_type": image_record.mime_type or "image/jpeg",
            "filename": image_record.source_filename or image_record.stored_file_name or image_record.image_access_key,
        }
        if not all([session["bucket"], session["endpoint"], session["object_key"]]):
            raise UserError("OSS image metadata is incomplete.")
        signed_url = signer._build_signed_oss_url(config, session, method="GET")
        if not download:
            return {"url": signed_url}
        result = signer._download_oss_object(config, session)
        if not result.get("ok"):
            raise UserError(result.get("message") or "OSS image download failed.")
        return result

    def _read_legacy_evidence_payload(self, storage, evidence):
        attachment = (
            request.env["ir.attachment"]
            .sudo()
            .search(
                [
                    ("res_model", "=", "logistics.trace.evidence"),
                    ("res_id", "=", evidence.id),
                    ("description", "=", evidence.image_access_key),
                ],
                limit=1,
            )
        )
        if attachment and attachment.datas:
            content = base64.b64decode(attachment.datas)
            return {
                "file_name": attachment.name or evidence.image_access_key,
                "content": content,
            }
        return storage.read_legacy_image(
            evidence.name or evidence.image_access_key or "evidence-image",
            evidence.full_url,
            evidence.preview_url,
        )

    def _unique_archive_name(self, file_name, used_names):
        safe_name = (file_name or "evidence-image").strip().replace("/", "_").replace("\\", "_")
        if not safe_name:
            safe_name = "evidence-image"
        candidate = safe_name
        index = 2
        while candidate in used_names:
            if "." in safe_name:
                stem, ext = safe_name.rsplit(".", 1)
                candidate = f"{stem}-{index}.{ext}"
            else:
                candidate = f"{safe_name}-{index}"
            index += 1
        used_names.add(candidate)
        return candidate
