from odoo import api, fields, models


class LogisticsDispatchWaybill(models.Model):
    _inherit = "logistics.dispatch.waybill"

    evidence_ids = fields.One2many(
        "logistics.trace.evidence",
        "waybill_id",
        string="证据项",
    )
    evidence_count = fields.Integer(
        string="证据数",
        compute="_compute_evidence_metrics",
        store=True,
        readonly=True,
    )
    evidence_status = fields.Selection(
        [("missing", "待补充"), ("partial", "部分齐全"), ("complete", "已齐全")],
        string="证据状态",
        compute="_compute_evidence_metrics",
        store=True,
        readonly=True,
    )

    @api.depends("trace_event_ids.evidence_ids")
    def _compute_evidence_metrics(self):
        for record in self:
            evidence_count = len(record.trace_event_ids.mapped("evidence_ids"))
            record.evidence_count = evidence_count
            if evidence_count <= 0:
                record.evidence_status = "missing"
            elif evidence_count < max(record.trace_count or 1, 2):
                record.evidence_status = "partial"
            else:
                record.evidence_status = "complete"
