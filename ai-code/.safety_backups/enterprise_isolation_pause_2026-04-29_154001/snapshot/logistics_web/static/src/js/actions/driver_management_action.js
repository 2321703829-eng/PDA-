/** @odoo-module */

import { Component, onWillStart, useState } from "@odoo/owl";
import { Layout } from "@web/search/layout";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

const MOCK_STORAGE_KEY = "logistics_web_driver_mock";

const MOCK_DRIVERS = [
    {
        driver_id: 101,
        driver_name: "Zhang Qiang",
        mobile: "13800000001",
        current_vehicle_id: 11,
        current_vehicle_label: "SH-A2198 / Cold Chain 4.2m",
        status: "active",
        status_label: "Active",
        latest_execution_at: "2026-04-17 10:12:00",
        has_own_vehicle: true,
        waybill_count: 148,
        month_avg_exception_rate: 0.021,
    },
    {
        driver_id: 102,
        driver_name: "Li Hai",
        mobile: "13800000002",
        current_vehicle_id: 12,
        current_vehicle_label: "SH-B8631 / Box Truck 7.6m",
        status: "resting",
        status_label: "Resting",
        latest_execution_at: "2026-04-16 18:08:00",
        has_own_vehicle: false,
        waybill_count: 132,
        month_avg_exception_rate: 0.046,
    },
];

const MOCK_BUCKETS = ["2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04"];

const MOCK_PROFILE_DATA = {
    101: {
        summary: {
            batch_count: 28,
            waybill_count: 148,
            recent_30d_waybill_count: 36,
            recent_30d_batch_count: 7,
            recent_store_count: 12,
            recent_region_count: 5,
            top_regions: ["Pudong", "Minhang", "Xuhui"],
            top_stores: ["Pudong Store 1", "Minhang Store 2", "Xuhui Flagship"],
        },
        kpis: {
            month_waybill_count: 36,
            month_avg_exception_rate: 0.021,
            current_month_signed_rate: 0.972,
            current_month_timeout_rate: 0.028,
            missing_evidence_rate: 0.014,
            exception_count: 3,
        },
        risk: {
            exception_waybill_count: 3,
            severe_exception_count: 1,
            timeout_waybill_count: 1,
            missing_evidence_waybill_count: 1,
            top_exception_types: [
                { key: "timeout", label: "Timeout", value: 1 },
                { key: "evidence_missing", label: "Missing Evidence", value: 1 },
                { key: "address_change", label: "Address Changed", value: 1 },
            ],
        },
        trends: {
            month_waybill_count: [21, 24, 28, 26, 31, 36],
            exception_rate: [0.041, 0.036, 0.032, 0.028, 0.024, 0.021],
            signed_rate: [0.935, 0.946, 0.952, 0.958, 0.966, 0.972],
            timeout_rate: [0.051, 0.047, 0.043, 0.038, 0.033, 0.028],
        },
        recentWaybills: [
            { waybill_id: 9101, waybill_no: "WB202604170001", status_label: "Signed", store_name: "Pudong Store 1", store_region: "Pudong", delivery_date: "2026-04-17" },
            { waybill_id: 9102, waybill_no: "WB202604160021", status_label: "In Transit", store_name: "Xuhui Flagship", store_region: "Xuhui", delivery_date: "2026-04-16" },
        ],
        recentExceptions: [
            { exception_id: 801, exception_no: "EX20260417001", status_label: "Pending", waybill_no: "WB202604170001", exception_type_label: "Missing Evidence", report_time: "2026-04-17 10:20:00" },
            { exception_id: 802, exception_no: "EX20260414008", status_label: "Closed", waybill_no: "WB202604140031", exception_type_label: "Address Changed", report_time: "2026-04-14 15:36:00" },
        ],
    },
    102: {
        summary: {
            batch_count: 24,
            waybill_count: 132,
            recent_30d_waybill_count: 28,
            recent_30d_batch_count: 6,
            recent_store_count: 9,
            recent_region_count: 4,
            top_regions: ["Baoshan", "Jiading", "Qingpu"],
            top_stores: ["Baoshan North", "Jiading Center", "Qingpu Hub"],
        },
        kpis: {
            month_waybill_count: 28,
            month_avg_exception_rate: 0.046,
            current_month_signed_rate: 0.943,
            current_month_timeout_rate: 0.051,
            missing_evidence_rate: 0.027,
            exception_count: 5,
        },
        risk: {
            exception_waybill_count: 5,
            severe_exception_count: 2,
            timeout_waybill_count: 2,
            missing_evidence_waybill_count: 1,
            top_exception_types: [
                { key: "timeout", label: "Timeout", value: 2 },
                { key: "customer_absent", label: "Customer Absent", value: 2 },
                { key: "evidence_missing", label: "Missing Evidence", value: 1 },
            ],
        },
        trends: {
            month_waybill_count: [30, 32, 29, 25, 27, 28],
            exception_rate: [0.038, 0.041, 0.044, 0.048, 0.047, 0.046],
            signed_rate: [0.952, 0.949, 0.947, 0.944, 0.945, 0.943],
            timeout_rate: [0.029, 0.031, 0.039, 0.046, 0.049, 0.051],
        },
        recentWaybills: [
            { waybill_id: 9201, waybill_no: "WB202604160112", status_label: "Signed", store_name: "Jiading Center", store_region: "Jiading", delivery_date: "2026-04-16" },
            { waybill_id: 9202, waybill_no: "WB202604150041", status_label: "Exception Handling", store_name: "Baoshan North", store_region: "Baoshan", delivery_date: "2026-04-15" },
        ],
        recentExceptions: [
            { exception_id: 803, exception_no: "EX20260416007", status_label: "Processing", waybill_no: "WB202604150041", exception_type_label: "Customer Absent", report_time: "2026-04-16 18:12:00" },
            { exception_id: 804, exception_no: "EX20260413003", status_label: "Closed", waybill_no: "WB202604130019", exception_type_label: "Timeout", report_time: "2026-04-13 11:05:00" },
        ],
    },
};

