from urllib.parse import quote

from odoo import http
from odoo.http import request

from ..services.image_storage_service import LogisticsEvidenceImageStorage


class LogisticsTraceEvidenceImageController(http.Controller):
    @http.route(
        ["/logistics_trace/evidence-images/<string:image_access_key>"],
        type="http",
        auth="user",
        methods=["GET"],
        csrf=False,
    )
    def get_evidence_image(self, image_access_key, download=False, **kwargs):
        image_record = (
            request.env["logistics.trace.evidence.image"]
            .sudo()
            .search([("image_access_key", "=", image_access_key)], limit=1)
        )
        if not image_record:
            return request.not_found()

        storage = LogisticsEvidenceImageStorage(request.env)
        payload = storage.read_image(image_record)
        file_name = payload["file_name"]
        disposition = "attachment" if download else "inline"
        encoded_name = quote(file_name)
        headers = [
            ("Content-Type", payload["content_type"]),
            ("Content-Length", str(payload["content_length"])),
            (
                "Content-Disposition",
                f"{disposition}; filename*=UTF-8''{encoded_name}",
            ),
        ]
        return request.make_response(payload["content"], headers=headers)
