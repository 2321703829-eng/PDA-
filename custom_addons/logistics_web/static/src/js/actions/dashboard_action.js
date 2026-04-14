/** @odoo-module */

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";

export class LogisticsDashboardAction extends Component {
    static template = "logistics_web.DashboardAction";

    setup() {
        this.orm = useService("orm");
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
            title: "管理工作台",
            subtitle: "先看哪些对象需要关注，再下钻到运单、批次和异常。",
            badgePrimary: "P0入口",
            badgeSecondary: "管理视角",
            loading: "正在加载工作台摘要...",
            sectionSummaryTitle: "今日概览",
            sectionSummaryHint: "通过这些卡片先判断应优先查看哪些对象。",
            sectionQueueTitle: "优先处理队列",
            sectionQueueHint: "这些对象应在常规浏览前优先处理。",
            sectionRecentTitle: "最近变更",
            sectionRecentHint: "快速查看最新异常或证据变化。",
            sectionDrilldownTitle: "下一步下钻目标",
            sectionDrilldownHint: "工作台应引导用户进入运单、异常和批次详情页。",
            queueOwner: "负责人",
            noPriority: "当前没有需要优先查看的对象。",
            noRecent: "当前还没有最近变更。",
            openWaybillTitle: "打开运单追踪",
            openWaybillHint: "使用运单列表进行第一轮筛选和详情查看。",
            openExceptionTitle: "打开当前异常",
            openExceptionHint: "使用异常列表处理活动问题并安排后续跟进。",
            openBatchTitle: "打开批次追踪",
            openBatchHint: "当风险集中在某个执行批次时，进入批次页继续分析。",
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
            medium: "中",
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

    extractTime(value) {
        return value ? value.slice(11, 16) : "--:--";
    }

    buildExceptionTitle(item) {
        const typeLabel = this.exceptionTypeLabels[item.exception_type] || item.exception_type || "异常";
        const waybillName = item.waybill_id?.[1] || "未知运单";
        return `${typeLabel}上报于${waybillName}`;
    }

    buildRecentExceptionTitle(item) {
        const severityLabel = this.severityLabels[item.severity_level] || item.severity_level || "未知";
        return `${severityLabel}级异常已更新`;
    }

    buildExceptionHint(item) {
        const parts = [];
        if (item.waybill_id?.[1]) {
            parts.push(`运单 ${item.waybill_id[1]}`);
        }
        if (item.batch_id?.[1]) {
            parts.push(`批次 ${item.batch_id[1]}`);
        }
        if (item.trace_event_id?.[1]) {
            parts.push(`留痕 ${item.trace_event_id[1]}`);
        }
        if (item.description) {
            parts.push(item.description.slice(0, 120));
        }
        return parts.join(" | ") || "异常详情可在异常记录中查看。";
    }

    async loadDashboard() {
        try {
            const openDomain = [["state", "in", ["open", "processing"]]];
            const [
                pendingExceptionCount,
                evidenceMissingCount,
                newDisputeCount,
                highRiskBatchRows,
                priorityExceptions,
                recentExceptions,
            ] = await Promise.all([
                this.orm.call("logistics.trace.exception", "search_count", [openDomain]),
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
                    [
                        ["state", "in", ["open", "processing", "resolved"]],
                        ["severity_level", "in", ["high", "critical"]],
                        ["batch_id", "!=", false],
                    ],
                    ["batch_id"],
                    { limit: 200 }
                ),
                this.orm.searchRead(
                    "logistics.trace.exception",
                    openDomain,
                    [
                        "name",
                        "state",
                        "exception_type",
                        "description",
                        "process_owner_name",
                        "reporter_user_name",
                        "waybill_id",
                        "batch_id",
                        "trace_event_id",
                        "report_time",
                    ],
                    { order: "is_overdue desc, report_time desc, id desc", limit: 5 }
                ),
                this.orm.searchRead(
                    "logistics.trace.exception",
                    [],
                    [
                        "id",
                        "severity_level",
                        "description",
                        "waybill_id",
                        "batch_id",
                        "trace_event_id",
                        "report_time",
                    ],
                    { order: "report_time desc, id desc", limit: 5 }
                ),
            ]);

            const highRiskBatchCount = new Set(
                (highRiskBatchRows || []).map((row) => row.batch_id && row.batch_id[0]).filter(Boolean)
            ).size;

            this.state.summaryCards = [
                { key: "pending_exception_count", label: "待处理异常", value: pendingExceptionCount, tone: pendingExceptionCount ? "danger" : "default" },
                { key: "evidence_missing_count", label: "证据缺失", value: evidenceMissingCount, tone: evidenceMissingCount ? "warning" : "default" },
                { key: "high_risk_batch_count", label: "高风险批次", value: highRiskBatchCount, tone: highRiskBatchCount ? "danger" : "default" },
                { key: "new_dispute_count", label: "今日新增争议", value: newDisputeCount, tone: newDisputeCount ? "info" : "default" },
            ];

            this.state.priorityItems = (priorityExceptions || []).map((item) => ({
                key: item.name,
                code: item.name,
                title: this.buildExceptionTitle(item),
                status: item.state,
                statusLabel: this.stateLabels[item.state] || item.state,
                targetType: "exception",
                owner: item.process_owner_name || item.reporter_user_name || "未分配",
                hint: this.buildExceptionHint(item),
            }));

            this.state.recentChanges = (recentExceptions || []).map((item) => ({
                key: `exception_${item.id}`,
                time: this.extractTime(item.report_time),
                title: this.buildRecentExceptionTitle(item),
                summary: this.buildExceptionHint(item),
            }));

            this.state.error = "";
        } catch {
            this.state.summaryCards = [];
            this.state.priorityItems = [];
            this.state.recentChanges = [];
            this.state.error = "当前无法加载管理工作台，请刷新页面或检查后端日志。";
        } finally {
            this.state.loading = false;
        }
    }

    async onSummaryCardClick(card) {
        const key = card?.key;
        if (key === "pending_exception_count") {
            return this.openExceptionList([["state", "in", ["open", "processing"]]], "打开异常列表");
        }
        if (key === "evidence_missing_count") {
            return this.openExceptionList(
                [["state", "in", ["open", "processing"]], ["exception_type", "=", "evidence_missing"]],
                "打开证据缺失异常"
            );
        }
        if (key === "high_risk_batch_count") {
            return this.openBatchList([], "打开高风险批次");
        }
        if (key === "new_dispute_count") {
            return this.openExceptionList([], "打开今日异常");
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
            return this.openExceptionList([["state", "in", ["open", "processing"]]], "打开当前异常");
        }
        if (target === "batch") {
            return this.openBatchList([], "打开批次追踪");
        }
    }

    async openWaybillList(domain = [], name = "打开运单追踪") {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name,
            res_model: "logistics.dispatch.waybill",
            views: [[false, "list"], [false, "form"]],
            domain,
        });
    }

    async openBatchList(domain = [], name = "打开批次列表") {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name,
            res_model: "logistics.dispatch.batch",
            views: [[false, "list"], [false, "form"]],
            domain,
        });
    }

    async openWaveList(domain = [], name = "打开波次列表") {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name,
            res_model: "logistics.dispatch.wave",
            views: [[false, "list"], [false, "form"]],
            domain,
        });
    }

    async openExceptionList(domain = [], name = "打开异常列表") {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name,
            res_model: "logistics.trace.exception",
            views: [[false, "list"], [false, "form"]],
            domain,
        });
    }
}

registry.category("actions").add("logistics_web.dashboard", LogisticsDashboardAction);
