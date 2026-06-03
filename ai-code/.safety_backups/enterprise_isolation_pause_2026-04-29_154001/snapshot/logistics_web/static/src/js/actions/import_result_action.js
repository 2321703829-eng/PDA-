/** @odoo-module */

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

const TASK_LINE_PAGE_SIZE = 20;
const TASK_ERROR_PAGE_SIZE = 20;
const TASK_LINE_STATUS_FILTERS = [
    { value: "all", label: "全部行结果" },
    { value: "pending", label: "待处理" },
    { value: "success", label: "成功" },
    { value: "failed", label: "失败" },
    { value: "skipped", label: "跳过" },
];

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
            taskLinesLoading: false,
            taskErrorsLoading: false,
            error: "",
            taskLinesError: "",
            taskErrorsError: "",
            taskNo: this.props.action?.params?.task_no || this.props.action?.params?.import_batch_no || "",
            sourceModel: this.props.action?.params?.source_model || "logistics.dispatch.waybill",
            result: null,
            taskLines: [],
            taskLineTotal: 0,
            taskLinePage: 1,
            taskLinePageSize: TASK_LINE_PAGE_SIZE,
            taskLineTotalPages: 1,
            taskLineStatusFilter: "all",
            taskLineStatusFilterLabel: "",
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

    get ui() {
        return {
            title: "导入结果",
            subtitle: "回看本次导入任务的结果状态、关键统计、行结果与字段错误明细。",
            badgePrimary: "导入回看",
            badgeSecondary: "结果闭环",
            heroNoteTitle: "当前工作方向",
            heroNoteBody: "先看任务摘要，再核对行结果和字段错误，最后决定是否继续核验或回到导入中心重试。",
            refresh: "刷新结果",
            downloadErrorReport: "下载错误报告",
            openWaybillList: "进入运单列表",
            continueReview: "按导入任务继续核验",
            backToImportCenter: "返回导入中心",
            resultSummaryTitle: "结果摘要",
            batchInfoTitle: "文件与任务信息",
            taskLinesTitle: "行结果明细",
            taskErrorsTitle: "字段错误明细",
            nextActionTitle: "后续动作",
            failureTitle: "失败说明与错误报告",
            loading: "正在加载导入结果...",
            detailLoading: "正在加载任务明细...",
            noReport: "当前任务无错误报告",
            missingBatch: "当前未指定导入任务，暂时无法查看导入结果。",
            emptyResult: "当前任务暂无可展示的导入结果。",
            notFound: "当前导入任务不存在，或结果已不可查看。",
            loadFailed: "导入结果加载失败，请刷新后重试。",
            taskLinesLoadFailed: "行结果加载失败，请稍后刷新结果重试。",
            taskErrorsLoadFailed: "错误明细加载失败，请稍后刷新结果重试。",
            noPermission: "当前账号暂无查看导入结果的权限。",
            pendingLabel: "待加载",
            resultHeaderTitle: "结果头部",
            resultSummaryHint: "优先阅读本次导入的成功、失败和写入规模，再决定后续核验动作。",
            importBatchNoLabel: "导入任务号",
            templateCodeLabel: "模板编码",
            templateVersionLabel: "模板版本",
            batchInfoHint: "这里固定展示源文件、操作人和任务时间，不在结果页做编辑。",
            nextActionHint: "行结果和错误明细核对完成后，再决定是否进入运单列表或返回导入中心。",
            failureHint: "失败记录或错误报告存在时，这里会保留处理提示。",
            failedRecordCountLabel: "失败记录数：",
            hasErrorReportLabel: "当前任务存在错误报告",
            noErrorReportLabel: "当前任务无错误报告",
            refreshingText: "刷新中...",
            fileInfoTitle: "文件信息",
            batchInfoCardTitle: "任务信息",
            fileNameLabel: "文件名",
            confirmedAtLabel: "确认时间",
            finishedAtLabel: "完成时间",
            statusLabel: "结果状态",
            operatorLabel: "操作人",
            lineNoLabel: "任务内行号",
            sourceRowNoLabel: "原始行号",
            businessKeyLabel: "业务摘要",
            targetObjectLabel: "目标对象",
            lineMessageLabel: "处理说明",
            fieldNameLabel: "字段名",
            rawValueLabel: "原始值",
            mappedValueLabel: "映射值",
            errorCodeLabel: "错误编码",
            errorMessageLabel: "错误说明",
            lineStatusLabel: "行状态",
            linesEmptyTitle: "暂无行结果",
            linesEmptyHint: "当前任务还没有可展示的行结果，稍后可刷新结果重新查看。",
            errorsEmptyTitle: "暂无字段错误",
            errorsEmptyHint: "当前任务没有字段级错误，或错误明细尚未生成。",
            showingCountLabel: "当前展示",
            totalCountLabel: "总数",
            lineFilterTitle: "状态筛选",
            lineFilterHint: "先用状态筛选聚焦失败或跳过行，再配合分页逐批核对。",
            lineFilterAllHint: "当前查看全部行结果。",
            lineFilterActiveHintPrefix: "当前按状态筛选：",
            pageInfoPrefix: "第",
            pageInfoMiddle: "页，共",
            pageInfoSuffix: "页",
            pageRangeSeparator: "-",
            pageRangeSuffix: " / 共",
            prevPage: "上一页",
            nextPage: "下一页",
            pageRangeEmpty: "当前没有可展示的数据。",
            linePagerTitle: "行结果分页",
            errorPagerTitle: "错误明细分页",
            pageMetaShowingPrefix: "当前展示第",
            pageMetaShowingSuffix: "条",
            pageMetaTotalPrefix: "共",
            pageMetaTotalSuffix: "条",
        };
    }

    get result() {
        return this.state.result;
    }

    get detailLoading() {
        return this.state.taskLinesLoading || this.state.taskErrorsLoading;
    }

    get statusTone() {
        const status = this.result?.status;
        if (status === "success" || status === "partial_failed" || status === "finished") {
            return "success";
        }
        if (status === "failed" || status === "expired" || status === "cancelled") {
            return "danger";
        }
        return "warning";
    }

    get summaryText() {
        const status = this.result?.status;
        if (status === "success" || status === "finished") {
            return "本次导入已完成，可以继续查看行结果并进入运单列表回看写入结果。";
        }
        if (status === "partial_failed") {
            return "本次导入已完成，但存在失败记录，建议先看字段错误明细和错误报告。";
        }
        if (status === "failed") {
            return "本次导入未成功写入，建议先看失败原因、行结果与字段错误。";
        }
        if (status === "expired") {
            return "当前任务已失效，如需继续处理，请返回导入中心重新发起。";
        }
        if (status === "importing" || status === "running") {
            return "当前任务仍在处理中，刷新后可以继续查看最新的行结果和错误明细。";
        }
        if (status === "prechecked" || status === "pending") {
            return "当前任务仍停留在预校验或待执行阶段，可以先查看预校验失败行和字段错误。";
        }
        return "请先确认本次导入结果，再决定后续核验动作。";
    }

    get resultCards() {
        const result = this.result || {};
        const businessSummary = result.business_summary || {};
        return [
            { key: "total", label: "总行数", value: this.formatCount(result.total_count ?? result.total_row_count), caption: "确认本次任务覆盖范围" },
            { key: "passed", label: "成功行数", value: this.formatCount(result.success_count ?? result.passed_row_count), tone: "success", caption: "可继续核验的有效行" },
            { key: "failed", label: "失败行数", value: this.formatCount(result.fail_count ?? result.failed_row_count), tone: (result.fail_count ?? result.failed_row_count) ? "warning" : "", caption: "失败存在时优先检查错误明细" },
            { key: "wave", label: "新建波次数", value: this.formatCount(businessSummary.written_wave_count ?? result.created_wave_count), caption: "主链起点是否成功建档" },
            { key: "batch", label: "新建批次数", value: this.formatCount(businessSummary.written_batch_count ?? result.created_batch_count), caption: "波次下的批次承接规模" },
            { key: "waybill", label: "新建运单数", value: this.formatCount(businessSummary.written_waybill_count ?? result.created_waybill_count), caption: "主业务对象写入规模" },
            { key: "customer", label: "新建客户明细数", value: this.formatCount(businessSummary.written_customer_line_count ?? result.created_customer_line_count), caption: "客户维度扩展写入量" },
            { key: "goods", label: "新建货物明细数", value: this.formatCount(businessSummary.written_goods_line_count ?? result.created_goods_line_count), caption: "货物明细补充是否完整" },
        ];
    }

    get batchInfoCards() {
        const result = this.result || {};
        const sourceFile = result.source_file || {};
        return [
            {
                key: "file",
                title: this.ui.fileInfoTitle,
                items: [
                    [this.ui.fileNameLabel, sourceFile.file_name || result.file_name || "--"],
                    [this.ui.templateCodeLabel, result.template_code || "--"],
                    [this.ui.templateVersionLabel, result.template_version || "--"],
                ],
            },
            {
                key: "batch",
                title: this.ui.batchInfoCardTitle,
                items: [
                    [this.ui.importBatchNoLabel, result.task_no || result.import_batch_no || this.state.taskNo || "--"],
                    [this.ui.operatorLabel, result.operator?.name || "--"],
                    [this.ui.confirmedAtLabel, result.started_at || result.confirmed_at || "--"],
                    [this.ui.finishedAtLabel, result.finished_at || "--"],
                    [this.ui.statusLabel, result.status_label || "--"],
                ],
            },
        ];
    }

    get canDownloadErrorReport() {
        return Boolean(this.result?.error_report?.download_ready || this.result?.error_report_url);
    }

    get canOpenWaybillList() {
        const result = this.result;
        if (!result) {
            return false;
        }
        return Boolean(
            result.status === "success" ||
            result.status === "partial_failed" ||
            result.status === "finished" ||
            result.business_summary?.written_wave_count ||
            result.business_summary?.written_batch_count ||
            result.business_summary?.written_waybill_count ||
            result.business_summary?.written_customer_line_count ||
            result.business_summary?.written_goods_line_count ||
            result.created_wave_count ||
            result.created_batch_count ||
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
        return Boolean(
            result.failure_reason ||
            result.failed_record_count ||
            result.fail_count ||
            result.failed_row_count ||
            result.error_report?.download_ready ||
            result.error_report_url
        );
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

    get currentLineStatusFilterLabel() {
        return this.lineStatusFilters.find((item) => item.value === this.state.taskLineStatusFilter)?.label || "";
    }

    get lineDetailHint() {
        const statusHint =
            this.state.taskLineStatusFilter === "all"
                ? this.ui.lineFilterAllHint
                : `${this.ui.lineFilterActiveHintPrefix}${this.currentLineStatusFilterLabel}。`;
        return `${this.buildDetailHint({
            totalCount: this.state.taskLineTotal,
            showingFrom: this.state.taskLineShowingFrom,
            showingTo: this.state.taskLineShowingTo,
            singularLabel: "行结果",
        })} ${statusHint}`;
    }

    get errorDetailHint() {
        return this.buildDetailHint({
            totalCount: this.state.taskErrorTotal,
            showingFrom: this.state.taskErrorShowingFrom,
            showingTo: this.state.taskErrorShowingTo,
            singularLabel: "字段错误",
        });
    }

    get taskLinePageLabel() {
        return this.buildPageLabel(this.state.taskLinePage, this.state.taskLineTotalPages);
    }

    get taskErrorPageLabel() {
        return this.buildPageLabel(this.state.taskErrorPage, this.state.taskErrorTotalPages);
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
            this.state.loading = false;
            this.state.result = null;
            this.state.error = this.ui.missingBatch;
            return;
        }
        try {
            const payload = await this.apiRequest(
                `/api/admin/logistics/imports/tasks/${encodeURIComponent(this.state.taskNo)}`
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
        await Promise.all([
            this.loadTaskLines({ taskNo }),
            this.loadTaskErrors({ taskNo }),
        ]);
    }

    async loadTaskLines({ taskNo = this.state.taskNo, page = this.state.taskLinePage, status = this.state.taskLineStatusFilter } = {}) {
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
                `/api/admin/logistics/imports/tasks/${encodeURIComponent(taskNo)}/lines?${query.toString()}`
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
            this.state.taskLineStatusFilterLabel = data.status_filter_label || "";
        } catch (error) {
            this.state.taskLines = [];
            this.state.taskLineTotal = 0;
            this.state.taskLinePage = 1;
            this.state.taskLineTotalPages = 1;
            this.state.taskLineStatusFilterLabel = "";
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
                `/api/admin/logistics/imports/tasks/${encodeURIComponent(taskNo)}/errors?${query.toString()}`
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
        this.state.taskLineStatusFilterLabel = "";
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

    downloadErrorReport() {
        if (!this.canDownloadErrorReport) {
            return;
        }
        const url = this.result?.error_report?.download_url || this.result?.error_report_url;
        if (url) {
            window.open(url, "_blank", "noopener");
        }
    }

    async openWaybillList() {
        if (!this.canOpenWaybillList) {
            return;
        }
        return this.actionService.doAction("logistics_dispatch.action_logistics_dispatch_waybill");
    }

    async continueReviewByTask() {
        if (!this.state.taskNo) {
            return;
        }
        this.notification.add(`已打开导入任务 ${this.state.taskNo} 的运单核验入口。`, { type: "info" });
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: `导入任务 ${this.state.taskNo} 运单`,
            res_model: "logistics.dispatch.waybill",
            views: [[false, "list"], [false, "form"]],
            context: {
                task_no: this.state.taskNo,
                import_batch_no: this.result?.import_batch_no || this.state.taskNo,
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
                task_no: this.state.taskNo,
                import_batch_no: this.result?.import_batch_no || this.state.taskNo,
            },
        });
    }

    buildDetailHint({ totalCount, showingFrom, showingTo, singularLabel }) {
        if (!totalCount) {
            return `当前没有可展示的${singularLabel}。`;
        }
        if (!showingFrom || !showingTo) {
            return `当前共 ${totalCount} 条${singularLabel}。`;
        }
        if (showingFrom === 1 && showingTo === totalCount) {
            return `当前共 ${totalCount} 条${singularLabel}，本页已全部展示。`;
        }
        return `当前展示第 ${showingFrom}-${showingTo} 条，共 ${totalCount} 条${singularLabel}。`;
    }

    buildPageLabel(page, totalPages) {
        return `${this.ui.pageInfoPrefix}${page}${this.ui.pageInfoMiddle}${totalPages}${this.ui.pageInfoSuffix}`;
    }

    buildRangeLabel(showingFrom, showingTo, totalCount) {
        if (!totalCount || !showingFrom || !showingTo) {
            return this.ui.pageRangeEmpty;
        }
        return `${showingFrom}${this.ui.pageRangeSeparator}${showingTo}${this.ui.pageRangeSuffix}${totalCount} 条`;
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

    formatTarget(item) {
        if (!item?.target_model) {
            return "--";
        }
        if (!item?.target_res_id) {
            return item.target_model;
        }
        return `${item.target_model} #${item.target_res_id}`;
    }

    mapLoadError(error, fallbackMessage = this.ui.loadFailed) {
        const message = String(error?.message || "").trim();
        const lower = message.toLowerCase();
        if (message.includes("权限") || lower.includes("forbidden") || lower.includes("permission")) {
            return this.ui.noPermission;
        }
        if (message.includes("未找到") || message.includes("不存在") || lower.includes("not found")) {
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
if (!actionsRegistry.contains("logistics_web.import_result")) {
    actionsRegistry.add("logistics_web.import_result", LogisticsImportResultAction);
}
