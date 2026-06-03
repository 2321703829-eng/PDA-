import json
import uuid

from odoo import http
from odoo.exceptions import AccessError, ValidationError
from odoo.http import Response, request


class LogisticsWebVehicleController(http.Controller):
    @http.route("/api/admin/logistics/vehicles/<int:vehicle_id>/profile", type="http", auth="user", methods=["GET"])
    def get_vehicle_profile(self, vehicle_id, **kwargs):
        return self._handle_payload(
            "req_vehicle_profile",
            lambda service: service.get_vehicle_profile_overview_payload(vehicle_id),
        )

    @http.route("/api/admin/logistics/vehicles/<int:vehicle_id>/kpis", type="http", auth="user", methods=["GET"])
    def get_vehicle_kpis(self, vehicle_id, **kwargs):
        return self._handle_payload(
            "req_vehicle_kpis",
            lambda service: service.get_vehicle_kpi_cards_payload(vehicle_id),
        )

    @http.route("/api/admin/logistics/vehicles/<int:vehicle_id>/risk-summary", type="http", auth="user", methods=["GET"])
    def get_vehicle_risk_summary(self, vehicle_id, **kwargs):
        return self._handle_payload(
            "req_vehicle_risk_summary",
            lambda service: service.get_vehicle_risk_summary_payload(vehicle_id),
        )

    @http.route("/api/admin/logistics/vehicles/<int:vehicle_id>/trends", type="http", auth="user", methods=["GET"])
    def get_vehicle_trends(self, vehicle_id, **kwargs):
        payload = self._merged_payload()
        metric_codes = payload.get("metric_codes") or ""
        if isinstance(metric_codes, str):
            metric_codes = [item.strip() for item in metric_codes.split(",") if item.strip()]
        return self._handle_payload(
            "req_vehicle_trends",
            lambda service: service.get_vehicle_trend_metrics_payload(
                vehicle_id,
                metric_codes=metric_codes,
                date_from=payload.get("date_from"),
                date_to=payload.get("date_to"),
            ),
        )

    @http.route("/api/admin/logistics/vehicles/<int:vehicle_id>/recent-waybills", type="http", auth="user", methods=["GET"])
    def get_vehicle_recent_waybills(self, vehicle_id, **kwargs):
        return self._handle_payload(
            "req_vehicle_recent_waybills",
            lambda service: service.get_vehicle_recent_waybills_payload(vehicle_id),
        )

    @http.route("/api/admin/logistics/vehicles/<int:vehicle_id>/recent-exceptions", type="http", auth="user", methods=["GET"])
    def get_vehicle_recent_exceptions(self, vehicle_id, **kwargs):
        return self._handle_payload(
            "req_vehicle_recent_exceptions",
            lambda service: service.get_vehicle_recent_exceptions_payload(vehicle_id),
        )

    def _handle_payload(self, request_prefix, callback):
        service = request.env["logistics.dispatch.waybill"]
        try:
            data = callback(service)
        except AccessError as exc:
            return self._json_response(
                {
                    "code": 4003,
                    "message": "forbidden",
                    "data": {"errors": [{"error_code": "VEHICLE_ACCESS_FORBIDDEN", "error_message": str(exc)}]},
                    "request_id": self._build_request_id(request_prefix),
                },
                status=403,
            )
        except (ValidationError, ValueError, TypeError) as exc:
            return self._json_response(
                {
                    "code": 4001,
                    "message": "bad_request",
                    "data": {"errors": [{"error_code": "VEHICLE_BAD_REQUEST", "error_message": str(exc)}]},
                    "request_id": self._build_request_id(request_prefix),
                },
                status=400,
            )

        return self._json_response(
            {
                "code": 0,
                "message": "success",
                "data": data,
                "request_id": self._build_request_id(request_prefix),
            }
        )

    def _merged_payload(self):
        payload = dict(request.params)
        if request.httprequest.mimetype == "application/json":
            json_payload = request.httprequest.get_json(silent=True) or {}
            if isinstance(json_payload, dict):
                payload.update({key: value for key, value in json_payload.items() if value is not None})
        return payload

    def _json_response(self, payload, *, status=200):
        return Response(
            json.dumps(payload, ensure_ascii=False),
            status=status,
            headers=[("Content-Type", "application/json; charset=utf-8")],
        )

    def _build_request_id(self, prefix):
        return f"{prefix}_{uuid.uuid4().hex[:12]}"
