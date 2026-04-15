/** @odoo-module */

import { App, useEffect } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { getTemplate } from "@web/core/templates";
import { useService } from "@web/core/utils/hooks";
import { formView } from "@web/views/form/form_view";
import { FormRenderer } from "@web/views/form/form_renderer";

import { TraceTimelineWidget } from "../widgets/trace_timeline_widget";
import { EvidenceViewerWidget } from "../widgets/evidence_viewer_widget";

export class LogisticsWaybillFormRenderer extends FormRenderer {
    setup() {
        super.setup();
        this.actionService = useService("action");
        this.notificationService = useService("notification");
        this.orm = useService("orm");
        useEffect(
            (resId, writeDate, latestTraceSummary, latestTraceTime, evidenceCount, openExceptionCount) => {
                const el = this.el;
                if (!el || !resId) {
                    return;
                }

                const timelineHost = el.querySelector(".o_logistics_waybill_timeline_host");
                const evidenceHost = el.querySelector(".o_logistics_waybill_evidence_host");
                if (!timelineHost || !evidenceHost) {
                    return;
                }
                let isDestroyed = false;
                let timelineApp;
                let evidenceApp;

                const mountWidgets = async () => {
                    const timelineItems = await this.loadTimelineItems(resId);
                    const evidenceItems = await this.loadEvidenceItems(resId);
                    if (isDestroyed) {
                        return;
                    }

                    timelineApp = new App(TraceTimelineWidget, {
                        env: this.env,
                        getTemplate,
                        props: {
                            waybillId: resId,
                            items: timelineItems,
                            loading: false,
                            emptyText: _t("当前运单还没有留痕记录。"),
                            onTraceClick: (item) => this.onTraceClick(item),
                            onEvidenceClick: (item) => this.onTraceEvidenceClick(item),
                            onExceptionClick: (item) => this.onTraceExceptionClick(item),
                        },
                    });
                    timelineApp.mount(timelineHost);

                    evidenceApp = new App(EvidenceViewerWidget, {
                        env: this.env,
                        getTemplate,
                        props: {
                            waybillId: resId,
                            items: evidenceItems,
                            loading: false,
                            emptyText: _t("当前运单还没有证据。"),
                            onTraceClick: (item) => this.onEvidenceTraceClick(item),
                            onExceptionClick: (item) => this.onEvidenceExceptionClick(item),
                            onOpenFullImage: (item) => this.onOpenFullImage(item),
                        },
                    });
                    evidenceApp.mount(evidenceHost);
                };

                mountWidgets();
                return () => {
                    isDestroyed = true;
                    timelineApp?.destroy();
                    evidenceApp?.destroy();
                    timelineHost.replaceChildren();
                    evidenceHost.replaceChildren();
                };
            },
            () => [
                this.props.record?.resId,
                this.props.record?.data?.write_date,
                this.props.record?.data?.latest_trace_summary,
                this.props.record?.data?.latest_trace_time,
                this.props.record?.data?.evidence_count,
                this.props.record?.data?.open_exception_count,
            ]
        );
    }

    get recordData() {
        return this.props.record?.data || {};
    }

    get fallbackTimelineItems() {
        const data = this.recordData;
        const latestTraceType = data.latest_trace_type || _t("留痕");
        const latestTraceSummary =
            data.latest_trace_summary || _t("最近留痕摘要会显示在这里。");
        const latestTraceTime = data.latest_trace_time || "--:--";
        const arriveStatus = data.arrive_trace_status || _t("待补充");
        const signoffStatus = data.signoff_trace_status || _t("待补充");
        const openExceptionCount = data.open_exception_count || 0;
        const evidenceCount = data.evidence_count || 0;
        const waybillNo = data.name || _t("运单");

        return [
            {
                id: `${waybillNo}_latest`,
                time: latestTraceTime,
                title: _t("最近进展"),
                eventType: latestTraceType,
                eventTypeLabel: latestTraceType,
                summary: latestTraceSummary,
                operator: this.getDisplayName(data.driver_employee_id) || _t("调度组"),
                evidenceCount,
                hasException: openExceptionCount > 0,
                exceptionLabel: openExceptionCount > 0 ? `${openExceptionCount} 条异常` : "",
            },
            {
                id: `${waybillNo}_arrive`,
                time: latestTraceTime,
                title: _t("到店留痕"),
                eventType: "arrive_status",
                eventTypeLabel: _t("到店状态"),
                summary: _t("当前到店留痕状态：%(status)s。").replace("%(status)s", arriveStatus),
                operator: this.getDisplayName(data.store_id) || _t("门店"),
                evidenceCount: evidenceCount > 0 ? 1 : 0,
                hasException: false,
            },
            {
                id: `${waybillNo}_signoff`,
                time: latestTraceTime,
                title: _t("签收留痕"),
                eventType: "signoff_status",
                eventTypeLabel: _t("签收状态"),
                summary: _t("当前签收留痕状态：%(status)s。").replace("%(status)s", signoffStatus),
                operator: this.getDisplayName(data.customer_id) || _t("客户"),
                evidenceCount: evidenceCount > 1 ? 1 : 0,
                hasException: signoffStatus === "exception",
                exceptionLabel: signoffStatus === "exception" ? _t("签收异常") : "",
            },
        ];
    }

