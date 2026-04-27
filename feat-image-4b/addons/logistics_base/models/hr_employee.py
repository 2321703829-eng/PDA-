from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    logistics_employee_code = fields.Char(
        string="Employee Code",
        index=True,
        copy=False,
    )
    logistics_role = fields.Selection(
        selection=[
            ("dispatcher", "Dispatcher"),
            ("customer_service", "Customer Service"),
            ("warehouse_keeper", "Warehouse Keeper"),
            ("driver", "Driver"),
            ("operator", "Operator"),
            ("manager", "Manager"),
        ],
        string="Logistics Role",
    )
    logistics_work_status = fields.Selection(
        selection=[
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("leave", "Leave"),
        ],
        string="Work Status",
        default="active",
    )
    logistics_service_area = fields.Char(
        string="Service Area",
    )
    logistics_default_warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Default Warehouse",
    )
    logistics_can_take_order = fields.Boolean(
        string="Can Take Order",
        default=False,
    )
