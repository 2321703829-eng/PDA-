from odoo import api, fields, models


class LogisticsDispatchWaybill(models.Model):
    _inherit = "logistics.dispatch.waybill"

    evidence_ids = fields.One2many(
        "logistics.trace.evidence",
        "waybill_id",
        string="留痕证据",
    )
    evidence_count = fields.Integer(
        string="证据数量",
        compute="_compute_evidence_metrics",
        store=True,
        readonly=True,
    )
    evidence_status = fields.Selection(
        [("missing", "Missing"), ("partial", "Partial"), ("complete", "Complete")],
        string="证据状态",
        compute="_compute_evidence_metrics",
        store=True,
        readonly=True,
    )
    latest_evidence_time = fields.Datetime(
        string="最新证据时间",
        compute="_compute_evidence_metrics",
        store=True,
        readonly=True,
    )
    latest_image_access_key = fields.Char(
        string="最新图片访问键",
        compute="_compute_evidence_metrics",
        store=True,
        readonly=True,
    )

    @api.depends(
        "trace_event_ids.evidence_ids",
        "trace_event_ids.evidence_ids.uploaded_at",
        "trace_event_ids.evidence_ids.image_access_key",
        "trace_event_ids.evidence_ids.image_ids.image_access_key",
        "trace_event_ids.state",
    )
    def _compute_evidence_metrics(self):
        for record in self:
            valid_events = record.trace_event_ids.filtered(lambda event: event.state == "submitted")
            evidences = valid_events.mapped("evidence_ids").sorted(
                key=lambda evidence: evidence.uploaded_at or fields.Datetime.now(),
                reverse=True,
            )
            latest_evidence = evidences[:1][0] if evidences else False

            record.evidence_count = len(evidences)
            record.latest_evidence_time = latest_evidence.uploaded_at if latest_evidence else False
            if latest_evidence:
                latest_image = latest_evidence._sorted_image_ids()[:1]
                latest_image = latest_image[0] if latest_image else False
                record.latest_image_access_key = (
                    latest_image.image_access_key if latest_image else latest_evidence.image_access_key or False
                )
            else:
                record.latest_image_access_key = False

            if record.evidence_count <= 0:
                record.evidence_status = "missing"
            elif record.evidence_count < max(record.trace_count or 1, 2):
                record.evidence_status = "partial"
            else:
                record.evidence_status = "complete"

    def action_open_evidences(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "运单证据",
            "res_model": "logistics.trace.evidence",
            "view_mode": "list,form",
            "domain": [("waybill_id", "=", self.id)],
            "context": {
                "default_waybill_id": self.id,
                "search_default_group_waybill": 1,
            },
        }
