/** @odoo-module */

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

export class LogisticsStatsCenterAction extends Component {
    static template = "logistics_web.StatsCenterAction";
    static components = { Layout };
    static props = { ...standardActionServiceProps };

    setup() {
        this.actionService = useService("action");
        this.display = { controlPanel: false, searchPanel: false };
        this.state = useState({
            loading: true,
            pageError: "",
            sectionErrors: { trends: "", distributions: "", rankings: "" },
            filters: this.getDefaultFilters(),
            overview: {
                summary: { waybill_count: 0, signed_rate: 0, timeout_rate: 0, exception_count: 0 },
                groups: [],
            },
            trends: [],
            distributions: [],
            rankings: [],
        });

        onWillStart(async () => {
            await this.loadStatsPage();
        });
    }

    getDefaultFilters() {
        const now = new Date();
        const dateTo = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
        const dateFromValue = new Date(now);
        dateFromValue.setDate(dateFromValue.getDate() - 29);
        const dateFrom = `${dateFromValue.getFullYear()}-${String(dateFromValue.getMonth() + 1).padStart(2, "0")}-${String(dateFromValue.getDate()).padStart(2, "0")}`;
        return { dateFrom, dateTo, granularity: "day" };
    }

    get ui() {
        return {
            title: "统计图表中心",
            subtitle: "先看执行波动和风险热点，再下钻到批次、司机、区域与异常对象。",
            badgePrimary: "物流分析",
            badgeSecondary: "全局统计",
            filtersTitle: "全局筛选",
            dateFrom: "开始日期",
            dateTo: "结束日期",
            granularity: "统计粒度",
            refresh: "刷新数据",
            reset: "恢复默认",
            loading: "正在加载统计图表...",
            pageError: "统计图表加载失败，请稍后重试。",
            executionTitle: "执行概览",
            executionHint: "先看整体运单量、签收率与超时率是否出现异常波动。",
            riskTitle: "风险概览",
            riskHint: "集中查看异常趋势、异常类型和高风险批次。",
            driverTitle: "司机与资源",
            driverHint: "只保留横向排行，单司机纵向解释继续留在司机画像页。",
            regionTitle: "区域与质量",
            regionHint: "围绕门店区域观察运单量、异常率、签收率与缺凭证问题。",
            trendError: "趋势数据加载失败，请稍后重试。",
            distributionError: "分布数据加载失败，请稍后重试。",
            rankingError: "排行数据加载失败，请稍后重试。",
            waybillTrendTitle: "运单量趋势",
            waybillTrendHint: "观察每日或每周的执行波动。",
            signTimeoutTitle: "签收率与超时率",
            signTimeoutHint: "对比服务质量和时效表现。",
            exceptionTrendTitle: "异常总量趋势",
            exceptionTrendHint: "快速发现风险抬头的时间段。",
            exceptionTypeTitle: "异常类型分布",
            exceptionTypeHint: "定位异常主要集中在哪些类型。",
            batchRankingTitle: "高风险批次排行",
            batchRankingHint: "按批次异常率、严重异常数和超时运单数排序。",
            driverRankingTitle: "司机月均异常率排行",
            driverRankingHint: "点击司机可继续进入司机画像页。",
            regionWaybillTitle: "区域运单量分布",
            regionWaybillHint: "围绕门店区域观察执行量差异。",
            regionExceptionTitle: "区域异常率排行",
            regionExceptionHint: "定位当前风险较高的重点区域。",
            regionSignedTitle: "区域签收率对比",
            regionSignedHint: "P1 图表，观察区域履约质量差异。",
            missingEvidenceTitle: "缺凭证率与缺凭证运单数",
            missingEvidenceHint: "P1 图表，定位证据链薄弱时段。",
            noTrendData: "当前图表暂无趋势数据。",
            noDistributionData: "当前图表暂无分布数据。",
            noRankingData: "当前图表暂无排行数据。",
            executionEmpty: "当前时间范围内暂无执行数据。",
            riskEmpty: "当前暂无风险相关统计数据。",
            driverEmpty: "当前暂无可展示的司机风险排行。",
            regionEmpty: "当前暂无地区与质量相关统计数据。",
            noPermission: "当前账号暂无查看统计图表的权限。",
            day: "按日",
            week: "按周",
            month: "按月",
        };
    }

    get summaryCards() {
        return [
            { key: "waybill_count", label: "运单量", value: this.state.overview.summary.waybill_count, percent: false },
            { key: "signed_rate", label: "签收率", value: this.state.overview.summary.signed_rate, percent: true },
            { key: "timeout_rate", label: "超时率", value: this.state.overview.summary.timeout_rate, percent: true },
            { key: "exception_count", label: "异常总量", value: this.state.overview.summary.exception_count, percent: false },
        ];
    }

