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
            brandTitle: "天枢科技企业系统",
            heroTitle: "先确认企业入口，再进入今天的工作模块",
            heroSubtitle: "这里统一放置物流、车队、员工、库存和统计入口；先选模块，再继续处理今天的物流重点和数据摘要。",
            badgePrimary: "Tianshu Enterprise Console",
            badgeSecondary: this.formatToday(new Date()),
            loading: "正在加载天枢科技企业系统首页...",
            sectionModules: "系统模块",
            sectionModulesHint: "先从企业总入口选择模块，再进入对应模块继续工作。",
            sectionHeadline: "物流今日重点",
            sectionHeadlineHint: "把当天需要优先处理的对象先捞出来，避免异常和超时继续扩大。",
            sectionMetrics: "物流核心指标",
            sectionMetricsHint: "这些指标更偏运营判断，帮助你快速识别今天整体执行情况。",
            sectionTrends: "趋势看板",
            sectionTrendsHint: "用最核心的环比指标先看趋势变化，再决定是否进入详细数据看板。",
            sectionCockpit: "物流仪表盘",
            sectionCockpitHint: "把执行、风险和证据三个维度放进一张首页驾驶舱里，先看全局，再决定往下钻取。",
            sectionQuick: "物流快捷入口",
            sectionQuickHint: "先从物流相关高频动作继续处理，不需要再回到旧的应用切换结构里找入口。",
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
            { key: "customer", title: "客户", hint: "进入统一客户入口，查看客户资料、配送规则和交付要求。", actionXmlid: "logistics_base.action_logistics_partner_profile" },
            { key: "logistics", title: "物流", hint: "进入物流工作台、运单、批次和异常处理。", menuLabels: ["物流"] },
            { key: "fleet", title: "车队", hint: "进入车队应用，查看车辆、车务记录和相关成本。", menuLabels: ["车队", "Vehicles"] },
            { key: "employee", title: "员工", hint: "进入员工应用，查看员工档案、岗位和组织信息。", menuLabels: ["员工", "Employees"] },
            { key: "inventory", title: "库存", hint: "进入库存应用，查看库存作业、出入库单和履约流转。", menuLabels: ["库存", "Inventory"] },
            { key: "dashboard", title: "所有统计图表", hint: "进入统计图表中心，查看物流分析与排行分布。", actionXmlid: "logistics_web.action_logistics_web_stats_center" },
            { key: "invoice", title: "发票", hint: "进入发票应用，查看开票、发票列表和对账处理。", menuLabels: ["发票", "Invoices"] },
            { key: "settings", title: "设置", hint: "进入系统设置和基础参数配置。", menuLabels: ["设置", "Settings"] },
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
                { key: "import_waybill", title: "物流导入", hint: "从标准导入页开始导入运单与订单数据。", action: "import_waybill", tone: "primary" },
                { key: "exception_center", title: "物流异常", hint: "直接进入物流异常列表，继续查看责任、证据和处理进度。", action: "open_exception", tone: "default" },
                { key: "waybill_center", title: "物流运单", hint: "进入物流运单列表，按运单号、批次号和门店继续筛选。", action: "open_waybill", tone: "default" },
                { key: "board_center", title: "物流工作台", hint: "进入物流工作台和管理看板，继续查看趋势与重点对象。", action: "open_board", tone: "default" },
            ];

            this.state.guideCards = [
                { key: "dispatcher", title: "调度", description: "先进入物流模块，再看待执行运单、批次和波次安排。" },
                { key: "operator", title: "运营", description: "先看待处理异常和待补证据，再进入物流模块中的异常与证据继续跟进。" },
                { key: "manager", title: "管理层", description: "先看首页摘要和管理看板，再决定是否进入物流模块定位重点问题。" },
                { key: "new_user", title: "新用户", description: "先理解企业模块结构，再进入对应模块，不需要一开始就理解全部业务表。" },
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
            this.state.error = "天枢科技企业系统首页加载失败，请刷新页面或稍后再试。";
        } finally {
            this.state.loading = false;
        }
    }

    async onModuleCardClick(item) {
        try {
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
