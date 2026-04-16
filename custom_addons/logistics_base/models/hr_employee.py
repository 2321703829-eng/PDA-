from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    logistics_employee_code = fields.Char(
        string="员工编号",
        index=True,
        copy=False,
    )
    logistics_role = fields.Selection(
        selection=[
            ("dispatcher", "调度"),
            ("customer_service", "客服"),
            ("warehouse_keeper", "仓管"),
            ("driver", "司机"),
            ("operator", "操作员"),
            ("manager", "管理人员"),
        ],
        string="物流角色",
    )
    logistics_work_status = fields.Selection(
        selection=[
            ("active", "在岗"),
            ("inactive", "停用"),
            ("leave", "请假"),
        ],
        string="工作状态",
        default="active",
    )
    logistics_service_area = fields.Char(
        string="服务区域",
    )
    logistics_default_warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="默认仓库",
    )
    logistics_can_take_order = fields.Boolean(
        string="可接单",
        default=False,
    )
