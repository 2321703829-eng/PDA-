from odoo import fields, models


class WmsTaskPhoto(models.Model):
    _name = "wms.task.photo"
    _description = "WMS PDA Task Photo"
    _order = "id desc"

    task_model = fields.Char(string="任务模型", required=True, index=True)
    task_id = fields.Integer(string="任务 ID", required=True, index=True)
    photo_url = fields.Char(string="图片 URL", required=True)
    operator_id = fields.Many2one("res.users", string="操作人", ondelete="set null")
    warehouse_id = fields.Many2one("stock.warehouse", string="仓库", ondelete="set null")
    device_id = fields.Char(string="设备号")
    gps = fields.Char(string="GPS")
    note = fields.Text(string="备注")
