/** @odoo-module */

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

export class LogisticsDashboardAction extends Component {
    static template = "logistics_web.DashboardAction";
    static components = { Layout };
    static props = { ...standardActionServiceProps };

    setup() {
        this.actionService = useService("action");
        this.menuService = useService("menu");
        this.display = {
            controlPanel: false,
            searchPanel: false,
        };
        this.state = useState({
            loading: true,
            error: "",
            summaryCards: [],
            priorityItems: [],
            recentChanges: [],
        });

        onWillStart(async () => {
            await this.loadDashboard();
        });
    }

    get ui() {
        return {
            title: "物流工作台",
            subtitle: "围绕异常、补证和高风险批次快速定位今日待办任务。",
            badgePrimary: "今日待办",
            badgeSecondary: "即时优先级",
            heroNoteTitle: "处理建议",
            heroNoteBody: "先从概览卡片判断风险面，再通过优先队列和最近变化快速进入具体运单、批次或异常对象。",
            loading: "正在加载工作台数据...",
            sectionSummaryTitle: "概览指标",
            sectionSummaryHint: "聚焦当前最需要关注的异常、补证和风险批次。",
            summaryEmpty: "暂无概览指标可供展示。",
            sectionQueueTitle: "优先处理队列",
            sectionQueueHint: "按当前风险和处理时效给出的待办项。",
            sectionRecentTitle: "最近变化",
            sectionRecentHint: "追踪最近新增或更新的异常、批次和运单。",
            sectionDrilldownTitle: "快速进入",
            sectionDrilldownHint: "按对象类型直接进入列表完成后续处理。",
            queueOwner: "负责人",
            noPriority: "暂无需要立即处理的队列项。",
            noRecent: "暂无需要关注的最近变化。",
            openWaybillTitle: "运单列表",
            openWaybillHint: "查看所有运单并继续下钻处理。",
            openExceptionTitle: "异常列表",
            openExceptionHint: "聚焦当前待处理或处理中的异常。",
            openBatchTitle: "批次列表",
            openBatchHint: "从批次视角分析波次执行与风险分布。",
            backHome: "返回首页",
            openStatsCenter: "打开统计中心",
            noPermission: "当前账号没有访问该页的权限。",
        };
    }

    get summaryCardMetaMap() {
        return {
            pending_exception_count: "\u5f85\u5904\u7406\u5f02\u5e38\u6570",
            evidence_missing_count: "\u5f85\u8865\u8bc1\u636e\u6570",
            high_risk_batch_count: "\u9ad8\u98ce\u9669\u6279\u6b21\u6570",
            today_new_exception_count: "\u4eca\u65e5\u65b0\u589e\u5f02\u5e38\u6570",
        };
    }

    get stateLabels() {
        return {
            draft: "\u8349\u7a3f",
            open: "\u5f85\u5904\u7406",
            processing: "\u5904\u7406\u4e2d",
            resolved: "\u5df2\u89e3\u51b3",
            closed: "\u5df2\u5173\u95ed",
            cancelled: "\u5df2\u53d6\u6d88",
        };
    }

    async loadDashboard() {
        try {
            const payload = await this.apiRequest("/api/admin/logistics/dashboard/summary", {
                method: "POST",
            });
            const data = payload.data || {};

            this.state.summaryCards = (data.summary_cards || []).map((card) => ({
                ...card,
                caption: this.summaryCardMetaMap[card.key] || "",
            }));
            this.state.priorityItems = (data.priority_items || []).map((item) => ({
                ...item,
                statusLabel: this.stateLabels[item.status] || item.status || "",
            }));
            this.state.recentChanges = data.recent_changes || [];
            this.state.error = "";
        } catch (error) {
            this.state.summaryCards = [];
            this.state.priorityItems = [];
            this.state.recentChanges = [];
            this.state.error = this.mapErrorMessage(error);
        } finally {
            this.state.loading = false;
        }
    }

