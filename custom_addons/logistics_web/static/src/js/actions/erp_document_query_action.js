/** @odoo-module */

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

export class LogisticsERPDocumentQueryAction extends Component {
    static template = "logistics_web.ERPDocumentQueryAction";
    static components = { Layout };
    static props = { ...standardActionServiceProps };

    setup() {
        this.actionService = useService("action");
        this.display = { controlPanel: false, searchPanel: false };
        this.state = useState({
            loading: true,
            pageError: "",
            filters: this.getDefaultFilters(),
            types: [],
            summary: {
                total: 0,
                current_page_count: 0,
                active_type_count: 0,
                latest_updated_at: "",
                date_range: "",
            },
            records: [],
            pagination: {
                page: 1,
                page_size: 20,
                total: 0,
                total_pages: 1,
                has_previous: false,
                has_next: false,
            },
        });

        onWillStart(async () => {
            await this.loadDocuments();
        });
    }

    getDefaultFilters() {
        const today = this.formatDate(new Date());
        const dateFromValue = new Date();
        dateFromValue.setDate(dateFromValue.getDate() - 29);
        return {
            documentType: "all",
            keyword: "",
            dateFrom: this.formatDate(dateFromValue),
            dateTo: today,
            page: 1,
            pageSize: 20,
        };
    }

    get ui() {
        return {
            title: "ERP 单据查询中心",
            subtitle: "实时汇总采购、销售、出入库、退货、补货和库存移动数据，按最新更新顺序分页查看。",
            badgePrimary: "实时查询",
            badgeSecondary: "从新到旧",
            noteTitle: "查询范围",
            noteBody: "覆盖 ERP 模板中的订单、入库单、出库单、退货单、补货计划和库存移动记录。",
            filterTitle: "筛选条件",
            filterHint: "按单据类型、日期范围和关键字快速定位每天产生的业务数据。",
            docType: "单据类型",
            keyword: "关键字",
            keywordPlaceholder: "单号、客户、供应商、商品、批次",
            dateFrom: "开始日期",
            dateTo: "结束日期",
            pageSize: "每页数量",
            refresh: "查询",
            reset: "重置",
            loading: "正在加载 ERP 单据数据...",
            pageError: "ERP 单据查询失败，请稍后重试。",
            noData: "当前条件下暂无单据数据。",
            openRecord: "查看",
            previous: "上一页",
            next: "下一页",
            total: "全部单据",
            pageRecords: "本页记录",
            activeTypes: "有数据类型",
            latest: "最近更新",
        };
    }

    get summaryCards() {
        return [
            { key: "total", label: this.ui.total, value: this.formatNumber(this.state.summary.total), caption: this.state.summary.date_range || "全部时间", tone: "info" },
            { key: "page", label: this.ui.pageRecords, value: this.formatNumber(this.state.summary.current_page_count), caption: `第 ${this.state.pagination.page} / ${this.state.pagination.total_pages} 页`, tone: "success" },
            { key: "types", label: this.ui.activeTypes, value: this.formatNumber(this.state.summary.active_type_count), caption: "按 ERP 模板单据归类", tone: "warning" },
            { key: "latest", label: this.ui.latest, value: this.state.summary.latest_updated_at || "--", caption: "以 Odoo 实时数据为准", tone: "neutral" },
        ];
    }

    get typeOptions() {
        return this.state.types.length
            ? this.state.types
            : [{ key: "all", label: "全部单据", count: 0, active: true }];
    }

    get pageSizeOptions() {
        return [10, 20, 50, 100];
    }

    get canPreviousPage() {
        return Boolean(this.state.pagination.has_previous);
    }

    get canNextPage() {
        return Boolean(this.state.pagination.has_next);
    }

    async loadDocuments() {
        this.state.loading = true;
        this.state.pageError = "";
        try {
            const payload = await this.apiRequest(`/api/admin/logistics/erp-documents/search?${this.buildQueryString({
                document_type: this.state.filters.documentType,
                keyword: this.state.filters.keyword,
                date_from: this.state.filters.dateFrom,
                date_to: this.state.filters.dateTo,
                page: this.state.filters.page,
                page_size: this.state.filters.pageSize,
            })}`);
            const data = payload.data || {};
            this.state.types = data.types || [];
            this.state.summary = data.summary || this.state.summary;
            this.state.records = data.records || [];
            this.state.pagination = data.pagination || this.state.pagination;
            this.state.filters.page = this.state.pagination.page || this.state.filters.page;
            this.state.filters.pageSize = this.state.pagination.page_size || this.state.filters.pageSize;
        } catch (error) {
            this.state.records = [];
            this.state.pageError = error?.message || this.ui.pageError;
        } finally {
            this.state.loading = false;
        }
    }

    buildQueryString(payload) {
        const params = new URLSearchParams();
        Object.entries(payload).forEach(([key, value]) => {
            if (value !== false && value !== null && value !== undefined && value !== "") {
                params.set(key, value);
            }
        });
        return params.toString();
    }

    formatDate(value) {
        return `${value.getFullYear()}-${String(value.getMonth() + 1).padStart(2, "0")}-${String(value.getDate()).padStart(2, "0")}`;
    }

    formatNumber(value) {
        return Number(value || 0).toLocaleString("zh-CN");
    }

    async onRefresh() {
        this.state.filters.page = 1;
        await this.loadDocuments();
    }

    async onResetFilters() {
        this.state.filters = this.getDefaultFilters();
        await this.loadDocuments();
    }

    async onTypeChange(typeKey) {
        this.state.filters.documentType = typeKey;
        this.state.filters.page = 1;
        await this.loadDocuments();
    }

    onFilterFieldChange(fieldName, value) {
        this.state.filters[fieldName] = value;
    }

    async onPageSizeChange(value) {
        this.state.filters.pageSize = Number(value || 20);
        this.state.filters.page = 1;
        await this.loadDocuments();
    }

    async onPreviousPage() {
        if (!this.canPreviousPage) return;
        this.state.filters.page = Math.max(1, this.state.filters.page - 1);
        await this.loadDocuments();
    }

    async onNextPage() {
        if (!this.canNextPage) return;
        this.state.filters.page = this.state.filters.page + 1;
        await this.loadDocuments();
    }

    async onKeywordKeydown(event) {
        if (event.key === "Enter") {
            await this.onRefresh();
        }
    }

    async openRecord(record) {
        if (!record?.action) return;
        await this.actionService.doAction(record.action);
    }

    async apiRequest(url, options = {}) {
        const response = await fetch(url, {
            method: options.method || "GET",
            headers: options.headers || {},
            body: options.body,
        });
        const payload = await response.json().catch(() => null);
        if (!response.ok || !payload || payload.code !== 0) {
            throw new Error(payload?.data?.errors?.[0]?.error_message || payload?.message || this.ui.pageError);
        }
        return payload;
    }
}

const actionsRegistry = registry.category("actions");
if (!actionsRegistry.contains("logistics_web.erp_document_query")) {
    actionsRegistry.add("logistics_web.erp_document_query", LogisticsERPDocumentQueryAction);
}
