import json
import uuid

from odoo import http
from odoo.exceptions import AccessError
from odoo.http import Response, request


class LogisticsWebStatsController(http.Controller):
    @http.route("/api/admin/logistics/stats/overview", type="http", auth="user", methods=["GET"])
    def get_stats_overview(self, **kwargs):
        payload = self._merged_payload()
        return self._handle_payload(
            "req_stats_overview",
            lambda service: service.get_stats_page_overview_payload(
                date_from=payload.get("date_from"),
                date_to=payload.get("date_to"),
                granularity=payload.get("granularity"),
            ),
        )

    @http.route("/api/admin/logistics/stats/trends", type="http", auth="user", methods=["GET"])
    def get_stats_trends(self, **kwargs):
        payload = self._merged_payload()
        metric_codes = self._normalize_metric_codes(payload.get("metric_codes"))
        return self._handle_payload(
            "req_stats_trends",
            lambda service: service.get_stats_trend_metrics_payload(
                metric_codes=metric_codes,
                date_from=payload.get("date_from"),
                date_to=payload.get("date_to"),
                granularity=payload.get("granularity"),
            ),
        )

    @http.route("/api/admin/logistics/stats/distributions", type="http", auth="user", methods=["GET"])
    def get_stats_distributions(self, **kwargs):
        payload = self._merged_payload()
        metric_codes = self._normalize_metric_codes(payload.get("metric_codes"))
        return self._handle_payload(
            "req_stats_distributions",
            lambda service: service.get_stats_distribution_metrics_payload(
                metric_codes=metric_codes,
                date_from=payload.get("date_from"),
                date_to=payload.get("date_to"),
            ),
        )

    @http.route("/api/admin/logistics/stats/rankings", type="http", auth="user", methods=["GET"])
    def get_stats_rankings(self, **kwargs):
        payload = self._merged_payload()
        metric_codes = self._normalize_metric_codes(payload.get("metric_codes"))
        return self._handle_payload(
            "req_stats_rankings",
            lambda service: service.get_stats_ranking_metrics_payload(
                metric_codes=metric_codes,
                date_from=payload.get("date_from"),
                date_to=payload.get("date_to"),
                limit=payload.get("limit"),
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

    def _normalize_metric_codes(self, metric_codes):
        if isinstance(metric_codes, str):
            return [item.strip() for item in metric_codes.split(",") if item.strip()]
        if isinstance(metric_codes, list):
            return [item for item in metric_codes if item]
        return []

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
