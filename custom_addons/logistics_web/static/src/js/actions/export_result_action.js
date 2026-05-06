/** @odoo-module */

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

const TASK_LINE_PAGE_SIZE = 20;
const TASK_ERROR_PAGE_SIZE = 20;
const TASK_LINE_STATUS_FILTERS = [
    { value: "all", label: "全部" },
    { value: "pending", label: "待处理" },
    { value: "success", label: "成功" },
    { value: "failed", label: "失败" },
    { value: "skipped", label: "跳过" },
];

const EXPORT_OBJECT_CONFIG = {
    dispatch_main: {
        objectLabel: "运单导出",
        listLabel: "运单列表",
        listActionXmlid: "logistics_dispatch.action_logistics_dispatch_waybill",
        successNoun: "运单导出",
    },
    customer_profile: {
        objectLabel: "客户画像导出",
        listLabel: "客户画像列表",
        listActionXmlid: "logistics_base.action_logistics_partner_profile",
        successNoun: "客户画像导出",
    },
    product_profile: {
        objectLabel: "货物画像导出",
        listLabel: "商品列表",
        listActionXmlid: "stock.product_template_action_product",
        successNoun: "货物画像导出",
    },
    evidence_image_bundle: {
        objectLabel: "图片批量导出",
        listLabel: "运单列表",
        listActionXmlid: "logistics_dispatch.action_logistics_dispatch_waybill",
        successNoun: "图片批量导出",
    },
};

