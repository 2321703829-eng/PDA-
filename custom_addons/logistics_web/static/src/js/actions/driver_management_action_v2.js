/** @odoo-module */

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

const MOCK_STORAGE_KEY = "logistics_web_driver_mock";
const MOCK_BUCKETS = ["2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04"];
const MOCK_DRIVERS = [
    { driver_id: 101, driver_name: "张强", mobile: "13800000001", current_vehicle_id: 11, current_vehicle_label: "SH-A2198 / 冷链车 4.2 米", status: "active", status_label: "在用", latest_execution_at: "2026-04-17 10:12:00", has_own_vehicle: true, waybill_count: 148, month_avg_exception_rate: 0.021 },
    { driver_id: 102, driver_name: "李海", mobile: "13800000002", current_vehicle_id: 12, current_vehicle_label: "SH-B8631 / 厢式车 7.6 米", status: "inactive", status_label: "停用", latest_execution_at: "2026-04-08 18:08:00", has_own_vehicle: false, waybill_count: 132, month_avg_exception_rate: 0.046 },
];
const MOCK_PROFILE_DATA = {
    101: {
        summary: { batch_count: 28, waybill_count: 148, recent_30d_waybill_count: 36, recent_30d_batch_count: 7, recent_store_count: 12, recent_region_count: 5, top_regions: ["浦东", "闵行", "徐汇"], top_stores: ["浦东门店 1", "闵行门店 2", "徐汇旗舰店"] },
        kpis: { month_waybill_count: 36, month_avg_exception_rate: 0.021, current_month_signed_rate: 0.972, current_month_timeout_rate: 0.028, missing_evidence_rate: 0.014, exception_count: 3 },
        risk: { exception_waybill_count: 3, severe_exception_count: 1, timeout_waybill_count: 1, missing_evidence_waybill_count: 1, top_exception_types: [{ key: "timeout", label: "超时", value: 1 }, { key: "evidence_missing", label: "缺少凭证", value: 1 }, { key: "address_change", label: "地址变更", value: 1 }] },
        trends: { month_waybill_count: [21, 24, 28, 26, 31, 36], exception_rate: [0.041, 0.036, 0.032, 0.028, 0.024, 0.021], signed_rate: [0.935, 0.946, 0.952, 0.958, 0.966, 0.972], timeout_rate: [0.051, 0.047, 0.043, 0.038, 0.033, 0.028] },
        recentWaybills: [{ waybill_id: 9101, waybill_no: "WB202604170001", status_label: "已签收", store_name: "浦东门店 1", store_region: "浦东", delivery_date: "2026-04-17" }, { waybill_id: 9102, waybill_no: "WB202604160021", status_label: "配送中", store_name: "徐汇旗舰店", store_region: "徐汇", delivery_date: "2026-04-16" }],
        recentExceptions: [{ exception_id: 801, exception_no: "EX20260417001", status_label: "待处理", waybill_id: 9101, waybill_no: "WB202604170001", exception_type_label: "缺少凭证", report_time: "2026-04-17 10:20:00" }, { exception_id: 802, exception_no: "EX20260414008", status_label: "已关闭", waybill_id: 9102, waybill_no: "WB202604140031", exception_type_label: "地址变更", report_time: "2026-04-14 15:36:00" }],
    },
    102: {
        summary: { batch_count: 24, waybill_count: 132, recent_30d_waybill_count: 28, recent_30d_batch_count: 6, recent_store_count: 9, recent_region_count: 4, top_regions: ["宝山", "嘉定", "青浦"], top_stores: ["宝山北门店", "嘉定中心店", "青浦集散点"] },
        kpis: { month_waybill_count: 28, month_avg_exception_rate: 0.046, current_month_signed_rate: 0.943, current_month_timeout_rate: 0.051, missing_evidence_rate: 0.027, exception_count: 5 },
        risk: { exception_waybill_count: 5, severe_exception_count: 2, timeout_waybill_count: 2, missing_evidence_waybill_count: 1, top_exception_types: [{ key: "timeout", label: "超时", value: 2 }, { key: "customer_absent", label: "客户不在场", value: 2 }, { key: "evidence_missing", label: "缺少凭证", value: 1 }] },
        trends: { month_waybill_count: [30, 32, 29, 25, 27, 28], exception_rate: [0.038, 0.041, 0.044, 0.048, 0.047, 0.046], signed_rate: [0.952, 0.949, 0.947, 0.944, 0.945, 0.943], timeout_rate: [0.029, 0.031, 0.039, 0.046, 0.049, 0.051] },
        recentWaybills: [{ waybill_id: 9201, waybill_no: "WB202604160112", status_label: "已签收", store_name: "嘉定中心店", store_region: "嘉定", delivery_date: "2026-04-16" }, { waybill_id: 9202, waybill_no: "WB202604150041", status_label: "异常处理中", store_name: "宝山北门店", store_region: "宝山", delivery_date: "2026-04-15" }],
        recentExceptions: [{ exception_id: 803, exception_no: "EX20260416007", status_label: "处理中", waybill_id: 9202, waybill_no: "WB202604150041", exception_type_label: "客户不在场", report_time: "2026-04-16 18:12:00" }, { exception_id: 804, exception_no: "EX20260413003", status_label: "已关闭", waybill_id: 9201, waybill_no: "WB202604130019", exception_type_label: "超时", report_time: "2026-04-13 11:05:00" }],
    },
};

