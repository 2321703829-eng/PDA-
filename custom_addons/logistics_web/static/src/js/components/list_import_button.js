/** @odoo-module */

import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";

const LOGISTICS_IMPORT_MODELS = new Set([
    "logistics.dispatch.wave",
    "logistics.dispatch.batch",
    "logistics.dispatch.waybill",
    "logistics.trace.event",
    "logistics.trace.evidence",
    "logistics.trace.exception",
]);

patch(ListController.prototype, {
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

    get showLogisticsExportButton() {
        return (
            !this.env.inDialog &&
            this.props.showButtons &&
            (
                this.props.resModel === "logistics.dispatch.waybill" ||
                this.props.resModel === "logistics.trace.evidence" ||
                this.isCustomerProfileExportList ||
                this.isProductProfileExportList
            )
        );
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
