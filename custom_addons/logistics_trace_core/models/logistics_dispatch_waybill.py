from odoo import _, api, fields, models


class LogisticsDispatchWaybill(models.Model):
    _inherit = "logistics.dispatch.waybill"

    TRACE_STATE_RANK = {
        "draft": 0,
        "ready": 1,
        "in_transit": 2,
        "arrived": 3,
        "signed": 4,
        "done": 5,
        "cancelled": 99,
    }

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
        string="Arrive Trace Status",
        compute="_compute_trace_metrics",
        store=True,
        readonly=True,
    )
    signoff_trace_status = fields.Selection(
        [("pending", "Pending"), ("partial", "Partial"), ("done", "Done")],
        string="Signoff Trace Status",
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
        "trace_event_ids.state",
    )
    def _compute_trace_metrics(self):
        for record in self:
            events = record.trace_event_ids.filtered(lambda event: event.state == "submitted").sorted(
                key=lambda event: event.trace_time or event.create_date or fields.Datetime.now(),
                reverse=True,
            )
            latest_event = events[:1][0] if events else False

            record.trace_count = len(events)
            record.latest_trace_time = latest_event.trace_time if latest_event else False
            record.latest_trace_type = latest_event.event_type if latest_event else False
            record.latest_trace_summary = latest_event.remark if latest_event else False

            event_types = set(events.mapped("event_type"))
            if "arrive_store" in event_types:
                record.arrive_trace_status = "done"
            elif events:
                record.arrive_trace_status = "partial"
            else:
                record.arrive_trace_status = "pending"

            if {"deliver_finish", "signoff"} & event_types:
                record.signoff_trace_status = "done"
            elif events:
                record.signoff_trace_status = "partial"
            else:
                record.signoff_trace_status = "pending"

    def _get_trace_driven_dispatch_state(self):
        self.ensure_one()
        events = self.trace_event_ids.filtered(lambda event: event.state == "submitted")
        event_types = set(events.mapped("event_type"))
        if {"deliver_finish", "signoff"} & event_types:
            return "done"
        if "arrive_store" in event_types:
            return "arrived"
        if events:
            return "in_transit"
        return False

    def _sync_dispatch_state_from_trace(self):
        for record in self:
            if record.state == "cancelled":
                continue
            target_state = record._get_trace_driven_dispatch_state()
            if not target_state:
                continue
            current_rank = self.TRACE_STATE_RANK.get(record.state, 0)
            target_rank = self.TRACE_STATE_RANK.get(target_state, 0)
            if target_rank > current_rank:
                super(LogisticsDispatchWaybill, record.sudo()).write({"state": target_state})

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