    async loadTimelineItems(waybillId) {
        try {
            const records = await this.orm.searchRead(
                "logistics.trace.event",
                [["waybill_id", "=", waybillId]],
                [
                    "id",
                    "trace_time",
                    "event_type",
                    "submit_user_name",
                    "remark",
                    "evidence_count",
                    "is_exception",
                    "open_exception_count",
                ],
                {
                    order: "trace_time desc, id desc",
                    limit: 30,
                }
            );
            return records.map((record) => this.mapTraceRecord(record));
        } catch {
            return this.fallbackTimelineItems;
        }
    }

    async loadEvidenceItems(waybillId) {
        try {
            const records = await this.orm.searchRead(
                "logistics.trace.evidence",
                [["waybill_id", "=", waybillId]],
                [
                    "id",
                    "name",
                    "trace_event_id",
                    "uploaded_at",
                    "uploader_name",
                    "remark",
                    "is_exception_related",
                    "image_access_key",
                    "preview_url",
                    "full_url",
                    "sequence",
                ],
                {
                    order: "uploaded_at desc, sequence asc, id desc",
                    limit: 30,
                }
            );
            return records.map((record) => this.mapEvidenceRecord(record));
        } catch {
            return [];
        }
    }

    getDisplayName(value) {
        if (Array.isArray(value)) {
            return value[1];
        }
        return value || "";
    }

    getRelationalRef(value) {
        if (Array.isArray(value)) {
            return {
                id: value[0],
                label: value[1],
            };
        }
        return {
            id: value || false,
            label: "",
        };
    }

    cleanImageValue(value) {
        if (!value || typeof value !== "string") {
            return "";
        }
        const trimmed = value.trim();
        if (
            (trimmed.startsWith('"') && trimmed.endsWith('"')) ||
            (trimmed.startsWith("'") && trimmed.endsWith("'"))
        ) {
            return trimmed.slice(1, -1).trim();
        }
        return trimmed;
    }

    normalizeImageUrl(value) {
        const cleanedValue = this.cleanImageValue(value);
        if (!cleanedValue) {
            return "";
        }
        if (
            cleanedValue.startsWith("http://") ||
            cleanedValue.startsWith("https://") ||
            cleanedValue.startsWith("file://") ||
            cleanedValue.startsWith("blob:") ||
            cleanedValue.startsWith("data:") ||
            cleanedValue.startsWith("/")
        ) {
            return cleanedValue;
        }
        if (/^[A-Za-z]:[\\/]/.test(cleanedValue)) {
            return `file:///${cleanedValue.replace(/\\/g, "/")}`;
        }
        return cleanedValue;
    }

    mapTraceRecord(record) {
        return {
            id: record.id,
            time: this.formatTraceTime(record.trace_time),
            title: this.getEventTypeLabel(record.event_type),
            eventType: record.event_type,
            eventTypeLabel: this.getEventTypeLabel(record.event_type),
            summary: record.remark || "",
            operator: record.submit_user_name || _t("未知"),
            evidenceCount: record.evidence_count || 0,
            hasException: !!record.is_exception,
            exceptionLabel:
                record.is_exception && (record.open_exception_count || 0) > 0
                    ? `${record.open_exception_count} 条异常`
                    : record.is_exception
                      ? _t("异常相关")
                      : "",
        };
    }