function deepClone(data) {
    return JSON.parse(JSON.stringify(data));
}

function buildMockFilterOptions() {
    return {
        status_options: [
            { value: "active", label: "Active" },
            { value: "resting", label: "Resting" },
        ],
        vehicle_options: MOCK_DRIVERS.map((item) => ({
            value: String(item.current_vehicle_id),
            label: item.current_vehicle_label,
        })),
        has_own_vehicle_options: [
            { value: "true", label: "Own Vehicle" },
            { value: "false", label: "No Own Vehicle" },
        ],
    };
}

function buildTrendSeries(metricCode, values) {
    return {
        metric_code: metricCode,
        points: values.map((value, index) => ({ bucket: MOCK_BUCKETS[index], value })),
    };
}

function getMockProfile(driverId) {
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
            latest_execution_at: driver.latest_execution_at,
            current_vehicle: {
                vehicle_id: driver.current_vehicle_id,
                vehicle_label: driver.current_vehicle_label,
            },
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
}

function buildMockListPayload(params) {
    const keyword = String(params.keyword || "").trim().toLowerCase();
    let items = MOCK_DRIVERS.filter((item) => {
        const haystack = [item.driver_name, item.mobile, item.current_vehicle_label].join(" ").toLowerCase();
        if (keyword && !haystack.includes(keyword)) {
            return false;
        }
        if (params.status && item.status !== params.status) {
            return false;
        }
        if (params.vehicle_id && String(item.current_vehicle_id) !== String(params.vehicle_id)) {
            return false;
        }
        if (params.has_own_vehicle === "true" && !item.has_own_vehicle) {
            return false;
        }
        if (params.has_own_vehicle === "false" && item.has_own_vehicle) {
            return false;
        }
        return true;
    });

    const sortBy = params.sort_by || "latest_execution_at";
    const sortOrder = params.sort_order === "asc" ? "asc" : "desc";
    items = [...items].sort((left, right) => {
        const leftValue = left[sortBy] ?? "";
        const rightValue = right[sortBy] ?? "";
        if (leftValue === rightValue) {
            return left.driver_name.localeCompare(right.driver_name, "zh-Hans-CN");
        }
        if (sortOrder === "asc") {
            return leftValue > rightValue ? 1 : -1;
        }
        return leftValue < rightValue ? 1 : -1;
    });

    const page = Number(params.page || 1);
    const pageSize = Number(params.page_size || 20);
    const start = (page - 1) * pageSize;
    return {
        items: deepClone(items.slice(start, start + pageSize)),
        total: items.length,
        page,
        page_size: pageSize,
    };
}

export class LogisticsDriverManagementAction extends Component {
    static template = "logistics_web.DriverManagementAction";
    static components = { Layout };
    static props = { ...standardActionServiceProps };

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.notification = useService("notification");
        this.display = {
            controlPanel: false,
            searchPanel: false,
        };
        this.state = useState({
            mode: "list",
            loading: true,
            error: "",
            keyword: "",
            filters: {
                status: "",
                hasOwnVehicle: "",
                vehicleId: "",
            },
            sortBy: "latest_execution_at",
            sortOrder: "desc",
            page: 1,
            pageSize: 20,
            total: 0,
            items: [],
            filterOptions: {
                status_options: [],
                vehicle_options: [],
                has_own_vehicle_options: [],
            },
            activeDriverId: null,
            profileLoading: false,
            profileError: "",
            mockEnabled: this.getInitialMockEnabled(),
            profile: this.createEmptyProfileState(),
        });

