import json
import uuid

from odoo import http
from odoo.exceptions import AccessError
from odoo.http import Response, request


class LogisticsWebDashboardController(http.Controller):
    @http.route(
        "/api/admin/logistics/dashboard/summary",
        type="http",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def dashboard_summary(self):
        return self._handle_payload(
            "req_dashboard_summary",
            lambda service: service.get_dashboard_summary_payload(),
        )

    @http.route(
        "/api/admin/logistics/boss_trace/summary",
        type="http",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def boss_trace_summary(self):
        return self._handle_payload(
            "req_boss_trace_summary",
            lambda service: service.get_boss_trace_summary_payload(),
        )

    def _handle_payload(self, request_prefix, callback):
        service = request.env["logistics.trace.exception"]
        try:
            data = callback(service)
        except AccessError as exc:
            return self._json_response(
                {
                    "code": 4003,
                    "message": "forbidden",
                    "data": {"errors": [{"error_code": "ANALYSIS_ACCESS_FORBIDDEN", "error_message": str(exc)}]},
                    "request_id": self._build_request_id(request_prefix),
                },
                status=403,
            )
        return self._json_response(
            {
                "code": 0,
                "message": "success",
                "data": data,
                "request_id": self._build_request_id(request_prefix),
            }
        )

    def _json_response(self, payload, *, status=200):
        return Response(
            json.dumps(payload, ensure_ascii=False),
            status=status,
            headers=[("Content-Type", "application/json; charset=utf-8")],
        )

    def _build_request_id(self, prefix):
        return f"{prefix}_{uuid.uuid4().hex[:12]}"
