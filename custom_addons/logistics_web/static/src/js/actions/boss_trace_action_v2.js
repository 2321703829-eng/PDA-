/** @odoo-module */

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

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
            subtitle: "先看风险和异常，再定位需要管理层重点关注的运单与批次。",
            badgePrimary: "管理层视角",
            badgeSecondary: "风险聚焦",
            loading: "正在加载管理看板...",
            headlineTitle: "风险概览",
            headlineHint: "优先看严重异常和待补证据，再决定是否继续下钻到运单与批次。",
            focusTitle: "重点异常对象",
            focusHint: "这些对象更适合先看异常结论，再核对责任和证据。",
            noFocus: "当前没有需要管理层重点关注的异常对象。",
            openException: "查看异常",
            openWaybill: "查看运单",
            openBatch: "查看批次",
            ownerLabel: "当前负责人",
            waybillLabel: "运单",
            batchLabel: "批次",
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
            this.state.error = error.message || "管理看板加载失败，请刷新页面或稍后再试。";
        } finally {
            this.state.loading = false;
        }
    }

    async onHeadlineCardClick(card) {
        const key = card?.key;
        if (key === "open_exceptions") {
            return this.openExceptionList([["state", "in", ["open", "processing"]]], "打开待处理异常");
        }
        if (key === "high_risk_batches") {
            return this.openBatchList([], "打开高风险批次");
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
                "打开证据缺失异常"
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