const deepClone = (value) => JSON.parse(JSON.stringify(value));
const buildTrendSeries = (metricCode, values) => ({ metric_code: metricCode, points: values.map((value, index) => ({ bucket: MOCK_BUCKETS[index], value })) });
const getMockProfile = (driverId) => {
    const driver = MOCK_DRIVERS.find((item) => item.driver_id === driverId);
    const extra = MOCK_PROFILE_DATA[driverId];
    if (!driver || !extra) {
        return null;
    }
    return deepClone({
        overview: {
            driver_id: driver.driver_id,
            driver_name: driver.driver_name,
            mobile: driver.mobile,
            status: driver.status,
            status_label: driver.status_label,
            has_own_vehicle: driver.has_own_vehicle,
            remark: driver.driver_id === 101 ? "负责浦东与徐汇冷链门店配送。" : "近两周重点覆盖嘉定与宝山线路。",
            latest_execution_at: driver.latest_execution_at,
            current_vehicle: { vehicle_id: driver.current_vehicle_id, vehicle_label: driver.current_vehicle_label },
            recent_vehicle: { vehicle_id: driver.current_vehicle_id, vehicle_label: driver.current_vehicle_label },
            execution_summary: extra.summary,
        },
        kpis: extra.kpis,
        risk: extra.risk,
        trends: [
            buildTrendSeries("month_waybill_count", extra.trends.month_waybill_count),
            buildTrendSeries("exception_rate", extra.trends.exception_rate),
            buildTrendSeries("signed_rate", extra.trends.signed_rate),
            buildTrendSeries("timeout_rate", extra.trends.timeout_rate),
        ],
        recentWaybills: extra.recentWaybills,
        recentExceptions: extra.recentExceptions,
    });
};

function buildMockListPayload(params) {
    const keyword = String(params.keyword || "").trim().toLowerCase();
    let items = MOCK_DRIVERS.filter((item) => {
        const haystack = [item.driver_name, item.mobile, item.current_vehicle_label].join(" ").toLowerCase();
        if (keyword && !haystack.includes(keyword)) return false;
        if (params.status && item.status !== params.status) return false;
        if (params.vehicle_id && String(item.current_vehicle_id) !== String(params.vehicle_id)) return false;
        if (params.has_own_vehicle === "true" && !item.has_own_vehicle) return false;
        if (params.has_own_vehicle === "false" && item.has_own_vehicle) return false;
        return true;
    });
    const sortBy = params.sort_by || "latest_execution_at";
    const sortOrder = params.sort_order === "asc" ? "asc" : "desc";
    items = [...items].sort((left, right) => {
        const leftValue = left[sortBy] ?? "";
        const rightValue = right[sortBy] ?? "";
        if (leftValue === rightValue) return left.driver_name.localeCompare(right.driver_name);
        return sortOrder === "asc" ? (leftValue > rightValue ? 1 : -1) : leftValue < rightValue ? 1 : -1;
    });
    const page = Number(params.page || 1);
    const pageSize = Number(params.page_size || 20);
    const start = (page - 1) * pageSize;
    return { items: deepClone(items.slice(start, start + pageSize)), total: items.length, page, page_size: pageSize };
}

