import base64
from urllib.parse import quote

from odoo import http
from odoo.http import request

from ..services.image_storage_service import LogisticsEvidenceImageStorage


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

        if image_record:
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
        file_name = payload["file_name"]
        disposition = "attachment" if download else "inline"
        encoded_name = quote(file_name)
        headers = [
            ("Content-Type", payload["content_type"]),
            ("Content-Length", str(payload["content_length"])),
            ("Content-Disposition", f"{disposition}; filename*=UTF-8''{encoded_name}"),
        ]
        return request.make_response(payload["content"], headers=headers)
