/** @odoo-module */

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class LogisticsDashboardAction extends Component {
    static template = "logistics_web.DashboardAction";

    setup() {
        this.actionService = useService("action");
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
            subtitle: "先看今天物流需要优先处理什么，再进入运单、批次和异常继续跟进。",
            badgePrimary: "今日重点",
            badgeSecondary: "运营视角",
            loading: "正在加载工作台数据...",
            sectionSummaryTitle: "今日重点",
            sectionSummaryHint: "卡片既是提醒，也是处理入口，点击后可直接进入对应列表。",
            summaryEmpty: "当前暂无可展示的今日重点摘要。",
            sectionQueueTitle: "优先处理队列",
            sectionQueueHint: "这些对象更适合优先查看，避免问题继续扩散到门店交付。",
            sectionRecentTitle: "最新动态",
            sectionRecentHint: "快速查看今天新增的异常、补图和状态变化。",
            sectionDrilldownTitle: "常用入口",
            sectionDrilldownHint: "从这里进入最常用的处理页面，继续查看详情和证据。",
            queueOwner: "当前负责人",
            noPriority: "当前没有需要优先处理的对象。",
            noRecent: "今天还没有新的异常或证据变化。",
            openWaybillTitle: "运单追踪",
            openWaybillHint: "按运单查看最新留痕、证据状态和异常进展。",
            openExceptionTitle: "异常处理",
            openExceptionHint: "直接进入待处理异常，查看责任、证据和处理进度。",
            openBatchTitle: "批次跟进",
            openBatchHint: "当问题集中在同一执行批次时，从批次视角继续查看。",
            noPermission: "当前账号暂无查看物流工作台的权限。",
        };
    }

    get stateLabels() {
        return {
            draft: "草稿",
            open: "待处理",
            processing: "处理中",
            resolved: "已解决",
            closed: "已关闭",
            cancelled: "已取消",
        };
    }

    async loadDashboard() {
        try {
            const payload = await this.apiRequest("/api/admin/logistics/dashboard/summary", {
                method: "POST",
            });
            const data = payload.data || {};

            this.state.summaryCards = data.summary_cards || [];
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
            return this.openExceptionList([["id", "in", card.record_ids || []]], "打开待处理异常");
        }
        if (key === "evidence_missing_count") {
            return this.openExceptionList([["id", "in", card.record_ids || []]], "打开待补证据异常");
        }
        if (key === "high_risk_batch_count") {
            return this.openBatchList([["id", "in", card.record_ids || []]], "打开风险批次");
        }
        if (key === "today_new_exception_count") {
            return this.openExceptionList([["id", "in", card.record_ids || []]], "打开今日新增异常");
        }
    }

    async onPriorityItemClick(item) {
        if (item?.targetType === "exception") {
            return this.openExceptionList([["name", "=", item.code]], `打开异常 ${item.code}`);
        }
        if (item?.targetType === "batch") {
            return this.openBatchList([["name", "=", item.code]], `打开批次 ${item.code}`);
        }
        if (item?.targetType === "wave") {
            return this.openWaveList([["name", "=", item.code]], `打开波次 ${item.code}`);
        }
        return this.openWaybillList([["name", "=", item.code]], `打开运单 ${item.code}`);
    }

    async onDrilldownClick(target) {
        if (target === "waybill") {
            return this.openWaybillList([], "运单追踪");
        }
        if (target === "exception") {
            return this.openExceptionList([["state", "in", ["open", "processing"]]], "异常处理");
        }
        if (target === "batch") {
            return this.openBatchList([], "批次跟进");
        }
    }

    async openWaybillList(domain = [], name = "运单追踪") {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name,
            res_model: "logistics.dispatch.waybill",
            views: [[false, "list"], [false, "form"]],
            domain,
        });
    }

    async openBatchList(domain = [], name = "批次列表") {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name,
            res_model: "logistics.dispatch.batch",
            views: [[false, "list"], [false, "form"]],
            domain,
        });
    }

    async openWaveList(domain = [], name = "波次列表") {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name,
            res_model: "logistics.dispatch.wave",
            views: [[false, "list"], [false, "form"]],
            domain,
        });
    }

    async openExceptionList(domain = [], name = "异常列表") {
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
        if (message.includes("权限") || message.includes("forbidden")) {
            return this.ui.noPermission;
        }
        return message || "物流工作台加载失败，请刷新页面或稍后再试。";
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
            throw new Error(payload?.data?.errors?.[0]?.error_message || payload?.message || "请求失败。");
        }
        return payload;
    }
}

const actionsRegistry = registry.category("actions");
if (!actionsRegistry.contains("logistics_web.dashboard")) {
    actionsRegistry.add("logistics_web.dashboard", LogisticsDashboardAction);
}
