/** @odoo-module */

import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";

const LOGISTICS_IMPORT_MODELS = new Set([
    "logistics.dispatch.wave",
    "logistics.dispatch.batch",
    "logistics.dispatch.waybill",
    "logistics.trace.event",
    "logistics.trace.evidence",
    "logistics.trace.evidence.summary",
    "logistics.trace.exception",
]);

const LOGISTICS_OPERATION_MODELS = new Set([
    "logistics.dispatch.wave",
    "logistics.dispatch.batch",
    "logistics.dispatch.waybill",
    "logistics.dispatch.waybill.customer.line",
    "logistics.dispatch.waybill.customer.goods.line",
    "logistics.dispatch.waybill.order.line",
]);

patch(ListController.prototype, {
    get showLogisticsDeleteButton() {
        return (
            !this.env.inDialog &&
            this.props.showButtons &&
            this.activeActions.delete &&
            LOGISTICS_OPERATION_MODELS.has(this.props.resModel)
        );
    },

    async onClickLogisticsDelete() {
        const selectedIds = await this.model.root.getResIds(true);
        if (!selectedIds.length) {
            this.env.services.notification.add("请先勾选至少一条记录，再执行删除。", {
                type: "warning",
            });
            return;
        }
        const confirmed = window.confirm(`确定删除已选中的 ${selectedIds.length} 条记录吗？`);
        if (!confirmed) {
            return;
        }
        try {
            await this.env.services.orm.unlink(this.props.resModel, selectedIds, {
                context: this.model.root.context,
            });
            this.env.services.notification.add("删除成功，正在刷新列表。", {
                type: "success",
            });
            window.location.reload();
        } catch (error) {
            this.env.services.notification.add(
                String(error?.message || "删除失败，请稍后重试。"),
                { type: "danger" }
            );
        }
    },

    get showLogisticsImportButton() {
        return (
            !this.env.inDialog &&
            this.props.showButtons &&
            this.activeActions.create &&
            LOGISTICS_IMPORT_MODELS.has(this.props.resModel)
        );
    },

    onClickLogisticsImport() {
        if (this.props.resModel === "logistics.dispatch.waybill") {
            this.actionService.doAction("logistics_web.action_logistics_web_import_center");
            return;
        }
        this.actionService.doAction({
            type: "ir.actions.client",
            tag: "import",
            params: {
                active_model: this.props.resModel,
                context: this.model.root.context,
            },
        });
    },

    getLogisticsExportActionDescription() {
        if (this.props.resModel === "logistics.trace.evidence" || this.props.resModel === "logistics.trace.evidence.summary") {
            return "下载图片";
        }
        return "导出";
    },

    get showLogisticsExportButton() {
        return (
            !this.env.inDialog &&
            this.props.showButtons &&
            (
                this.props.resModel === "logistics.dispatch.waybill" ||
                this.props.resModel === "logistics.trace.evidence" ||
                this.props.resModel === "logistics.trace.evidence.summary" ||
                this.isCustomerProfileExportList ||
                this.isProductProfileExportList
            )
        );
    },

    getStaticActionMenuItems() {
        const items = super.getStaticActionMenuItems();
        if (this.showLogisticsExportButton) {
            items.logistics_export = {
                sequence: 12,
                icon: "fa fa-download",
                description: this.getLogisticsExportActionDescription(),
                callback: () => this.onClickLogisticsExport(),
            };
        }
        return items;
    },

    get isCustomerProfileExportList() {
        const context = this.model.root.context || {};
        return (
            this.props.resModel === "res.partner" &&
            Boolean(
                context.default_is_logistics_partner ||
                context.default_is_logistics_customer ||
                context.default_is_logistics_store
            )
        );
    },

    get isProductProfileExportList() {
        return this.props.resModel === "product.template" || this.props.resModel === "logistics.product.unit";
    },

    async onClickLogisticsExport() {
        if (this.props.resModel === "logistics.dispatch.waybill") {
            await this.exportWaybillProfiles();
            return;
        }
        if (this.props.resModel === "logistics.trace.evidence") {
            await this.exportEvidenceImages();
            return;
        }
        if (this.props.resModel === "logistics.trace.evidence.summary") {
            await this.exportEvidenceSummaryImages();
            return;
        }
        if (this.isCustomerProfileExportList) {
            await this.exportCustomerProfiles();
            return;
        }
        if (this.isProductProfileExportList) {
            await this.exportProductProfiles();
        }
    },

    async exportWaybillProfiles() {
        const selectedIds = await this.model.root.getResIds(true);
        if (!selectedIds.length) {
            this.env.services.notification.add("请先选择至少一条运单，再发起导出。", {
                type: "warning",
            });
            return;
        }
        await this.openExportResultFromRequest(
            "/api/admin/logistics/exports/waybill",
            {
                object_type: "dispatch_main",
                entry_type: "from_waybill",
                export_mode: "standard_xlsx",
                selected_ids: selectedIds,
                from_page: "waybill_list",
                scope_snapshot: {
                    selected_waybill_ids: selectedIds,
                },
            },
            "运单导出失败，请稍后重试。"
        );
    },

    async exportEvidenceImages() {
        const selectedIds = await this.model.root.getResIds(true);
        if (!selectedIds.length) {
            this.env.services.notification.add("请先选择至少一条证据，再发起导出。", {
                type: "warning",
            });
            return;
        }
        await this.openExportResultFromRequest(
            "/api/admin/logistics/exports/evidence-images",
            {
                object_type: "evidence_image_bundle",
                entry_type: "from_evidence",
                export_mode: "zip_package",
                package_structure: "evidence_image_bundle_v1",
                source_model: "logistics.trace.evidence",
                selected_ids: selectedIds,
                from_page: "evidence_list",
                scope_snapshot: {
                    selected_evidence_ids: selectedIds,
                },
            },
            "证据原图批量导出失败，请稍后重试。"
        );
    },

    async exportEvidenceSummaryImages() {
        const selectedIds = await this.model.root.getResIds(true);
        if (!selectedIds.length) {
            this.env.services.notification.add("\u8bf7\u5148\u9009\u62e9\u81f3\u5c11\u4e00\u6761\u7559\u75d5\u6c47\u603b\uff0c\u518d\u53d1\u8d77\u5bfc\u51fa\u3002", {
                type: "warning",
            });
            return;
        }
        const rows = await this.env.services.orm.read(
            "logistics.trace.evidence.summary",
            selectedIds,
            ["waybill_id", "waybill_no", "upload_role"]
        );
        const seen = new Set();
        const waybillIds = [];
        const items = [];
        for (const row of rows || []) {
            const value = row.waybill_id;
            const waybillId = Array.isArray(value) ? value[0] : value;
            if (!waybillId || seen.has(waybillId)) {
                continue;
            }
            seen.add(waybillId);
            waybillIds.push(waybillId);
            items.push({
                summary_id: row.id,
                waybill_id: waybillId,
                waybill_no: row.waybill_no || (Array.isArray(value) ? value[1] : ""),
                upload_role: row.upload_role,
            });
        }
        if (!waybillIds.length) {
            this.env.services.notification.add("\u9009\u4e2d\u7684\u7559\u75d5\u6c47\u603b\u6ca1\u6709\u5173\u8054\u8fd0\u5355\uff0c\u6682\u65f6\u65e0\u6cd5\u5bfc\u51fa\u3002", {
                type: "warning",
            });
            return;
        }
        await this.openExportResultFromRequest(
            "/api/admin/logistics/exports/evidence-images",
            {
                object_type: "evidence_image_bundle",
                entry_type: "from_waybill",
                export_mode: "zip_package",
                package_structure: "evidence_image_bundle_v1",
                source_model: "logistics.dispatch.waybill",
                selected_ids: waybillIds,
                from_page: "evidence_summary_list",
                scope_snapshot: {
                    selected_summary_ids: selectedIds,
                    selected_waybill_ids: waybillIds,
                    items,
                },
            },
            "\u7559\u75d5\u56fe\u7247\u6279\u91cf\u5bfc\u51fa\u5931\u8d25\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5\u3002"
        );
    },

    async exportCustomerProfiles() {
        const selectedIds = await this.model.root.getResIds(true);
        if (!selectedIds.length) {
            this.env.services.notification.add("请先选择至少一条客户画像，再发起导出。", {
                type: "warning",
            });
            return;
        }
        await this.openExportResultFromRequest(
            "/api/admin/logistics/exports/customer-profile",
            {
                object_type: "customer_profile",
                entry_type: "from_customer",
                export_mode: "standard_xlsx",
                selected_ids: selectedIds,
                from_page: "customer_profile_list",
                scope_snapshot: {
                    selected_partner_ids: selectedIds,
                },
            },
            "客户画像导出失败，请稍后重试。"
        );
    },

    async exportProductProfiles() {
        const selectedIds = await this.model.root.getResIds(true);
        if (!selectedIds.length) {
            this.env.services.notification.add("请先选择至少一条货物画像，再发起导出。", {
                type: "warning",
            });
            return;
        }

        let productTemplateIds = selectedIds;
        let fromPage = "product_profile_list";
        let scopeSnapshot = {
            selected_product_template_ids: selectedIds,
        };

        if (this.props.resModel === "logistics.product.unit") {
            const units = await this.env.services.orm.read("logistics.product.unit", selectedIds, ["product_tmpl_id"]);
            productTemplateIds = this.normalizeProductTemplateIds(units);
            if (!productTemplateIds.length) {
                this.env.services.notification.add("选中的商品规格没有关联商品主档，暂时无法导出。", {
                    type: "warning",
                });
                return;
            }
            fromPage = "product_unit_list";
            scopeSnapshot = {
                selected_product_unit_ids: selectedIds,
                selected_product_template_ids: productTemplateIds,
            };
        }

        await this.openExportResultFromRequest(
            "/api/admin/logistics/exports/product-profile",
            {
                object_type: "product_profile",
                entry_type: "from_product",
                export_mode: "standard_xlsx",
                selected_ids: productTemplateIds,
                from_page: fromPage,
                scope_snapshot: scopeSnapshot,
            },
            "货物画像导出失败，请稍后重试。"
        );
    },

    normalizeProductTemplateIds(rows) {
        const seen = new Set();
        const result = [];
        for (const row of rows || []) {
            const value = row.product_tmpl_id;
            const productTemplateId = Array.isArray(value) ? value[0] : value;
            if (!productTemplateId || seen.has(productTemplateId)) {
                continue;
            }
            seen.add(productTemplateId);
            result.push(productTemplateId);
        }
        return result;
    },

    async openExportResultFromRequest(url, payloadBody, fallbackMessage) {
        try {
            const payload = await this.logisticsExportRequest(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payloadBody),
            });
            const taskNo = payload.data?.task_no;
            if (!taskNo) {
                throw new Error("导出任务未返回 task_no。");
            }
            await this.actionService.doAction({
                type: "ir.actions.client",
                name: "导出结果",
                tag: "logistics_web.export_result",
                params: {
                    task_no: taskNo,
                    source_model: this.props.resModel,
                },
            });
        } catch (error) {
            this.env.services.notification.add(String(error?.message || fallbackMessage), {
                type: "danger",
            });
        }
    },

    async logisticsExportRequest(url, options = {}) {
        const response = await fetch(url, {
            method: options.method || "GET",
            headers: options.headers || {},
            body: options.body,
        });
        const payload = await response.json().catch(() => null);
        if (!response.ok || !payload || payload.code !== 0) {
            throw new Error(payload?.data?.errors?.[0]?.error_message || payload?.message || "导出请求失败。");
        }
        return payload;
    },
});
