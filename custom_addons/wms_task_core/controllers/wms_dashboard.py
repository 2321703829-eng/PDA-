# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class WmsDashboardController(http.Controller):

    def _build_card(self, name, icon, model, action_xmlid, desc):
        action = request.env.ref(action_xmlid, raise_if_not_found=False) if action_xmlid else False
        model_exists = model in request.env.registry
        action_id = action.id if action and model_exists else False
        return {
            "name": name,
            "icon": icon,
            "model": model,
            "action": "ir.actions.act_window,%s" % action_id if action_id else "ir.actions.act_window,0",
            "desc": desc,
            "disabled": not bool(action_id),
        }

    @http.route("/wms/dashboard", type="http", auth="user")
    def dashboard(self, **kw):
        cards = [
            self._build_card("收货任务", "fa-download", "wms.receipt.task", "wms_task_core.action_wms_receipt_task", "采购入库收货管理"),
            self._build_card("上架任务", "fa-arrow-up", "wms.putaway.task", "wms_task_core.action_wms_putaway_task", "货物上架库位管理"),
            self._build_card("出库任务", "fa-upload", "wms.outbound.task", "wms_task_core.action_wms_outbound_task", "销售出库任务"),
            self._build_card("拣货任务", "fa-shopping-basket", "wms.pick.task", "wms_task_core.action_wms_pick_task", "按单/波次拣货"),
            self._build_card("复核任务", "fa-check-circle", "wms.check.task", "wms_task_core.action_wms_check_task", "出库前复核校验"),
            self._build_card("交接单", "fa-handshake-o", "wms.handover.order", "wms_task_core.action_wms_handover_center", "仓库到司机交接"),
            self._build_card("盘点单", "fa-clipboard", "wms.inventory.operation", "wms_task_core.action_wms_inventory_operation", "库存盘点与调整"),
            self._build_card("库存台账", "fa-book", "wms.inventory.ledger", "wms_task_core.action_wms_inventory_ledger", "库位库存明细"),
            self._build_card("仓库证据", "fa-shield", "logistics.trace.evidence", "logistics_trace_evidence.action_logistics_trace_evidence_warehouse", "仓库留痕证据"),
            self._build_card("到货计划", "fa-calendar-check-o", "purchase.order", "wms_task_core.action_wms_arrival_plan", "采购到货计划"),
            self._build_card("库存查询", "fa-search", "stock.quant", "logistics_web.action_enterprise_stock_quants", "实时库存查询"),
        ]
        return request.render("wms_task_core.dashboard_template", {"cards": cards})