    get granularityOptions() {
        return [
            { value: "day", label: this.ui.day },
            { value: "week", label: this.ui.week },
            { value: "month", label: this.ui.month },
        ];
    }

    get waybillTrendSeries() { return this.getTrendSeries("waybill_count"); }
    get signedRateSeries() { return this.getTrendSeries("signed_rate"); }
    get timeoutRateSeries() { return this.getTrendSeries("timeout_rate"); }
    get exceptionTrendSeries() { return this.getTrendSeries("exception_count"); }
    get missingEvidenceRateSeries() { return this.getTrendSeries("missing_evidence_rate"); }
    get missingEvidenceCountSeries() { return this.getTrendSeries("missing_evidence_waybill_count"); }
    get exceptionTypeDataset() { return this.getDistributionDataset("exception_type_distribution"); }
    get regionWaybillDataset() { return this.getDistributionDataset("region_waybill_distribution"); }
    get highRiskBatchDataset() { return this.getRankingDataset("high_risk_batch_ranking"); }
    get driverRankingDataset() { return this.getRankingDataset("driver_month_avg_exception_rate_ranking"); }
    get regionExceptionDataset() { return this.getRankingDataset("region_exception_rate_ranking"); }
    get regionSignedDataset() { return this.getRankingDataset("region_signed_rate_ranking"); }

    hasNonZeroTrendData(series) {
        return Boolean((series?.points || []).some((item) => Number(item.value || 0) > 0));
    }

    get executionHasData() {
        return Boolean(
            this.hasNonZeroTrendData(this.waybillTrendSeries) ||
            this.hasNonZeroTrendData(this.signedRateSeries) ||
            this.hasNonZeroTrendData(this.timeoutRateSeries)
        );
    }

    get riskHasData() {
        return Boolean(
            this.hasNonZeroTrendData(this.exceptionTrendSeries) ||
            this.exceptionTypeDataset?.items?.length ||
            this.highRiskBatchDataset?.items?.length
        );
    }

    get driverHasData() {
        return Boolean(this.driverRankingDataset?.items?.length);
    }

    get regionHasData() {
        return Boolean(
            this.regionWaybillDataset?.items?.length ||
            this.regionExceptionDataset?.items?.length ||
            this.regionSignedDataset?.items?.length ||
            this.hasNonZeroTrendData(this.missingEvidenceRateSeries) ||
            this.hasNonZeroTrendData(this.missingEvidenceCountSeries)
        );
    }

    getTrendSeries(metricCode) {
        return this.state.trends.find((item) => item.metric_code === metricCode) || null;
    }

    getDistributionDataset(metricCode) {
        return this.state.distributions.find((item) => item.metric_code === metricCode) || { items: [] };
    }

    getRankingDataset(metricCode) {
        return this.state.rankings.find((item) => item.metric_code === metricCode) || { items: [] };
    }

