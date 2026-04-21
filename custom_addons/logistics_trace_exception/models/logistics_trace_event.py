from odoo import api, fields, models


class LogisticsTraceEvent(models.Model):
    _inherit = "logistics.trace.event"

    exception_ids = fields.One2many(
        "logistics.trace.exception",
        "trace_event_id",
        string="异常记录",
    )
    open_exception_count = fields.Integer(
        string="待处理异常数",
        compute="_compute_open_exception_count",
        store=True,
        readonly=True,
    )
    is_exception = fields.Boolean(
        string="异常事件",
        compute="_compute_is_exception",
        store=True,
        readonly=True,
    )

    @api.depends("exception_ids.state")
    def _compute_open_exception_count(self):
        for record in self:
            record.open_exception_count = len(
                record.exception_ids.filtered(lambda exc: exc.state in ("open", "processing"))
            )

    @api.depends("exception_ids")
    def _compute_is_exception(self):
        for record in self:
            record.is_exception = bool(record.exception_ids)
