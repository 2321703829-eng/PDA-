from odoo import fields, models


class LogisticsDispatchWaybill(models.Model):
    _inherit = "logistics.dispatch.waybill"

    trace_timeline_panel = fields.Char(
        string="Trace Timeline Panel",
        compute="_compute_ui_panels",
        readonly=True,
    )
    evidence_viewer_panel = fields.Char(
        string="Evidence Viewer Panel",
        compute="_compute_ui_panels",
        readonly=True,
    )

    def _compute_ui_panels(self):
        for record in self:
            record.trace_timeline_panel = ""
            record.evidence_viewer_panel = ""
