/** @odoo-module */

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

export class LogisticsImportResultAction extends Component {
    static template = "logistics_web.ImportResultAction";
    static components = { Layout };
    static props = { ...standardActionServiceProps };

    setup() {
        this.actionService = this.env.services.action;
        this.notification = this.env.services.notification;
        this.display = {
            controlPanel: false,
            searchPanel: false,
        };
        this.state = useState({
            loading: true,
            refreshing: false,
            error: "",
            importBatchNo: this.props.action?.params?.import_batch_no || "",
            sourceModel: this.props.action?.params?.source_model || "logistics.dispatch.waybill",
            result: null,
        });

        onWillStart(async () => {
            await this.loadResult();
        });
    }

    get ui() {
        return {
            title: "导入结果",
            subtitle: "回看本次导入批次的结果状态、关键统计和后续核验入口。",
            refresh: "刷新结果",
            downloadErrorReport: "下载错误报告",
            openWaybillList: "进入运单列表",
            continueReview: "按导入批次继续核验",
            backToImportCenter: "返回导入中心",
            resultSummaryTitle: "结果摘要",
            batchInfoTitle: "文件与批次信息",
            nextActionTitle: "后续动作",
            failureTitle: "失败说明与错误报告",
            loading: "正在加载导入结果...",
            noReport: "当前批次无错误报告",
            missingBatch: "当前未指定导入批次，暂时无法查看导入结果。",
            emptyResult: "当前批次暂无可展示的导入结果。",
            notFound: "当前导入批次不存在，或结果已不可查看。",
            loadFailed: "导入结果加载失败，请刷新后重试。",
            noPermission: "当前账号暂无查看导入结果的权限。",
        };
    }

    get result() {
        return this.state.result;
    }

    get statusTone() {
        const status = this.result?.status;
        if (status === "finished") {
            return "info";
        }
        if (status === "failed" || status === "expired") {
            return "danger";
        }
        return "warning";
    }

    get summaryText() {
        const status = this.result?.status;
        if (status === "finished") {
            return "本次导入已完成，可继续前往运单列表回看写入结果。";
        }
        if (status === "failed") {
            return "本次导入未成功写入，请先查看失败原因和错误报告。";
        }
        if (status === "expired") {
            return "当前批次已失效，如需继续处理，请返回导入中心重新发起。";
        }
        if (status === "importing") {
            return "当前批次仍在处理，请稍后刷新结果。";
        }
        if (status === "prechecked") {
            return "当前批次仍停留在预校验阶段，可返回导入中心继续处理。";
        }
        return "请先确认本次导入结果，再决定后续核验动作。";
    }

    get resultCards() {
        const result = this.result || {};
        return [
            { key: "total", label: "总行数", value: this.formatCount(result.total_row_count) },
            { key: "passed", label: "通过行数", value: this.formatCount(result.passed_row_count) },
            { key: "failed", label: "失败行数", value: this.formatCount(result.failed_row_count), tone: result.failed_row_count ? "warning" : "" },
            { key: "waybill", label: "新建运单数", value: this.formatCount(result.created_waybill_count) },
            { key: "customer", label: "新建客户明细数", value: this.formatCount(result.created_customer_line_count) },
            { key: "goods", label: "新建货物明细数", value: this.formatCount(result.created_goods_line_count) },
        ];
    }

    get batchInfoCards() {
        const result = this.result || {};
        return [
            {
                key: "file",
                title: "文件信息",
                items: [
                    ["文件名", result.file_name || "--"],
                    ["模板编码", result.template_code || "--"],
                    ["模板版本", result.template_version || "--"],
                ],
            },
            {
                key: "batch",
                title: "批次信息",
                items: [
                    ["导入批次号", result.import_batch_no || this.state.importBatchNo || "--"],
                    ["确认时间", result.confirmed_at || "--"],
                    ["完成时间", result.finished_at || "--"],
                    ["结果状态", result.status_label || "--"],
                ],
            },
        ];
    }

    get canDownloadErrorReport() {
        return Boolean(this.result?.error_report_url);
    }

    get canOpenWaybillList() {
        const result = this.result;
        if (!result) {
            return false;
        }
        return Boolean(
            result.status === "finished" ||
            result.created_waybill_count ||
            result.created_customer_line_count ||
            result.created_goods_line_count
        );
    }

    get shouldShowFailureSection() {
        const result = this.result;
        if (!result) {
            return false;
        }
        return Boolean(result.failure_reason || result.failed_record_count || result.failed_row_count || result.error_report_url);
    }

    async loadResult({ silent = false } = {}) {
        if (!silent) {
            this.state.loading = true;
        }
        this.state.refreshing = silent;
        this.state.error = "";
        if (!this.state.importBatchNo) {
            this.state.loading = false;
            this.state.result = null;
            this.state.error = this.ui.missingBatch;
            return;
        }
        try {
            const payload = await this.apiRequest(
                `/api/admin/logistics/imports/waybill-standard/result?import_batch_no=${encodeURIComponent(this.state.importBatchNo)}`
            );
            this.state.result = payload.data || null;
            if (!payload.data) {
                this.state.error = this.ui.emptyResult;
            }
        } catch (error) {
            this.state.result = null;
            this.state.error = this.mapLoadError(error);
        } finally {
            this.state.loading = false;
            this.state.refreshing = false;
        }
    }

    async refreshResult() {
        await this.loadResult({ silent: true });
    }

    downloadErrorReport() {
        if (!this.canDownloadErrorReport) {
            return;
        }
        window.open(this.result.error_report_url, "_blank", "noopener");
    }

    async openWaybillList() {
        if (!this.canOpenWaybillList) {
            return;
        }
        return this.actionService.doAction("logistics_dispatch.action_logistics_dispatch_waybill");
    }

    async continueReviewByBatch() {
        if (!this.state.importBatchNo) {
            return;
        }
        this.notification.add(`已打开导入批次 ${this.state.importBatchNo} 的运单核验入口。`, { type: "info" });
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: `导入批次 ${this.state.importBatchNo} 运单`,
            res_model: "logistics.dispatch.waybill",
            views: [[false, "list"], [false, "form"]],
            context: {
                import_batch_no: this.state.importBatchNo,
                source_model: this.state.sourceModel,
            },
        });
    }

    async backToImportCenter() {
        return this.actionService.doAction({
            type: "ir.actions.client",
            name: "导入中心",
            tag: "logistics_web.import_center",
            params: {
                source_model: this.state.sourceModel,
                import_batch_no: this.state.importBatchNo,
            },
        });
    }

    formatCount(value) {
        if (value === 0) {
            return "0";
        }
        return value || value === 0 ? String(value) : "--";
    }

    mapLoadError(error) {
        const message = error?.message || "";
        if (message.includes("权限")) {
            return this.ui.noPermission;
        }
        if (message.includes("未找到") || message.includes("不存在")) {
            return this.ui.notFound;
        }
        return message || this.ui.loadFailed;
    }

    async apiRequest(url, options = {}) {
        const response = await fetch(url, {
            method: options.method || "GET",
            headers: options.headers || {},
            body: options.body,
        });
        const payload = await response.json().catch(() => null);
        if (!response.ok || !payload || payload.code !== 0) {
            const errorMessage =
                payload?.data?.errors?.[0]?.error_message || payload?.message || "请求失败，请稍后重试。";
            throw new Error(errorMessage);
        }
        return payload;
    }
}

const actionsRegistry = registry.category("actions");
if (!actionsRegistry.contains("logistics_web.import_result")) {
    actionsRegistry.add("logistics_web.import_result", LogisticsImportResultAction);
}
