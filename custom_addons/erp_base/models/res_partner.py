from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # 编码
    partner_code = fields.Char(
        string="客户/供应商编码",
        index=True,
        copy=False,
    )

    # 经营属性
    customer_level = fields.Selection(
        [
            ("a", "A 级"),
            ("b", "B 级"),
            ("c", "C 级"),
            ("d", "D 级"),
        ],
        string="客户等级",
    )
    credit_days = fields.Integer(
        string="账期 (天)",
        help="客户/供应商结算账期天数",
    )
    settlement_method = fields.Selection(
        [
            ("cash", "现结"),
            ("monthly", "月结"),
            ("batch", "批次结"),
            ("other", "其他"),
        ],
        string="结算方式",
    )

    # 物流标记
    is_logistics_serviceable = fields.Boolean(
        string="可配送",
        default=True,
        help="取消勾选后不生成配送任务",
    )

    # 门店属性 (用于 partner 类型为门店时)
    store_code = fields.Char(
        string="门店编码",
        index=True,
    )
    is_store = fields.Boolean(
        string="是否为门店",
        help="标记该客户同时是物流配送门店",
    )

    # 分类标记
    partner_type_ext = fields.Selection(
        [
            ("customer", "客户"),
            ("supplier", "供应商"),
            ("store", "门店"),
            ("both_cs", "客户兼供应商"),
        ],
        string="往来类型",
        help="用于快速筛选和报表分组",
    )

    # 联系人与配送备注
    delivery_note = fields.Text(
        string="配送备注",
        help="停车、上楼、收货时间等配送注意信息",
    )