    async onSummaryCardClick(card) {
        const key = card?.key;
        if (key === "pending_exception_count") {
            return this.openExceptionList([["id", "in", card.record_ids || []]], "\u5f85\u5904\u7406\u5f02\u5e38");
        }
        if (key === "evidence_missing_count") {
            return this.openExceptionList([["id", "in", card.record_ids || []]], "\u5f85\u8865\u8bc1\u636e");
        }
        if (key === "high_risk_batch_count") {
            return this.openBatchList([["id", "in", card.record_ids || []]], "\u9ad8\u98ce\u9669\u6279\u6b21");
        }
        if (key === "today_new_exception_count") {
            return this.openExceptionList([["id", "in", card.record_ids || []]], "\u5f85\u8865\u8bc1\u636e");
        }
    }

    async onPriorityItemClick(item) {
        if (item?.targetType === "exception") {
            return this.openExceptionList([["name", "=", item.code]], `\u5f02\u5e38 ${item.code}`);
        }
        if (item?.targetType === "batch") {
            return this.openBatchList([["name", "=", item.code]], `\u6279\u6b21 ${item.code}`);
        }
        if (item?.targetType === "wave") {
            return this.openWaveList([["name", "=", item.code]], `\u6ce2\u6b21 ${item.code}`);
        }
        return this.openWaybillList([["name", "=", item.code]], `\u8fd0\u5355 ${item.code}`);
    }

    async onDrilldownClick(target) {
        if (target === "waybill") {
            return this.openWaybillList([], "\u8fd0\u5355\u5217\u8868");
        }
        if (target === "exception") {
            return this.openExceptionList([["state", "in", ["open", "processing"]]], "\u5f02\u5e38\u5217\u8868");
        }
        if (target === "batch") {
            return this.openBatchList([], "\u6279\u6b21\u5217\u8868");
        }
    }

    async goToEnterpriseHome() {
        const menu = this.findMenuByLabels(["\u7269\u6d41\u5de5\u4f5c\u533a", "\u9996\u9875"]);
        if (menu) {
            return this.menuService.selectMenu(menu);
        }
        return this.actionService.doAction("logistics_web.action_logistics_web_home");
    }

    async goToStatsCenter() {
        return this.actionService.doAction("logistics_web.action_logistics_web_stats_center");
    }

    findMenuByLabels(labels) {
        const normalized = new Set(labels);
        return this.menuService.getAll().find((menu) => normalized.has(menu.name) && menu.actionID);
    }

    async openWaybillList(domain = [], name = "\u8fd0\u5355") {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name,
            res_model: "logistics.dispatch.waybill",
            views: [[false, "list"], [false, "form"]],
            domain,
        });
    }

    async openBatchList(domain = [], name = "\u6279\u6b21") {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name,
            res_model: "logistics.dispatch.batch",
            views: [[false, "list"], [false, "form"]],
            domain,
        });
    }

    async openWaveList(domain = [], name = "\u6ce2\u6b21") {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name,
            res_model: "logistics.dispatch.wave",
            views: [[false, "list"], [false, "form"]],
            domain,
        });
    }

    async openExceptionList(domain = [], name = "\u5f02\u5e38") {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name,
            res_model: "logistics.trace.exception",
            views: [[false, "list"], [false, "form"]],
            domain,
        });
    }

    mapErrorMessage(error) {
        const message = error?.message || "";
        if (message.includes("\u6743\u9650") || message.includes("forbidden")) {
            return this.ui.noPermission;
        }
        return message || "\u5f53\u524d\u83dc\u5355\u6682\u672a\u914d\u7f6e\uff0c\u8bf7\u7a0d\u540e\u518d\u8bd5\u3002";
    }

    async apiRequest(url, options = {}) {
        const method = options.method || "GET";
        const response = await fetch(url, {
            method,
            headers: { "Content-Type": "application/json", ...(options.headers || {}) },
            body: options.body !== undefined ? options.body : (method === "POST" ? JSON.stringify({}) : undefined),
        });
        const payload = await response.json().catch(() => null);
        if (!response.ok || !payload || payload.code !== 0) {
            throw new Error(payload?.data?.errors?.[0]?.error_message || payload?.message || "\u8bf7\u6c42\u5931\u8d25\u3002");
        }
        return payload;
    }
}

const actionsRegistry = registry.category("actions");
if (!actionsRegistry.contains("logistics_web.dashboard")) {
    actionsRegistry.add("logistics_web.dashboard", LogisticsDashboardAction);
}
