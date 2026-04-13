import json
from urllib.parse import quote

from odoo import http
from odoo.exceptions import UserError
from odoo.http import request

from ..services.image_storage_service import LogisticsEvidenceImageStorage


class LogisticsTraceEvidenceImageController(http.Controller):
    @http.route(
        ["/api/mini/logistics/traces"],
        type="http",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def create_trace_event(self, **kwargs):
        try:
            payload = self._get_json_payload()
            biz_type = payload.get("biz_type") or "waybill"
            values = {
                "biz_type": biz_type,
                "trace_type": payload.get("trace_type") or "arrive",
                "trace_source": "mini",
                "batch_no": payload.get("batch_no"),
                "waybill_no": payload.get("waybill_no"),
                "remark": payload.get("remark"),
                "driver_name": payload.get("driver_name"),
                "vehicle_no": payload.get("vehicle_no"),
                "location_text": payload.get("location_text"),
                "route_sequence": payload.get("route_sequence"),
            }
            if payload.get("partner_id"):
                values["partner_id"] = payload["partner_id"]
            if payload.get("stock_picking_id"):
                values["stock_picking_id"] = payload["stock_picking_id"]
            if payload.get("occurred_at"):
                values["occurred_at"] = payload["occurred_at"]

            trace = request.env["logistics.trace.event"].sudo().create(values)
            return self._json_response(
                {
                    "ok": True,
                    "message": "Trace event created successfully.",
                    "data": {
                        "trace_event_id": trace.id,
                        "trace_no": trace.name,
                        "biz_type": trace.biz_type,
                        "trace_type": trace.trace_type,
                        "batch_no": trace.batch_no,
                        "waybill_no": trace.waybill_no,
                        "state": trace.state,
                    },
                },
                status=200,
            )
        except UserError as exc:
            return self._json_response({"ok": False, "message": str(exc)}, status=400)

    @http.route(
        ["/api/mini/logistics/evidences"],
        type="http",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def create_evidence(self, **kwargs):
        try:
            payload = self._get_json_payload()
            trace_id = payload.get("trace_id")
            if not trace_id:
                return self._json_response(
                    {"ok": False, "message": "trace_id is required."},
                    status=400,
                )

            trace = (
                request.env["logistics.trace.event"]
                .sudo()
                .browse(trace_id)
                .exists()
            )
            if not trace:
                return self._json_response(
                    {"ok": False, "message": "Trace event not found."},
                    status=404,
                )

            evidence = request.env["logistics.trace.evidence"].sudo().create(
                {
                    "trace_id": trace.id,
                    "evidence_type": payload.get("evidence_type") or "image",
                    "remark": payload.get("remark"),
                }
            )
            return self._json_response(
                {
                    "ok": True,
                    "message": "Evidence created successfully.",
                    "data": {
                        "evidence_id": evidence.id,
                        "evidence_no": evidence.name,
                        "trace_event_id": trace.id,
                        "trace_no": trace.name,
                        "evidence_type": evidence.evidence_type,
                        "state": evidence.state,
                    },
                },
                status=200,
            )
        except UserError as exc:
            return self._json_response({"ok": False, "message": str(exc)}, status=400)

    @http.route(
        ["/api/mini/logistics/evidences/<int:evidence_id>/images"],
        type="http",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def upload_evidence_image(self, evidence_id, **kwargs):
        try:
            evidence = (
                request.env["logistics.trace.evidence"]
                .sudo()
                .browse(evidence_id)
                .exists()
            )
            if not evidence:
                return self._json_response(
                    {"ok": False, "message": "Evidence not found."},
                    status=404,
                )

            uploaded_file = request.httprequest.files.get("file")
            if not uploaded_file:
                return self._json_response(
                    {"ok": False, "message": "File field is required."},
                    status=400,
                )

            image_record = evidence.upload_image_binary(
                file_name=uploaded_file.filename,
                content=uploaded_file.read(),
                content_type=uploaded_file.content_type or "application/octet-stream",
            )
            return self._json_response(
                {
                    "ok": True,
                    "message": "Image uploaded successfully.",
                    "data": {
                        "evidence_id": evidence.id,
                        "image_id": image_record.id,
                        "image_access_key": image_record.image_access_key,
                        "preview_url": image_record.preview_url,
                        "download_url": image_record.download_url,
                        "storage_status": image_record.storage_status,
                    },
                },
                status=200,
            )
        except UserError as exc:
            return self._json_response(
                {"ok": False, "message": str(exc)},
                status=400,
            )

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

    @staticmethod
    def _json_response(payload, *, status):
        return request.make_response(
            json.dumps(payload),
            headers=[("Content-Type", "application/json")],
            status=status,
        )

    @staticmethod
    def _get_json_payload():
        return request.httprequest.get_json(silent=True) or {}
