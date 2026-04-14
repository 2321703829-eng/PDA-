from odoo import api, fields, models


class LogisticsTraceExceptionProcessLog(models.Model):
    _name = "logistics.trace.exception.process.log"
    _description = "Logistics Trace Exception Process Log"
    _order = "action_time desc, id desc"

    ACTION_SELECTION = [
        ("create", "Create"),
        ("state_change", "State Change"),
        ("note", "Note"),
    ]

    exception_id = fields.Many2one(
        "logistics.trace.exception",
        string="Exception",
        required=True,
        ondelete="cascade",
        index=True,
    )
    action_type = fields.Selection(
        ACTION_SELECTION,
        string="Action Type",
        required=True,
        default="note",
    )
    operator_id = fields.Many2one(
        "res.users",
        string="Operator",
        default=lambda self: self.env.user,
    )
    operator_name = fields.Char(
        string="Operator Name",
        compute="_compute_operator_name",
        store=True,
    )
    action_time = fields.Datetime(
        string="Action Time",
        required=True,
        default=fields.Datetime.now,
        index=True,
    )
    from_state = fields.Char(string="From State")
    to_state = fields.Char(string="To State")
    note = fields.Text(string="Note")

    @api.depends("operator_id")
    def _compute_operator_name(self):
        for record in self:
            record.operator_name = record.operator_id.name or ""