export class LogisticsDriverManagementActionV2 extends Component {
    static template = "logistics_web.DriverManagementActionV2";
    static components = { Layout };
    static props = { ...standardActionServiceProps };

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.notification = useService("notification");
        this.display = { controlPanel: false, searchPanel: false };
        this.state = useState({
            mode: "list",
            loading: true,
            error: "",
            keyword: "",
            filters: { status: "", hasOwnVehicle: "", vehicleId: "" },
            sortBy: "latest_execution_at",
            sortOrder: "desc",
            page: 1,
            pageSize: 20,
            total: 0,
            items: [],
            filterOptions: { status_options: [], vehicle_options: [], has_own_vehicle_options: [] },
            activeDriverId: null,
            profileLoading: false,
            profileError: "",
            mockEnabled: this.getInitialMockEnabled(),
            hiddenTrendMetrics: { signed_rate: false, timeout_rate: false },
            sectionErrors: this.emptySectionErrors(),
            profile: this.emptyProfile(),
        });
        onWillStart(async () => {
            await Promise.all([this.loadFilterOptions(), this.loadDriverList()]);
            const initialDriverId = Number(this.props.action?.params?.driver_id || 0);
            if (initialDriverId) {
                await this.openProfile(initialDriverId);
            }
            this.state.loading = false;
        });
    }

    emptyProfile() {
        return {
            overview: null,
            kpis: {
                month_waybill_count: 0,
                month_avg_exception_rate: 0,
                current_month_signed_rate: 0,
                current_month_timeout_rate: 0,
                missing_evidence_rate: 0,
                exception_count: 0,
            },
            risk: {
                exception_waybill_count: 0,
                severe_exception_count: 0,
                timeout_waybill_count: 0,
                missing_evidence_waybill_count: 0,
                top_exception_types: [],
            },
            trends: [],
            recentWaybills: [],
            recentExceptions: [],
        };
    }

    emptySectionErrors() {
        return {
            kpis: "",
            trends: "",
            risk: "",
            recentWaybills: "",
            recentExceptions: "",
        };
    }

    getInitialMockEnabled() {
        try {
            return this.props.action?.params?.mock ?? window.localStorage.getItem(MOCK_STORAGE_KEY) === "1";
        } catch {
            return false;
        }
    }

    persistMockMode() {
        try {
            this.state.mockEnabled ? window.localStorage.setItem(MOCK_STORAGE_KEY, "1") : window.localStorage.removeItem(MOCK_STORAGE_KEY);
        } catch {
            // ignore
        }
    }

    get ui() {
        return {
            title: "司机管理",
            subtitle: "快速定位司机，并查看执行表现、趋势变化与风险情况。",
            badgePrimary: "司机画像",
            badgeSecondary: "执行资源",
            searchPlaceholder: "按司机姓名、手机号或车辆搜索",
            searchButton: "搜索",
            resetButton: "重置",
            empty: "当前没有符合条件的司机。",
            error: "司机列表加载失败，请刷新后重试。",
            noPermission: "当前账号暂无查看司机管理的权限。",
            viewProfile: "查看画像",
            listTitle: "司机列表",
            profileTitle: "概览",
            backToList: "返回列表",
            openWaybills: "查看关联运单",
            openExceptions: "查看关联异常",
            statusLabel: "状态",
            ownVehicleLabel: "自有车辆",
            vehicleLabel: "当前车辆",
            latestExecution: "最近执行时间",
            profileLoading: "正在加载司机画像...",
            profileError: "司机画像加载失败，请返回列表后重试。",
            noTrendData: "当前时间范围内暂无执行数据。",
            noRecentWaybills: "当前没有关联运单。",
            noRecentExceptions: "当前没有关联异常。",
            noExecutionData: "当前司机还没有可统计的执行记录。",
            noRiskData: "当前暂无风险相关数据。",
            noRiskTypeData: "当前暂无异常类型分布。",
            sectionKpi: "核心指标",
            sectionTrends: "趋势分析",
            sectionExecution: "执行概览",
            sectionRisk: "风险与异常",
            sectionRecords: "最近记录",
            sectionRecentExceptions: "最近异常记录",
            remarkLabel: "备注",
            recentVehicleLabel: "最近使用车辆",
            viewAllWaybills: "查看全部运单",
            viewAllExceptions: "查看全部异常",
            timeoutBadge: "超时",
            missingEvidenceBadge: "缺少凭证",
            staleExecutionBadge: "近 7 天无执行",
            drilldownEmptyWaybills: "当前条件下没有可打开的运单记录。",
            drilldownEmptyExceptions: "当前条件下没有可打开的异常记录。",
            kpiSectionError: "核心指标加载失败，已展示为空值，请稍后重试。",
            trendSectionError: "趋势数据加载失败，请稍后重试。",
            riskSectionError: "风险摘要加载失败，请稍后重试。",
            recentWaybillsError: "最近运单加载失败，请稍后重试。",
            recentExceptionsError: "最近异常加载失败，请稍后重试。",
            actionError: "操作失败，请稍后重试。",
            mockOn: "关闭模拟模式",
            mockOff: "开启模拟模式",
            mockTitle: "本地模拟模式",
            mockDescription: "当前页面正在使用演示数据，你可以在本地直接点完整流程，而不依赖真实司机、批次或运单数据。",
            mockReadonlyTip: "模拟模式为只读演示，不会打开真实业务单据。",
        };
    }

    get hasPrevPage() { return this.state.page > 1; }
    get hasNextPage() { return this.state.page * this.state.pageSize < this.state.total; }
    get totalPages() { return Math.max(1, Math.ceil(this.state.total / this.state.pageSize)); }
    get currentProfileDriverName() { return this.state.profile.overview?.driver_name || "司机画像"; }

    get trendCards() {
        const seriesMap = Object.fromEntries((this.state.profile.trends || []).map((item) => [item.metric_code, item]));
        return [
            { key: "month_waybill_count", title: "月度运单趋势", hint: "观察每月配送工作量变化。", series: seriesMap.month_waybill_count || null, percent: false },
            { key: "exception_rate", title: "异常率趋势", hint: "判断风险是偶发还是持续存在。", series: seriesMap.exception_rate || null, percent: true },
            { key: "delivery_quality", title: "签收率与超时率趋势", hint: "对比服务质量与时效变化。", series: this.deliveryQualitySeries, percent: true },
        ];
    }

    get deliveryQualitySeries() {
        const seriesMap = Object.fromEntries((this.state.profile.trends || []).map((item) => [item.metric_code, item]));
        return [seriesMap.signed_rate || null, seriesMap.timeout_rate || null]
            .filter(Boolean)
            .filter((series) => !this.state.hiddenTrendMetrics[series.metric_code]);
    }

    get recentRiskExceptions() {
        return (this.state.profile.recentExceptions || []).slice(0, 3);
    }

    get sortItems() {
        return [
            { key: "latest_execution_at", label: "最近执行时间" },
            { key: "month_avg_exception_rate", label: "月均异常率" },
            { key: "waybill_count", label: "运单数" },
        ];
    }

    async toggleMockMode() {
        this.state.mockEnabled = !this.state.mockEnabled;
        this.persistMockMode();
        this.state.mode = "list";
        this.state.page = 1;
        this.state.activeDriverId = null;
        this.state.hiddenTrendMetrics = { signed_rate: false, timeout_rate: false };
        this.state.profile = this.emptyProfile();
        this.state.sectionErrors = this.emptySectionErrors();
        await Promise.all([this.loadFilterOptions(), this.loadDriverList()]);
        this.notification.add(this.state.mockEnabled ? "已开启本地模拟模式。" : "已关闭本地模拟模式。", { type: "success" });
    }

    async loadFilterOptions() {
        if (this.state.mockEnabled) {
            this.state.filterOptions = {
                status_options: [{ value: "active", label: "在用" }, { value: "inactive", label: "停用" }],
                vehicle_options: MOCK_DRIVERS.map((item) => ({ value: String(item.current_vehicle_id), label: item.current_vehicle_label })),
                has_own_vehicle_options: [{ value: "true", label: "有自有车辆" }, { value: "false", label: "无自有车辆" }],
            };
            return;
        }
        try {
            this.state.filterOptions = await this.orm.call("logistics.dispatch.waybill", "getDriverFilterOptions", []);
        } catch (error) {
            this.state.filterOptions = { status_options: [], vehicle_options: [], has_own_vehicle_options: [] };
            if (!this.state.error) this.state.error = this.getListErrorMessage(error);
        }
    }

    buildListParams() {
        return { keyword: this.state.keyword, status: this.state.filters.status, vehicle_id: this.state.filters.vehicleId || false, has_own_vehicle: this.state.filters.hasOwnVehicle, sort_by: this.state.sortBy, sort_order: this.state.sortOrder, page: this.state.page, page_size: this.state.pageSize };
    }

    async loadDriverList() {
        this.state.loading = true;
        this.state.error = "";
        try {
            const payload = this.state.mockEnabled ? buildMockListPayload(this.buildListParams()) : await this.orm.call("logistics.dispatch.waybill", "getDriverList", [this.buildListParams()]);
            this.state.items = payload.items || [];
            this.state.total = payload.total || 0;
            this.state.page = payload.page || this.state.page;
            this.state.pageSize = payload.page_size || this.state.pageSize;
        } catch (error) {
            this.state.items = [];
            this.state.total = 0;
            this.state.error = this.getListErrorMessage(error);
        } finally {
            this.state.loading = false;
        }
    }

    async openProfile(driverId) {
        this.state.mode = "profile";
        this.state.activeDriverId = driverId;
        this.state.profileLoading = true;
        this.state.profileError = "";
        this.state.hiddenTrendMetrics = { signed_rate: false, timeout_rate: false };
        this.state.sectionErrors = this.emptySectionErrors();
        try {
            if (this.state.mockEnabled) {
                this.state.profile = getMockProfile(driverId) || this.emptyProfile();
                return;
            }
            const range = this.getTrendDateRange();
            const [overview, kpis, risk, trends, recentWaybills, recentExceptions] = await Promise.allSettled([
                this.apiRequest(`/api/admin/logistics/drivers/${driverId}/profile`),
                this.apiRequest(`/api/admin/logistics/drivers/${driverId}/kpis`),
                this.apiRequest(`/api/admin/logistics/drivers/${driverId}/risk-summary`),
                this.apiRequest(`/api/admin/logistics/drivers/${driverId}/trends?metric_codes=month_waybill_count,exception_rate,signed_rate,timeout_rate&date_from=${encodeURIComponent(range.dateFrom)}&date_to=${encodeURIComponent(range.dateTo)}`),
                this.apiRequest(`/api/admin/logistics/drivers/${driverId}/recent-waybills`),
                this.apiRequest(`/api/admin/logistics/drivers/${driverId}/recent-exceptions`),
            ]);

            if (overview.status !== "fulfilled") {
                throw new Error(overview.reason?.message || this.ui.profileError);
            }

            const sectionErrors = this.emptySectionErrors();
            if (kpis.status !== "fulfilled") sectionErrors.kpis = this.ui.kpiSectionError;
            if (trends.status !== "fulfilled") sectionErrors.trends = this.ui.trendSectionError;
            if (risk.status !== "fulfilled") sectionErrors.risk = this.ui.riskSectionError;
            if (recentWaybills.status !== "fulfilled") sectionErrors.recentWaybills = this.ui.recentWaybillsError;
            if (recentExceptions.status !== "fulfilled") sectionErrors.recentExceptions = this.ui.recentExceptionsError;

            this.state.profile = {
                overview: overview.value.data,
                kpis: kpis.status === "fulfilled" ? kpis.value.data : this.emptyProfile().kpis,
                risk: risk.status === "fulfilled" ? risk.value.data : this.emptyProfile().risk,
                trends: trends.status === "fulfilled" ? trends.value.data.series || [] : [],
                recentWaybills: recentWaybills.status === "fulfilled" ? recentWaybills.value.data.items || [] : [],
                recentExceptions: recentExceptions.status === "fulfilled" ? recentExceptions.value.data.items || [] : [],
            };
            this.state.sectionErrors = sectionErrors;
        } catch (error) {
            this.state.profile = this.emptyProfile();
            this.state.profileError = this.getProfileErrorMessage(error);
        } finally {
            this.state.profileLoading = false;
        }
    }

    backToList() { this.state.mode = "list"; this.state.activeDriverId = null; }
    onKeywordInput(ev) { this.state.keyword = ev.target.value; }
    onKeywordKeydown(ev) { if (ev.key === "Enter") this.onSearch(); }
    onStatusChange(ev) { this.state.filters.status = ev.target.value; }
    onVehicleChange(ev) { this.state.filters.vehicleId = ev.target.value; }
    onOwnVehicleChange(ev) { this.state.filters.hasOwnVehicle = ev.target.value; }
    async onSearch() { this.state.page = 1; await this.loadDriverList(); }
    async onReset() { this.state.keyword = ""; this.state.filters = { status: "", hasOwnVehicle: "", vehicleId: "" }; this.state.sortBy = "latest_execution_at"; this.state.sortOrder = "desc"; this.state.page = 1; await this.loadDriverList(); }
    async onPageChange(direction) { if (direction === "prev" && this.hasPrevPage) this.state.page -= 1; if (direction === "next" && this.hasNextPage) this.state.page += 1; await this.loadDriverList(); }
    async onSortChange(sortKey) { if (this.state.sortBy === sortKey) this.state.sortOrder = this.state.sortOrder === "desc" ? "asc" : "desc"; else { this.state.sortBy = sortKey; this.state.sortOrder = "desc"; } this.state.page = 1; await this.loadDriverList(); }

    getTrendDateRange() {
        const now = new Date();
        const end = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
        const start = new Date(now.getFullYear(), now.getMonth() - 5, 1);
        return { dateFrom: `${start.getFullYear()}-${String(start.getMonth() + 1).padStart(2, "0")}-01`, dateTo: end };
    }

    getCurrentMonthBucket() {
        const now = new Date();
        return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
    }

    buildSectionTitle(suffix) {
        return `${this.currentProfileDriverName}${suffix ? `·${suffix}` : ""}`;
    }

    formatDateTime(value) { return value ? value.replace("T", " ").slice(0, 16) : "-"; }
    formatPercent(value) { return `${((value || 0) * 100).toFixed(1)}%`; }
    formatValue(value, isPercent = false) { return isPercent ? this.formatPercent(value) : `${value ?? 0}`; }
    getSeriesIndex(seriesList, metricCode) { return (seriesList || []).findIndex((item) => item.metric_code === metricCode); }
    getRateRiskMeta(value) {
        const rate = Number(value || 0);
        if (rate >= 0.05) return { tone: "high", label: "高风险" };
        if (rate >= 0.02) return { tone: "medium", label: "中风险" };
        return { tone: "low", label: "低风险" };
    }
    getRateRiskLabel(value) { return this.getRateRiskMeta(value).label; }
    getRateRiskTone(value) { return this.getRateRiskMeta(value).tone; }
    isStaleExecution(value) {
        if (!value) return true;
        const parsed = new Date(String(value).replace(" ", "T"));
        if (Number.isNaN(parsed.getTime())) return false;
        return Date.now() - parsed.getTime() >= 7 * 24 * 60 * 60 * 1000;
    }
    getTrendMax(points = []) { return Math.max(...points.map((item) => Number(item.value || 0)), 0); }
    getBarHeight(series, point) { const max = this.getTrendMax(series?.points || []); return max ? Math.max(8, Math.round((Number(point.value || 0) / max) * 100)) : 8; }
    getDualBarHeight(seriesList, point, index) { const values = (seriesList || []).flatMap((series) => (series?.points || []).map((item) => Number(item.value || 0))); const max = Math.max(...values, 0); const value = Number(seriesList[index]?.points?.find((item) => item.bucket === point.bucket)?.value || 0); return max ? Math.max(8, Math.round((value / max) * 100)) : 8; }
    getTrendPointValue(series, bucket) { return Number(series?.points?.find((item) => item.bucket === bucket)?.value || 0); }
    getTrendMetricLabel(metricCode) {
        if (metricCode === "signed_rate") return "签收率";
        if (metricCode === "timeout_rate") return "超时率";
        return metricCode || "-";
    }
    extractErrorMessage(error) { return String(error?.message || error?.data?.message || error?.data?.debug || "").trim(); }
    isPermissionError(error) {
        const message = this.extractErrorMessage(error).toLowerCase();
        return ["accesserror", "access denied", "forbidden", "permission", "权限", "无权", "denied"].some((keyword) => message.includes(keyword));
    }
    getListErrorMessage(error) { return this.isPermissionError(error) ? this.ui.noPermission : this.ui.error; }
    getProfileErrorMessage(error) { return this.isPermissionError(error) ? this.ui.noPermission : (this.extractErrorMessage(error) || this.ui.profileError); }
    notifyMockReadonly() { this.notification.add(this.ui.mockReadonlyTip, { type: "info" }); }
    notifyActionError(error) { this.notification.add(error?.message || this.ui.actionError, { type: "danger" }); }
    toggleTrendMetric(metricCode) { this.state.hiddenTrendMetrics[metricCode] = !this.state.hiddenTrendMetrics[metricCode]; }

    async onHeaderAction(target) {
        if (!this.state.activeDriverId) return;
        if (this.state.mockEnabled) return this.notifyMockReadonly();
        if (target === "waybills") return this.openDriverWaybillList([], this.buildSectionTitle("关联运单"));
        if (target === "exceptions") return this.openDriverExceptionList([], this.buildSectionTitle("关联异常"));
    }

    async onKpiClick(metricCode) {
        if (this.state.mockEnabled) return this.notifyMockReadonly();
        try {
            const currentMonthBucket = this.getCurrentMonthBucket();
            if (metricCode === "exception_count") {
                return this.openExceptionDrilldown(metricCode, { title: this.buildSectionTitle("关联异常") });
            }
            if (metricCode === "month_avg_exception_rate") {
                return this.openWaybillDrilldown(metricCode, { title: this.buildSectionTitle("异常运单") });
            }
            if (metricCode === "missing_evidence_rate") {
                return this.openWaybillDrilldown(metricCode, { title: this.buildSectionTitle("缺少凭证运单") });
            }
            if (metricCode === "current_month_signed_rate") {
                return this.openWaybillDrilldown(metricCode, { bucket: currentMonthBucket, title: this.buildSectionTitle("本月签收运单") });
            }
            if (metricCode === "current_month_timeout_rate") {
                return this.openWaybillDrilldown(metricCode, { bucket: currentMonthBucket, title: this.buildSectionTitle("本月超时运单") });
            }
            return this.openWaybillDrilldown(metricCode, { bucket: currentMonthBucket, title: this.buildSectionTitle("本月运单") });
        } catch (error) {
            this.notifyActionError(error);
        }
    }

    async onRiskSummaryClick(metricCode) {
        if (this.state.mockEnabled) return this.notifyMockReadonly();
        try {
            if (metricCode === "severe_exception_count") {
                return this.openExceptionDrilldown("exception_count", {
                    title: this.buildSectionTitle("严重异常"),
                    severityLevels: ["high", "critical"],
                });
            }
            if (metricCode === "timeout_waybill_count") {
                return this.openWaybillDrilldown("current_month_timeout_rate", { title: this.buildSectionTitle("超时运单") });
            }
            if (metricCode === "missing_evidence_waybill_count") {
                return this.openWaybillDrilldown("missing_evidence_rate", { title: this.buildSectionTitle("缺少凭证运单") });
            }
            return this.openWaybillDrilldown("month_avg_exception_rate", { title: this.buildSectionTitle("异常运单") });
        } catch (error) {
            this.notifyActionError(error);
        }
    }

    async onExecutionSummaryClick(target) {
        if (this.state.mockEnabled) return this.notifyMockReadonly();
        try {
            if (target === "recent_30d_waybill_count") {
                return this.openDriverWaybillList(this.buildRecentDaysDomain(30), this.buildSectionTitle("近 30 天运单"));
            }
            if (target === "waybill_count") {
                return this.openDriverWaybillList([], this.buildSectionTitle("全部运单"));
            }
        } catch (error) {
            this.notifyActionError(error);
        }
    }

    buildCurrentMonthDomain() {
        const now = new Date();
        const firstDay = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-01`;
        const lastDay = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate()).padStart(2, "0")}`;
        return [["delivery_date", ">=", firstDay], ["delivery_date", "<=", lastDay]];
    }

    buildRecentDaysDomain(days) {
        const end = new Date();
        const start = new Date(end.getTime() - (days - 1) * 24 * 60 * 60 * 1000);
        const format = (value) => `${value.getFullYear()}-${String(value.getMonth() + 1).padStart(2, "0")}-${String(value.getDate()).padStart(2, "0")}`;
        return [["delivery_date", ">=", format(start)], ["delivery_date", "<=", format(end)]];
    }

    async onTrendPointClick(metricCode, bucket) {
        if (this.state.mockEnabled) return this.notifyMockReadonly();
        try {
            if (metricCode === "exception_rate") {
                return this.openWaybillDrilldown(metricCode, { bucket, title: this.buildSectionTitle(`${bucket}异常运单`) });
            }
            if (metricCode === "signed_rate") {
                return this.openWaybillDrilldown(metricCode, { bucket, title: this.buildSectionTitle(`${bucket}签收运单`) });
            }
            if (metricCode === "timeout_rate") {
                return this.openWaybillDrilldown(metricCode, { bucket, title: this.buildSectionTitle(`${bucket}超时运单`) });
            }
            return this.openWaybillDrilldown(metricCode, { bucket, title: this.buildSectionTitle(`${bucket}运单`) });
        } catch (error) {
            this.notifyActionError(error);
        }
    }

    buildBucketDomain(bucket) {
        const [year, month] = bucket.split("-").map(Number);
        const lastDay = new Date(year, month, 0).getDate();
        return [["delivery_date", ">=", `${bucket}-01`], ["delivery_date", "<=", `${bucket}-${String(lastDay).padStart(2, "0")}`]];
    }

    async openWaybillDrilldown(metricCode, { bucket = null, title } = {}) {
        const payload = await this.apiRequest(`/api/admin/logistics/drivers/${this.state.activeDriverId}/waybills/drilldown`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ metric_code: metricCode, bucket, page: 1, page_size: 100 }),
        });
        const recordIds = payload.data?.record_ids || [];
        if (!recordIds.length) {
            this.notification.add(this.ui.drilldownEmptyWaybills, { type: "info" });
            return;
        }
        return this.openDriverWaybillList([["id", "in", recordIds]], title || this.buildSectionTitle("关联运单"));
    }

    async openExceptionDrilldown(metricCode, { bucket = null, title, exceptionType = null, severityLevels = null } = {}) {
        const payload = await this.apiRequest(`/api/admin/logistics/drivers/${this.state.activeDriverId}/exceptions/drilldown`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ metric_code: metricCode, bucket, page: 1, page_size: 100, exception_type: exceptionType, severity_levels: severityLevels }),
        });
        const recordIds = payload.data?.record_ids || [];
        if (!recordIds.length) {
            this.notification.add(this.ui.drilldownEmptyExceptions, { type: "info" });
            return;
        }
        return this.openDriverExceptionList([["id", "in", recordIds]], title || this.buildSectionTitle("关联异常"));
    }

    async openExceptionTypeDrilldown(exceptionType, exceptionTypeLabel) {
        if (this.state.mockEnabled) return this.notifyMockReadonly();
        try {
            return this.openExceptionDrilldown("exception_count", {
                exceptionType,
                title: this.buildSectionTitle(`${exceptionTypeLabel}异常`),
            });
        } catch (error) {
            this.notifyActionError(error);
        }
    }

    async openDriverWaybillList(extraDomain = [], name = "司机关联运单") {
        if (this.state.mockEnabled) return this.notifyMockReadonly();
        return this.actionService.doAction({ type: "ir.actions.act_window", name, res_model: "logistics.dispatch.waybill", views: [[false, "list"], [false, "form"]], domain: [["driver_employee_id", "=", this.state.activeDriverId], ...extraDomain] });
    }

    async openDriverExceptionList(extraDomain = [], name = "司机关联异常") {
        if (this.state.mockEnabled) return this.notifyMockReadonly();
        return this.actionService.doAction({ type: "ir.actions.act_window", name, res_model: "logistics.trace.exception", views: [[false, "list"], [false, "form"]], domain: [["waybill_id.driver_employee_id", "=", this.state.activeDriverId], ...extraDomain] });
    }

    async openWaybillForm(waybillId) {
        if (this.state.mockEnabled) return this.notifyMockReadonly();
        return this.actionService.doAction({ type: "ir.actions.act_window", res_model: "logistics.dispatch.waybill", views: [[false, "form"]], res_id: waybillId });
    }

    async openExceptionForm(exceptionId) {
        if (this.state.mockEnabled) return this.notifyMockReadonly();
        return this.actionService.doAction({ type: "ir.actions.act_window", res_model: "logistics.trace.exception", views: [[false, "form"]], res_id: exceptionId });
    }

    async apiRequest(url, options = {}) {
        const response = await fetch(url, { method: options.method || "GET", headers: options.headers || {}, body: options.body });
        const payload = await response.json().catch(() => null);
        const fallbackMessage = response.status === 403 ? this.ui.noPermission : "请求失败。";
        if (!response.ok || !payload || payload.code !== 0) throw new Error(payload?.data?.errors?.[0]?.error_message || payload?.message || fallbackMessage);
        return payload;
    }
}

const actionsRegistry = registry.category("actions");
if (!actionsRegistry.contains("logistics_web.driver_management")) {
    actionsRegistry.add("logistics_web.driver_management", LogisticsDriverManagementActionV2);
}
