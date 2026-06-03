# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class WmsDashboardController(http.Controller):

    @http.route("/wms/dashboard", type="http", auth="user")
    def dashboard(self, **kw):
        cards = [
            {"name": "收货任务", "icon": "fa-download", "model": "wms.receipt.task",
             "action": "ir.actions.act_window,692", "desc": "采购入库收货管理"},
            {"name": "上架任务", "icon": "fa-arrow-up", "model": "wms.putaway.task",
             "action": "ir.actions.act_window,693", "desc": "货物上架库位管理"},
            {"name": "出库任务", "icon": "fa-upload", "model": "wms.outbound.task",
             "action": "ir.actions.act_window,694", "desc": "销售出库任务"},
            {"name": "拣货任务", "icon": "fa-shopping-basket", "model": "wms.pick.task",
             "action": "ir.actions.act_window,695", "desc": "按单/波次拣货"},
            {"name": "复核任务", "icon": "fa-check-circle", "model": "wms.check.task",
             "action": "ir.actions.act_window,696", "desc": "出库前复核校验"},
            {"name": "交接单", "icon": "fa-handshake-o", "model": "wms.handover.order",
             "action": "ir.actions.act_window,697", "desc": "仓库→司机交接"},
            {"name": "盘点单", "icon": "fa-clipboard", "model": "wms.inventory.operation",
             "action": "ir.actions.act_window,699", "desc": "库存盘点与调整"},
            {"name": "库存台账", "icon": "fa-book", "model": "wms.inventory.ledger",
             "action": "ir.actions.act_window,700", "desc": "库位库存明细"},
            {"name": "仓库证据", "icon": "fa-shield", "model": "logistics.trace.evidence",
             "action": "ir.actions.act_window,541", "desc": "仓库留痕证据"},
            {"name": "到货计划", "icon": "fa-calendar-check-o", "model": "wms.arrival.plan",
             "action": "ir.actions.act_window,701", "desc": "采购到货计划"},
            {"name": "库存查询", "icon": "fa-search", "model": "stock.quant",
             "action": "ir.actions.act_window,702", "desc": "实时库存查询"},
        ]
        return request.render("wms_task_core.dashboard_template", {"cards": cards})
