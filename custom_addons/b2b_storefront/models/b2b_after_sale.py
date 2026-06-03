from odoo import fields, models


class B2bAfterSaleTicket(models.Model):
    _name = "b2b.after.sale.ticket"
    _description = "B2B 售后申请"
    _order = "create_date desc"

    name = fields.Char(string="申请编号", required=True, default="售后申请")
    order_id = fields.Many2one("sale.order", string="关联订单", required=True)
    partner_id = fields.Many2one("res.partner", string="客户", required=True)
    ticket_type = fields.Selection(
        [("shortage", "缺货"), ("damage", "破损"), ("wrong_item", "错货"),
         ("quality", "质量问题"), ("other", "其他")],
        string="售后类型", required=True,
    )
    description = fields.Text(string="问题描述")
    image_ids = fields.Many2many("ir.attachment", string="附件图片")
    state = fields.Selection(
        [("draft", "待处理"), ("accepted", "已受理"), ("resolved", "已解决"),
         ("rejected", "已驳回")],
        string="状态", default="draft",
    )
