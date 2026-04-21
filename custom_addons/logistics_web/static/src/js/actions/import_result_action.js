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
            title: "\u5bfc\u5165\u7ed3\u679c",
            subtitle: "\u56de\u770b\u672c\u6b21\u5bfc\u5165\u6279\u6b21\u7684\u7ed3\u679c\u72b6\u6001\u3001\u5173\u952e\u7edf\u8ba1\u548c\u540e\u7eed\u6838\u9a8c\u5165\u53e3\u3002",
            badgePrimary: "\u5bfc\u5165\u56de\u770b",
            badgeSecondary: "\u7ed3\u679c\u95ed\u73af",
            heroNoteTitle: "\u5f53\u524d\u5de5\u4f5c\u65b9\u5411",
            heroNoteBody: "\u5148\u786e\u8ba4\u6279\u6b21\u72b6\u6001\u548c\u6458\u8981\uff0c\u518d\u51b3\u5b9a\u662f\u7ee7\u7eed\u6838\u9a8c\u3001\u8fdb\u5165\u8fd0\u5355\u5217\u8868\uff0c\u8fd8\u662f\u8fd4\u56de\u5bfc\u5165\u4e2d\u5fc3\u91cd\u65b0\u5904\u7406\u3002",
            refresh: "\u5237\u65b0\u7ed3\u679c",
            downloadErrorReport: "\u4e0b\u8f7d\u9519\u8bef\u62a5\u544a",
            openWaybillList: "\u8fdb\u5165\u8fd0\u5355\u5217\u8868",
            continueReview: "\u6309\u5bfc\u5165\u6279\u6b21\u7ee7\u7eed\u6838\u9a8c",
            backToImportCenter: "\u8fd4\u56de\u5bfc\u5165\u4e2d\u5fc3",
            resultSummaryTitle: "\u7ed3\u679c\u6458\u8981",
            batchInfoTitle: "\u6587\u4ef6\u4e0e\u6279\u6b21\u4fe1\u606f",
            nextActionTitle: "\u540e\u7eed\u52a8\u4f5c",
            failureTitle: "\u5931\u8d25\u8bf4\u660e\u4e0e\u9519\u8bef\u62a5\u544a",
            loading: "\u6b63\u5728\u52a0\u8f7d\u5bfc\u5165\u7ed3\u679c...",
            noReport: "\u5f53\u524d\u6279\u6b21\u65e0\u9519\u8bef\u62a5\u544a",
            missingBatch: "\u5f53\u524d\u672a\u6307\u5b9a\u5bfc\u5165\u6279\u6b21\uff0c\u6682\u65f6\u65e0\u6cd5\u67e5\u770b\u5bfc\u5165\u7ed3\u679c\u3002",
            emptyResult: "\u5f53\u524d\u6279\u6b21\u6682\u65e0\u53ef\u5c55\u793a\u7684\u5bfc\u5165\u7ed3\u679c\u3002",
            notFound: "\u5f53\u524d\u5bfc\u5165\u6279\u6b21\u4e0d\u5b58\u5728\uff0c\u6216\u7ed3\u679c\u5df2\u4e0d\u53ef\u67e5\u770b\u3002",
            loadFailed: "\u5bfc\u5165\u7ed3\u679c\u52a0\u8f7d\u5931\u8d25\uff0c\u8bf7\u5237\u65b0\u540e\u91cd\u8bd5\u3002",
            noPermission: "\u5f53\u524d\u8d26\u53f7\u6682\u65e0\u67e5\u770b\u5bfc\u5165\u7ed3\u679c\u7684\u6743\u9650\u3002",
            pendingLabel: "\u5f85\u52a0\u8f7d",
            resultHeaderTitle: "\u7ed3\u679c\u5934\u90e8",
            resultSummaryHint: "\u4f18\u5148\u9605\u8bfb\u672c\u6b21\u5bfc\u5165\u7684\u884c\u7ea7\u7ed3\u679c\u548c\u65b0\u589e\u5199\u5165\u89c4\u6a21\u3002",
            importBatchNoLabel: "\u5bfc\u5165\u6279\u6b21\u53f7",
            templateCodeLabel: "\u6a21\u677f\u7f16\u7801",
            templateVersionLabel: "\u6a21\u677f\u7248\u672c",
            batchInfoHint: "\u56de\u770b\u6587\u4ef6\u6765\u6e90\u548c\u6279\u6b21\u5904\u7406\u65f6\u95f4\uff0c\u4e0d\u5728\u7ed3\u679c\u9875\u505a\u53ef\u7f16\u8f91\u8868\u5355\u3002",
            nextActionHint: "\u4f18\u5148\u7ee7\u7eed\u6838\u9a8c\u7ed3\u679c\uff0c\u518d\u51b3\u5b9a\u662f\u5426\u8fd4\u56de\u5bfc\u5165\u4e2d\u5fc3\u91cd\u65b0\u5904\u7406\u3002",
            failureHint: "\u5931\u8d25\u8bb0\u5f55\u6216\u9519\u8bef\u62a5\u544a\u5b58\u5728\u65f6\uff0c\u8fd9\u91cc\u4f1a\u5c55\u5f00\u663e\u793a\u5904\u7406\u63d0\u793a\u3002",
            failedRecordCountLabel: "\u5931\u8d25\u8bb0\u5f55\u6570\uff1a",
            hasErrorReportLabel: "\u5f53\u524d\u6279\u6b21\u5b58\u5728\u9519\u8bef\u62a5\u544a",
            noErrorReportLabel: "\u5f53\u524d\u6279\u6b21\u65e0\u9519\u8bef\u62a5\u544a",
            refreshingText: "\u5237\u65b0\u4e2d...",
            fileInfoTitle: "\u6587\u4ef6\u4fe1\u606f",
            batchInfoCardTitle: "\u6279\u6b21\u4fe1\u606f",
            fileNameLabel: "\u6587\u4ef6\u540d",
            confirmedAtLabel: "\u786e\u8ba4\u65f6\u95f4",
            finishedAtLabel: "\u5b8c\u6210\u65f6\u95f4",
            statusLabel: "\u7ed3\u679c\u72b6\u6001",
        };
    }

    get result() {
        return this.state.result;
    }

    get statusTone() {
        const status = this.result?.status;
        if (status === "finished") {
            return "success";
        }
        if (status === "failed" || status === "expired") {
            return "danger";
        }
        return "warning";
    }

    get summaryText() {
        const status = this.result?.status;
        if (status === "finished") {
            return "\u672c\u6b21\u5bfc\u5165\u5df2\u5b8c\u6210\uff0c\u53ef\u4ee5\u7ee7\u7eed\u524d\u5f80\u8fd0\u5355\u5217\u8868\u56de\u770b\u5199\u5165\u7ed3\u679c\u3002";
        }
        if (status === "failed") {
            return "\u672c\u6b21\u5bfc\u5165\u672a\u6210\u529f\u5199\u5165\uff0c\u8bf7\u5148\u67e5\u770b\u5931\u8d25\u539f\u56e0\u548c\u9519\u8bef\u62a5\u544a\u3002";
        }
        if (status === "expired") {
            return "\u5f53\u524d\u6279\u6b21\u5df2\u5931\u6548\uff0c\u5982\u9700\u7ee7\u7eed\u5904\u7406\uff0c\u8bf7\u8fd4\u56de\u5bfc\u5165\u4e2d\u5fc3\u91cd\u65b0\u53d1\u8d77\u3002";
        }
        if (status === "importing") {
            return "\u5f53\u524d\u6279\u6b21\u4ecd\u5728\u5904\u7406\uff0c\u8bf7\u7a0d\u540e\u5237\u65b0\u7ed3\u679c\u3002";
        }
        if (status === "prechecked") {
            return "\u5f53\u524d\u6279\u6b21\u4ecd\u505c\u7559\u5728\u9884\u6821\u9a8c\u9636\u6bb5\uff0c\u53ef\u8fd4\u56de\u5bfc\u5165\u4e2d\u5fc3\u7ee7\u7eed\u5904\u7406\u3002";
        }
        return "\u8bf7\u5148\u786e\u8ba4\u672c\u6b21\u5bfc\u5165\u7ed3\u679c\uff0c\u518d\u51b3\u5b9a\u540e\u7eed\u6838\u9a8c\u52a8\u4f5c\u3002";
    }

    get resultCards() {
        const result = this.result || {};
        return [
            { key: "total", label: "\u603b\u884c\u6570", value: this.formatCount(result.total_row_count), caption: "\u786e\u8ba4\u672c\u6b21\u5bfc\u5165\u8986\u76d6\u8303\u56f4" },
            { key: "passed", label: "\u901a\u8fc7\u884c\u6570", value: this.formatCount(result.passed_row_count), tone: "success", caption: "\u4f18\u5148\u770b\u53ef\u7ee7\u7eed\u6838\u9a8c\u7684\u6709\u6548\u884c" },
            { key: "failed", label: "\u5931\u8d25\u884c\u6570", value: this.formatCount(result.failed_row_count), tone: result.failed_row_count ? "warning" : "", caption: "\u5931\u8d25\u884c\u5b58\u5728\u65f6\u4f18\u5148\u68c0\u67e5\u9519\u8bef\u62a5\u544a" },
            { key: "waybill", label: "\u65b0\u5efa\u8fd0\u5355\u6570", value: this.formatCount(result.created_waybill_count), caption: "\u786e\u8ba4\u4e3b\u4e1a\u52a1\u5bf9\u8c61\u5199\u5165\u89c4\u6a21" },
            { key: "customer", label: "\u65b0\u5efa\u5ba2\u6237\u660e\u7ec6\u6570", value: this.formatCount(result.created_customer_line_count), caption: "\u56de\u770b\u5ba2\u6237\u7ef4\u5ea6\u6269\u5c55\u5199\u5165\u91cf" },
            { key: "goods", label: "\u65b0\u5efa\u8d27\u7269\u660e\u7ec6\u6570", value: this.formatCount(result.created_goods_line_count), caption: "\u786e\u8ba4\u8d27\u7269\u660e\u7ec6\u8865\u5145\u662f\u5426\u5b8c\u6574" },
        ];
    }

    get batchInfoCards() {
        const result = this.result || {};
        return [
            {
                key: "file",
                title: this.ui.fileInfoTitle,
                items: [
                    [this.ui.fileNameLabel, result.file_name || "--"],
                    [this.ui.templateCodeLabel, result.template_code || "--"],
                    [this.ui.templateVersionLabel, result.template_version || "--"],
                ],
            },
            {
                key: "batch",
                title: this.ui.batchInfoCardTitle,
                items: [
                    [this.ui.importBatchNoLabel, result.import_batch_no || this.state.importBatchNo || "--"],
                    [this.ui.confirmedAtLabel, result.confirmed_at || "--"],
                    [this.ui.finishedAtLabel, result.finished_at || "--"],
                    [this.ui.statusLabel, result.status_label || "--"],
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
        this.notification.add(`\u5df2\u6253\u5f00\u5bfc\u5165\u6279\u6b21 ${this.state.importBatchNo} \u7684\u8fd0\u5355\u6838\u9a8c\u5165\u53e3\u3002`, { type: "info" });
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: `\u5bfc\u5165\u6279\u6b21 ${this.state.importBatchNo} \u8fd0\u5355`,
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
            name: "\u5bfc\u5165\u4e2d\u5fc3",
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
        const lower = message.toLowerCase();
        if (message.includes("\u6743\u9650") || lower.includes("forbidden") || lower.includes("permission")) {
            return this.ui.noPermission;
        }
        if (message.includes("\u672a\u627e\u5230") || message.includes("\u4e0d\u5b58\u5728") || lower.includes("not found")) {
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
                payload?.data?.errors?.[0]?.error_message || payload?.message || this.ui.loadFailed;
            throw new Error(errorMessage);
        }
        return payload;
    }
}

const actionsRegistry = registry.category("actions");
if (!actionsRegistry.contains("logistics_web.import_result")) {
    actionsRegistry.add("logistics_web.import_result", LogisticsImportResultAction);
}
