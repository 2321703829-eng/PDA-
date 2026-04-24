/** @odoo-module */

import { Component, onWillStart, useRef, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

const SOURCE_MODEL_CONFIG = {
    "logistics.dispatch.waybill": {
        entryTitle: "\u8fd0\u5355\u5bfc\u5165",
        focusSheetLabel: "\u56db Sheet \u6b63\u5f0f\u6a21\u677f",
        focusHint: "\u4f18\u5148\u6309 Waybill / CustomerLine / OrderLine / GoodsLine \u56db\u4e2a\u5de5\u4f5c\u8868\u586b\u5199\uff0c\u8ba9\u7cfb\u7edf\u7a33\u5b9a\u65b0\u5efa\u6ce2\u6b21\u3001\u6279\u6b21\u3001\u8fd0\u5355\u4e0e\u4e0b\u6e38\u660e\u7ec6\u3002",
    },
    "logistics.dispatch.waybill.customer.line": {
        entryTitle: "\u5ba2\u6237\u660e\u7ec6\u5bfc\u5165",
        focusSheetLabel: "\u56db Sheet \u6b63\u5f0f\u6a21\u677f",
        focusHint: "\u4f18\u5148\u786e\u8ba4 CustomerLine \u5de5\u4f5c\u8868\u5185\u7684\u95e8\u5e97\u8282\u70b9\u6807\u8bc6\u3001\u5ba2\u6237\u5feb\u7167\u548c\u914d\u9001\u753b\u50cf\u5b57\u6bb5\uff0c\u907f\u514d\u540c\u4e00\u8fd0\u5355\u4e0b\u51fa\u73b0\u51b2\u7a81\u8282\u70b9\u3002",
    },
    "logistics.dispatch.waybill.customer.goods.line": {
        entryTitle: "\u8d27\u7269\u660e\u7ec6\u5bfc\u5165",
        focusSheetLabel: "\u56db Sheet \u6b63\u5f0f\u6a21\u677f",
        focusHint: "\u4f18\u5148\u68c0\u67e5 GoodsLine \u5de5\u4f5c\u8868\u5185\u7684\u8d27\u7269\u540d\u79f0\u3001\u6570\u91cf\u3001\u91d1\u989d\u3001\u91cd\u91cf\u4f53\u79ef\u4e0e order_line_no \u5f52\u5c5e\u5173\u7cfb\uff0c\u907f\u514d\u5f71\u54cd\u6574\u6761\u4e3b\u94fe\u5bfc\u5165\u3002",
    },
};

export class LogisticsImportCenterAction extends Component {
    static template = "logistics_web.ImportCenterAction";
    static components = { Layout };
    static props = { ...standardActionServiceProps };

    setup() {
        this.actionService = this.env.services.action;
        this.notification = this.env.services.notification;
        this.fileInputRef = useRef("fileInput");
        this.display = {
            controlPanel: false,
            searchPanel: false,
        };
        this.state = useState({
            loading: true,
            error: "",
            templateMeta: null,
            selectedFile: null,
            prechecking: false,
            confirming: false,
            refreshingResult: false,
            precheckResult: null,
            importResult: null,
            sourceModel: this.props.action?.params?.source_model || "logistics.dispatch.waybill",
        });

        onWillStart(async () => {
            await this.loadTemplateMeta();
            const taskNo = this.props.action?.params?.task_no || this.props.action?.params?.import_batch_no;
            if (taskNo) {
                await this.loadImportResultByTask(taskNo, { silent: true });
            }
        });
    }

    get ui() {
        return {
            title: "\u5bfc\u5165\u4e2d\u5fc3",
            subtitle: "\u5148\u4e0b\u8f7d\u56db Sheet \u6807\u51c6\u6a21\u677f\uff0c\u518d\u4e0a\u4f20\u6587\u4ef6\u6267\u884c\u9884\u6821\u9a8c\uff0c\u786e\u8ba4\u901a\u8fc7\u540e\u518d\u6b63\u5f0f\u5bfc\u5165\uff0c\u8ba9\u7cfb\u7edf\u76f4\u63a5\u65b0\u5efa\u6ce2\u6b21\u3001\u6279\u6b21\u3001\u8fd0\u5355\u3001\u95e8\u5e97\u8282\u70b9\u3001\u8ba2\u5355\u884c\u548c\u8d27\u7269\u884c\u3002",
            badgePrimary: "TSL-IMPORT-WAYBILL-V3",
            badgeSecondary: "\u56db Sheet \u6b63\u5f0f\u6a21\u677f",
            heroNoteTitle: "\u5f53\u524d\u5de5\u4f5c\u65b9\u5411",
            heroNoteBody: "\u5148\u786e\u8ba4\u5165\u53e3\u548c\u6a21\u677f\uff0c\u518d\u5b8c\u6210\u9884\u6821\u9a8c\u3001\u6b63\u5f0f\u5bfc\u5165\u4e0e\u7ed3\u679c\u56de\u770b\uff0c\u907f\u514d\u628a\u6d41\u7a0b\u62c6\u6563\u5230\u591a\u4e2a\u9875\u9762\u91cc\u3002",
            loading: "\u6b63\u5728\u52a0\u8f7d\u5bfc\u5165\u4e2d\u5fc3...",
            sectionTemplateTitle: "\u6807\u51c6\u6a21\u677f\u4e0b\u8f7d",
            sectionTemplateHint: "\u5f53\u524d\u9ed8\u8ba4\u4f7f\u7528 V3 \u56db Sheet \u6807\u51c6\u6a21\u677f\uff1b\u65e7\u5355\u8868\u4e0e\u65e7\u4e09\u5f20\u5de5\u4f5c\u8868\u53e3\u5f84\u4ec5\u4fdd\u7559\u517c\u5bb9\uff0c\u4e0d\u518d\u662f\u9ed8\u8ba4\u5165\u53e3\u3002",
            sectionUploadTitle: "\u4e0a\u4f20\u4e0e\u9884\u6821\u9a8c",
            sectionUploadHint: "\u4e0a\u4f20\u56db Sheet \u6807\u51c6\u6a21\u677f\u540e\uff0c\u5148\u505a\u53ef\u5efa\u6863\u9884\u6821\u9a8c\uff0c\u518d\u51b3\u5b9a\u662f\u5426\u6b63\u5f0f\u5bfc\u5165\u3002",
            sectionPrecheckTitle: "\u9884\u6821\u9a8c\u7ed3\u679c",
            sectionPrecheckHint: "\u5148\u770b\u901a\u8fc7\u6570\u91cf\u548c\u9519\u8bef\u660e\u7ec6\uff0c\u518d\u51b3\u5b9a\u662f\u5426\u6267\u884c\u6b63\u5f0f\u5bfc\u5165\u3002",
            sectionResultTitle: "\u5bfc\u5165\u7ed3\u679c",
            sectionResultHint: "\u6b63\u5f0f\u5bfc\u5165\u5b8c\u6210\u540e\uff0c\u5728\u8fd9\u91cc\u67e5\u770b\u6279\u6b21\u53f7\u3001\u521b\u5efa\u6570\u91cf\u548c\u540e\u7eed\u5904\u7406\u5165\u53e3\u3002",
            chooseFile: "\u9009\u62e9\u5bfc\u5165\u6587\u4ef6",
            replaceFile: "\u91cd\u65b0\u9009\u62e9\u6587\u4ef6",
            runPrecheck: "\u5f00\u59cb\u9884\u6821\u9a8c",
            confirmImport: "\u786e\u8ba4\u6b63\u5f0f\u5bfc\u5165",
            refreshResult: "\u5237\u65b0\u7ed3\u679c",
            openWaybillList: "\u8fdb\u5165\u8fd0\u5355\u5217\u8868",
            openErrorReport: "\u4e0b\u8f7d\u9519\u8bef\u62a5\u544a",
            openResultPage: "\u67e5\u770b\u7ed3\u679c\u9875",
            noFile: "\u5c1a\u672a\u9009\u62e9\u6587\u4ef6\uff0c\u8bf7\u5148\u4e0b\u8f7d\u6807\u51c6\u6a21\u677f\u5e76\u586b\u5199\u540e\u518d\u4e0a\u4f20\u3002",
            noErrors: "\u5f53\u524d\u6ca1\u6709\u9884\u6821\u9a8c\u9519\u8bef\uff0c\u53ef\u4ee5\u7ee7\u7eed\u6b63\u5f0f\u5bfc\u5165\u3002",
            loadFailed: "\u5bfc\u5165\u4e2d\u5fc3\u52a0\u8f7d\u5931\u8d25\uff0c\u8bf7\u5237\u65b0\u9875\u9762\u540e\u91cd\u8bd5\u3002",
            noPermission: "\u5f53\u524d\u8d26\u53f7\u6682\u65e0\u67e5\u770b\u5bfc\u5165\u4e2d\u5fc3\u7684\u6743\u9650\u3002",
            precheckFailed: "\u9884\u6821\u9a8c\u5931\u8d25\uff0c\u8bf7\u5237\u65b0\u9875\u9762\u6216\u7a0d\u540e\u518d\u8bd5\u3002",
            confirmFailed: "\u6b63\u5f0f\u5bfc\u5165\u5931\u8d25\uff0c\u8bf7\u91cd\u65b0\u6267\u884c\u9884\u6821\u9a8c\u540e\u518d\u8bd5\u3002",
            refreshResultFailed: "\u5bfc\u5165\u7ed3\u679c\u5237\u65b0\u5931\u8d25\uff0c\u8bf7\u5237\u65b0\u9875\u9762\u6216\u7a0d\u540e\u518d\u8bd5\u3002",
            entryCurrentLabel: "\u5f53\u524d\u5165\u53e3",
            entryRecommendLabel: "\u5efa\u8bae\u4f18\u5148\u586b\u5199",
            fileNameLabel: "\u6587\u4ef6\u540d",
            downloadTemplate: "\u4e0b\u8f7d\u6a21\u677f",
            currentFileLabel: "\u5f53\u524d\u6587\u4ef6",
            precheckingText: "\u9884\u6821\u9a8c\u4e2d...",
            importBatchNoLabel: "\u5bfc\u5165\u4efb\u52a1\u53f7",
            totalRowsLabel: "\u603b\u884c\u6570",
            failedRowsLabel: "\u5931\u8d25\u884c\u6570",
            canImportLabel: "\u53ef\u6b63\u5f0f\u5bfc\u5165",
            yesLabel: "\u662f",
            noLabel: "\u5426",
            importingText: "\u5bfc\u5165\u4e2d...",
            errorDetailsTitle: "\u9519\u8bef\u660e\u7ec6",
            errorDetailsHint: "\u5f53\u524d\u6700\u591a\u5c55\u793a\u524d 20 \u6761\u9519\u8bef\uff0c\u5b8c\u6574\u5185\u5bb9\u8bf7\u4e0b\u8f7d\u9519\u8bef\u62a5\u544a\u3002",
            rowNumberLabel: "\u884c\u53f7",
            fieldLabel: "\u5b57\u6bb5",
            errorCodeLabel: "\u9519\u8bef\u7f16\u7801",
            errorMessageLabel: "\u9519\u8bef\u8bf4\u660e",
            precheckEmptyHint: "\u5b8c\u6210\u6587\u4ef6\u4e0a\u4f20\u540e\uff0c\u9884\u6821\u9a8c\u7ed3\u679c\u4f1a\u663e\u793a\u5728\u8fd9\u91cc\u3002",
            statusLabel: "\u72b6\u6001",
            createdWaybillLabel: "\u65b0\u589e\u8fd0\u5355",
            createdCustomerLabel: "\u65b0\u589e\u5ba2\u6237\u660e\u7ec6",
            createdGoodsLabel: "\u65b0\u589e\u8d27\u7269\u660e\u7ec6",
            refreshingText: "\u5237\u65b0\u4e2d...",
            resultEmptyHint: "\u5b8c\u6210\u6b63\u5f0f\u5bfc\u5165\u540e\uff0c\u7ed3\u679c\u6458\u8981\u4f1a\u663e\u793a\u5728\u8fd9\u91cc\u3002",
        };
    }

    get sourceConfig() {
        return SOURCE_MODEL_CONFIG[this.state.sourceModel] || SOURCE_MODEL_CONFIG["logistics.dispatch.waybill"];
    }

    get hasSelectedFile() {
        return Boolean(this.state.selectedFile);
    }

    get hasPrecheckResult() {
        return Boolean(this.state.precheckResult);
    }

    get canConfirmImport() {
        return Boolean(this.state.precheckResult?.can_confirm_import && (this.state.precheckResult?.task_no || this.state.precheckResult?.import_batch_no));
    }

    get hasImportResult() {
        return Boolean(this.state.importResult);
    }

    get currentTaskNo() {
        return (
            this.state.importResult?.task_no ||
            this.state.precheckResult?.task_no ||
            this.state.importResult?.import_batch_no ||
            this.state.precheckResult?.import_batch_no ||
            ""
        );
    }

    get availableTemplates() {
        return this.state.templateMeta?.available_templates || [];
    }

    get visibleErrors() {
        return (this.state.precheckResult?.errors || []).slice(0, 20);
    }

    get fileLabel() {
        return this.state.selectedFile?.name || this.ui.noFile;
    }

    async loadTemplateMeta() {
        this.state.loading = true;
        this.state.error = "";
        try {
            const payload = await this.apiRequest("/api/admin/logistics/imports/waybill-standard/template");
            this.state.templateMeta = payload.data;
        } catch (error) {
            this.state.error = this.mapLoadError(error, this.ui.loadFailed);
        } finally {
            this.state.loading = false;
        }
    }

    triggerFileSelect() {
        if (this.fileInputRef.el) {
            this.fileInputRef.el.value = "";
        }
        this.fileInputRef.el?.click();
    }

    onFileChanged(ev) {
        const file = ev.target.files?.[0];
        this.state.selectedFile = file || null;
        this.state.precheckResult = null;
        this.state.importResult = null;
        this.state.error = "";
    }

    async runPrecheck() {
        if (!this.state.selectedFile) {
            this.state.error = this.ui.noFile;
            return;
        }
        this.state.prechecking = true;
        this.state.error = "";
        this.state.precheckResult = null;
        this.state.importResult = null;
        try {
            const formData = new FormData();
            formData.append("file", this.state.selectedFile);
            formData.append("template_code", this.state.templateMeta?.template_code || "TSL-IMPORT-WAYBILL-V3");
            formData.append("template_version", this.state.templateMeta?.template_version || "v3");
            const payload = await this.apiRequest("/api/admin/logistics/imports/waybill-standard/precheck", {
                method: "POST",
                body: formData,
            });
            this.state.precheckResult = payload.data;
            if (payload.data?.can_confirm_import) {
                this.notification.add("\u9884\u6821\u9a8c\u901a\u8fc7\uff0c\u53ef\u4ee5\u7ee7\u7eed\u6b63\u5f0f\u5bfc\u5165\u3002", { type: "success" });
            } else {
                this.notification.add("\u9884\u6821\u9a8c\u5df2\u5b8c\u6210\uff0c\u8bf7\u5148\u5904\u7406\u9519\u8bef\u660e\u7ec6\u3002", { type: "warning" });
            }
        } catch (error) {
            this.state.error = this.mapLoadError(error, this.ui.precheckFailed);
        } finally {
            this.state.prechecking = false;
        }
    }

    async confirmImport() {
        if (!this.canConfirmImport) {
            return;
        }
        this.state.confirming = true;
        this.state.error = "";
        try {
            const payload = await this.apiRequest("/api/admin/logistics/imports/waybill-standard/confirm", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    task_no: this.state.precheckResult.task_no || this.state.precheckResult.import_batch_no,
                    import_batch_no: this.state.precheckResult.import_batch_no,
                }),
            });
            this.state.importResult = payload.data;
            await this.openImportResultPage(payload.data?.task_no || payload.data?.import_batch_no);
            this.notification.add("\u6b63\u5f0f\u5bfc\u5165\u5b8c\u6210\u3002", { type: "success" });
        } catch (error) {
            this.state.error = this.mapLoadError(error, this.ui.confirmFailed);
        } finally {
            this.state.confirming = false;
        }
    }

    async refreshResult() {
        const taskNo = this.currentTaskNo;
        if (!taskNo) {
            return;
        }
        await this.loadImportResultByTask(taskNo);
    }

    downloadErrorReport() {
        const url =
            this.state.importResult?.error_report?.download_url ||
            this.state.importResult?.error_report_url ||
            this.state.precheckResult?.error_report?.download_url ||
            this.state.precheckResult?.error_report_url;
        if (url) {
            window.open(url, "_blank", "noopener");
        }
    }

    async openWaybillList() {
        return this.actionService.doAction("logistics_dispatch.action_logistics_dispatch_waybill");
    }

    async openImportResultPage(taskNo = this.currentTaskNo) {
        if (!taskNo) {
            return;
        }
        return this.actionService.doAction({
            type: "ir.actions.client",
            name: "\u5bfc\u5165\u7ed3\u679c",
            tag: "logistics_web.import_result",
            params: {
                task_no: taskNo,
                import_batch_no: taskNo,
                source_model: this.state.sourceModel,
            },
        });
    }

    async loadImportResultByTask(taskNo, { silent = false } = {}) {
        if (!taskNo) {
            return;
        }
        this.state.refreshingResult = !silent;
        this.state.error = "";
        try {
            const payload = await this.apiRequest(
                `/api/admin/logistics/imports/tasks/${encodeURIComponent(taskNo)}`
            );
            this.state.importResult = payload.data;
        } catch (error) {
            this.state.error = this.mapLoadError(error, this.ui.refreshResultFailed);
        } finally {
            this.state.refreshingResult = false;
        }
    }

    mapLoadError(error, fallbackMessage) {
        const message = String(error?.message || "").trim();
        const lower = message.toLowerCase();
        if (message.includes("\u6743\u9650") || lower.includes("forbidden") || lower.includes("permission")) {
            return this.ui.noPermission;
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
                payload?.data?.errors?.[0]?.error_message ||
                payload?.message ||
                (response.status === 403
                    ? this.ui.noPermission
                    : "\u8bf7\u6c42\u5931\u8d25\uff0c\u8bf7\u5237\u65b0\u9875\u9762\u6216\u7a0d\u540e\u518d\u8bd5\u3002");
            throw new Error(errorMessage);
        }
        return payload;
    }
}

const actionsRegistry = registry.category("actions");
if (!actionsRegistry.contains("logistics_web.import_center")) {
    actionsRegistry.add("logistics_web.import_center", LogisticsImportCenterAction);
}
