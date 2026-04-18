import json
import uuid

from odoo import http
from odoo.exceptions import AccessError, ValidationError
from odoo.http import Response, request


class LogisticsWebDriverController(http.Controller):
    @http.route("/api/admin/logistics/drivers/<int:driver_id>/profile", type="http", auth="user", methods=["GET"])
    def get_driver_profile(self, driver_id, **kwargs):
        return self._handle_payload(
            "req_driver_profile",
            lambda service: service.get_driver_profile_overview_payload(driver_id),
        )

    @http.route("/api/admin/logistics/drivers/<int:driver_id>/kpis", type="http", auth="user", methods=["GET"])
    def get_driver_kpis(self, driver_id, **kwargs):
        return self._handle_payload(
            "req_driver_kpis",
            lambda service: service.get_driver_kpi_cards_payload(driver_id),
        )

    @http.route("/api/admin/logistics/drivers/<int:driver_id>/risk-summary", type="http", auth="user", methods=["GET"])
    def get_driver_risk_summary(self, driver_id, **kwargs):
        return self._handle_payload(
            "req_driver_risk_summary",
            lambda service: service.get_driver_risk_summary_payload(driver_id),
        )

    @http.route("/api/admin/logistics/drivers/<int:driver_id>/trends", type="http", auth="user", methods=["GET"])
    def get_driver_trends(self, driver_id, **kwargs):
        payload = self._merged_payload()
        metric_codes = payload.get("metric_codes") or ""
        if isinstance(metric_codes, str):
            metric_codes = [item.strip() for item in metric_codes.split(",") if item.strip()]
        return self._handle_payload(
            "req_driver_trends",
            lambda service: service.get_driver_trend_metrics_payload(
                driver_id,
                metric_codes=metric_codes,
                date_from=payload.get("date_from"),
                date_to=payload.get("date_to"),
            ),
        )

    @http.route("/api/admin/logistics/drivers/<int:driver_id>/recent-waybills", type="http", auth="user", methods=["GET"])
    def get_driver_recent_waybills(self, driver_id, **kwargs):
        return self._handle_payload(
            "req_driver_recent_waybills",
            lambda service: service.get_driver_recent_waybills_payload(driver_id),
        )

    @http.route("/api/admin/logistics/drivers/<int:driver_id>/recent-exceptions", type="http", auth="user", methods=["GET"])
    def get_driver_recent_exceptions(self, driver_id, **kwargs):
        return self._handle_payload(
            "req_driver_recent_exceptions",
            lambda service: service.get_driver_recent_exceptions_payload(driver_id),
        )

    @http.route(
        "/api/admin/logistics/drivers/<int:driver_id>/waybills/drilldown",
        type="http",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def get_driver_waybill_drilldown(self, driver_id, **kwargs):
        payload = self._merged_payload()
        return self._handle_payload(
            "req_driver_waybill_drilldown",
            lambda service: service.get_driver_waybill_drilldown_payload(
                driver_id,
                metric_code=payload.get("metric_code"),
                bucket=payload.get("bucket"),
                page=payload.get("page"),
                page_size=payload.get("page_size"),
            ),
        )

    @http.route(
        "/api/admin/logistics/drivers/<int:driver_id>/exceptions/drilldown",
        type="http",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def get_driver_exception_drilldown(self, driver_id, **kwargs):
        payload = self._merged_payload()
        return self._handle_payload(
            "req_driver_exception_drilldown",
            lambda service: service.get_driver_exception_drilldown_payload(
                driver_id,
                metric_code=payload.get("metric_code"),
                bucket=payload.get("bucket"),
                page=payload.get("page"),
                page_size=payload.get("page_size"),
                exception_type=payload.get("exception_type"),
                severity_levels=payload.get("severity_levels"),
            ),
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
                    "data": {"errors": [{"error_code": "DRIVER_ACCESS_FORBIDDEN", "error_message": str(exc)}]},
                    "request_id": self._build_request_id(request_prefix),
                },
                status=403,
            )
        except ValidationError as exc:
            return self._json_response(
                {
                    "code": 1,
                    "message": "request_failed",
                    "data": {"errors": [{"error_code": "DRIVER_REQUEST_FAILED", "error_message": str(exc)}]},
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
