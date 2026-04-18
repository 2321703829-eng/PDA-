from collections import defaultdict
from datetime import datetime, time, timedelta

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError


LOGISTICS_ANALYSIS_VIEW_GROUP = "logistics_web.group_logistics_analysis_viewer"
LOGISTICS_ANALYSIS_ACCESS_ERROR = "当前账号暂无查看物流分析中心的权限。"


class LogisticsDispatchWaybill(models.Model):
    _inherit = "logistics.dispatch.waybill"

    @api.model
    def get_stats_page_overview_payload(self, date_from=None, date_to=None, granularity="day"):
        self._ensure_logistics_analysis_access()
        date_from_value, date_to_value = self._get_stats_date_range(date_from=date_from, date_to=date_to)
        waybills = self._get_stats_waybills(date_from_value, date_to_value)
        exceptions = self._get_stats_exceptions(date_from_value, date_to_value)

        return {
            "summary": {
                "waybill_count": len(waybills),
                "signed_rate": self._safe_ratio(
                    len(waybills.filtered(lambda item: item.state in ("signed", "done"))),
                    len(waybills),
                ),
                "timeout_rate": self._safe_ratio(
                    len(waybills.filtered(self._is_timeout_waybill)),
                    len(waybills),
                ),
                "exception_count": len(exceptions),
            },
            "filters": {
                "date_from": fields.Date.to_string(date_from_value),
                "date_to": fields.Date.to_string(date_to_value),
                "granularity": granularity,
            },
            "groups": [
                {"group_code": "execution", "group_label": "执行概览"},
                {"group_code": "risk", "group_label": "风险概览"},
                {"group_code": "driver", "group_label": "司机与资源"},
                {"group_code": "region", "group_label": "区域与质量"},
            ],
        }

    @api.model
    def get_stats_trend_metrics_payload(self, metric_codes=None, date_from=None, date_to=None, granularity="day"):
        self._ensure_logistics_analysis_access()
        metric_codes = metric_codes or [
            "waybill_count",
            "signed_rate",
            "timeout_rate",
            "exception_count",
            "missing_evidence_rate",
            "missing_evidence_waybill_count",
        ]
        date_from_value, date_to_value = self._get_stats_date_range(date_from=date_from, date_to=date_to)
        buckets = self._build_stats_buckets(date_from_value, date_to_value, granularity)
        waybills = self._get_stats_waybills(date_from_value, date_to_value)
        exceptions = self._get_stats_exceptions(date_from_value, date_to_value)

        series = []
        for metric_code in metric_codes:
            points = []
            for bucket in buckets:
                bucket_waybills = waybills.filtered(
                    lambda item, item_bucket=bucket: item.delivery_date and item_bucket["date_from"] <= item.delivery_date <= item_bucket["date_to"]
                )
                bucket_exceptions = exceptions.filtered(
                    lambda item, item_bucket=bucket: item.report_time and item_bucket["datetime_from"] <= item.report_time <= item_bucket["datetime_to"]
                )
                value = self._compute_stats_trend_value(metric_code, bucket_waybills, bucket_exceptions)
                points.append(
                    {
                        "bucket": bucket["bucket"],
                        "label": bucket["label"],
                        "value": round(value, 4) if isinstance(value, float) else value,
                    }
                )
            series.append(
                {
                    "metric_code": metric_code,
                    "metric_label": self._get_stats_metric_label(metric_code),
                    "points": points,
                }
            )

        return {"series": series}

    @api.model
    def get_stats_distribution_metrics_payload(self, metric_codes=None, date_from=None, date_to=None):
        self._ensure_logistics_analysis_access()
        metric_codes = metric_codes or ["exception_type_distribution", "region_waybill_distribution"]
        date_from_value, date_to_value = self._get_stats_date_range(date_from=date_from, date_to=date_to)
        waybills = self._get_stats_waybills(date_from_value, date_to_value)
        exceptions = self._get_stats_exceptions(date_from_value, date_to_value)
        exception_type_labels = dict(self.env["logistics.trace.exception"]._fields["exception_type"].selection)

        datasets = []
        for metric_code in metric_codes:
            if metric_code == "exception_type_distribution":
                grouped = defaultdict(list)
                for exception in exceptions:
                    grouped[exception.exception_type or "other"].append(exception)
                items = [
                    {
                        "key": key,
                        "label": exception_type_labels.get(key, key),
                        "value": len(records),
                        "record_ids": [record.id for record in records],
                    }
                    for key, records in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0]))
                ]
            elif metric_code == "region_waybill_distribution":
                grouped = self._group_waybills_by_region(waybills)
                items = [
                    {
                        "key": key,
                        "label": key,
                        "value": len(records),
                        "record_ids": [record.id for record in records],
                    }
                    for key, records in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0]))
                ]
            else:
                items = []

            datasets.append(
                {
                    "metric_code": metric_code,
                    "metric_label": self._get_stats_metric_label(metric_code),
                    "items": items,
                }
            )

        return {"datasets": datasets}

    @api.model
    def get_stats_ranking_metrics_payload(self, metric_codes=None, date_from=None, date_to=None, limit=10):
        self._ensure_logistics_analysis_access()
        metric_codes = metric_codes or [
            "high_risk_batch_ranking",
            "driver_month_avg_exception_rate_ranking",
            "region_exception_rate_ranking",
            "region_signed_rate_ranking",
        ]
        date_from_value, date_to_value = self._get_stats_date_range(date_from=date_from, date_to=date_to)
        limit = min(max(int(limit or 10), 1), 20)
        waybills = self._get_stats_waybills(date_from_value, date_to_value)
        exceptions = self._get_stats_exceptions(date_from_value, date_to_value)

        datasets = []
        for metric_code in metric_codes:
            if metric_code == "high_risk_batch_ranking":
                items = self._get_high_risk_batch_ranking_items(waybills, exceptions, limit=limit)
            elif metric_code == "driver_month_avg_exception_rate_ranking":
                items = self._get_driver_exception_rate_ranking_items(waybills, date_from_value, date_to_value, limit=limit)
            elif metric_code == "region_exception_rate_ranking":
                items = self._get_region_rate_ranking_items(waybills, metric_code="exception", limit=limit)
            elif metric_code == "region_signed_rate_ranking":
                items = self._get_region_rate_ranking_items(waybills, metric_code="signed", limit=limit)
            else:
                items = []

            datasets.append(
                {
                    "metric_code": metric_code,
                    "metric_label": self._get_stats_metric_label(metric_code),
                    "items": items,
                }
            )

        return {"datasets": datasets}

    @api.model
    def _ensure_logistics_analysis_access(self):
        user = self.env.user
        if user.has_group("base.group_system") or user.has_group(LOGISTICS_ANALYSIS_VIEW_GROUP):
            return True
        raise AccessError(LOGISTICS_ANALYSIS_ACCESS_ERROR)

    @api.model
    def _get_stats_date_range(self, date_from=None, date_to=None):
        today = fields.Date.context_today(self)
        date_to_value = fields.Date.to_date(date_to) if date_to else today
        date_from_value = fields.Date.to_date(date_from) if date_from else (date_to_value - relativedelta(days=29))
        if date_from_value > date_to_value:
            date_from_value, date_to_value = date_to_value, date_from_value
        return date_from_value, date_to_value

    @api.model
    def _get_stats_waybills(self, date_from, date_to):
        return self.sudo().search(
            [
                ("delivery_date", ">=", date_from),
                ("delivery_date", "<=", date_to),
                ("state", "!=", "cancelled"),
            ],
            order="delivery_date asc, id asc",
        )

    @api.model
    def _get_stats_exceptions(self, date_from, date_to):
        return self.env["logistics.trace.exception"].sudo().search(
            [
                ("report_time", ">=", datetime.combine(date_from, time.min)),
                ("report_time", "<=", datetime.combine(date_to, time.max)),
                ("state", "!=", "cancelled"),
            ],
            order="report_time asc, id asc",
        )

    @api.model
    def _build_stats_buckets(self, date_from, date_to, granularity):
        buckets = []
        granularity = granularity if granularity in ("day", "week", "month") else "day"
        if granularity == "month":
            cursor = date_from.replace(day=1)
            end = date_to.replace(day=1)
            while cursor <= end:
                bucket_end = cursor + relativedelta(months=1, days=-1)
                buckets.append(
                    self._build_stats_bucket(
                        bucket=cursor.strftime("%Y-%m"),
                        label=cursor.strftime("%Y-%m"),
                        date_from=max(cursor, date_from),
                        date_to=min(bucket_end, date_to),
                    )
                )
                cursor += relativedelta(months=1)
            return buckets

        if granularity == "week":
            cursor = date_from - timedelta(days=date_from.weekday())
            while cursor <= date_to:
                bucket_end = cursor + timedelta(days=6)
                buckets.append(
                    self._build_stats_bucket(
                        bucket=f"{cursor.strftime('%Y-%m-%d')}~{bucket_end.strftime('%Y-%m-%d')}",
                        label=f"{cursor.strftime('%m-%d')}~{bucket_end.strftime('%m-%d')}",
                        date_from=max(cursor, date_from),
                        date_to=min(bucket_end, date_to),
                    )
                )
                cursor += timedelta(days=7)
            return buckets

        cursor = date_from
        while cursor <= date_to:
            buckets.append(
                self._build_stats_bucket(
                    bucket=fields.Date.to_string(cursor),
                    label=cursor.strftime("%m-%d"),
                    date_from=cursor,
                    date_to=cursor,
                )
            )
            cursor += timedelta(days=1)
        return buckets

    @api.model
    def _build_stats_bucket(self, bucket, label, date_from, date_to):
        return {
            "bucket": bucket,
            "label": label,
            "date_from": date_from,
            "date_to": date_to,
            "datetime_from": datetime.combine(date_from, time.min),
            "datetime_to": datetime.combine(date_to, time.max),
        }

    @api.model
    def _compute_stats_trend_value(self, metric_code, waybills, exceptions):
        total_waybills = len(waybills)
        if metric_code == "waybill_count":
            return total_waybills
        if metric_code == "signed_rate":
            return self._safe_ratio(
                len(waybills.filtered(lambda item: item.state in ("signed", "done"))),
                total_waybills,
            )
        if metric_code == "timeout_rate":
            return self._safe_ratio(
                len(waybills.filtered(self._is_timeout_waybill)),
                total_waybills,
            )
        if metric_code == "exception_count":
            return len(exceptions)
        if metric_code == "missing_evidence_rate":
            return self._safe_ratio(
                len(waybills.filtered(lambda item: item.evidence_status in ("missing", "partial"))),
                total_waybills,
            )
        if metric_code == "missing_evidence_waybill_count":
            return len(waybills.filtered(lambda item: item.evidence_status in ("missing", "partial")))
        return 0

    @api.model
    def _group_waybills_by_region(self, waybills):
        grouped = defaultdict(list)
        for waybill in waybills:
            region = self._get_store_region(waybill.store_id) or "未标记区域"
            grouped[region].append(waybill)
        return grouped

    @api.model
    def _get_high_risk_batch_ranking_items(self, waybills, exceptions, limit=10):
        grouped_waybills = defaultdict(list)
        for waybill in waybills.filtered(lambda item: item.batch_id):
            grouped_waybills[waybill.batch_id.id].append(waybill)

        severe_exception_ids_by_batch = defaultdict(list)
        for exception in exceptions.filtered(lambda item: item.batch_id and item.severity_level in ("high", "critical")):
            severe_exception_ids_by_batch[exception.batch_id.id].append(exception.id)

        ranked = []
        for batch_id, records in grouped_waybills.items():
            batch = records[0].batch_id
            total_count = len(records)
            exception_waybills = [record for record in records if record.exception_status in ("open", "processing", "closed")]
            timeout_waybills = [record for record in records if self._is_timeout_waybill(record)]
            ranked.append(
                {
                    "entity_id": batch.id,
                    "entity_type": "batch",
                    "label": batch.name,
                    "primary_value": self._safe_ratio(len(exception_waybills), total_count),
                    "secondary_value": len(severe_exception_ids_by_batch.get(batch.id, [])),
                    "tertiary_value": len(timeout_waybills),
                    "record_ids": [record.id for record in records],
                }
            )

        ranked.sort(
            key=lambda item: (
                item["primary_value"],
                item["secondary_value"],
                item["tertiary_value"],
                item["entity_id"],
            ),
            reverse=True,
        )
        return ranked[:limit]

    @api.model
    def _get_driver_exception_rate_ranking_items(self, waybills, date_from, date_to, limit=10):
        grouped = defaultdict(list)
        for waybill in waybills.filtered(lambda item: item.driver_employee_id):
            grouped[waybill.driver_employee_id.id].append(waybill)

        buckets = self._build_stats_buckets(date_from, date_to, "month")
        ranked = []
        for driver_id, records in grouped.items():
            driver = records[0].driver_employee_id
            rates = []
            for bucket in buckets:
                bucket_records = [
                    record
                    for record in records
                    if record.delivery_date and bucket["date_from"] <= record.delivery_date <= bucket["date_to"]
                ]
                if not bucket_records:
                    continue
                exception_waybill_count = len(
                    [record for record in bucket_records if record.exception_status in ("open", "processing", "closed")]
                )
                rates.append(self._safe_ratio(exception_waybill_count, len(bucket_records)))

            if not rates:
                continue
            ranked.append(
                {
                    "entity_id": driver.id,
                    "entity_type": "driver",
                    "label": driver.name,
                    "primary_value": round(sum(rates) / len(rates), 4),
                    "secondary_value": len(records),
                }
            )

        ranked.sort(key=lambda item: (item["primary_value"], item["secondary_value"], item["entity_id"]), reverse=True)
        return ranked[:limit]

    @api.model
    def _get_region_rate_ranking_items(self, waybills, metric_code="exception", limit=10):
        grouped = self._group_waybills_by_region(waybills)
        ranked = []
        for region, records in grouped.items():
            total_count = len(records)
            if not total_count:
                continue
            if metric_code == "signed":
                primary_value = self._safe_ratio(
                    len([record for record in records if record.state in ("signed", "done")]),
                    total_count,
                )
            else:
                primary_value = self._safe_ratio(
                    len([record for record in records if record.exception_status in ("open", "processing", "closed")]),
                    total_count,
                )
            ranked.append(
                {
                    "entity_id": region,
                    "entity_type": "region",
                    "label": region,
                    "primary_value": primary_value,
                    "secondary_value": total_count,
                    "record_ids": [record.id for record in records],
                }
            )

        ranked.sort(key=lambda item: (item["primary_value"], item["secondary_value"], item["label"]), reverse=True)
        return ranked[:limit]

    @api.model
    def _get_stats_metric_label(self, metric_code):
        mapping = {
            "waybill_count": "运单量趋势",
            "signed_rate": "签收率",
            "timeout_rate": "超时率",
            "exception_count": "异常总量趋势",
            "missing_evidence_rate": "缺凭证率",
            "missing_evidence_waybill_count": "缺凭证运单数",
            "exception_type_distribution": "异常类型分布",
            "region_waybill_distribution": "区域运单量分布",
            "high_risk_batch_ranking": "高风险批次排行",
            "driver_month_avg_exception_rate_ranking": "司机月均异常率排行",
            "region_exception_rate_ranking": "区域异常率排行",
            "region_signed_rate_ranking": "区域签收率对比",
        }
        return mapping.get(metric_code, metric_code)

    @api.model
    def _get_store_region(self, store):
        if not store:
            return ""
        return store.state_id.name or store.city or store.parent_id.name or ""

    @api.model
    def _is_timeout_waybill(self, waybill):
        today = fields.Date.context_today(self)
        return bool(
            waybill.delivery_date
            and waybill.delivery_date < today
            and waybill.state not in ("signed", "done", "cancelled")
        )

    @api.model
    def _safe_ratio(self, numerator, denominator):
        if not denominator:
            return 0
        return round(numerator / denominator, 4)
