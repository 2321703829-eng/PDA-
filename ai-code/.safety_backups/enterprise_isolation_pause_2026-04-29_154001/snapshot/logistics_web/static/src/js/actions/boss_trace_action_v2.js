/** @odoo-module */

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const HEADLINE_CARD_COPY = {
    open_exceptions: {
        tone: "danger",
        caption: "先处理仍在流转中的异常对象，避免问题继续扩散。",
    },
    high_risk_batches: {
        tone: "warning",
        caption: "优先锁定影响面较大的批次，再判断是否需要下钻。",
    },
    critical_exceptions: {
        tone: "danger",
        caption: "管理层优先确认严重异常是否已进入闭环处理。",
    },
    evidence_missing: {
        tone: "warning",
        caption: "证据链薄弱时，先确认责任和补证路径是否明确。",
    },
    today_new: {
        tone: "info",
        caption: "快速判断今天新增风险是否在可控区间内。",
    },
};

const ENTRY_GROUPS = [
    {
        key: "open_exception",
        title: "异常处理",
        hint: "先看待处理和处理中异常，再决定是否继续追责或升级。",
        actionLabel: "进入异常列表",
        method: "openOpenExceptionList",
        tone: "danger",
    },
    {
        key: "risk_batch",
        title: "风险批次",
        hint: "先锁定高风险批次，再下钻批次内的运单和异常对象。",
        actionLabel: "查看风险批次",
        method: "openHighRiskBatchList",
        tone: "warning",
    },
    {
        key: "waybill_review",
        title: "运单回看",
        hint: "进入运单列表回看业务主体，确认异常是否已影响执行结果。",
        actionLabel: "进入运单列表",
        method: "openWaybillList",
        tone: "info",
    },
];

export class LogisticsBossTraceAction extends Component {
    static template = "logistics_web.BossTraceAction";

    setup() {
        this.actionService = useService("action");
        this.state = useState({
            loading: true,
            error: "",
            headlineCards: [],
            focusObjects: [],
        });

        onWillStart(async () => {
            await this.loadBossTrace();
        });
    }

    get ui() {
        return {
            title: "管理看板",
            subtitle: "先看管理层需要立即判断的风险摘要，再进入重点对象和责任分布，避免把看板做成另一张统计页。",
            badgePrimary: "管理层视角",
            badgeSecondary: "经营判断",
            heroNoteTitle: "当前工作方向",
            heroNoteBody: "先看风险概况和重点提醒，再判断是进入异常、批次还是运单回看，不在这里堆叠大量图表。",
            loading: "正在加载管理看板...",
            noPermission: "当前账号暂无查看管理看板的权限。",
            loadFailed: "管理看板加载失败，请刷新页面或稍后再试。",
            headlineTitle: "风险概览",
            headlineHint: "先看严重异常、待处理对象和证据缺口，再决定管理层今天的关注顺序。",
            priorityTitle: "重点提醒",
            priorityHint: "这些对象更适合优先看异常结论，再核对责任和证据。",
            entryTitle: "入口分组",
            entryHint: "管理看板只给出决策入口，不替代业务列表本身。",
            analysisTitle: "管理判断",
            analysisHint: "这一层更偏经营判断和异常聚焦，而不是铺满趋势图。",
            noFocus: "当前没有需要管理层重点关注的异常对象。",
            noFocusHint: "可以先查看风险概览，或进入异常列表确认是否仍有未闭环对象。",
            emptyTitle: "当前暂无可展示的管理数据",
            emptyHint: "当管理摘要和重点对象都为空时，这里会进入空态。你可以稍后刷新，或先进入业务列表确认是否存在新数据。",
            retry: "重新加载",
            openException: "查看异常",
            openWaybill: "查看运单",
            openBatch: "查看批次",
            openAllExceptions: "进入异常列表",
            openAllBatches: "查看风险批次",
            openAllWaybills: "进入运单列表",
            ownerLabel: "当前负责人",
            waybillLabel: "运单",
            batchLabel: "批次",
            watchTitle: "异常聚焦",
            watchHint: "优先看严重级别分布和责任人集中度，判断是否需要升级处理。",
            ownerFocusTitle: "责任人关注",
            ownerFocusEmpty: "当前暂无可汇总的责任人关注项。",
            signalUrgentTitle: "待立即处理",
            signalUrgentHint: "仍处于 open / processing 且严重级别偏高的对象。",
            signalEvidenceTitle: "证据链风险",
            signalEvidenceHint: "优先确认缺证据异常是否已经进入补证动作。",
            signalBatchTitle: "批次影响面",
            signalBatchHint: "高风险批次越多，越需要先锁定批次层闭环。",
        };
    }

