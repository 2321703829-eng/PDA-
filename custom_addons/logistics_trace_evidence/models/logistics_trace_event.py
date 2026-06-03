from odoo import api, fields, models


class LogisticsTraceEvent(models.Model):
    _inherit = "logistics.trace.event"

    evidence_ids = fields.One2many(
        "logistics.trace.evidence",
        "trace_event_id",
        string="证据记录",
    )
    evidence_count = fields.Integer(
        string="证据数",
        compute="_compute_evidence_count",
        store=True,
        readonly=True,
    )

    @api.depends("evidence_ids")
    def _compute_evidence_count(self):
        for record in self:
            record.evidence_count = len(record.evidence_ids)

    def action_back_to_evidences(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "logistics_trace_evidence.action_logistics_trace_evidence"
        )
        action["target"] = "current"
        action["domain"] = [("trace_event_id", "=", self.id)]
        return action
