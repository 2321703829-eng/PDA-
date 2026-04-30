/** @odoo-module */

import { Component, onWillStart, useRef, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

const SOURCE_MODEL_CONFIG = {
    phase5_workbook: {
        entryTitle: "五期五表导入",
        focusSheetLabel: "五张业务样例表",
        focusHint: "优先按商品资料、客户资料、排线门店详情、排线订单详情、门店货物三联单五张表分别导入，先保快照可查、可展示、可导出。",
    },
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

const EXPORT_SHORTCUTS = [
    {
        key: "waybill",
        title: "\u8fd0\u5355\u6807\u51c6\u5bfc\u51fa",
        lead: "\u5148\u53bb\u8fd0\u5355\u5217\u8868\u52fe\u9009\u8fd0\u5355\uff0c\u518d\u53d1\u8d77\u5bfc\u51fa\u3002",
        detail: "\u9002\u5408\u7ed3\u6784\u5316\u56de\u770b\u3001\u4fee\u8ba2\u540e\u518d\u5bfc\u5165\uff0c\u7ee7\u7eed\u6cbf\u7528\u73b0\u6709\u8fd0\u5355\u5217\u8868\u52fe\u9009\u94fe\u8def\u3002",
        buttonLabel: "\u8fdb\u5165\u8fd0\u5355\u5217\u8868\u5bfc\u51fa",
        actionXmlid: "logistics_dispatch.action_logistics_dispatch_waybill",
    },
    {
        key: "customer_profile",
        title: "\u5ba2\u6237\u753b\u50cf\u6807\u51c6\u5bfc\u51fa",
        lead: "\u5148\u53bb\u5ba2\u6237\u753b\u50cf\u5217\u8868\u52fe\u9009\u9700\u8981\u6838\u5bf9\u7684\u5ba2\u6237\uff0c\u518d\u53d1\u8d77\u5bfc\u51fa\u3002",
        detail: "\u9002\u5408\u5728\u5bfc\u5165\u5ba2\u6237\u660e\u7ec6\u524d\uff0c\u5148\u5bf9\u5ba2\u6237\u4e3b\u6863\u3001\u7b7e\u6536\u8981\u6c42\u548c\u914d\u9001\u753b\u50cf\u505a\u7ed3\u6784\u5316\u56de\u770b\u3002",
        buttonLabel: "\u8fdb\u5165\u5ba2\u6237\u753b\u50cf\u5217\u8868\u5bfc\u51fa",
        actionXmlid: "logistics_base.action_logistics_partner_profile",
    },
    {
        key: "product_profile",
        title: "\u8d27\u7269\u753b\u50cf\u6807\u51c6\u5bfc\u51fa",
        lead: "\u5148\u53bb\u5546\u54c1\u89c4\u683c\u5217\u8868\u52fe\u9009\u9700\u8981\u6838\u5bf9\u7684\u89c4\u683c\uff0c\u518d\u53d1\u8d77\u5bfc\u51fa\u3002",
        detail: "\u9002\u5408\u5728\u5bfc\u5165\u8d27\u7269\u660e\u7ec6\u524d\uff0c\u5148\u5bf9\u5546\u54c1\u4e3b\u6863\u3001SKU\u3001\u6761\u7801\u548c\u89c4\u683c\u5173\u7cfb\u505a\u7ed3\u6784\u5316\u56de\u770b\u3002",
        buttonLabel: "\u8fdb\u5165\u5546\u54c1\u89c4\u683c\u5217\u8868\u5bfc\u51fa",
        actionXmlid: "logistics_base.action_logistics_product_unit",
    },
];

const PHASE5_EXPORT_SHORTCUTS = [
    {
        key: "order_detail",
        title: "导出0429订单详情",
        detail: "按当前配送日期导出订单详情表，若当前入口带了批次号，则自动缩小到该批次。",
        buttonLabel: "下载订单详情",
    },
    {
        key: "store_detail",
        title: "导出0429门店详情",
        detail: "按当前配送日期导出门店详情表，门店备注按运单备注口径输出。",
        buttonLabel: "下载门店详情",
    },
    {
        key: "store_goods_triplet",
        title: "导出0429门店货物信息三联单",
        detail: "按当前配送日期导出货物三联单，未落库的新字段本版先按空值输出。",
        buttonLabel: "下载货物三联单",
    },
];

export class LogisticsImportCenterAction extends Component {
    static template = "logistics_web.ImportCenterAction";
    static components = { Layout };
    static props = { ...standardActionServiceProps };

    setup() {
        this.actionService = this.env.services.action;
        this.notification = this.env.services.notification;
        this.fileInputRef = useRef("fileInput");
        this.routePlanningFileInputRef = useRef("routePlanningFileInput");
        this.phase5FileInputRef = useRef("phase5FileInput");
        this.display = {
            controlPanel: false,
            searchPanel: false,
        };
        this.state = useState({
            loading: true,
            error: "",
            templateMeta: null,
            routePlanningTemplateMeta: null,
            phase5TemplateMeta: null,
            selectedFile: null,
            routePlanningSelectedFile: null,
            phase5SelectedFile: null,
            prechecking: false,
            routePlanningPrechecking: false,
            phase5Prechecking: false,
            confirming: false,
            routePlanningConfirming: false,
            phase5Confirming: false,
            refreshingResult: false,
            precheckResult: null,
            routePlanningPrecheckResult: null,
            phase5PrecheckResult: null,
            importResult: null,
            routePlanningImportResult: null,
            phase5ImportResult: null,
            sourceModel: this.props.action?.params?.source_model || "logistics.dispatch.waybill",
            driverExportDate: this.props.action?.params?.driver_export_delivery_date || "",
            driverExportBatchNo: this.props.action?.params?.driver_export_batch_no || "",
            driverExportHint: this.props.action?.params?.driver_export_hint || "",
            driverExportDownloading: false,
            phase5ExportDownloadingKey: "",
        });

        onWillStart(async () => {
            await Promise.all([
                this.loadTemplateMeta(),
                this.loadRoutePlanningTemplateMeta(),
                this.loadPhase5TemplateMeta(),
            ]);
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
            sectionPhase5TemplateTitle: "五期导入模板下载",
            sectionPhase5TemplateHint: "下载五期五张业务样例表模板，按单表口径逐张整理后再上传，适合当前五期导入与0429导出配套场景。",
            sectionPhase5UploadTitle: "五期五表导入",
            sectionPhase5UploadHint: "先上传五期模板中的任意一张工作表执行预校验，通过后再正式写入；当前版本按单文件单表处理，不要求一次上传五张。",
            phase5ChooseFile: "选择五期文件",
            phase5ReplaceFile: "重新选择五期文件",
            phase5RunPrecheck: "开始五期预校验",
            phase5ConfirmImport: "确认写入五期数据",
            phase5PrecheckingText: "预校验中...",
            phase5ImportingText: "导入中...",
            phase5PrecheckEmptyHint: "完成五期文件上传后，预校验结果会显示在这里。",
            phase5ResultEmptyHint: "确认写入后，五期导入结果会显示在这里。",
            phase5PrecheckFailed: "五期预校验失败，请刷新页面或稍后再试。",
            phase5ConfirmFailed: "五期正式导入失败，请先处理错误后重试。",
            sectionPhase5PrecheckTitle: "五期预校验结果",
            sectionPhase5PrecheckHint: "当前展示前 20 条错误；如无错误即可继续正式导入。",
            sectionPhase5ResultTitle: "五期导入结果",
            sectionPhase5ResultHint: "正式写入后，这里汇总本次导入的成功、失败和跳过情况。",
            phase5SuccessCountLabel: "成功行数",
            phase5SkippedCountLabel: "跳过行数",
            phase5ImportSuccess: "五期导入已完成。",
            sectionRoutePlanningTemplateTitle: "\u6392\u7ebf\u6a21\u677f\u4e0b\u8f7d",
            sectionRoutePlanningTemplateHint: "\u72ec\u7acb\u4e8e\u6b63\u5f0f\u56db Sheet \u4e3b\u94fe\u7684\u5355\u8868\u6392\u7ebf\u6a21\u677f\uff0c\u53ea\u56f4\u7ed5\u6279\u6b21\u3001\u8fd0\u5355\u3001\u505c\u9760\u70b9\u987a\u5e8f\u3001\u95e8\u5e97\u8054\u7cfb\u4fe1\u606f\u548c\u5730\u7406\u5750\u6807\u3002",
            sectionRoutePlanningUploadTitle: "\u6392\u7ebf\u7528\u6570\u636e\u5bfc\u5165",
            sectionRoutePlanningUploadHint: "\u4e0a\u4f20\u5355\u8868\u6392\u7ebf\u6587\u4ef6\u540e\uff0c\u5148\u505a\u6700\u5c0f\u6821\u9a8c\u548c\u4eba\u5de5\u590d\u67e5\u63d0\u9192\uff0c\u518d\u786e\u8ba4\u5199\u5165\u6392\u7ebf\u8349\u7a3f\u3002",
            routePlanningChooseFile: "\u9009\u62e9\u6392\u7ebf\u6587\u4ef6",
            routePlanningReplaceFile: "\u91cd\u65b0\u9009\u62e9\u6392\u7ebf\u6587\u4ef6",
            routePlanningRunPrecheck: "\u5f00\u59cb\u6392\u7ebf\u9884\u6821\u9a8c",
            routePlanningConfirmImport: "\u786e\u8ba4\u5199\u5165\u6392\u7ebf\u8349\u7a3f",
            routePlanningPrecheckingText: "\u9884\u6821\u9a8c\u4e2d...",
            routePlanningImportingText: "\u5199\u5165\u4e2d...",
            routePlanningPrecheckEmptyHint: "\u5b8c\u6210\u6392\u7ebf\u6587\u4ef6\u4e0a\u4f20\u540e\uff0c\u9884\u6821\u9a8c\u7ed3\u679c\u4f1a\u663e\u793a\u5728\u8fd9\u91cc\u3002",
            routePlanningResultEmptyHint: "\u786e\u8ba4\u5199\u5165\u540e\uff0c\u6392\u7ebf\u5bfc\u5165\u7ed3\u679c\u4f1a\u663e\u793a\u5728\u8fd9\u91cc\u3002",
            routePlanningFailed: "\u6392\u7ebf\u9884\u6821\u9a8c\u5931\u8d25\uff0c\u8bf7\u7a0d\u540e\u518d\u8bd5\u3002",
            routePlanningConfirmFailed: "\u6392\u7ebf\u5bfc\u5165\u5931\u8d25\uff0c\u8bf7\u5148\u5904\u7406\u9519\u8bef\u540e\u91cd\u8bd5\u3002",
            routePlanningWarningsTitle: "\u4eba\u5de5\u590d\u67e5\u63d0\u9192",
            routePlanningWarningsHint: "\u4e0d\u963b\u65ad\u5bfc\u5165\uff0c\u4f46\u5efa\u8bae\u5728\u518d\u6b21\u786e\u8ba4\u524d\u5148\u505a\u4eba\u5de5\u590d\u67e5\u3002",
            warningCodeLabel: "\u63d0\u9192\u7f16\u7801",
            warningMessageLabel: "\u63d0\u9192\u8bf4\u660e",
            routePlanningStopCountLabel: "\u5199\u5165\u505c\u9760\u70b9",
            routePlanningBatchCountLabel: "\u5199\u5165\u6392\u7ebf\u6279\u6b21",
            routePlanningReviewLabel: "\u9700\u4eba\u5de5\u590d\u67e5",
            loading: "\u6b63\u5728\u52a0\u8f7d\u5bfc\u5165\u4e2d\u5fc3...",
            sectionTemplateTitle: "\u6807\u51c6\u6a21\u677f\u4e0b\u8f7d",
            sectionTemplateHint: "\u5f53\u524d\u9ed8\u8ba4\u4f7f\u7528 V3 \u56db Sheet \u6807\u51c6\u6a21\u677f\uff1b\u65e7\u5355\u8868\u4e0e\u65e7\u4e09\u5f20\u5de5\u4f5c\u8868\u53e3\u5f84\u4ec5\u4fdd\u7559\u517c\u5bb9\uff0c\u4e0d\u518d\u662f\u9ed8\u8ba4\u5165\u53e3\u3002",
            sectionUploadTitle: "\u4e0a\u4f20\u4e0e\u9884\u6821\u9a8c",
            sectionUploadHint: "\u4e0a\u4f20\u56db Sheet \u6807\u51c6\u6a21\u677f\u540e\uff0c\u5148\u505a\u53ef\u5efa\u6863\u9884\u6821\u9a8c\uff0c\u518d\u51b3\u5b9a\u662f\u5426\u6b63\u5f0f\u5bfc\u5165\u3002",
            sectionDriverExportTitle: "\u53f8\u673a\u4fa7\u8def\u7ebf\u5bfc\u51fa",
            sectionDriverExportHint: "\u6309\u914d\u9001\u65e5\u671f\u4e00\u6b21\u6027\u5bfc\u51fa\u5f53\u5929\u6240\u6709\u8def\u7ebf\uff0c\u751f\u6210\u5355\u8868 `\u53f8\u673a\u8def\u7ebf\u6e05\u5355`\uff0c\u4f9b\u8c03\u5ea6\u548c\u53f8\u673a\u4eba\u5de5\u590d\u6838\u540e\u4f7f\u7528\u3002",
            driverExportDateLabel: "\u914d\u9001\u65e5\u671f",
            driverExportDateHint: "\u8bf7\u9009\u62e9\u9700\u8981\u5bfc\u51fa\u7684\u5f53\u5929\u8def\u7ebf\u65e5\u671f\u3002",
            driverExportButton: "\u5bfc\u51fa\u5f53\u5929\u8def\u7ebf",
            driverExportDownloading: "\u5bfc\u51fa\u4e2d...",
            driverExportFailed: "\u53f8\u673a\u8def\u7ebf\u5bfc\u51fa\u5931\u8d25\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5\u3002",
            driverExportDateRequired: "\u8bf7\u5148\u9009\u62e9\u914d\u9001\u65e5\u671f\uff0c\u518d\u5bfc\u51fa\u5f53\u5929\u8def\u7ebf\u3002",
            driverExportSuccess: "\u53f8\u673a\u8def\u7ebf\u6e05\u5355\u5df2\u5f00\u59cb\u4e0b\u8f7d\u3002",
            driverExportBatchContextLabel: "\u5f53\u524d\u6765\u81ea\u6279\u6b21",
            phase5ExportFailed: "0429\u8868\u683c\u5bfc\u51fa\u5931\u8d25\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5\u3002",
            phase5ExportSuccess: "0429\u8868\u683c\u5df2\u5f00\u59cb\u4e0b\u8f7d\u3002",
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

    get exportShortcuts() {
        return EXPORT_SHORTCUTS;
    }

    get phase5ExportShortcuts() {
        return PHASE5_EXPORT_SHORTCUTS;
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

    get routePlanningTemplates() {
        return this.state.routePlanningTemplateMeta?.available_templates || [];
    }

    get phase5Templates() {
        return this.state.phase5TemplateMeta?.available_templates || [];
    }

    get visibleErrors() {
        return (this.state.precheckResult?.errors || []).slice(0, 20);
    }

    get routePlanningVisibleErrors() {
        return (this.state.routePlanningPrecheckResult?.errors || []).slice(0, 20);
    }

    get routePlanningVisibleWarnings() {
        return (this.state.routePlanningPrecheckResult?.warnings || []).slice(0, 20);
    }

    get phase5VisibleErrors() {
        return (this.state.phase5PrecheckResult?.errors || []).slice(0, 20);
    }

    get fileLabel() {
        return this.state.selectedFile?.name || this.ui.noFile;
    }

    get routePlanningFileLabel() {
        return this.state.routePlanningSelectedFile?.name || this.ui.noFile;
    }

    get hasRoutePlanningSelectedFile() {
        return Boolean(this.state.routePlanningSelectedFile);
    }

    get phase5FileLabel() {
        return this.state.phase5SelectedFile?.name || this.ui.noFile;
    }

    get hasPhase5SelectedFile() {
        return Boolean(this.state.phase5SelectedFile);
    }

    get hasRoutePlanningPrecheckResult() {
        return Boolean(this.state.routePlanningPrecheckResult);
    }

    get hasPhase5PrecheckResult() {
        return Boolean(this.state.phase5PrecheckResult);
    }

    get canConfirmRoutePlanningImport() {
        return Boolean(
            this.state.routePlanningPrecheckResult?.can_confirm_import &&
                (this.state.routePlanningPrecheckResult?.task_no || this.state.routePlanningPrecheckResult?.import_batch_no)
        );
    }

    get canConfirmPhase5Import() {
        return Boolean(
            this.state.phase5PrecheckResult?.can_confirm_import &&
                (this.state.phase5PrecheckResult?.task_no || this.state.phase5PrecheckResult?.import_batch_no)
        );
    }

    get hasRoutePlanningImportResult() {
        return Boolean(this.state.routePlanningImportResult);
    }

    get hasPhase5ImportResult() {
        return Boolean(this.state.phase5ImportResult);
    }

    get hasDriverExportContext() {
        return Boolean(this.state.driverExportBatchNo || this.state.driverExportHint);
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

    async loadRoutePlanningTemplateMeta() {
        this.state.error = "";
        try {
            const payload = await this.apiRequest("/api/admin/logistics/imports/route-planning/template");
            this.state.routePlanningTemplateMeta = payload.data;
        } catch (error) {
            this.state.error = this.mapLoadError(error, this.ui.loadFailed);
        }
    }

    async loadPhase5TemplateMeta() {
        this.state.error = "";
        try {
            const payload = await this.apiRequest("/api/admin/logistics/imports/phase5-workbook/template");
            this.state.phase5TemplateMeta = payload.data;
        } catch (error) {
            this.state.error = this.mapLoadError(error, this.ui.loadFailed);
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

    triggerRoutePlanningFileSelect() {
        if (this.routePlanningFileInputRef.el) {
            this.routePlanningFileInputRef.el.value = "";
        }
        this.routePlanningFileInputRef.el?.click();
    }

    onRoutePlanningFileChanged(ev) {
        const file = ev.target.files?.[0];
        this.state.routePlanningSelectedFile = file || null;
        this.state.routePlanningPrecheckResult = null;
        this.state.routePlanningImportResult = null;
        this.state.error = "";
    }

    triggerPhase5FileSelect() {
        if (this.phase5FileInputRef.el) {
            this.phase5FileInputRef.el.value = "";
        }
        this.phase5FileInputRef.el?.click();
    }

    onPhase5FileChanged(ev) {
        const file = ev.target.files?.[0];
        this.state.phase5SelectedFile = file || null;
        this.state.phase5PrecheckResult = null;
        this.state.phase5ImportResult = null;
        this.state.error = "";
    }

    onDriverExportDateChanged(ev) {
        this.state.driverExportDate = ev.target.value || "";
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

    async runRoutePlanningPrecheck() {
        if (!this.state.routePlanningSelectedFile) {
            this.state.error = this.ui.noFile;
            return;
        }
        this.state.routePlanningPrechecking = true;
        this.state.error = "";
        this.state.routePlanningPrecheckResult = null;
        this.state.routePlanningImportResult = null;
        try {
            const formData = new FormData();
            formData.append("file", this.state.routePlanningSelectedFile);
            formData.append(
                "template_code",
                this.state.routePlanningTemplateMeta?.template_code || "TSL-IMPORT-ROUTE-PLANNING-V1"
            );
            formData.append("template_version", this.state.routePlanningTemplateMeta?.template_version || "v1");
            const payload = await this.apiRequest("/api/admin/logistics/imports/route-planning/precheck", {
                method: "POST",
                body: formData,
            });
            this.state.routePlanningPrecheckResult = payload.data;
            if (payload.data?.can_confirm_import) {
                this.notification.add(
                    payload.data?.has_review_warning
                        ? "\u6392\u7ebf\u9884\u6821\u9a8c\u901a\u8fc7\uff0c\u4f46\u5b58\u5728\u9700\u4eba\u5de5\u590d\u67e5\u7684\u63d0\u9192\u3002"
                        : "\u6392\u7ebf\u9884\u6821\u9a8c\u901a\u8fc7\uff0c\u53ef\u4ee5\u7ee7\u7eed\u5199\u5165\u6392\u7ebf\u8349\u7a3f\u3002",
                    { type: payload.data?.has_review_warning ? "warning" : "success" }
                );
            } else {
                this.notification.add("\u6392\u7ebf\u9884\u6821\u9a8c\u5df2\u5b8c\u6210\uff0c\u8bf7\u5148\u5904\u7406\u9519\u8bef\u518d\u7ee7\u7eed\u3002", {
                    type: "warning",
                });
            }
        } catch (error) {
            this.state.error = this.mapLoadError(error, this.ui.routePlanningFailed);
        } finally {
            this.state.routePlanningPrechecking = false;
        }
    }

    async runPhase5Precheck() {
        if (!this.state.phase5SelectedFile) {
            this.state.error = this.ui.noFile;
            return;
        }
        this.state.phase5Prechecking = true;
        this.state.error = "";
        this.state.phase5PrecheckResult = null;
        this.state.phase5ImportResult = null;
        try {
            const formData = new FormData();
            formData.append("file", this.state.phase5SelectedFile);
            formData.append(
                "template_code",
                this.state.phase5TemplateMeta?.template_code || "TSL-IMPORT-PHASE5-WORKBOOK-V1"
            );
            formData.append("template_version", this.state.phase5TemplateMeta?.template_version || "v1");
            const payload = await this.apiRequest("/api/admin/logistics/imports/phase5-workbook/precheck", {
                method: "POST",
                body: formData,
            });
            this.state.phase5PrecheckResult = payload.data;
            if (payload.data?.can_confirm_import) {
                this.notification.add("五期预校验通过，可以继续正式导入。", { type: "success" });
            } else {
                this.notification.add("五期预校验已完成，请先处理错误明细。", { type: "warning" });
            }
        } catch (error) {
            this.state.error = this.mapLoadError(error, this.ui.phase5PrecheckFailed);
        } finally {
            this.state.phase5Prechecking = false;
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

    async confirmRoutePlanningImport() {
        if (!this.canConfirmRoutePlanningImport) {
            return;
        }
        this.state.routePlanningConfirming = true;
        this.state.error = "";
        try {
            const payload = await this.apiRequest("/api/admin/logistics/imports/route-planning/confirm", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    task_no:
                        this.state.routePlanningPrecheckResult.task_no ||
                        this.state.routePlanningPrecheckResult.import_batch_no,
                    import_batch_no: this.state.routePlanningPrecheckResult.import_batch_no,
                }),
            });
            this.state.routePlanningImportResult = payload.data;
            this.notification.add("\u6392\u7ebf\u8349\u7a3f\u5199\u5165\u5b8c\u6210\u3002", { type: "success" });
        } catch (error) {
            this.state.error = this.mapLoadError(error, this.ui.routePlanningConfirmFailed);
        } finally {
            this.state.routePlanningConfirming = false;
        }
    }

    async confirmPhase5Import() {
        if (!this.canConfirmPhase5Import) {
            return;
        }
        this.state.phase5Confirming = true;
        this.state.error = "";
        try {
            const payload = await this.apiRequest("/api/admin/logistics/imports/phase5-workbook/confirm", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    task_no: this.state.phase5PrecheckResult.task_no || this.state.phase5PrecheckResult.import_batch_no,
                    import_batch_no: this.state.phase5PrecheckResult.import_batch_no,
                }),
            });
            this.state.phase5ImportResult = payload.data;
            this.notification.add(this.ui.phase5ImportSuccess, { type: "success" });
        } catch (error) {
            this.state.error = this.mapLoadError(error, this.ui.phase5ConfirmFailed);
        } finally {
            this.state.phase5Confirming = false;
        }
    }

    async refreshResult() {
        const taskNo = this.currentTaskNo;
        if (!taskNo) {
            return;
        }
        await this.loadImportResultByTask(taskNo);
    }

    async downloadDriverRouteExcel() {
        if (!this.state.driverExportDate) {
            this.state.error = this.ui.driverExportDateRequired;
            return;
        }
        this.state.driverExportDownloading = true;
        this.state.error = "";
        try {
            const { blob, fileName } = await this.binaryRequest("/api/admin/logistics/exports/driver-route-excel/direct-download", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    delivery_date: this.state.driverExportDate,
                    file_locale: "zh_CN",
                }),
            });
            this.triggerBrowserDownload(blob, fileName || `driver_route_${this.state.driverExportDate}.xlsx`);
            this.notification.add(this.ui.driverExportSuccess, { type: "success" });
        } catch (error) {
            this.state.error = this.mapLoadError(error, this.ui.driverExportFailed);
        } finally {
            this.state.driverExportDownloading = false;
        }
    }

    async downloadPhase5Export(exportKey) {
        if (!this.state.driverExportDate) {
            this.state.error = this.ui.driverExportDateRequired;
            return;
        }
        this.state.phase5ExportDownloadingKey = exportKey;
        this.state.error = "";
        try {
            const { blob, fileName } = await this.binaryRequest(
                `/api/admin/logistics/exports/phase5-0429/${encodeURIComponent(exportKey)}/direct-download`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        delivery_date: this.state.driverExportDate,
                        batch_no: this.state.driverExportBatchNo || "",
                        file_locale: "zh_CN",
                    }),
                }
            );
            this.triggerBrowserDownload(blob, fileName || `${exportKey}_${this.state.driverExportDate}.xlsx`);
            this.notification.add(this.ui.phase5ExportSuccess, { type: "success" });
        } catch (error) {
            this.state.error = this.mapLoadError(error, this.ui.phase5ExportFailed);
        } finally {
            this.state.phase5ExportDownloadingKey = "";
        }
    }

    downloadErrorReport() {
        const url =
            this.state.importResult?.error_report?.download_url ||
            this.state.importResult?.error_report_url ||
            this.state.precheckResult?.error_report?.download_url ||
            this.state.precheckResult?.error_report_url ||
            this.state.routePlanningImportResult?.error_report?.download_url ||
            this.state.routePlanningImportResult?.error_report_url ||
            this.state.routePlanningPrecheckResult?.error_report?.download_url ||
            this.state.routePlanningPrecheckResult?.error_report_url ||
            this.state.phase5ImportResult?.error_report?.download_url ||
            this.state.phase5ImportResult?.error_report_url ||
            this.state.phase5PrecheckResult?.error_report?.download_url ||
            this.state.phase5PrecheckResult?.error_report_url;
        if (url) {
            window.open(url, "_blank", "noopener");
        }
    }

    async openWaybillList() {
        return this.actionService.doAction("logistics_dispatch.action_logistics_dispatch_waybill");
    }

    async openExportEntry(actionXmlid) {
        if (!actionXmlid) {
            return;
        }
        return this.actionService.doAction(actionXmlid);
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

    async binaryRequest(url, options = {}) {
        const response = await fetch(url, {
            method: options.method || "GET",
            headers: options.headers || {},
            body: options.body,
        });
        const contentType = response.headers.get("content-type") || "";
        if (!response.ok || contentType.includes("application/json")) {
            const payload = await response.json().catch(() => null);
            throw new Error(payload?.data?.errors?.[0]?.error_message || payload?.message || "Binary request failed.");
        }
        const blob = await response.blob();
        return {
            blob,
            fileName: this.extractFileName(response.headers.get("content-disposition")),
        };
    }

    extractFileName(contentDisposition) {
        if (!contentDisposition) {
            return "";
        }
        const utf8Match = contentDisposition.match(/filename\*=UTF-8''([^;]+)/i);
        if (utf8Match?.[1]) {
            return decodeURIComponent(utf8Match[1]);
        }
        const basicMatch = contentDisposition.match(/filename=\"?([^\";]+)\"?/i);
        return basicMatch?.[1] || "";
    }

    triggerBrowserDownload(blob, fileName) {
        const objectUrl = window.URL.createObjectURL(blob);
        const anchor = document.createElement("a");
        anchor.href = objectUrl;
        anchor.download = fileName;
        document.body.appendChild(anchor);
        anchor.click();
        anchor.remove();
        window.URL.revokeObjectURL(objectUrl);
    }
}

const actionsRegistry = registry.category("actions");
if (!actionsRegistry.contains("logistics_web.import_center")) {
    actionsRegistry.add("logistics_web.import_center", LogisticsImportCenterAction);
}