export class LogisticsExportResultAction extends Component {
    static template = "logistics_web.ExportResultAction";
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
            taskLinesLoading: false,
            taskErrorsLoading: false,
            error: "",
            taskLinesError: "",
            taskErrorsError: "",
            taskNo: this.props.action?.params?.task_no || "",
            sourceModel: this.props.action?.params?.source_model || "logistics.dispatch.waybill",
            result: null,
            taskLines: [],
            taskLineTotal: 0,
            taskLinePage: 1,
            taskLinePageSize: TASK_LINE_PAGE_SIZE,
            taskLineTotalPages: 1,
            taskLineStatusFilter: "all",
            taskLineShowingFrom: 0,
            taskLineShowingTo: 0,
            taskErrors: [],
            taskErrorTotal: 0,
            taskErrorPage: 1,
            taskErrorPageSize: TASK_ERROR_PAGE_SIZE,
            taskErrorTotalPages: 1,
            taskErrorShowingFrom: 0,
            taskErrorShowingTo: 0,
        });

        onWillStart(async () => {
            await this.loadResult();
        });
    }

    get result() {
        return this.state.result;
    }

    get exportObjectConfig() {
        const objectType = this.result?.object_type || "dispatch_main";
        return EXPORT_OBJECT_CONFIG[objectType] || EXPORT_OBJECT_CONFIG.dispatch_main;
    }

    get sourceListMeta() {
        const sourcePage = this.result?.source_scope?.source_page || "";
        const objectType = this.result?.object_type || "dispatch_main";
        if (objectType === "evidence_image_bundle" && sourcePage.startsWith("evidence")) {
            return {
                label: "证据列表",
                actionXmlid: "logistics_trace_evidence.action_logistics_trace_evidence",
            };
        }
        if (objectType === "product_profile" && sourcePage.startsWith("product_unit")) {
            return {
                label: "商品规格列表",
                actionXmlid: "logistics_base.action_logistics_product_unit",
            };
        }
        return {
            label: this.exportObjectConfig.listLabel,
            actionXmlid: this.exportObjectConfig.listActionXmlid,
        };
    }

    get ui() {
        const sourceList = this.sourceListMeta;
        return {
            title: "导出结果",
            subtitle: "回看本次导出任务的执行结果、文件状态、行结果和错误明细。",
            refresh: "刷新结果",
            refreshingText: "刷新中...",
            downloadFile: "下载导出文件",
            downloadErrorReport: "下载错误报告",
            openWaybillList: `进入${sourceList.label}`,
            backToWaybillList: `返回${sourceList.label}`,
            loading: "正在加载导出结果...",
            detailLoading: "正在加载任务明细...",
            missingTask: "当前未指定导出任务，暂时无法查看导出结果。",
            emptyResult: "当前任务暂无可展示的导出结果。",
            loadFailed: "导出结果加载失败，请刷新后重试。",
            taskLinesLoadFailed: "导出行结果加载失败，请稍后重试。",
            taskErrorsLoadFailed: "导出错误明细加载失败，请稍后重试。",
            noPermission: "当前账号暂无查看导出结果的权限。",
            notFound: "当前导出任务不存在，或结果已不可查看。",
            noDownloadFile: "当前任务暂无可下载的导出文件。",
            noErrorReport: "当前任务暂无错误报告。",
            heroNoteTitle: "查看建议",
            heroNoteBody: `先确认任务摘要和文件状态，再核对失败或跳过的任务行，最后决定是否回到${sourceList.label}继续处理。`,
            summaryTitle: "结果摘要",
            infoTitle: "任务与文件信息",
            lineTitle: "行结果明细",
            errorTitle: "错误明细",
            lineFilterTitle: "状态筛选",
            lineNoLabel: "任务行号",
            statusLabel: "状态",
            businessKeyLabel: "业务键",
            displayNameLabel: "显示名称",
            countSummaryLabel: "导出统计",
            messageLabel: "处理说明",
            errorStageLabel: "失败阶段",
            fieldNameLabel: "字段名",
            rawValueLabel: "原始值",
            errorCodeLabel: "错误码",
            errorMessageLabel: "错误说明",
            prevPage: "上一页",
            nextPage: "下一页",
            linesEmptyTitle: "暂无行结果",
            linesEmptyHint: "当前任务还没有可展示的行结果，可以稍后刷新再看。",
            errorsEmptyTitle: "暂无错误明细",
            errorsEmptyHint: "当前任务没有错误明细，或错误明细尚未生成。",
            summaryHint: "优先确认成功、失败、跳过数量和导出文件可用性，再决定是否继续处理。",
            infoHint: "这里展示任务号、入口、发起人、执行时间和导出文件信息。",
            fileNameLabel: "文件名",
            fileSizeLabel: "文件大小",
            objectTypeLabel: "对象类型",
            entryTypeLabel: "入口类型",
            exportModeLabel: "导出模式",
            packageStructureLabel: "包结构",
            operatorLabel: "操作人",
            sourcePageLabel: "来源页面",
            selectedCountLabel: "选中数量",
            startedAtLabel: "开始时间",
            finishedAtLabel: "完成时间",
        };
    }

    get statusTone() {
        const status = this.result?.status;
        if (status === "success") {
            return "success";
        }
        if (status === "partial_failed") {
            return "warning";
        }
        if (status === "failed" || status === "expired" || status === "cancelled") {
            return "danger";
        }
        return "info";
    }

    get summaryText() {
        const status = this.result?.status;
        const { successNoun } = this.exportObjectConfig;
        const { label } = this.sourceListMeta;
        if (status === "success") {
            return `本次${successNoun}已经完成，主文件已可下载，可以继续回到${label}核对结果。`;
        }
        if (status === "partial_failed") {
            return `本次${successNoun}已完成，但存在失败或跳过记录，建议先查看错误明细和错误报告。`;
        }
        if (status === "failed") {
            return `本次${successNoun}未成功生成可用文件，建议先查看错误明细，再决定是否重试。`;
        }
        if (status === "expired") {
            return "当前导出文件已过期，如需继续使用，请重新发起导出。";
        }
        if (status === "running" || status === "pending") {
            return "当前任务仍在处理中，可以稍后刷新查看最新结果。";
        }
        return "请先确认当前任务状态，再决定是否下载文件或返回列表继续处理。";
    }

    get summaryCards() {
        const result = this.result || {};
        const business = result.business_summary || {};
        const metrics = result.business_metrics || {};
        const baseCards = [
            {
                key: "total",
                label: "总任务行",
                value: this.formatCount(result.total_count),
                caption: "本次导出的入口对象数量。",
            },
            {
                key: "success",
                label: "已导出",
                value: this.formatCount(result.success_count),
                tone: "success",
                caption: "成功生成内容的任务行。",
            },
            {
                key: "failed",
                label: "未导出-系统异常",
                value: this.formatCount(result.fail_count),
                tone: result.fail_count ? "danger" : "",
                caption: "执行失败的任务行。",
            },
            {
                key: "skipped",
                label: "未导出-数据缺失",
                value: this.formatCount(result.skipped_count),
                tone: result.skipped_count ? "warning" : "",
                caption: "因无下游数据等原因跳过的任务行。",
            },
        ];

        if (result.object_type === "customer_profile") {
            return [
                ...baseCards,
                {
                    key: "customer_profile",
                    label: "导出客户",
                    value: this.formatCount(metrics.customer_count),
                    caption: "写入 CustomerProfile Sheet 的客户数。",
                },
            ];
        }

        if (result.object_type === "product_profile") {
            return [
                ...baseCards,
                {
                    key: "product_profile",
                    label: "导出商品",
                    value: this.formatCount(metrics.product_count),
                    caption: "写入 ProductProfile Sheet 的商品数。",
                },
                {
                    key: "product_unit",
                    label: "导出商品规格",
                    value: this.formatCount(metrics.product_unit_count),
                    caption: "写入 ProductUnit Sheet 的规格数。",
                },
            ];
        }

        if (result.object_type === "evidence_image_bundle") {
            return [
                ...baseCards,
                {
                    key: "image_matched",
                    label: "命中图片",
                    value: this.formatCount(metrics.matched_image_count),
                    caption: "列表范围内命中的图片总数。",
                },
                {
                    key: "image_waybill",
                    label: "导出运单",
                    value: this.formatCount(metrics.waybill_count),
                    caption: "写入 ZIP 清单的运单数。",
                },
                {
                    key: "image_evidence",
                    label: "导出证据",
                    value: this.formatCount(metrics.evidence_count),
                    caption: "至少导出 1 张图片的证据数。",
                },
                {
                    key: "image_total",
                    label: "导出图片",
                    value: this.formatCount(metrics.image_count),
                    caption: "实际写入 ZIP 的图片数。",
                },
                {
                    key: "image_missing",
                    label: "未导出-数据缺失",
                    value: this.formatCount(metrics.skipped_image_count),
                    tone: metrics.skipped_image_count ? "warning" : "",
                    caption: "历史图片缺失或当前记录无可导图片，未写入 ZIP。",
                },
                {
                    key: "image_failed",
                    label: "未导出-系统异常",
                    value: this.formatCount(metrics.failed_image_count),
                    tone: metrics.failed_image_count ? "danger" : "",
                    caption: "读取或打包图片时发生系统异常，未写入 ZIP。",
                },
            ];
        }

        return [
            ...baseCards,
            {
                key: "waybill",
                label: "导出运单",
                value: this.formatCount(business.exported_waybill_count),
                caption: "写入 Waybill Sheet 的运单数。",
            },
            {
                key: "customer",
                label: "导出客户",
                value: this.formatCount(business.exported_customer_line_count),
                caption: "写入 CustomerLine Sheet 的客户数。",
            },
            {
                key: "order",
                label: "导出订单",
                value: this.formatCount(business.exported_order_line_count),
                caption: "写入 OrderLine Sheet 的订单数。",
            },
            {
                key: "goods",
                label: "导出货物",
                value: this.formatCount(business.exported_goods_line_count),
                caption: "写入 GoodsLine Sheet 的货物数。",
            },
        ];
    }

    get infoCards() {
        const result = this.result || {};
        const sourceScope = result.source_scope || {};
        const downloadFile = result.download_file || {};
        return [
            {
                key: "task",
                title: "任务信息",
                items: [
                    ["Task No", result.task_no || this.state.taskNo || "--"],
                    [this.ui.objectTypeLabel, result.object_type_label || result.object_type || "--"],
                    [this.ui.entryTypeLabel, result.entry_type_label || result.entry_type || "--"],
                    [this.ui.exportModeLabel, result.export_mode || "--"],
                    [this.ui.packageStructureLabel, result.package_structure || "--"],
                    [this.ui.operatorLabel, result.operator?.name || "--"],
                    [this.ui.startedAtLabel, result.started_at || "--"],
                    [this.ui.finishedAtLabel, result.finished_at || "--"],
                ],
            },
            {
                key: "file",
                title: "文件与范围",
                items: [
                    [this.ui.fileNameLabel, downloadFile.name || "--"],
                    [this.ui.fileSizeLabel, this.formatCount(downloadFile.size)],
                    [this.ui.sourcePageLabel, sourceScope.source_page || "--"],
                    [this.ui.selectedCountLabel, this.formatCount(sourceScope.selected_count)],
                    ["Scope No", sourceScope.scope_no || "--"],
                    ["Source Model", sourceScope.source_model || "--"],
                ],
            },
        ];
    }

    get canDownloadFile() {
        return Boolean(this.result?.download_file?.ready && this.result?.download_file?.download_url);
    }

    get canDownloadErrorReport() {
        return Boolean(this.result?.error_report?.download_ready && this.result?.error_report?.download_url);
    }

    get taskLines() {
        return this.state.taskLines || [];
    }

    get taskErrors() {
        return this.state.taskErrors || [];
    }

    get lineStatusFilters() {
        return TASK_LINE_STATUS_FILTERS;
    }

    get lineDetailHint() {
        return this.buildDetailHint({
            totalCount: this.state.taskLineTotal,
            showingFrom: this.state.taskLineShowingFrom,
            showingTo: this.state.taskLineShowingTo,
            singularLabel: "条行结果",
        });
    }

    get errorDetailHint() {
        return this.buildDetailHint({
            totalCount: this.state.taskErrorTotal,
            showingFrom: this.state.taskErrorShowingFrom,
            showingTo: this.state.taskErrorShowingTo,
            singularLabel: "条错误明细",
        });
    }

    get taskLinePageLabel() {
        return `第 ${this.state.taskLinePage} 页，共 ${this.state.taskLineTotalPages} 页`;
    }

    get taskErrorPageLabel() {
        return `第 ${this.state.taskErrorPage} 页，共 ${this.state.taskErrorTotalPages} 页`;
    }

    get taskLineRangeLabel() {
        return this.buildRangeLabel(this.state.taskLineShowingFrom, this.state.taskLineShowingTo, this.state.taskLineTotal);
    }

    get taskErrorRangeLabel() {
        return this.buildRangeLabel(this.state.taskErrorShowingFrom, this.state.taskErrorShowingTo, this.state.taskErrorTotal);
    }

    async loadResult({ silent = false } = {}) {
        if (!silent) {
            this.state.loading = true;
        }
        this.state.refreshing = silent;
        this.state.error = "";
        if (!this.state.taskNo) {
            this.resetTaskDetails();
            this.state.result = null;
            this.state.loading = false;
            this.state.error = this.ui.missingTask;
            return;
        }
        try {
            const payload = await this.apiRequest(
                `/api/admin/logistics/exports/tasks/${encodeURIComponent(this.state.taskNo)}`
            );
            this.state.result = payload.data || null;
            this.state.taskNo = payload.data?.task_no || this.state.taskNo;
            if (!payload.data) {
                this.resetTaskDetails();
                this.state.error = this.ui.emptyResult;
            } else {
                await this.loadTaskDetails(this.state.taskNo);
            }
        } catch (error) {
            this.resetTaskDetails();
            this.state.result = null;
            this.state.error = this.mapLoadError(error, this.ui.loadFailed);
        } finally {
            this.state.loading = false;
            this.state.refreshing = false;
        }
    }

    async loadTaskDetails(taskNo) {
        if (!taskNo) {
            this.resetTaskDetails();
            return;
        }
        await Promise.all([this.loadTaskLines({ taskNo }), this.loadTaskErrors({ taskNo })]);
    }

    async loadTaskLines({
        taskNo = this.state.taskNo,
        page = this.state.taskLinePage,
        status = this.state.taskLineStatusFilter,
    } = {}) {
        if (!taskNo) {
            return;
        }
        this.state.taskLinesLoading = true;
        this.state.taskLinesError = "";
        try {
            const query = new URLSearchParams({
                page: String(page),
                page_size: String(this.state.taskLinePageSize),
            });
            if (status && status !== "all") {
                query.set("status", status);
            }
            const payload = await this.apiRequest(
                `/api/admin/logistics/exports/tasks/${encodeURIComponent(taskNo)}/lines?${query.toString()}`
            );
            const data = payload.data || {};
            this.state.taskLines = data.items || [];
            this.state.taskLineTotal = data.total || 0;
            this.state.taskLinePage = data.page || page;
            this.state.taskLinePageSize = data.page_size || this.state.taskLinePageSize;
            this.state.taskLineTotalPages = data.total_pages || 1;
            this.state.taskLineShowingFrom = data.showing_from || 0;
            this.state.taskLineShowingTo = data.showing_to || 0;
            this.state.taskLineStatusFilter = status || "all";
        } catch (error) {
            this.state.taskLines = [];
            this.state.taskLineTotal = 0;
            this.state.taskLinePage = 1;
            this.state.taskLineTotalPages = 1;
            this.state.taskLineShowingFrom = 0;
            this.state.taskLineShowingTo = 0;
            this.state.taskLinesError = this.mapLoadError(error, this.ui.taskLinesLoadFailed);
        } finally {
            this.state.taskLinesLoading = false;
        }
    }

    async loadTaskErrors({ taskNo = this.state.taskNo, page = this.state.taskErrorPage } = {}) {
        if (!taskNo) {
            return;
        }
        this.state.taskErrorsLoading = true;
        this.state.taskErrorsError = "";
        try {
            const query = new URLSearchParams({
                page: String(page),
                page_size: String(this.state.taskErrorPageSize),
            });
            const payload = await this.apiRequest(
                `/api/admin/logistics/exports/tasks/${encodeURIComponent(taskNo)}/errors?${query.toString()}`
            );
            const data = payload.data || {};
            this.state.taskErrors = data.items || [];
            this.state.taskErrorTotal = data.total || 0;
            this.state.taskErrorPage = data.page || page;
            this.state.taskErrorPageSize = data.page_size || this.state.taskErrorPageSize;
            this.state.taskErrorTotalPages = data.total_pages || 1;
            this.state.taskErrorShowingFrom = data.showing_from || 0;
            this.state.taskErrorShowingTo = data.showing_to || 0;
        } catch (error) {
            this.state.taskErrors = [];
            this.state.taskErrorTotal = 0;
            this.state.taskErrorPage = 1;
            this.state.taskErrorTotalPages = 1;
            this.state.taskErrorShowingFrom = 0;
            this.state.taskErrorShowingTo = 0;
            this.state.taskErrorsError = this.mapLoadError(error, this.ui.taskErrorsLoadFailed);
        } finally {
            this.state.taskErrorsLoading = false;
        }
    }

    resetTaskDetails() {
        this.state.taskLinesLoading = false;
        this.state.taskErrorsLoading = false;
        this.state.taskLinesError = "";
        this.state.taskErrorsError = "";
        this.state.taskLines = [];
        this.state.taskLineTotal = 0;
        this.state.taskLinePage = 1;
        this.state.taskLinePageSize = TASK_LINE_PAGE_SIZE;
        this.state.taskLineTotalPages = 1;
        this.state.taskLineStatusFilter = "all";
        this.state.taskLineShowingFrom = 0;
        this.state.taskLineShowingTo = 0;
        this.state.taskErrors = [];
        this.state.taskErrorTotal = 0;
        this.state.taskErrorPage = 1;
        this.state.taskErrorPageSize = TASK_ERROR_PAGE_SIZE;
        this.state.taskErrorTotalPages = 1;
        this.state.taskErrorShowingFrom = 0;
        this.state.taskErrorShowingTo = 0;
    }

    async refreshResult() {
        await this.loadResult({ silent: true });
    }

    async changeTaskLineStatusFilter(status) {
        if (!status || status === this.state.taskLineStatusFilter) {
            return;
        }
        this.state.taskLineStatusFilter = status;
        this.state.taskLinePage = 1;
        await this.loadTaskLines({ page: 1, status });
    }

    async goToTaskLinePage(page) {
        const targetPage = this.normalizePage(page, this.state.taskLineTotalPages);
        if (targetPage === this.state.taskLinePage || this.state.taskLinesLoading) {
            return;
        }
        await this.loadTaskLines({ page: targetPage });
    }

    async goToTaskErrorPage(page) {
        const targetPage = this.normalizePage(page, this.state.taskErrorTotalPages);
        if (targetPage === this.state.taskErrorPage || this.state.taskErrorsLoading) {
            return;
        }
        await this.loadTaskErrors({ page: targetPage });
    }

    downloadExportFile() {
        if (!this.canDownloadFile) {
            this.notification.add(this.ui.noDownloadFile, { type: "warning" });
            return;
        }
        window.open(this.result.download_file.download_url, "_blank", "noopener");
    }

    downloadErrorReport() {
        if (!this.canDownloadErrorReport) {
            this.notification.add(this.ui.noErrorReport, { type: "warning" });
            return;
        }
        window.open(this.result.error_report.download_url, "_blank", "noopener");
    }

    async openWaybillList() {
        return this.openSourceList();
    }

    async backToWaybillList() {
        return this.openSourceList();
    }

    async openSourceList() {
        const actionXmlid = this.sourceListMeta.actionXmlid;
        if (!actionXmlid) {
            this.notification.add("当前结果页还没有配置返回列表入口。", { type: "warning" });
            return;
        }
        return this.actionService.doAction(actionXmlid);
    }

    buildDetailHint({ totalCount, showingFrom, showingTo, singularLabel }) {
        if (!totalCount) {
            return `当前没有可展示的${singularLabel}。`;
        }
        if (!showingFrom || !showingTo) {
            return `当前共 ${totalCount} ${singularLabel}。`;
        }
        if (showingFrom === 1 && showingTo === totalCount) {
            return `当前共 ${totalCount} ${singularLabel}，本页已全部展示。`;
        }
        return `当前展示第 ${showingFrom}-${showingTo} 条，共 ${totalCount} ${singularLabel}。`;
    }

    buildRangeLabel(showingFrom, showingTo, totalCount) {
        if (!totalCount || !showingFrom || !showingTo) {
            return "当前没有可展示的数据。";
        }
        return `${showingFrom}-${showingTo} / 共 ${totalCount} 条`;
    }

    normalizePage(page, totalPages) {
        const safeTotalPages = Math.max(Number(totalPages) || 1, 1);
        const parsedPage = Math.max(Number(page) || 1, 1);
        return Math.min(parsedPage, safeTotalPages);
    }

    formatCount(value) {
        if (value === 0) {
            return "0";
        }
        return value || value === 0 ? String(value) : "--";
    }

    mapLoadError(error, fallbackMessage = this.ui.loadFailed) {
        const message = String(error?.message || "").trim();
        const lower = message.toLowerCase();
        if (message.includes("权限") || lower.includes("forbidden") || lower.includes("permission")) {
            return this.ui.noPermission;
        }
        if (message.includes("不存在") || lower.includes("not found")) {
            return this.ui.notFound;
        }
        return message || fallbackMessage;
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
if (!actionsRegistry.contains("logistics_web.export_result")) {
    actionsRegistry.add("logistics_web.export_result", LogisticsExportResultAction);
}
