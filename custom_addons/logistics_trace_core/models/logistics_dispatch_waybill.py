from odoo import _, api, fields, models


class LogisticsDispatchWaybill(models.Model):
    _inherit = "logistics.dispatch.waybill"

    trace_event_ids = fields.One2many(
        "logistics.trace.event",
        "waybill_id",
        string="Trace Events",
    )
    trace_count = fields.Integer(
        string="Trace Count",
        compute="_compute_trace_metrics",
        store=True,
        readonly=True,
    )
    latest_trace_time = fields.Datetime(
        string="Latest Trace Time",
        compute="_compute_trace_metrics",
        store=True,
        readonly=True,
    )
    latest_trace_type = fields.Char(
        string="Latest Trace Type",
        compute="_compute_trace_metrics",
        store=True,
        readonly=True,
    )
    latest_trace_summary = fields.Char(
        string="Latest Trace Summary",
        compute="_compute_trace_metrics",
        store=True,
        readonly=True,
    )
    arrive_trace_status = fields.Selection(
        [("pending", "Pending"), ("partial", "Partial"), ("done", "Done")],
        string="Arrival Trace",
        compute="_compute_trace_metrics",
        store=True,
        readonly=True,
    )
    signoff_trace_status = fields.Selection(
        [("pending", "Pending"), ("partial", "Partial"), ("done", "Done")],
        string="Signoff Trace",
        compute="_compute_trace_metrics",
        store=True,
        readonly=True,
    )

    @api.depends(
        "trace_event_ids",
        "trace_event_ids.trace_time",
        "trace_event_ids.event_type",
        "trace_event_ids.remark",
        "trace_event_ids.submit_user_name",
    )
    def _compute_trace_metrics(self):
        for record in self:
            events = record.trace_event_ids.sorted(
                key=lambda event: event.trace_time or event.create_date or fields.Datetime.now(),
                reverse=True,
            )
            latest = events[:1]
            latest_event = latest[0] if latest else False

            record.trace_count = len(events)
            record.latest_trace_time = latest_event.trace_time if latest_event else False
            record.latest_trace_type = latest_event.event_type if latest_event else False
            record.latest_trace_summary = latest_event.remark if latest_event else False

            event_types = set(events.mapped("event_type"))
            record.arrive_trace_status = "done" if "arrive_store" in event_types else "pending"
            record.signoff_trace_status = (
                "done" if {"deliver_finish", "signoff"} & event_types else "pending"
            )

    def action_open_trace_events(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Trace Events"),
            "res_model": "logistics.trace.event",
            "view_mode": "list,form",
            "domain": [("waybill_id", "=", self.id)],
            "context": {
                "default_waybill_id": self.id,
                "default_batch_id": self.batch_id.id,
                "default_object_type": "waybill",
            },
        }
