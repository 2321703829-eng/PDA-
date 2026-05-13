from odoo import fields, models


class ErpClaimRule(models.Model):
    _name = "erp.claim.rule"
    _description = "扣赔核销规则"
    _order = "sequence, id"

    name = fields.Char(string="规则名称", required=True)
    sequence = fields.Integer(string="排序", default=10)
    claim_type = fields.Selection(
        [("customer_deduct", "客户扣款"), ("driver_penalty", "司机赔付"),
         ("warehouse_loss", "仓内损耗"), ("other", "其他")],
        string="扣赔类型", required=True,
    )
    source_module = fields.Selection(
        [("tms", "配送异常"), ("wms", "仓库异常"), ("erp", "经营调整"),
         ("manual", "人工调整")],
        string="来源模块",
    )
    account_id = fields.Many2one("account.account", string="核算科目")
    amount_rule = fields.Selection(
        [("fixed", "固定金额"), ("percent", "按比例"), ("manual", "人工判定")],
        string="金额规则", default="manual",
    )
    is_active = fields.Boolean(string="启用", default=True)
    note = fields.Text(string="规则说明")
