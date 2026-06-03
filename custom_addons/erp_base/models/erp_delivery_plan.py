from odoo import api, fields, models


class ErpDeliveryPlan(models.Model):
    _name = "erp.delivery.plan"
    _description = "销售出库计划"
    _order = "planned_date, id desc"

    sale_order_id = fields.Many2one("sale.order", string="销售订单", ondelete="cascade")
    name = fields.Char(string="计划编号", required=True)
    planned_date = fields.Date(string="计划出库日期", default=fields.Date.context_today)
    state = fields.Selection(
        [
            ("draft", "草稿"),
            ("confirmed", "已确认"),
            ("in_progress", "执行中"),
            ("done", "已完成"),
            ("cancelled", "已取消"),
        ],
        string="状态",
        default="draft",
    )
    picking_ids = fields.Many2many(
        "stock.picking",
        compute="_compute_picking_ids",
        string="关联出库单",
    )
    locked = fields.Boolean(string="已锁定库存")
    note = fields.Text(string="备注")

    @api.depends("sale_order_id", "sale_order_id.name")
    def _compute_picking_ids(self):
        Picking = self.env["stock.picking"]
        for plan in self:
            pickings = Picking
            if plan.sale_order_id:
                if "picking_ids" in plan.sale_order_id._fields:
                    pickings |= plan.sale_order_id.picking_ids
                pickings |= Picking.search([("origin", "=", plan.sale_order_id.name)])
            plan.picking_ids = pickings

    def action_lock_stock(self):
        for plan in self:
            plan.locked = True
            plan.state = "confirmed"
