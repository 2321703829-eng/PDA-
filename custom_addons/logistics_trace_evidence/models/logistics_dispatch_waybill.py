from odoo import api, fields, models


class LogisticsDispatchWaybill(models.Model):
    _inherit = "logistics.dispatch.waybill"

    evidence_ids = fields.One2many(
        "logistics.trace.evidence",
        "waybill_id",
        string="Evidence Items",
    )
    evidence_count = fields.Integer(
        string="Evidence Count",
        compute="_compute_evidence_metrics",
        store=True,
        readonly=True,
    )
    evidence_status = fields.Selection(
        [("missing", "Missing"), ("partial", "Partial"), ("complete", "Complete")],
        string="Evidence Status",
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