    get severityLabels() {
        return {
            low: "低",
            medium: "中",
            high: "高",
            critical: "严重",
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

    get headlineCardsDecorated() {
        return this.state.headlineCards.map((card) => {
            const copy = HEADLINE_CARD_COPY[card.key] || {};
            return {
                ...card,
                tone: copy.tone || card.tone || "info",
                caption: copy.caption || "",
            };
        });
    }

    get urgentFocusObjects() {
        return this.state.focusObjects.slice(0, 4);
    }

    get ownerFocusGroups() {
        const owners = new Map();
        for (const item of this.state.focusObjects) {
            const key = item.owner || "未分配";
            if (!owners.has(key)) {
                owners.set(key, {
                    owner: key,
                    count: 0,
                    urgentCount: 0,
                    criticalCount: 0,
                });
            }
            const target = owners.get(key);
            target.count += 1;
            if (item.state === "open" || item.state === "processing") {
                target.urgentCount += 1;
            }
            if (item.severity === "critical") {
                target.criticalCount += 1;
            }
        }
        return [...owners.values()].sort((a, b) => {
            if (b.criticalCount !== a.criticalCount) {
                return b.criticalCount - a.criticalCount;
            }
            if (b.urgentCount !== a.urgentCount) {
                return b.urgentCount - a.urgentCount;
            }
            return b.count - a.count;
        });
    }

    get severityGroups() {
        const groups = new Map([
            ["critical", { key: "critical", label: this.severityLabels.critical, count: 0, tone: "danger" }],
            ["high", { key: "high", label: this.severityLabels.high, count: 0, tone: "warning" }],
            ["medium", { key: "medium", label: this.severityLabels.medium, count: 0, tone: "info" }],
            ["low", { key: "low", label: this.severityLabels.low, count: 0, tone: "default" }],
        ]);
        for (const item of this.state.focusObjects) {
            const target = groups.get(item.severity);
            if (target) {
                target.count += 1;
            }
        }
        return [...groups.values()].filter((item) => item.count > 0);
    }

    get managementSignals() {
        const urgentCount = this.state.focusObjects.filter(
            (item) => ["open", "processing"].includes(item.state) && ["high", "critical"].includes(item.severity)
        ).length;
        const evidenceCard = this.headlineCardsDecorated.find((item) => item.key === "evidence_missing");
        const batchCard = this.headlineCardsDecorated.find((item) => item.key === "high_risk_batches");
        return [
            {
                key: "urgent",
                title: this.ui.signalUrgentTitle,
                value: urgentCount,
                hint: this.ui.signalUrgentHint,
                tone: "danger",
            },
            {
                key: "evidence",
                title: this.ui.signalEvidenceTitle,
                value: evidenceCard?.value ?? "--",
                hint: this.ui.signalEvidenceHint,
                tone: "warning",
            },
            {
                key: "batch",
                title: this.ui.signalBatchTitle,
                value: batchCard?.value ?? "--",
                hint: this.ui.signalBatchHint,
                tone: "info",
            },
        ];
    }

    get entryGroups() {
        return ENTRY_GROUPS;
    }

    get isEmpty() {
        return !this.state.loading && !this.state.error && !this.state.headlineCards.length && !this.state.focusObjects.length;
    }

    async loadBossTrace() {
        try {
            const payload = await this.apiRequest("/api/admin/logistics/boss_trace/summary", {
                method: "POST",
            });
            const data = payload.data || {};

            this.state.headlineCards = data.headline_cards || [];
            this.state.focusObjects = (data.focus_objects || []).map((item) => ({
                ...item,
                severityLabel: this.severityLabels[item.severity] || item.severity || "",
                stateLabel: this.stateLabels[item.state] || item.state || "",
            }));
            this.state.error = "";
        } catch (error) {
            this.state.headlineCards = [];
            this.state.focusObjects = [];
            this.state.error = this.mapLoadError(error);
        } finally {
            this.state.loading = false;
        }
    }

    mapLoadError(error) {
        const message = error?.message || "";
        const lower = message.toLowerCase();
        if (message.includes("权限") || lower.includes("forbidden") || lower.includes("permission")) {
            return this.ui.noPermission;
        }
        return message || this.ui.loadFailed;
    }

    async retryLoad() {
        this.state.loading = true;
        await this.loadBossTrace();
    }

    async onHeadlineCardClick(card) {
        const key = card?.key;
        if (key === "open_exceptions") {
            return this.openOpenExceptionList();
        }
        if (key === "high_risk_batches") {
            return this.openHighRiskBatchList();
        }
        if (key === "critical_exceptions") {
            return this.openExceptionList(
                [["state", "in", ["open", "processing"]], ["severity_level", "=", "critical"]],
                "打开严重异常"
            );
        }
        if (key === "evidence_missing") {
            return this.openExceptionList(
                [["state", "in", ["open", "processing"]], ["exception_type", "=", "evidence_missing"]],
                "打开缺少证据异常"
            );
        }
        if (key === "today_new") {
            return this.openExceptionList([], "打开今日新增异常");
        }
    }

    async onFocusObjectClick(item) {
        if (item?.exception_id) {
            return this.openExceptionForm(item.exception_id, `异常 ${item.code}`);
        }
        return this.openExceptionList([["name", "=", item.code]], `打开异常 ${item.code}`);
    }

    async onFocusExceptionClick(ev, item) {
        ev.stopPropagation();
        return this.onFocusObjectClick(item);
    }

    async onFocusWaybillClick(ev, item) {
        ev.stopPropagation();
        if (!item?.waybill_id) {
            return;
        }
        return this.openWaybillForm(item.waybill_id, item.waybill || "运单");
    }

    async onFocusBatchClick(ev, item) {
        ev.stopPropagation();
        if (!item?.batch_id) {
            return;
        }
        return this.openBatchForm(item.batch_id, item.batch || "批次");
    }

    async onEntryGroupClick(group) {
        const method = group?.method;
        if (method && typeof this[method] === "function") {
            return this[method]();
        }
    }

    async openOpenExceptionList() {
        return this.openExceptionList([["state", "in", ["open", "processing"]]], "打开待处理异常");
    }

    async openHighRiskBatchList() {
        return this.openBatchList([], "打开高风险批次");
    }

    async openWaybillList() {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "运单列表",
            res_model: "logistics.dispatch.waybill",
            views: [[false, "list"], [false, "form"]],
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

    async openExceptionForm(resId, name = "打开异常") {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name,
            res_model: "logistics.trace.exception",
            views: [[false, "form"]],
            res_id: resId,
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

    async openBatchForm(resId, name = "打开批次") {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name,
            res_model: "logistics.dispatch.batch",
            views: [[false, "form"]],
            res_id: resId,
        });
    }

    async openWaybillForm(resId, name = "打开运单") {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name,
            res_model: "logistics.dispatch.waybill",
            views: [[false, "form"]],
            res_id: resId,
        });
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
if (!actionsRegistry.contains("logistics_web.boss_trace")) {
    actionsRegistry.add("logistics_web.boss_trace", LogisticsBossTraceAction);
}
