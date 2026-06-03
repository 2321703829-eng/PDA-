# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class TmsDashboardController(http.Controller):

    @http.route("/tms/dashboard", type="http", auth="user")
    def dashboard(self, **kw):
        cards = [
            {"name": "排线调度", "icon": "fa-map-signs", "model": "logistics.route.planning.batch",
             "action": "ir.actions.act_window,680", "desc": "路线规划批次与站点管理"},
            {"name": "批次", "icon": "fa-cubes", "model": "logistics.dispatch.batch",
             "action": "ir.actions.act_window,517", "desc": "物流调度批次"},
            {"name": "波次", "icon": "fa-sitemap", "model": "logistics.dispatch.wave",
             "action": "ir.actions.act_window,518", "desc": "物流调度波次"},
            {"name": "运单列表", "icon": "fa-file-text-o", "model": "logistics.dispatch.waybill",
             "action": "ir.actions.act_window,519", "desc": "运单管理与追踪"},
            {"name": "配送节点明细", "icon": "fa-map-marker", "model": "logistics.dispatch.waybill.customer.line",
             "action": "ir.actions.act_window,520", "desc": "客户配送节点"},
            {"name": "订单明细", "icon": "fa-list-alt", "model": "logistics.dispatch.waybill.order.line",
             "action": "ir.actions.act_window,539", "desc": "运单关联订单"},
            {"name": "货物明细", "icon": "fa-cube", "model": "logistics.dispatch.waybill.customer.goods.line",
             "action": "ir.actions.act_window,521", "desc": "运单货物明细"},
            {"name": "派车单", "icon": "fa-truck", "model": "tms.dispatch.order",
             "action": "ir.actions.act_window,598", "desc": "TMS 派车调度"},
            {"name": "司机任务", "icon": "fa-user", "model": "tms.driver.task",
             "action": "ir.actions.act_window,599", "desc": "司机配送任务"},
            {"name": "导入中心", "icon": "fa-upload", "model": "logistics.import.task",
             "action": "ir.actions.client,533", "desc": "物流数据导入"},
            {"name": "配送异常", "icon": "fa-exclamation-triangle", "model": "tms.delivery.exception",
             "action": "ir.actions.act_window,601", "desc": "配送异常管理"},
            {"name": "仓库证据", "icon": "fa-shield", "model": "logistics.trace.evidence",
             "action": "ir.actions.act_window,541", "desc": "仓库端留痕证据"},
            {"name": "司机证据", "icon": "fa-camera", "model": "logistics.trace.evidence",
             "action": "ir.actions.act_window,542", "desc": "司机端留痕证据"},
            {"name": "证据汇总", "icon": "fa-bar-chart", "model": "logistics.trace.evidence.summary",
             "action": "ir.actions.act_window,540", "desc": "证据统计汇总"},
        ]
        return request.render("tms_dispatch_core.dashboard_template", {"cards": cards})