        onWillStart(async () => {
            await Promise.all([this.loadFilterOptions(), this.loadDriverList()]);
            this.state.loading = false;
        });
    }

    createEmptyProfileState() {
        return {
            overview: null,
            kpis: null,
            risk: null,
            trends: [],
            recentWaybills: [],
            recentExceptions: [],
        };
    }

    getInitialMockEnabled() {
        const actionMock = this.props.action?.params?.mock;
        if (actionMock !== undefined) {
            return Boolean(actionMock);
        }
        try {
            return window.localStorage.getItem(MOCK_STORAGE_KEY) === "1";
        } catch {
            return false;
        }
    }

    persistMockMode() {
        try {
            if (this.state.mockEnabled) {
                window.localStorage.setItem(MOCK_STORAGE_KEY, "1");
            } else {
                window.localStorage.removeItem(MOCK_STORAGE_KEY);
            }
        } catch {
            // ignore
        }
    }

    get ui() {
        return {
            title: "司机管理",
            subtitle: "先在列表里快速找人，再进入画像页看执行表现、趋势和风险。",
            badgePrimary: "司机画像",
            badgeSecondary: "执行资源",
            searchPlaceholder: "搜索司机姓名、联系方式或车牌号",
            searchButton: "搜索",
            resetButton: "重置",
            empty: "当前没有符合条件的司机。",
            error: "司机列表加载失败，请刷新后重试。",
            viewProfile: "查看画像",
            listTitle: "司机列表",
            profileTitle: "司机画像",
            backToList: "返回司机列表",
            openWaybills: "查看关联运单",
            openExceptions: "查看关联异常",
            statusLabel: "当前状态",
            ownVehicleLabel: "是否有自有车",
            vehicleLabel: "所属车辆",
            latestExecution: "最近执行时间",
            profileLoading: "正在加载司机画像...",
            profileError: "当前司机信息加载失败，请返回列表后重试。",
            noTrendData: "当前时间范围内暂无趋势数据。",
            noRecentWaybills: "暂无最近运单。",
            noRecentExceptions: "暂无最近异常。",
            sectionKpi: "核心指标带",
            sectionTrends: "个人趋势图区",
            sectionExecution: "执行概览区",
            sectionRisk: "风险与异常区",
            sectionRecords: "关联记录区",
        };
    }

    get hasPrevPage() {
        return this.state.page > 1;
    }

    get hasNextPage() {
        return this.state.page * this.state.pageSize < this.state.total;
    }

    get totalPages() {
        return Math.max(1, Math.ceil(this.state.total / this.state.pageSize));
    }

    get currentProfileDriverName() {
        return this.state.profile.overview?.driver_name || "司机画像";
    }

    get trendCards() {
        const seriesMap = Object.fromEntries((this.state.profile.trends || []).map((item) => [item.metric_code, item]));
        return [
            {
                key: "month_waybill_count",
                title: "司机月度运单量趋势",
                hint: "看这个司机最近几个月的运单活跃度。",
                series: seriesMap.month_waybill_count || null,
                percent: false,
            },
            {
                key: "exception_rate",
                title: "司机异常率趋势",
                hint: "看异常风险是否持续偏高。",
                series: seriesMap.exception_rate || null,
                percent: true,
            },
            {
                key: "delivery_quality",
                title: "签收率与超时率趋势",
                hint: "对比签收表现和超时表现的月度变化。",
                series: [seriesMap.signed_rate || null, seriesMap.timeout_rate || null].filter(Boolean),
                percent: true,
            },
        ];
    }

    get sortItems() {
        return [
            { key: "latest_execution_at", label: "最近执行时间" },
            { key: "month_avg_exception_rate", label: "月均异常率" },
            { key: "waybill_count", label: "关联运单数" },
        ];
    }

    async loadFilterOptions() {
        this.state.filterOptions = await this.orm.call("logistics.dispatch.waybill", "getDriverFilterOptions", []);
    }

    async loadDriverList() {
        this.state.loading = true;
        this.state.error = "";
        try {
            const payload = await this.orm.call("logistics.dispatch.waybill", "getDriverList", [this.buildListParams()]);
            this.state.items = payload.items || [];
            this.state.total = payload.total || 0;
            this.state.page = payload.page || this.state.page;
            this.state.pageSize = payload.page_size || this.state.pageSize;
        } catch {
            this.state.items = [];
            this.state.total = 0;
            this.state.error = this.ui.error;
        } finally {
            this.state.loading = false;
        }
    }

    buildListParams() {
        return {
            keyword: this.state.keyword,
            status: this.state.filters.status,
            vehicle_id: this.state.filters.vehicleId || false,
            has_own_vehicle: this.state.filters.hasOwnVehicle,
            sort_by: this.state.sortBy,
            sort_order: this.state.sortOrder,
            page: this.state.page,
            page_size: this.state.pageSize,
        };
    }

    async openProfile(driverId) {
        this.state.mode = "profile";
        this.state.activeDriverId = driverId;
        this.state.profileLoading = true;
        this.state.profileError = "";
        try {
            const dateRange = this.getTrendDateRange();
            const [overview, kpis, risk, trends, recentWaybills, recentExceptions] = await Promise.all([
                this.apiRequest(`/api/admin/logistics/drivers/${driverId}/profile`),
                this.apiRequest(`/api/admin/logistics/drivers/${driverId}/kpis`),
                this.apiRequest(`/api/admin/logistics/drivers/${driverId}/risk-summary`),
                this.apiRequest(
                    `/api/admin/logistics/drivers/${driverId}/trends?metric_codes=month_waybill_count,exception_rate,signed_rate,timeout_rate&date_from=${encodeURIComponent(dateRange.dateFrom)}&date_to=${encodeURIComponent(dateRange.dateTo)}`
                ),
                this.apiRequest(`/api/admin/logistics/drivers/${driverId}/recent-waybills`),
                this.apiRequest(`/api/admin/logistics/drivers/${driverId}/recent-exceptions`),
            ]);
            this.state.profile.overview = overview.data;
            this.state.profile.kpis = kpis.data;
            this.state.profile.risk = risk.data;
            this.state.profile.trends = trends.data.series || [];
            this.state.profile.recentWaybills = recentWaybills.data.items || [];
            this.state.profile.recentExceptions = recentExceptions.data.items || [];
        } catch (error) {
            this.state.profileError = error.message || this.ui.profileError;
        } finally {
            this.state.profileLoading = false;
        }
    }

    backToList() {
        this.state.mode = "list";
        this.state.activeDriverId = null;
    }

    onKeywordInput(ev) {
        this.state.keyword = ev.target.value;
    }

    onKeywordKeydown(ev) {
        if (ev.key === "Enter") {
            this.onSearch();
        }
    }

    onStatusChange(ev) {
        this.state.filters.status = ev.target.value;
    }

    onVehicleChange(ev) {
        this.state.filters.vehicleId = ev.target.value;
    }

    onOwnVehicleChange(ev) {
        this.state.filters.hasOwnVehicle = ev.target.value;
    }

    async onSearch() {
        this.state.page = 1;
        await this.loadDriverList();
    }

    async onReset() {
        this.state.keyword = "";
        this.state.filters.status = "";
        this.state.filters.vehicleId = "";
        this.state.filters.hasOwnVehicle = "";
        this.state.sortBy = "latest_execution_at";
        this.state.sortOrder = "desc";
        this.state.page = 1;
        await this.loadDriverList();
    }

    async onPageChange(direction) {
        if (direction === "prev" && this.hasPrevPage) {
            this.state.page -= 1;
        }
        if (direction === "next" && this.hasNextPage) {
            this.state.page += 1;
        }
        await this.loadDriverList();
    }

    async onSortChange(sortKey) {
        if (this.state.sortBy === sortKey) {
            this.state.sortOrder = this.state.sortOrder === "desc" ? "asc" : "desc";
        } else {
            this.state.sortBy = sortKey;
            this.state.sortOrder = "desc";
        }
        this.state.page = 1;
        await this.loadDriverList();
    }

    getTrendDateRange() {
        const now = new Date();
        const end = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
        const start = new Date(now.getFullYear(), now.getMonth() - 5, 1);
        const dateFrom = `${start.getFullYear()}-${String(start.getMonth() + 1).padStart(2, "0")}-01`;
        return { dateFrom, dateTo: end };
    }

    formatDateTime(value) {
        if (!value) {
            return "-";
        }
        return value.replace("T", " ").slice(0, 16);
    }

    formatPercent(value) {
        return `${((value || 0) * 100).toFixed(1)}%`;
    }

    formatValue(value, isPercent = false) {
        return isPercent ? this.formatPercent(value) : `${value ?? 0}`;
    }

    getTrendMax(points = []) {
        const values = points.map((item) => Number(item.value || 0));
        return Math.max(...values, 0);
    }

    getBarHeight(series, point) {
        const max = this.getTrendMax(series?.points || []);
        if (!max) {
            return 8;
        }
        return Math.max(8, Math.round((Number(point.value || 0) / max) * 100));
    }

    getDualBarHeight(seriesList, point, index) {
        const values = (seriesList || []).flatMap((series) => (series?.points || []).map((item) => Number(item.value || 0)));
        const max = Math.max(...values, 0);
        const value = Number(seriesList[index]?.points?.find((item) => item.bucket === point.bucket)?.value || 0);
        if (!max) {
            return 8;
        }
        return Math.max(8, Math.round((value / max) * 100));
    }

    async onHeaderAction(target) {
        if (!this.state.activeDriverId) {
            return;
        }
        if (target === "waybills") {
            return this.openDriverWaybillList([], `${this.currentProfileDriverName}关联运单`);
        }
        if (target === "exceptions") {
            return this.openDriverExceptionList([], `${this.currentProfileDriverName}关联异常`);
        }
    }

    async onKpiClick(metricCode) {
        if (metricCode === "exception_count" || metricCode === "month_avg_exception_rate") {
            return this.openDriverExceptionList([], `${this.currentProfileDriverName}异常列表`);
        }
        if (metricCode === "missing_evidence_rate") {
            return this.openDriverWaybillList([["evidence_status", "=", "missing"]], `${this.currentProfileDriverName}缺证据运单`);
        }
        if (metricCode === "current_month_signed_rate") {
            return this.openDriverWaybillList([["state", "in", ["signed", "done"]], ...this.buildCurrentMonthDomain()], `${this.currentProfileDriverName}本月签收运单`);
        }
        if (metricCode === "current_month_timeout_rate") {
            return this.openDriverWaybillList(this.buildCurrentMonthDomain(), `${this.currentProfileDriverName}本月运单`);
        }
        if (metricCode === "month_waybill_count") {
            return this.openDriverWaybillList(this.buildCurrentMonthDomain(), `${this.currentProfileDriverName}本月运单`);
        }
    }

    buildCurrentMonthDomain() {
        const now = new Date();
        const dateFrom = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-01`;
        const dateTo = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate()).padStart(2, "0")}`;
        return [["delivery_date", ">=", dateFrom], ["delivery_date", "<=", dateTo]];
    }

    async onTrendPointClick(metricCode, bucket) {
        if (metricCode === "exception_rate") {
            return this.openDriverExceptionList([], `${this.currentProfileDriverName} ${bucket}异常`);
        }
        return this.openDriverWaybillList(this.buildBucketDomain(bucket), `${this.currentProfileDriverName} ${bucket}运单`);
    }

    buildBucketDomain(bucket) {
        const [year, month] = bucket.split("-").map(Number);
        const lastDay = new Date(year, month, 0).getDate();
        return [
            ["delivery_date", ">=", `${bucket}-01`],
            ["delivery_date", "<=", `${bucket}-${String(lastDay).padStart(2, "0")}`],
        ];
    }

    async openDriverWaybillList(extraDomain = [], name = "司机运单列表") {
        const domain = [["driver_employee_id", "=", this.state.activeDriverId], ...extraDomain];
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name,
            res_model: "logistics.dispatch.waybill",
            views: [[false, "list"], [false, "form"]],
            domain,
        });
    }

    async openDriverExceptionList(extraDomain = [], name = "司机异常列表") {
        const domain = [["waybill_id.driver_employee_id", "=", this.state.activeDriverId], ...extraDomain];
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name,
            res_model: "logistics.trace.exception",
            views: [[false, "list"], [false, "form"]],
            domain,
        });
    }

    async openWaybillForm(waybillId) {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: "logistics.dispatch.waybill",
            views: [[false, "form"]],
            res_id: waybillId,
        });
    }

    async openExceptionForm(exceptionId) {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: "logistics.trace.exception",
            views: [[false, "form"]],
            res_id: exceptionId,
        });
    }

    async apiRequest(url, options = {}) {
        const response = await fetch(url, {
            method: options.method || "GET",
            headers: options.headers || {},
            body: options.body,
        });
        const payload = await response.json().catch(() => null);
        if (!response.ok || !payload || payload.code !== 0) {
            throw new Error(payload?.data?.errors?.[0]?.error_message || payload?.message || "请求失败，请稍后重试。");
        }
        return payload;
    }
}

registry.category("actions").add("logistics_web.driver_management", LogisticsDriverManagementAction);
