from odoo import fields, models, api
from odoo.exceptions import UserError


class ErpPeriodClose(models.Model):
    _name = "erp.period.close"
    _description = "结账/反结账/期间控制"
    _order = "period_end desc, id desc"

    name = fields.Char(string="结账批次", required=True)
    period_start = fields.Date(string="期间起", required=True)
    period_end = fields.Date(string="期间止", required=True)
    state = fields.Selection(
        [("draft", "草稿"), ("in_review", "复核中"), ("closed", "已结账"),
         ("reopened", "已反结账")],
        string="状态", default="draft",
    )
    closed_by = fields.Many2one("res.users", string="结账人")
    closed_at = fields.Datetime(string="结账时间")
    reopened_by = fields.Many2one("res.users", string="反结账人")
    reopened_at = fields.Datetime(string="反结账时间")
    note = fields.Text(string="备注")

    def action_close(self):
        for rec in self:
            if rec.state == "closed":
                raise UserError("该期间已结账")
            rec.state = "closed"
            rec.closed_by = self.env.user
            rec.closed_at = fields.Datetime.now()

    def action_reopen(self):
        for rec in self:
            if rec.state != "closed":
                raise UserError("只能反结账已结账的期间")
            rec.state = "reopened"
            rec.reopened_by = self.env.user
            rec.reopened_at = fields.Datetime.now()
