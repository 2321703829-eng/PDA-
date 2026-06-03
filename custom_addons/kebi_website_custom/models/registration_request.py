# -*- coding: utf-8 -*-
from odoo import fields, models


class KebiRegistrationRequest(models.Model):
    _name = "kebi.registration.request"
    _description = "Kebi Registration Request"
    _order = "create_date desc, id desc"
    _rec_name = "name"

    name = fields.Char(string="联系人", required=True)
    company = fields.Char(string="企业名称")
    contact = fields.Char(string="联系电话/邮箱", required=True)
    message = fields.Text(string="备注")
    request_ip = fields.Char(string="IP")
    user_agent = fields.Char(string="浏览器")
    state = fields.Selection(
        [
            ("new", "待处理"),
            ("contacted", "已联系"),
            ("closed", "已关闭"),
        ],
        string="状态",
        default="new",
        required=True,
    )
