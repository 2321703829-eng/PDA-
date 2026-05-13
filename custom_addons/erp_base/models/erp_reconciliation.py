from odoo import fields, models


class ErpReconciliation(models.Model):
    _name = "erp.reconciliation"
    _description = "客户/供应商对账"
    _order = "recon_date desc, id desc"

    name = fields.Char(string="对账单号", required=True)
    partner_id = fields.Many2one("res.partner", string="客户/供应商", required=True)
    recon_type = fields.Selection(
        [("customer", "客户对账"), ("supplier", "供应商对账")],
        string="对账类型", required=True,
    )
    recon_date = fields.Date(string="对账日期", default=fields.Date.context_today)
    period_start = fields.Date(string="期间起")
    period_end = fields.Date(string="期间止")
    opening_balance = fields.Float(string="期初余额")
    closing_balance = fields.Float(string="期末余额")
    total_invoiced = fields.Float(string="本期开票")
    total_paid = fields.Float(string="本期收款/付款")
    total_adjustment = fields.Float(string="调整金额")
    state = fields.Selection(
        [("draft", "草稿"), ("confirmed", "已确认"), ("sent", "已发送"),
         ("settled", "已结算"), ("disputed", "有争议")],
        string="状态", default="draft",
    )
    note = fields.Text(string="备注")
