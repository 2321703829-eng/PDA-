/** @odoo-module */

import { Component, onWillStart, useRef, useState } from "@odoo/owl";
import { Layout } from "@web/search/layout";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

const SOURCE_MODEL_CONFIG = {
    "logistics.dispatch.waybill": {
        entryTitle: "运单导入",
        focusSheetLabel: "运单",
        focusHint: "从运单入口进入时，优先填写运单 Sheet，再继续补齐客户明细和货物明细。",
    },
    "logistics.dispatch.waybill.customer.line": {
        entryTitle: "客户明细导入",
        focusSheetLabel: "客户明细",
        focusHint: "从客户明细入口进入时，请优先检查客户明细 Sheet，同时确认它引用的运单号已经出现在运单 Sheet 中。",
    },
    "logistics.dispatch.waybill.customer.goods.line": {
        entryTitle: "货物明细导入",
        focusSheetLabel: "货物明细",
        focusHint: "从货物明细入口进入时，请优先检查货物明细 Sheet，并确认对应客户关系已经出现在客户明细 Sheet 中。",
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
        });
    }

    get ui() {
        return {
            title: "导入中心",
            subtitle: "先下载标准模板，再上传 V2 三 Sheet 文件执行预校验，确认通过后再正式导入，避免把不完整数据直接写进业务库。",
            badgePrimary: "TSL-IMPORT-WAYBILL-V2",
            badgeSecondary: "整单导入闭环",
            loading: "正在加载导入中心...",
            sectionTemplateTitle: "标准模板下载",
            sectionTemplateHint: "当前统一使用一份 V2 标准模板，内部固定包含运单、客户明细、货物明细 3 个 Sheet。",
            sectionUploadTitle: "上传与预校验",
            sectionUploadHint: "上传标准模板文件后，先做跨 Sheet 预校验，再决定是否正式导入。",
            sectionPrecheckTitle: "预校验结果",
            sectionPrecheckHint: "先看通过数量和错误明细，再决定是否执行正式导入。",
            sectionResultTitle: "导入结果",
            sectionResultHint: "正式导入完成后，在这里查看批次号、创建数量和后续处理入口。",
            chooseFile: "选择导入文件",
            replaceFile: "重新选择文件",
            runPrecheck: "开始预校验",
            confirmImport: "确认正式导入",
            refreshResult: "刷新结果",
            openWaybillList: "进入运单列表",
            openErrorReport: "下载错误报告",
            noFile: "尚未选择文件，请先下载标准模板并填写后再上传。",
            noErrors: "当前没有预校验错误，可以继续正式导入。",
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
        return Boolean(this.state.precheckResult?.can_confirm_import && this.state.precheckResult?.precheck_token);
    }

    get hasImportResult() {
        return Boolean(this.state.importResult);
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
            this.state.error = error.message || "导入中心加载失败，请刷新页面后重试。";
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
            formData.append("template_code", this.state.templateMeta?.template_code || "TSL-IMPORT-WAYBILL-V2");
            formData.append("template_version", this.state.templateMeta?.template_version || "v2");
            const payload = await this.apiRequest("/api/admin/logistics/imports/waybill-standard/precheck", {
                method: "POST",
                body: formData,
            });
            this.state.precheckResult = payload.data;
            if (payload.data?.can_confirm_import) {
                this.notification.add("预校验通过，可以继续正式导入。", { type: "success" });
            } else {
                this.notification.add("预校验已完成，请先处理错误明细。", { type: "warning" });
            }
        } catch (error) {
            this.state.error = error.message || "预校验失败，请稍后重试。";
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
                    precheck_token: this.state.precheckResult.precheck_token,
                    import_batch_no: this.state.precheckResult.import_batch_no,
                }),
            });
            this.state.importResult = payload.data;
            this.notification.add("正式导入完成。", { type: "success" });
        } catch (error) {
            this.state.error = error.message || "正式导入失败，请重新执行预校验后再试。";
        } finally {
            this.state.confirming = false;
        }
    }

    async refreshResult() {
        const importBatchNo = this.state.importResult?.import_batch_no || this.state.precheckResult?.import_batch_no;
        if (!importBatchNo) {
            return;
        }
        this.state.refreshingResult = true;
        this.state.error = "";
        try {
            const payload = await this.apiRequest(
                `/api/admin/logistics/imports/waybill-standard/result?import_batch_no=${encodeURIComponent(importBatchNo)}`
            );
            this.state.importResult = payload.data;
        } catch (error) {
            this.state.error = error.message || "导入结果刷新失败，请稍后重试。";
        } finally {
            this.state.refreshingResult = false;
        }
    }

    downloadErrorReport() {
        const url = this.state.importResult?.error_report_url || this.state.precheckResult?.error_report_url;
        if (url) {
            window.open(url, "_blank", "noopener");
        }
    }

    async openWaybillList() {
        return this.actionService.doAction("logistics_dispatch.action_logistics_dispatch_waybill");
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
                payload?.data?.errors?.[0]?.error_message || payload?.message || "请求失败，请稍后重试。";
            throw new Error(errorMessage);
        }
        return payload;
    }
}
