/** @odoo-module */

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";

export class LogisticsBossTraceAction extends Component {
    static template = "logistics_web.BossTraceAction";

    setup() {
        this.orm = useService("orm");
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
            title: "老板追溯总览",
            subtitle: "先看决策摘要，再下钻到需要重点关注的争议。",
            badgePrimary: "管理层视角",
            badgeSecondary: "争议聚焦",
            loading: "正在加载老板追溯摘要...",
            headlineTitle: "核心信号",
            headlineHint: "通过这些卡片判断是进入争议处理还是批次级风险查看。",
            focusTitle: "争议焦点对象",
            focusHint: "这些是当前最可能需要管理层关注的争议对象。",
            noFocus: "当前没有需要管理层重点关注的争议对象。",
            openException: "打开异常",
            openWaybill: "打开运单",
            openBatch: "打开批次",
            ownerLabel: "负责人",
            waybillLabel: "运单",
            batchLabel: "批次",
        };
    }

    get exceptionTypeLabels() {
        return {
            delay: "延误",
            damage: "破损",
            missing: "缺失",
            rejected: "拒收",
            store_closed: "门店关闭",
            signoff_problem: "签收异常",
            evidence_missing: "证据缺失",
            other: "其他",
        };
    }

    get severityLabels() {
        return {
            low: "低",
            medium: "中等",
            high: "高",
            critical: "严重",
        };
    }

    get stateLabels() {
        return {
            draft: "草稿",
            open: "打开",
            processing: "处理中",
            resolved: "已解决",
            closed: "已关闭",
            cancelled: "已取消",
        };
    }

    get todayStart() {
        return this.formatDateTime(new Date(new Date().setHours(0, 0, 0, 0)));
    }

    get todayEnd() {
        return this.formatDateTime(new Date(new Date().setHours(23, 59, 59, 999)));
    }

    formatDateTime(date) {
        const pad = (value) => String(value).padStart(2, "0");
        return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
    }

    buildExceptionTitle(item) {
        const typeLabel = this.exceptionTypeLabels[item.exception_type] || item.exception_type || "异常";
        const waybillName = item.waybill_id?.[1] || "未知运单";
        return `${typeLabel}上报于${waybillName}`;
    }

    buildExceptionHint(item) {
        const parts = [];
        if (item.waybill_id?.[1]) {
            parts.push(`运单: ${item.waybill_id[1]}`);
        }
        if (item.batch_id?.[1]) {
            parts.push(`批: ${item.batch_id[1]}`);
        }
        if (item.trace_event_id?.[1]) {
            parts.push(`留痕: ${item.trace_event_id[1]}`);
        }
        if (item.description) {
            parts.push(item.description.slice(0, 120));
        }
        return parts.join(" | ") || "异常详情可在异常记录中查看。";
    }

    async loadBossTrace() {
        try {
            const openDomain = [["state", "in", ["open", "processing"]]];
            const [openDisputes, criticalDisputes, highRiskBatchRows, evidenceMissing, todayNew, focusExceptions] =
                await Promise.all([
                    this.orm.call("logistics.trace.exception", "search_count", [openDomain]),
                    this.orm.call("logistics.trace.exception", "search_count", [[
                        ["state", "in", ["open", "processing"]],
                        ["severity_level", "=", "critical"],
                    ]]),
                    this.orm.searchRead(
                        "logistics.trace.exception",
                        [
                            ["state", "in", ["open", "processing"]],
                            ["severity_level", "in", ["high", "critical"]],
                            ["batch_id", "!=", false],
                        ],
                        ["batch_id"],
                        { limit: 200 }
                    ),
                    this.orm.call("logistics.trace.exception", "search_count", [[
                        ["state", "in", ["open", "processing"]],
                        ["exception_type", "=", "evidence_missing"],
                    ]]),
                    this.orm.call("logistics.trace.exception", "search_count", [[
                        ["report_time", ">=", this.todayStart],
                        ["report_time", "<=", this.todayEnd],
                    ]]),
                    this.orm.searchRead(
                        "logistics.trace.exception",
                        openDomain,
                        [
                            "id",
                            "name",
                            "exception_type",
                            "severity_level",
                            "state",
                            "description",
                            "process_owner_name",
                            "reporter_user_name",
                            "waybill_id",
                            "batch_id",
                            "trace_event_id",
                        ],
                        { order: "severity_level desc, is_overdue desc, report_time desc, id desc", limit: 6 }
                    ),
                ]);

            const highRiskBatches = new Set(
                (highRiskBatchRows || []).map((row) => row.batch_id && row.batch_id[0]).filter(Boolean)
            ).size;

            this.state.headlineCards = [
                { key: "open_disputes", label: "待处理争议", value: openDisputes, tone: openDisputes ? "danger" : "default" },
                { key: "high_risk_batches", label: "高风险批次", value: highRiskBatches, tone: highRiskBatches ? "warning" : "default" },
                { key: "critical_disputes", label: "严重争议", value: criticalDisputes, tone: criticalDisputes ? "danger" : "default" },
                { key: "evidence_missing", label: "证据缺失", value: evidenceMissing, tone: evidenceMissing ? "warning" : "default" },
                { key: "today_new", label: "今日新增", value: todayNew, tone: todayNew ? "info" : "default" },
            ];

            this.state.focusObjects = (focusExceptions || []).map((item) => ({
                key: item.name,
                code: item.name,
                exception_id: item.id,
                waybill_id: item.waybill_id?.[0] || false,
                batch_id: item.batch_id?.[0] || false,
                title: this.buildExceptionTitle(item),
                severity: item.severity_level,
                severityLabel: this.severityLabels[item.severity_level] || item.severity_level,
                state: item.state,
                stateLabel: this.stateLabels[item.state] || item.state,
                owner: item.process_owner_name || item.reporter_user_name || "未分配",
                waybill: item.waybill_id?.[1] || "",
                batch: item.batch_id?.[1] || "",
                hint: this.buildExceptionHint(item),
            }));

            this.state.error = "";
        } catch {
            this.state.headlineCards = [];
            this.state.focusObjects = [];
            this.state.error = "当前无法加载老板追溯总览，请刷新页面或检查后端日志。";
        } finally {
            this.state.loading = false;
        }
    }

    async onHeadlineCardClick(card) {
        const key = card?.key;
        if (key === "open_disputes") {
            return this.openExceptionList([["state", "in", ["open", "processing"]]], "打开待处理争议");
        }
        if (key === "high_risk_batches") {
            return this.openBatchList([], "打开高风险批次");
        }
        if (key === "critical_disputes") {
            return this.openExceptionList(
                [["state", "in", ["open", "processing"]], ["severity_level", "=", "critical"]],
                "打开严重争议"
            );
        }
        if (key === "evidence_missing") {
            return this.openExceptionList(
                [["state", "in", ["open", "processing"]], ["exception_type", "=", "evidence_missing"]],
                "打开证据缺失异常"
            );
        }
        if (key === "today_new") {
            return this.openExceptionList([], "打开今日异常");
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

    async openExceptionList(domain = [], name = "异常") {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name,
            res_model: "logistics.trace.exception",
            views: [
                [false, "list"],
                [false, "form"],
            ],
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

    async openBatchList(domain = [], name = "打开批次列表") {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name,
            res_model: "logistics.dispatch.batch",
            views: [
                [false, "list"],
                [false, "form"],
            ],
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
}

registry.category("actions").add("logistics_web.boss_trace", LogisticsBossTraceAction);
