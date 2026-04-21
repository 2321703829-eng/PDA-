from odoo import api, fields, models


class LogisticsTraceExceptionProcessLog(models.Model):
    _name = "logistics.trace.exception.process.log"
    _description = "异常处理日志"
    _order = "action_time desc, id desc"

    ACTION_SELECTION = [
        ("create", "新建"),
        ("state_change", "状态变更"),
        ("note", "备注"),
    ]

    exception_id = fields.Many2one(
        "logistics.trace.exception",
        string="异常",
        required=True,
        ondelete="cascade",
        index=True,
    )
    action_type = fields.Selection(
        ACTION_SELECTION,
        string="操作类型",
        required=True,
        default="note",
    )
    operator_id = fields.Many2one(
        "res.users",
        string="操作人",
        default=lambda self: self.env.user,
    )
    operator_name = fields.Char(
        string="操作人姓名",
        compute="_compute_operator_name",
        store=True,
    )
    action_time = fields.Datetime(
        string="操作时间",
        required=True,
        default=fields.Datetime.now,
        index=True,
    )
    from_state = fields.Char(string="原状态")
    to_state = fields.Char(string="新状态")
    note = fields.Text(string="备注")

    @api.depends("operator_id")
    def _compute_operator_name(self):
        for record in self:
            record.operator_name = record.operator_id.name or ""