    async loadStatsPage() {
        this.state.loading = true;
        this.state.pageError = "";
        this.state.sectionErrors = { trends: "", distributions: "", rankings: "" };
        try {
            const [overview, trends, distributions, rankings] = await Promise.allSettled([
                this.apiRequest(`/api/admin/logistics/stats/overview?${this.buildQueryString({
                    date_from: this.state.filters.dateFrom,
                    date_to: this.state.filters.dateTo,
                    granularity: this.state.filters.granularity,
                })}`),
                this.apiRequest(`/api/admin/logistics/stats/trends?${this.buildQueryString({
                    date_from: this.state.filters.dateFrom,
                    date_to: this.state.filters.dateTo,
                    granularity: this.state.filters.granularity,
                    metric_codes: [
                        "waybill_count",
                        "signed_rate",
                        "timeout_rate",
                        "exception_count",
                        "missing_evidence_rate",
                        "missing_evidence_waybill_count",
                    ].join(","),
                })}`),
                this.apiRequest(`/api/admin/logistics/stats/distributions?${this.buildQueryString({
                    date_from: this.state.filters.dateFrom,
                    date_to: this.state.filters.dateTo,
                    metric_codes: ["exception_type_distribution", "region_waybill_distribution"].join(","),
                })}`),
                this.apiRequest(`/api/admin/logistics/stats/rankings?${this.buildQueryString({
                    date_from: this.state.filters.dateFrom,
                    date_to: this.state.filters.dateTo,
                    limit: 10,
                    metric_codes: [
                        "high_risk_batch_ranking",
                        "driver_month_avg_exception_rate_ranking",
                        "region_exception_rate_ranking",
                        "region_signed_rate_ranking",
                    ].join(","),
                })}`),
            ]);

            if (overview.status !== "fulfilled") {
                throw new Error(overview.reason?.message || this.ui.pageError);
            }

            this.state.overview = overview.value.data || this.state.overview;
            this.state.trends = trends.status === "fulfilled" ? trends.value.data.series || [] : [];
            this.state.distributions = distributions.status === "fulfilled" ? distributions.value.data.datasets || [] : [];
            this.state.rankings = rankings.status === "fulfilled" ? rankings.value.data.datasets || [] : [];
            this.state.sectionErrors = {
                trends: trends.status === "fulfilled" ? "" : this.mapStatsError(trends.reason, this.ui.trendError),
                distributions: distributions.status === "fulfilled" ? "" : this.mapStatsError(distributions.reason, this.ui.distributionError),
                rankings: rankings.status === "fulfilled" ? "" : this.mapStatsError(rankings.reason, this.ui.rankingError),
            };
        } catch (error) {
            this.state.overview = {
                summary: { waybill_count: 0, signed_rate: 0, timeout_rate: 0, exception_count: 0 },
                groups: [],
            };
            this.state.trends = [];
            this.state.distributions = [];
            this.state.rankings = [];
            this.state.pageError = this.mapStatsError(error, this.ui.pageError);
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

    onDateChange(fieldName, event) { this.state.filters[fieldName] = event.target.value; }
    onGranularityChange(event) { this.state.filters.granularity = event.target.value; }
    async onRefresh() { await this.loadStatsPage(); }
    async onResetFilters() { this.state.filters = this.getDefaultFilters(); await this.loadStatsPage(); }

    formatPercent(value) { return `${((value || 0) * 100).toFixed(1)}%`; }
    formatNumber(value) { return `${value ?? 0}`; }
    formatMetricValue(value, asPercent = false) { return asPercent ? this.formatPercent(value) : this.formatNumber(value); }

    getMaxTrendValue(points = []) { return Math.max(...points.map((item) => Number(item.value || 0)), 0); }
    getMaxItemValue(items = []) { return Math.max(...items.map((item) => Number(item.value || item.primary_value || 0)), 0); }
    getTrendBarHeight(series, point) { const max = this.getMaxTrendValue(series?.points || []); return max ? Math.max(8, Math.round((Number(point.value || 0) / max) * 100)) : 8; }
    getDualTrendBarHeight(seriesList, point, index) {
        const values = (seriesList || []).flatMap((series) => (series?.points || []).map((item) => Number(item.value || 0)));
        const max = Math.max(...values, 0);
        const value = Number(seriesList[index]?.points?.find((item) => item.bucket === point.bucket)?.value || 0);
        return max ? Math.max(8, Math.round((value / max) * 100)) : 8;
    }
    getDistributionWidth(item, dataset) { const max = this.getMaxItemValue(dataset?.items || []); const value = Number(item.value || 0); return max ? Math.max(12, Math.round((value / max) * 100)) : 12; }
    getRankingWidth(item, dataset) { const max = this.getMaxItemValue(dataset?.items || []); const value = Number(item.primary_value || 0); return max ? Math.max(12, Math.round((value / max) * 100)) : 12; }

    getTodayString() {
        const now = new Date();
        return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
    }

    buildDateRangeDomain(fieldName = "delivery_date", isDateTime = false) {
        if (isDateTime) {
            return [[fieldName, ">=", `${this.state.filters.dateFrom} 00:00:00`], [fieldName, "<=", `${this.state.filters.dateTo} 23:59:59`]];
        }
        return [[fieldName, ">=", this.state.filters.dateFrom], [fieldName, "<=", this.state.filters.dateTo]];
    }

    buildBucketDateRange(bucket) {
        if (this.state.filters.granularity === "month") {
            const [year, month] = bucket.split("-").map(Number);
            const lastDay = new Date(year, month, 0).getDate();
            return { dateFrom: `${bucket}-01`, dateTo: `${bucket}-${String(lastDay).padStart(2, "0")}` };
        }
        if (this.state.filters.granularity === "week") {
            const [start, end] = bucket.split("~");
            return { dateFrom: start, dateTo: end };
        }
        return { dateFrom: bucket, dateTo: bucket };
    }

    buildWaybillTrendDomain(metricCode, bucket) {
        const bucketRange = this.buildBucketDateRange(bucket);
        const domain = [["delivery_date", ">=", bucketRange.dateFrom], ["delivery_date", "<=", bucketRange.dateTo]];
        if (metricCode === "signed_rate") domain.push(["state", "in", ["signed", "done"]]);
        if (metricCode === "timeout_rate") {
            domain.push(["delivery_date", "<", this.getTodayString()]);
            domain.push(["state", "not in", ["signed", "done", "cancelled"]]);
        }
        if (metricCode === "missing_evidence_rate" || metricCode === "missing_evidence_waybill_count") domain.push(["evidence_status", "in", ["missing", "partial"]]);
        return domain;
    }

    buildExceptionTrendDomain(bucket) {
        const bucketRange = this.buildBucketDateRange(bucket);
        return [["report_time", ">=", `${bucketRange.dateFrom} 00:00:00`], ["report_time", "<=", `${bucketRange.dateTo} 23:59:59`]];
    }

    async onSummaryCardClick(cardKey) {
        if (cardKey === "waybill_count") return this.openWaybillList(this.buildDateRangeDomain(), "当前时间范围运单");
        if (cardKey === "signed_rate") return this.openWaybillList([...this.buildDateRangeDomain(), ["state", "in", ["signed", "done"]]], "当前时间范围已签收运单");
        if (cardKey === "timeout_rate") return this.openWaybillList([...this.buildDateRangeDomain(), ["delivery_date", "<", this.getTodayString()], ["state", "not in", ["signed", "done", "cancelled"]]], "当前时间范围超时运单");
        if (cardKey === "exception_count") return this.openExceptionList(this.buildDateRangeDomain("report_time", true), "当前时间范围异常");
    }

    async onTrendPointClick(metricCode, bucket) {
        if (metricCode === "exception_count") return this.openExceptionList(this.buildExceptionTrendDomain(bucket), `${bucket} 异常`);
        return this.openWaybillList(this.buildWaybillTrendDomain(metricCode, bucket), `${bucket} 指标详情`);
    }

    async onDistributionItemClick(metricCode, item) {
        if (metricCode === "exception_type_distribution") return this.openExceptionList([["id", "in", item.record_ids || []]], `${item.label}异常列表`);
        if (metricCode === "region_waybill_distribution") return this.openWaybillList([["id", "in", item.record_ids || []]], `${item.label}运单列表`);
    }

    async onRankingItemClick(metricCode, item) {
        if (metricCode === "high_risk_batch_ranking") return this.openBatchList([["id", "=", item.entity_id]], `${item.label}批次`);
        if (metricCode === "driver_month_avg_exception_rate_ranking") return this.openDriverProfile(item.entity_id);
        if (metricCode === "region_exception_rate_ranking") return this.openWaybillList([["id", "in", item.record_ids || []], ["exception_status", "in", ["open", "processing", "closed"]]], `${item.label}异常运单`);
        if (metricCode === "region_signed_rate_ranking") return this.openWaybillList([["id", "in", item.record_ids || []], ["state", "in", ["signed", "done"]]], `${item.label}签收运单`);
    }

    async openWaybillList(domain = [], name = "运单列表") {
        return this.actionService.doAction({ type: "ir.actions.act_window", name, res_model: "logistics.dispatch.waybill", views: [[false, "list"], [false, "form"]], domain });
    }

    async openExceptionList(domain = [], name = "异常列表") {
        return this.actionService.doAction({ type: "ir.actions.act_window", name, res_model: "logistics.trace.exception", views: [[false, "list"], [false, "form"]], domain });
    }

    async openBatchList(domain = [], name = "批次列表") {
        return this.actionService.doAction({ type: "ir.actions.act_window", name, res_model: "logistics.dispatch.batch", views: [[false, "list"], [false, "form"]], domain });
    }

    async openDriverProfile(driverId) {
        return this.actionService.doAction({ type: "ir.actions.client", name: "司机画像", tag: "logistics_web.driver_management", params: { driver_id: driverId } });
    }

    mapStatsError(error, fallbackMessage) {
        const message = error?.message || "";
        if (message.includes("权限") || message.includes("forbidden")) {
            return this.ui.noPermission;
        }
        return message || fallbackMessage;
    }

    async apiRequest(url, options = {}) {
        const response = await fetch(url, { method: options.method || "GET", headers: options.headers || {}, body: options.body });
        const payload = await response.json().catch(() => null);
        if (!response.ok || !payload || payload.code !== 0) throw new Error(payload?.data?.errors?.[0]?.error_message || payload?.message || "请求失败。");
        return payload;
    }
}

const actionsRegistry = registry.category("actions");
if (!actionsRegistry.contains("logistics_web.stats_center")) {
    actionsRegistry.add("logistics_web.stats_center", LogisticsStatsCenterAction);
}
