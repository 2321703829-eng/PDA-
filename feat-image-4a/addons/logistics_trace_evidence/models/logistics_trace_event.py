from odoo import api, fields, models


class LogisticsTraceEvent(models.Model):
    _inherit = "logistics.trace.event"

    evidence_ids = fields.One2many(
        "logistics.trace.evidence",
        "trace_id",
        string="Evidence",
    )
    evidence_count = fields.Integer(compute="_compute_evidence_count")

    @api.depends("evidence_ids")
    def _compute_evidence_count(self):
        for record in self:
            record.evidence_count = len(record.evidence_ids)
