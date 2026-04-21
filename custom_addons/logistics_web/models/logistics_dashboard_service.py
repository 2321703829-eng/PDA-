from datetime import datetime, time

from odoo import _, api, fields, models
from odoo.exceptions import AccessError


LOGISTICS_ANALYSIS_VIEW_GROUP = "logistics_web.group_logistics_analysis_viewer"
LOGISTICS_ANALYSIS_ACCESS_ERROR = "当前账号暂无查看物流分析中心的权限。"


class LogisticsTraceException(models.Model):
    _inherit = "logistics.trace.exception"

    @api.model
    def get_dashboard_summary_payload(self):
        self._ensure_logistics_analysis_access()
        exception_model = self.sudo()
        now = fields.Datetime.context_timestamp(self, fields.Datetime.now())
        today_start = datetime.combine(now.date(), time.min)
        today_end = datetime.combine(now.date(), time.max)
        open_domain = [("state", "in", ["open", "processing"])]
        exception_domain = [("state", "in", ["open", "processing", "resolved"])]
        pending_exceptions = exception_model.search(open_domain, order="report_time desc, id desc")
        evidence_missing_exceptions = exception_model.search(
            [("state", "in", ["open", "processing"]), ("exception_type", "=", "evidence_missing")],
            order="report_time desc, id desc",
        )
        today_exceptions = exception_model.search(
            [("report_time", ">=", today_start), ("report_time", "<=", today_end)],
            order="report_time desc, id desc",
        )
        high_risk_batch_ids = list(
            dict.fromkeys(
                exception_model.search(
                    exception_domain + [("severity_level", "in", ["high", "critical"]), ("batch_id", "!=", False)]
                ).mapped("batch_id.id")
            )
        )
        pending_exception_count = len(pending_exceptions)
        evidence_missing_count = len(evidence_missing_exceptions)
        today_new_exception_count = len(today_exceptions)
        high_risk_batch_count = len(high_risk_batch_ids)
        priority_exceptions = exception_model.search(
            open_domain,
            order="is_overdue desc, report_time desc, id desc",
            limit=5,
        )
        recent_exceptions = exception_model.search([], order="report_time desc, id desc", limit=5)

        return {
            "summary_cards": [
                {
                    "key": "pending_exception_count",
                    "label": _("待处理异常"),
                    "value": pending_exception_count,
                    "tone": "danger" if pending_exception_count else "default",
                    "record_ids": pending_exceptions.ids,
                },
                {
                    "key": "evidence_missing_count",
                    "label": _("待补证据"),
                    "value": evidence_missing_count,
                    "tone": "warning" if evidence_missing_count else "default",
                    "record_ids": evidence_missing_exceptions.ids,
                },
                {
                    "key": "high_risk_batch_count",
                    "label": _("风险批次"),
                    "value": high_risk_batch_count,
                    "tone": "danger" if high_risk_batch_count else "default",
                    "record_ids": high_risk_batch_ids,
                },
                {
                    "key": "today_new_exception_count",
                    "label": _("今日新增"),
                    "value": today_new_exception_count,
                    "tone": "info" if today_new_exception_count else "default",
                    "record_ids": today_exceptions.ids,
                },
            ],
            "priority_items": [
                {
                    "key": exception.name,
                    "code": exception.name,
                    "title": self._build_exception_title(exception),
                    "status": exception.state,
                    "targetType": "exception",
                    "owner": exception.process_owner_name or exception.reporter_user_name or _("未分配"),
                    "hint": self._build_exception_hint(exception),
                }
                for exception in priority_exceptions
            ],
            "recent_changes": [
                {
                    "key": f"exception_{exception.id}",
                    "time": fields.Datetime.to_string(exception.report_time or fields.Datetime.now())[11:16],
                    "title": self._build_recent_exception_title(exception),
                    "summary": self._build_exception_hint(exception),
                }
                for exception in recent_exceptions
            ],
        }

    @api.model
    def get_boss_trace_summary_payload(self):
        self._ensure_logistics_analysis_access()
        exception_model = self.sudo()
        now = fields.Datetime.context_timestamp(self, fields.Datetime.now())
        today_start = datetime.combine(now.date(), time.min)
        today_end = datetime.combine(now.date(), time.max)
        open_domain = [("state", "in", ["open", "processing"])]

        open_disputes = exception_model.search_count(open_domain)
        critical_disputes = exception_model.search_count(open_domain + [("severity_level", "=", "critical")])
        high_risk_batches = len(
            set(
                exception_model.search(
                    open_domain + [("severity_level", "in", ["high", "critical"]), ("batch_id", "!=", False)]
                ).mapped("batch_id.id")
            )
        )
        evidence_missing = exception_model.search_count(
            open_domain + [("exception_type", "=", "evidence_missing")]
        )
        today_new = exception_model.search_count(
            [("report_time", ">=", today_start), ("report_time", "<=", today_end)]
        )
        focus_exceptions = exception_model.search(
            open_domain,
            order="severity_level desc, is_overdue desc, report_time desc, id desc",
            limit=6,
        )

        return {
            "headline_cards": [
                {
                    "key": "open_exceptions",
                    "label": _("待处理异常"),
                    "value": open_disputes,
                    "tone": "danger" if open_disputes else "default",
                },
                {
                    "key": "high_risk_batches",
                    "label": _("高风险批次"),
                    "value": high_risk_batches,
                    "tone": "warning" if high_risk_batches else "default",
                },
                {
                    "key": "critical_exceptions",
                    "label": _("严重异常"),
                    "value": critical_disputes,
                    "tone": "danger" if critical_disputes else "default",
                },
                {
                    "key": "evidence_missing",
                    "label": _("证据缺失"),
                    "value": evidence_missing,
                    "tone": "warning" if evidence_missing else "default",
                },
                {
                    "key": "today_new",
                    "label": _("今日新增"),
                    "value": today_new,
                    "tone": "info" if today_new else "default",
                },
            ],
            "focus_objects": [
                {
                    "key": exception.name,
                    "code": exception.name,
                    "exception_id": exception.id,
                    "waybill_id": exception.waybill_id.id or False,
                    "batch_id": exception.batch_id.id or False,
                    "title": self._build_exception_title(exception),
                    "severity": exception.severity_level,
                    "state": exception.state,
                    "owner": exception.process_owner_name or exception.reporter_user_name or _("未分配"),
                    "waybill": exception.waybill_id.name or "",
                    "batch": exception.batch_id.name or "",
                    "hint": self._build_exception_hint(exception),
                }
                for exception in focus_exceptions
            ],
        }

    @api.model
    def _ensure_logistics_analysis_access(self):
        user = self.env.user
        if user.has_group("base.group_system") or user.has_group(LOGISTICS_ANALYSIS_VIEW_GROUP):
            return True
        raise AccessError(LOGISTICS_ANALYSIS_ACCESS_ERROR)

    def _build_exception_title(self, exception):
        waybill_name = exception.waybill_id.name or _("未知运单")
        exception_type = dict(exception._fields["exception_type"].selection).get(
            exception.exception_type,
            exception.exception_type or _("异常"),
        )
        return _("%(waybill_name)s发生%(exception_type)s") % {
            "exception_type": exception_type,
            "waybill_name": waybill_name,
        }

    def _build_recent_exception_title(self, exception):
        severity_label = dict(exception._fields["severity_level"].selection).get(
            exception.severity_level,
            exception.severity_level or _("未知"),
        )
        return _("%(severity_label)s异常已更新") % {"severity_label": severity_label}

    def _build_exception_hint(self, exception):
        parts = []
        if exception.waybill_id:
            parts.append(_("运单 %(name)s") % {"name": exception.waybill_id.name})
        if exception.batch_id:
            parts.append(_("批次 %(name)s") % {"name": exception.batch_id.name})
        if exception.trace_event_id:
            parts.append(_("留痕 %(name)s") % {"name": exception.trace_event_id.name})
        if exception.description:
            parts.append(exception.description[:120])
        return " | ".join(parts) or _("可在异常记录中查看详情。")