    mapEvidenceRecord(record) {
        const traceRef = this.getRelationalRef(record.trace_event_id);
        const imageAccessKey = this.cleanImageValue(record.image_access_key);
        const previewUrl = this.cleanImageValue(record.preview_url);
        const fullUrl = this.cleanImageValue(record.full_url);
        return {
            id: record.id,
            label: record.name || `${_t("证据")} ${record.id}`,
            name: record.name || `${_t("证据")} ${record.id}`,
            traceEventId: traceRef.id,
            traceLabel: traceRef.label || _t("留痕事件"),
            uploadedAt: record.uploaded_at || "--",
            uploader: record.uploader_name || _t("未知"),
            remark: record.remark || "",
            isExceptionEvidence: !!record.is_exception_related,
            hasRelatedException: !!record.is_exception_related,
            previewText: record.name || _t("证据预览"),
            imageAccessKey,
            previewUrl,
            fullUrl,
            sequence: record.sequence || 10,
        };
    }

    formatTraceTime(value) {
        if (!value) {
            return "--:--";
        }
        if (typeof value === "string" && value.length >= 16) {
            return value.slice(11, 16);
        }
        return value;
    }

    getEventTypeLabel(eventType) {
        const labels = {
            arrive_loading_point: _t("到达装货点"),
            start_loading: _t("开始装车"),
            finish_loading: _t("装车完成"),
            departed: _t("仓库发车"),
            arrive_store: _t("到店"),
            deliver_finish: _t("交付完成"),
            signoff: _t("签收"),
            exception_report: _t("异常上报"),
        };
        return labels[eventType] || _t("留痕事件");
    }

    async onTraceClick(item) {
        if (!item?.id || typeof item.id !== "number") {
            return this.notifyPending(_t('暂时还不能打开“%s”的留痕详情。').replace("%s", item.title));
        }
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: item.title || _t("查看留痕"),
            res_model: "logistics.trace.event",
            res_id: item.id,
            views: [[false, "form"]],
        });
    }

    async onTraceEvidenceClick(item) {
        if (!item?.id || typeof item.id !== "number") {
            return this.notifyPending(_t('暂时还不能打开“%s”的证据列表。').replace("%s", item.title));
        }
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: `${_t("查看证据")} - ${item.title || _t("留痕事件")}`,
            res_model: "logistics.trace.evidence",
            views: [
                [false, "list"],
                [false, "form"],
            ],
            domain: [["trace_event_id", "=", item.id]],
        });
    }

    async onTraceExceptionClick(item) {
        if (item?.id && typeof item.id === "number") {
            return this.actionService.doAction({
                type: "ir.actions.act_window",
                name: `查看异常 - ${item.title || "留痕事件"}`,
                res_model: "logistics.trace.exception",
                views: [
                    [false, "list"],
                    [false, "form"],
                ],
                domain: [["trace_event_id", "=", item.id]],
            });
        }
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: _t("查看异常"),
            res_model: "logistics.trace.exception",
            views: [
                [false, "list"],
                [false, "form"],
            ],
            domain: [["state", "in", ["open", "processing"]]],
        });
    }

    async onEvidenceTraceClick(item) {
        if (!item?.traceEventId) {
            return this.notifyPending(_t("当前证据暂时还不能打开关联留痕。"));
        }
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: item.traceLabel || _t("查看留痕"),
            res_model: "logistics.trace.event",
            res_id: item.traceEventId,
            views: [[false, "form"]],
        });
    }

    async onEvidenceExceptionClick(item) {
        if (!item?.traceEventId) {
            return this.notifyPending(_t("当前证据暂时还不能打开关联异常。"));
        }
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: _t("查看关联异常"),
            res_model: "logistics.trace.exception",
            views: [
                [false, "list"],
                [false, "form"],
            ],
            domain: [["trace_event_id", "=", item.traceEventId]],
        });
    }

    onOpenFullImage(item) {
        const openUrl = this.normalizeImageUrl(item?.fullUrl || item?.previewUrl || item?.imageAccessKey);
        if (openUrl) {
            window.open(openUrl, "_blank", "noopener");
            return;
        }
        this.notifyPending(
            _t('暂时还不能打开“%s”的原图。').replace("%s", item.name || item.label)
        );
    }

    notifyPending(message) {
        this.notificationService.add(message, { type: "info" });
    }
}

export const logisticsWaybillFormView = {
    ...formView,
    Renderer: LogisticsWaybillFormRenderer,
};

registry.category("views").add("logistics_waybill_form", logisticsWaybillFormView);
