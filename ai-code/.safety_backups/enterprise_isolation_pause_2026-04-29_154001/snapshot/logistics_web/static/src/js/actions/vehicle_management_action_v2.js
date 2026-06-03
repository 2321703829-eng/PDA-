/** @odoo-module */

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

export class LogisticsVehicleManagementActionV2 extends Component {
    static template = "logistics_web.VehicleManagementActionV2";
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
            filters: { status: "", warehouseId: "", driverId: "" },
            sortBy: "latest_execution_at",
            sortOrder: "desc",
            page: 1,
            pageSize: 20,
            total: 0,
            items: [],
            filterOptions: { status_options: [], warehouse_options: [], driver_options: [] },
            activeVehicleId: null,
            profileLoading: false,
            profileError: "",
            profile: this.emptyProfile(),
        });

        onWillStart(async () => {
            await Promise.all([this.loadFilterOptions(), this.loadVehicleList()]);
            const initialVehicleId = Number(this.props.action?.params?.vehicle_id || 0);
            if (initialVehicleId) {
                await this.openProfile(initialVehicleId);
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

    get hasPrevPage() {
        return this.state.page > 1;
    }

    get hasNextPage() {
        return this.state.page * this.state.pageSize < this.state.total;
    }

    get totalPages() {
        return Math.max(1, Math.ceil(this.state.total / this.state.pageSize));
    }

    get currentProfileVehicleName() {
        return this.state.profile.overview?.vehicle_label || "车辆画像";
    }

    get sortItems() {
        return [
            { key: "latest_execution_at", label: "最近执行时间" },
            { key: "month_avg_exception_rate", label: "月均异常率" },
            { key: "waybill_count", label: "运单数" },
        ];
    }

    async loadFilterOptions() {
        try {
            this.state.filterOptions = await this.orm.call("logistics.dispatch.waybill", "getVehicleFilterOptions", []);
        } catch (error) {
            this.state.filterOptions = { status_options: [], warehouse_options: [], driver_options: [] };
            if (!this.state.error) {
                this.state.error = this.getErrorMessage(error, "车辆筛选项加载失败");
            }
        }
    }

    buildListParams() {
        return {
            keyword: this.state.keyword,
            status: this.state.filters.status,
            warehouse_id: this.state.filters.warehouseId || false,
            driver_id: this.state.filters.driverId || false,
            sort_by: this.state.sortBy,
            sort_order: this.state.sortOrder,
            page: this.state.page,
            page_size: this.state.pageSize,
        };
    }

    async loadVehicleList() {
        this.state.loading = true;
        this.state.error = "";
        try {
            const payload = await this.orm.call("logistics.dispatch.waybill", "getVehicleList", [this.buildListParams()]);
            this.state.items = payload.items || [];
            this.state.total = payload.total || 0;
            this.state.page = payload.page || this.state.page;
            this.state.pageSize = payload.page_size || this.state.pageSize;
        } catch (error) {
            this.state.items = [];
            this.state.total = 0;
            this.state.error = this.getErrorMessage(error, "车辆列表加载失败");
        } finally {
            this.state.loading = false;
        }
    }

    async openProfile(vehicleId) {
        this.state.mode = "profile";
        this.state.activeVehicleId = vehicleId;
        this.state.profileLoading = true;
        this.state.profileError = "";
        try {
            const range = this.getTrendDateRange();
            const [overview, kpis, risk, trends, recentWaybills, recentExceptions] = await Promise.allSettled([
                this.apiRequest(`/api/admin/logistics/vehicles/${vehicleId}/profile`),
                this.apiRequest(`/api/admin/logistics/vehicles/${vehicleId}/kpis`),
                this.apiRequest(`/api/admin/logistics/vehicles/${vehicleId}/risk-summary`),
                this.apiRequest(
                    `/api/admin/logistics/vehicles/${vehicleId}/trends?metric_codes=month_waybill_count,exception_rate,signed_rate,timeout_rate&date_from=${encodeURIComponent(range.dateFrom)}&date_to=${encodeURIComponent(range.dateTo)}`
                ),
                this.apiRequest(`/api/admin/logistics/vehicles/${vehicleId}/recent-waybills`),
                this.apiRequest(`/api/admin/logistics/vehicles/${vehicleId}/recent-exceptions`),
            ]);

            if (overview.status !== "fulfilled") {
                throw new Error(overview.reason?.message || "车辆画像加载失败");
            }

            this.state.profile = {
                overview: overview.value.data,
                kpis: kpis.status === "fulfilled" ? kpis.value.data : this.emptyProfile().kpis,
                risk: risk.status === "fulfilled" ? risk.value.data : this.emptyProfile().risk,
                trends: trends.status === "fulfilled" ? trends.value.data.series || [] : [],
                recentWaybills: recentWaybills.status === "fulfilled" ? recentWaybills.value.data.items || [] : [],
                recentExceptions: recentExceptions.status === "fulfilled" ? recentExceptions.value.data.items || [] : [],
            };
        } catch (error) {
            this.state.profile = this.emptyProfile();
            this.state.profileError = this.getErrorMessage(error, "车辆画像加载失败");
        } finally {
            this.state.profileLoading = false;
        }
    }

    backToList() {
        this.state.mode = "list";
        this.state.activeVehicleId = null;
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

    onWarehouseChange(ev) {
        this.state.filters.warehouseId = ev.target.value;
    }

    onDriverChange(ev) {
        this.state.filters.driverId = ev.target.value;
    }

    async onSearch() {
        this.state.page = 1;
        await this.loadVehicleList();
    }

    async onReset() {
        this.state.keyword = "";
        this.state.filters = { status: "", warehouseId: "", driverId: "" };
        this.state.sortBy = "latest_execution_at";
        this.state.sortOrder = "desc";
        this.state.page = 1;
        await this.loadVehicleList();
    }

    async onPageChange(direction) {
        if (direction === "prev" && this.hasPrevPage) {
            this.state.page -= 1;
        }
        if (direction === "next" && this.hasNextPage) {
            this.state.page += 1;
        }
        await this.loadVehicleList();
    }

    async onSortChange(sortKey) {
        if (this.state.sortBy === sortKey) {
            this.state.sortOrder = this.state.sortOrder === "desc" ? "asc" : "desc";
        } else {
            this.state.sortBy = sortKey;
            this.state.sortOrder = "desc";
        }
        this.state.page = 1;
        await this.loadVehicleList();
    }

    async openVehicleWaybillList() {
        if (!this.state.activeVehicleId) {
            return;
        }
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "车辆关联运单",
            res_model: "logistics.dispatch.waybill",
            views: [[false, "list"], [false, "form"]],
            domain: [["vehicle_id", "=", this.state.activeVehicleId]],
        });
    }

    async openVehicleExceptionList() {
        if (!this.state.activeVehicleId) {
            return;
        }
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "车辆关联异常",
            res_model: "logistics.trace.exception",
            views: [[false, "list"], [false, "form"]],
            domain: [["waybill_id.vehicle_id", "=", this.state.activeVehicleId]],
        });
    }

    async openVehicleMasterRecord() {
        if (!this.state.activeVehicleId) {
            return;
        }
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "车辆主档",
            res_model: "fleet.vehicle",
            res_id: this.state.activeVehicleId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    async openVehicleProfileRecord() {
        if (!this.state.activeVehicleId) {
            return;
        }
        const records = await this.orm.searchRead(
            "logistics.vehicle.profile",
            [["vehicle_id", "=", this.state.activeVehicleId]],
            ["id"],
            { limit: 1 }
        );
        if (!records.length) {
            this.notification.add("当前车辆还没有创建车辆画像。", {
                title: "未找到车辆画像",
                type: "warning",
            });
            return;
        }
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "车辆画像",
            res_model: "logistics.vehicle.profile",
            res_id: records[0].id,
            views: [[false, "form"]],
            target: "current",
        });
    }

    getTrendDateRange() {
        const now = new Date();
        const end = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
        const start = new Date(now.getFullYear(), now.getMonth() - 5, 1);
        return {
            dateFrom: `${start.getFullYear()}-${String(start.getMonth() + 1).padStart(2, "0")}-01`,
            dateTo: end,
        };
    }

    formatDateTime(value) {
        return value ? value.replace("T", " ").slice(0, 16) : "-";
    }

    formatPercent(value) {
        return `${((value || 0) * 100).toFixed(1)}%`;
    }

    formatTrendPoints(points = [], percent = false) {
        if (!points.length) {
            return "-";
        }
        return points.map((item) => `${item.bucket}: ${percent ? this.formatPercent(item.value) : item.value}`).join(" / ");
    }

    formatNumber(value, digits = 0) {
        const target = Number(value || 0);
        return target.toFixed(digits);
    }

    getRateRiskTone(value) {
        const rate = Number(value || 0);
        if (rate >= 0.05) return "high";
        if (rate >= 0.02) return "medium";
        return "low";
    }

    getRateRiskLabel(value) {
        const tone = this.getRateRiskTone(value);
        if (tone === "high") return "高风险";
        if (tone === "medium") return "中风险";
        return "低风险";
    }

    isStaleExecution(value) {
        if (!value) {
            return true;
        }
        const target = new Date(value.replace(" ", "T"));
        const diff = Date.now() - target.getTime();
        return diff > 7 * 24 * 60 * 60 * 1000;
    }

    async apiRequest(url, options = {}) {
        const response = await fetch(url, {
            method: options.method || "GET",
            headers: {
                "Content-Type": "application/json",
                ...(options.headers || {}),
            },
            body: options.body ? JSON.stringify(options.body) : undefined,
        });
        const payload = await response.json();
        if (!response.ok || payload.code !== 0) {
            throw new Error(payload?.data?.errors?.[0]?.error_message || payload?.message || "request_failed");
        }
        return payload;
    }

    getErrorMessage(error, fallback) {
        if (error?.message) {
            return error.message;
        }
        return fallback;
    }
}

const actionsRegistry = registry.category("actions");
if (!actionsRegistry.contains("logistics_web.vehicle_management")) {
    actionsRegistry.add("logistics_web.vehicle_management", LogisticsVehicleManagementActionV2);
}
