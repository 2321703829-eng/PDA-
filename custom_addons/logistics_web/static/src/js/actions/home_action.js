/** @odoo-module */

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Layout } from "@web/search/layout";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

export class LogisticsHomeAction extends Component {
    static template = "logistics_web.HomeAction";
    static components = { Layout };
    static props = { ...standardActionServiceProps };

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.menuService = useService("menu");
        this.display = {
            controlPanel: false,
            searchPanel: false,
        };
        this.state = useState({
            loading: true,
            error: "",
            moduleCards: [],
            headlineCards: [],
            metricCards: [],
            trendCards: [],
            boardPanels: [],
            quickLinks: [],
            guideCards: [],
            recentItems: [],
        });

        onWillStart(async () => {
            await this.loadHome();
        });
    }

    get ui() {
        return {
            brandTitle: "天枢科技物流系统",
            heroTitle: "先选择业务工作区，再处理当前任务",
            heroSubtitle: "这里统一放置订单经营、B2B 商城、仓库作业、配送调度和数据看板入口；原生模块只做业务支撑，页面按企业工作流组织。",
            badgePrimary: "Tianshu Enterprise Console",
            badgeSecondary: this.formatToday(new Date()),
            loading: "正在加载天枢科技物流系统首页...",
            sectionModules: "业务工作区",
            sectionModulesHint: "先从企业总入口选择工作区，再进入对应页面继续处理。",
            sectionHeadline: "今日重点",
            sectionHeadlineHint: "把当天需要优先处理的对象先捞出来，避免异常和超时继续扩大。",
            sectionMetrics: "物流核心指标",
            sectionMetricsHint: "这些指标更偏运营判断，帮助你快速识别今天整体执行情况。",
            sectionTrends: "趋势看板",
            sectionTrendsHint: "用最核心的环比指标先看趋势变化，再决定是否进入详细数据看板。",
            sectionCockpit: "物流仪表盘",
            sectionCockpitHint: "把执行、风险和证据三个维度放进一张首页驾驶舱里，先看全局，再决定往下钻取。",
            sectionQuick: "快捷入口",
            sectionQuickHint: "把销售、采购、仓库和调度的高频动作放到一起，减少在原生菜单里来回切换。",
            sectionGuides: "系统指引",
            sectionGuidesHint: "不同角色先看不同卡片，首页负责告诉你从哪里开始。",
            sectionRecent: "最近动态",
            sectionRecentHint: "快速查看最新异常、补证据和风险对象变更。",
            noRecent: "当前还没有新的动态，可先进入物流或数据看板继续查看。",
        };
    }

    get waybillDoneStates() {
        return ["signed", "done"];
    }

    formatDate(date) {
        const pad = (value) => String(value).padStart(2, "0");
        return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
    }

    formatToday(date) {
        const pad = (value) => String(value).padStart(2, "0");
        return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
    }

    calcRate(numerator, denominator) {
        if (!denominator) {
            return 0;
        }
        return Number(((numerator / denominator) * 100).toFixed(1));
    }

    calcDelta(todayValue, yesterdayValue) {
        const delta = Number((todayValue - yesterdayValue).toFixed(1));
        return {
            value: delta,
            tone: delta > 0 ? "danger" : delta < 0 ? "success" : "default",
            label: delta > 0 ? `较昨日 +${delta}%` : delta < 0 ? `较昨日 ${delta}%` : "与昨日持平",
        };
    }

    formatRecentTime(value) {
        return value ? value.slice(0, 16).replace("T", " ") : "--";
    }

    async loadHome() {
        const today = new Date();
        const yesterday = new Date(today);
        yesterday.setDate(today.getDate() - 1);
        const todayStr = this.formatDate(today);
        const yesterdayStr = this.formatDate(yesterday);

        this.state.moduleCards = [
            { key: "erp", title: "订单经营 ERP", hint: "进入销售订单、采购订单、客户供应商和商品资料。", actionXmlid: "logistics_web.action_enterprise_sales_orders" },
            { key: "b2b", title: "B2B 商城", hint: "进入客户商品可见范围、购物车草稿、商城订单和售后处理。", targetUrl: "/b2b/products", actionXmlid: "b2b_storefront.action_cart_draft" },
            { key: "wms", title: "仓库作业 WMS", hint: "进入收货、出库、出入库单和库存查询。", actionXmlid: "logistics_web.action_enterprise_wms_receipts" },
            { key: "tms", title: "配送调度 TMS", hint: "进入调度工作台、派车单、司机任务、签收和异常。", actionXmlid: "logistics_web.action_logistics_web_dashboard" },
            { key: "bi", title: "数据看板 BI", hint: "查看订单、仓库、配送、异常和运营指标。", actionXmlid: "logistics_web.action_logistics_web_stats_center" },
            { key: "master", title: "基础资料", hint: "维护客户/供应商、商品等主数据。", actionXmlid: "logistics_web.action_enterprise_partners" },
            { key: "settings", title: "系统设置", hint: "进入用户、角色、接口、日志和基础参数配置。", menuLabels: ["设置", "Settings"] },
        ];

        try {
            const [
                todayWaybillCount,
                todaySignedCount,
                todayEvidenceCompleteCount,
                todayExceptionWaybillCount,
                todayOpenExceptionCount,
                todayEvidenceMissingCount,
                todayReadyWaybillCount,
                overdueRiskWaybillCount,
                yesterdayWaybillCount,
                yesterdaySignedCount,
                yesterdayEvidenceCompleteCount,
                yesterdayExceptionWaybillCount,
                recentExceptions,
            ] = await Promise.all([
                this.orm.call("logistics.dispatch.waybill", "search_count", [[["delivery_date", "=", todayStr]]]),
                this.orm.call("logistics.dispatch.waybill", "search_count", [[
                    ["delivery_date", "=", todayStr],
                    ["state", "in", this.waybillDoneStates],
                ]]),
                this.orm.call("logistics.dispatch.waybill", "search_count", [[
                    ["delivery_date", "=", todayStr],
                    ["evidence_status", "=", "complete"],
                ]]),
                this.orm.call("logistics.dispatch.waybill", "search_count", [[
                    ["delivery_date", "=", todayStr],
                    ["exception_status", "in", ["open", "processing", "closed"]],
                ]]),
                this.orm.call("logistics.trace.exception", "search_count", [[["state", "in", ["open", "processing"]]]]),
                this.orm.call("logistics.trace.exception", "search_count", [[
                    ["state", "in", ["open", "processing"]],
                    ["exception_type", "=", "evidence_missing"],
                ]]),
                this.orm.call("logistics.dispatch.waybill", "search_count", [[
                    ["delivery_date", "=", todayStr],
                    ["state", "in", ["draft", "ready"]],
                ]]),
                this.orm.call("logistics.dispatch.waybill", "search_count", [[
                    ["delivery_date", "<", todayStr],
                    ["state", "not in", ["signed", "done", "cancelled"]],
                ]]),
                this.orm.call("logistics.dispatch.waybill", "search_count", [[["delivery_date", "=", yesterdayStr]]]),
                this.orm.call("logistics.dispatch.waybill", "search_count", [[
                    ["delivery_date", "=", yesterdayStr],
                    ["state", "in", this.waybillDoneStates],
                ]]),
                this.orm.call("logistics.dispatch.waybill", "search_count", [[
                    ["delivery_date", "=", yesterdayStr],
                    ["evidence_status", "=", "complete"],
                ]]),
                this.orm.call("logistics.dispatch.waybill", "search_count", [[
                    ["delivery_date", "=", yesterdayStr],
                    ["exception_status", "in", ["open", "processing", "closed"]],
                ]]),
                this.orm.searchRead(
                    "logistics.trace.exception",
                    [],
                    ["name", "exception_type", "severity_level", "waybill_id", "batch_id", "report_time"],
                    { order: "report_time desc, id desc", limit: 5 }
                ),
            ]);

            const todaySignedRate = this.calcRate(todaySignedCount, todayWaybillCount);
            const todayEvidenceRate = this.calcRate(todayEvidenceCompleteCount, todayWaybillCount);
            const todayExceptionRate = this.calcRate(todayExceptionWaybillCount, todayWaybillCount);
            const yesterdaySignedRate = this.calcRate(yesterdaySignedCount, yesterdayWaybillCount);
            const yesterdayEvidenceRate = this.calcRate(yesterdayEvidenceCompleteCount, yesterdayWaybillCount);
            const yesterdayExceptionRate = this.calcRate(yesterdayExceptionWaybillCount, yesterdayWaybillCount);

            this.state.headlineCards = [
                { key: "open_exception", label: "今日待处理异常", value: todayOpenExceptionCount, tone: todayOpenExceptionCount ? "danger" : "default" },
                { key: "evidence_missing", label: "今日待补证据", value: todayEvidenceMissingCount, tone: todayEvidenceMissingCount ? "warning" : "default" },
                { key: "ready_waybill", label: "今日待执行运单", value: todayReadyWaybillCount, tone: todayReadyWaybillCount ? "info" : "default" },
                { key: "overdue_risk", label: "今日超时风险运单", value: overdueRiskWaybillCount, tone: overdueRiskWaybillCount ? "danger" : "default" },
            ];

            this.state.metricCards = [
                { key: "today_waybill", label: "今日运单总量", value: todayWaybillCount, suffix: "单" },
                { key: "signed_rate", label: "已签收率", value: todaySignedRate, suffix: "%" },
                { key: "evidence_rate", label: "证据补齐率", value: todayEvidenceRate, suffix: "%" },
                { key: "exception_rate", label: "异常运单率", value: todayExceptionRate, suffix: "%" },
            ];

            this.state.trendCards = [
                {
                    key: "exception_rate_delta",
                    title: "异常运单率日环比",
                    current: `${todayExceptionRate}%`,
                    ...this.calcDelta(todayExceptionRate, yesterdayExceptionRate),
                },
                {
                    key: "signed_rate_delta",
                    title: "运单完成率日环比",
                    current: `${todaySignedRate}%`,
                    ...this.calcDelta(todaySignedRate, yesterdaySignedRate),
                },
                {
                    key: "evidence_rate_delta",
                    title: "证据补齐率日环比",
                    current: `${todayEvidenceRate}%`,
                    ...this.calcDelta(todayEvidenceRate, yesterdayEvidenceRate),
                },
            ];

            this.state.boardPanels = [
                {
                    key: "execution",
                    tone: "info",
                    title: "执行概览",
                    emphasis: `${todayWaybillCount} 单`,
                    summary: `今日待执行 ${todayReadyWaybillCount} 单，已签收率 ${todaySignedRate}%`,
                    items: [
                        { label: "今日运单", value: todayWaybillCount },
                        { label: "待执行", value: todayReadyWaybillCount },
                        { label: "已签收率", value: `${todaySignedRate}%` },
                    ],
                },
                {
                    key: "risk",
                    tone: todayOpenExceptionCount || overdueRiskWaybillCount ? "danger" : "default",
                    title: "风险概览",
                    emphasis: `${todayOpenExceptionCount} 条`,
                    summary: `当前超时风险运单 ${overdueRiskWaybillCount} 单，异常运单率 ${todayExceptionRate}%`,
                    items: [
                        { label: "待处理异常", value: todayOpenExceptionCount },
                        { label: "超时风险", value: overdueRiskWaybillCount },
                        { label: "异常运单率", value: `${todayExceptionRate}%` },
                    ],
                },
                {
                    key: "evidence",
                    tone: todayEvidenceMissingCount ? "warning" : "default",
                    title: "证据概览",
                    emphasis: `${todayEvidenceRate}%`,
                    summary: `当前待补证据 ${todayEvidenceMissingCount} 条，证据补齐率较昨日 ${this.calcDelta(todayEvidenceRate, yesterdayEvidenceRate).label}`,
                    items: [
                        { label: "待补证据", value: todayEvidenceMissingCount },
                        { label: "补齐率", value: `${todayEvidenceRate}%` },
                        { label: "最近异常", value: recentExceptions.length },
                    ],
                },
            ];

            this.state.quickLinks = [
                { key: "sales_order", title: "销售订单", hint: "进入销售订单列表，继续处理客户下单和发货前置流程。", action: "open_sales", tone: "primary" },
                { key: "purchase_order", title: "采购订单", hint: "进入采购订单列表，跟进供应商采购和补货。", action: "open_purchase", tone: "default" },
                { key: "stock_picking", title: "出入库单", hint: "进入仓库出入库单，查看收货、出库和调拨流转。", action: "open_stock", tone: "default" },
                { key: "board_center", title: "调度工作台", hint: "进入调度工作台和管理看板，继续查看趋势与重点对象。", action: "open_board", tone: "default" },
            ];

            this.state.guideCards = [
                { key: "sales", title: "销售", description: "从订单经营进入销售订单，跟进客户订单、发货状态和开票前置数据。" },
                { key: "purchase", title: "采购", description: "从订单经营进入采购订单，处理供应商采购和补货需求。" },
                { key: "warehouse", title: "仓库", description: "从仓库作业进入收货、出库、出入库单和库存查询。" },
                { key: "dispatcher", title: "调度", description: "从配送调度进入调度工作台、派车单、司机任务、签收和异常。" },
            ];

            this.state.recentItems = (recentExceptions || []).map((item) => ({
                key: item.name,
                title: item.name,
                subtitle: `${item.exception_type || "异常"} / ${item.waybill_id?.[1] || "未知运单"}`,
                summary: [
                    item.batch_id?.[1] ? `批次 ${item.batch_id[1]}` : "",
                    item.report_time ? `上报于 ${this.formatRecentTime(item.report_time)}` : "",
                ].filter(Boolean).join(" / "),
            }));

            this.state.error = "";
        } catch {
            this.state.headlineCards = [];
            this.state.metricCards = [];
            this.state.trendCards = [];
            this.state.boardPanels = [];
            this.state.quickLinks = [];
            this.state.guideCards = [];
            this.state.recentItems = [];
            this.state.error = "天枢科技物流系统首页加载失败，请刷新页面或稍后再试。";
        } finally {
            this.state.loading = false;
        }
    }

    async onModuleCardClick(item) {
        try {
            if (item?.targetUrl) {
                window.location.assign(item.targetUrl);
                return;
            }
            if (item?.menuLabels?.length) {
                const menu = this.findMenuByLabels(item.menuLabels);
                if (menu) {
                    return this.menuService.selectMenu(menu);
                }
            }
            if (item?.action) {
                return this.actionService.doAction(item.action);
            }
            if (item?.actionXmlid) {
                return this.actionService.doAction(item.actionXmlid);
            }
        } catch {
            this.state.error = `${item?.title || "当前模块"}入口暂未启用，请刷新页面或稍后再试。`;
        }
    }

    findMenuByLabels(labels) {
        const menus = this.menuService.getAll();
        const normalized = new Set(labels);
        return menus.find((menu) => normalized.has(menu.name) && menu.actionID);
    }

    async onHeadlineClick(card) {
        if (card?.key === "open_exception" || card?.key === "evidence_missing") {
            return this.openExceptionCenter();
        }
        return this.openWaybillCenter();
    }

    async onQuickLinkClick(item) {
        if (item?.action === "import_waybill") {
            return this.actionService.doAction("logistics_web.action_logistics_web_import_center");
        }
        if (item?.action === "open_sales") {
            return this.actionService.doAction("logistics_web.action_enterprise_sales_orders");
        }
        if (item?.action === "open_purchase") {
            return this.actionService.doAction("logistics_web.action_enterprise_purchase_orders");
        }
        if (item?.action === "open_stock") {
            return this.actionService.doAction("logistics_web.action_enterprise_stock_pickings");
        }
        if (item?.action === "open_exception") {
            return this.openExceptionCenter();
        }
        if (item?.action === "open_waybill") {
            return this.openWaybillCenter();
        }
        if (item?.action === "open_board") {
            return this.actionService.doAction("logistics_web.action_logistics_web_dashboard");
        }
    }

    async openWaybillCenter() {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "运单",
            res_model: "logistics.dispatch.waybill",
            views: [[false, "list"], [false, "form"]],
        });
    }

    async openExceptionCenter() {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "异常",
            res_model: "logistics.trace.exception",
            views: [[false, "list"], [false, "form"]],
            domain: [["state", "in", ["open", "processing"]]],
        });
    }
}

const actionsRegistry = registry.category("actions");
if (!actionsRegistry.contains("logistics_web.home")) {
    actionsRegistry.add("logistics_web.home", LogisticsHomeAction);
}
