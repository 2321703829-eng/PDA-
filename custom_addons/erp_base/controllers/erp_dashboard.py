# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class ErpDashboardController(http.Controller):

    @http.route("/erp/dashboard", type="http", auth="user")
    def dashboard(self, **kw):
        cards = [
            {"name": "销售订单", "icon": "fa-file-text", "model": "sale.order", "desc": "客户销售订单管理"},
            {"name": "采购订单", "icon": "fa-shopping-cart", "model": "purchase.order", "desc": "供应商采购管理"},
            {"name": "客户/供应商", "icon": "fa-users", "model": "res.partner", "desc": "往来单位主数据"},
            {"name": "商品管理", "icon": "fa-cube", "model": "product.template", "desc": "商品主档与价格"},
            {"name": "订单导入", "icon": "fa-upload", "model": "erp.order.import", "desc": "Excel批量导入订单"},
            {"name": "价格管理", "icon": "fa-tag", "model": "product.price.adjustment", "desc": "调价记录与价格规则"},
            {"name": "客户对账", "icon": "fa-calculator", "model": "erp.reconciliation", "desc": "应收账款对账"},
            {"name": "供应商对账", "icon": "fa-balance-scale", "model": "erp.reconciliation", "desc": "应付账款对账"},
            {"name": "出库计划", "icon": "fa-calendar", "model": "erp.delivery.plan", "desc": "销售出库计划"},
            {"name": "退货单", "icon": "fa-reply", "model": "erp.sale.return", "desc": "销售退货管理"},
            {"name": "扣赔核销", "icon": "fa-gavel", "model": "erp.claim.rule", "desc": "扣款赔付规则"},
            {"name": "结账管理", "icon": "fa-lock", "model": "erp.period.close", "desc": "期间结账与反结账"},
        ]
        return request.render("erp_base.dashboard_template", {"cards": cards})
