from odoo import fields, models


class WmsPdaCheckLine(models.Model):
    _name = "wms.pda.check.line"
    _description = "WMS PDA Check Line"
    _order = "task_id, id"

    task_id = fields.Many2one("wms.check.task", string="复核任务", required=True, ondelete="cascade", index=True)
    pick_line_id = fields.Many2one("wms.pick.task.line", string="拣货明细", ondelete="cascade", index=True)
    product_id = fields.Many2one("product.product", string="商品", required=True, ondelete="restrict", index=True)
    source_location_id = fields.Many2one("stock.location", string="拣货库位", ondelete="set null")
    demand_qty = fields.Float(string="应复核数量", default=0.0, digits=(16, 4))
    picked_qty = fields.Float(string="已拣数量", default=0.0, digits=(16, 4))
    checked_qty = fields.Float(string="已复核数量", default=0.0, digits=(16, 4))
    state = fields.Selection(
        [
            ("waiting", "待复核"),
            ("partial", "部分复核"),
            ("full", "已复核"),
            ("over", "超量复核"),
        ],
        string="状态",
        default="waiting",
        required=True,
        index=True,
    )
