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
                            emptyText: _t("No trace events are available yet for this waybill."),
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
                            emptyText: _t("No evidence images are available yet for this waybill."),
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
        const latestTraceType = data.latest_trace_type || _t("trace");
        const latestTraceSummary =
            data.latest_trace_summary || _t("Latest trace summary will appear here.");
        const latestTraceTime = data.latest_trace_time || "--:--";
        const arriveStatus = data.arrive_trace_status || _t("pending");
        const signoffStatus = data.signoff_trace_status || _t("pending");
        const openExceptionCount = data.open_exception_count || 0;
        const evidenceCount = data.evidence_count || 0;
        const waybillNo = data.name || _t("Waybill");

        return [
            {
                id: `${waybillNo}_latest`,
                time: latestTraceTime,
                title: _t("Latest Trace"),
                eventType: latestTraceType,
                summary: latestTraceSummary,
                operator: this.getDisplayName(data.driver_employee_id) || _t("Dispatch Team"),
                evidenceCount,
                hasException: openExceptionCount > 0,
                exceptionLabel: openExceptionCount > 0 ? `${openExceptionCount} ${_t("open")}` : "",
            },
            {
                id: `${waybillNo}_arrive`,
                time: latestTraceTime,
                title: _t("Arrival Trace Status"),
                eventType: "arrive_status",
                summary: _t("Current arrival trace status: %(status)s.") .replace("%(status)s", arriveStatus),
                operator: this.getDisplayName(data.store_id) || _t("Store"),
                evidenceCount: evidenceCount > 0 ? 1 : 0,
                hasException: false,
            },
            {
                id: `${waybillNo}_signoff`,
                time: latestTraceTime,
                title: _t("Signoff Trace Status"),
                eventType: "signoff_status",
                summary: _t("Current signoff trace status: %(status)s.").replace("%(status)s", signoffStatus),
                operator: this.getDisplayName(data.customer_id) || _t("Customer"),
                evidenceCount: evidenceCount > 1 ? 1 : 0,
                hasException: signoffStatus === "exception",
                exceptionLabel: signoffStatus === "exception" ? _t("signoff issue") : "",
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
            return this.fallbackEvidenceItems;
        }
    }

    get fallbackEvidenceItems() {
        const data = this.recordData;
        const evidenceCount = Math.max(data.evidence_count || 0, 1);
        const latestTraceTime = data.latest_trace_time || "--";
        const storeName = this.getDisplayName(data.store_id) || _t("Store");
        const driverName = this.getDisplayName(data.driver_employee_id) || _t("Driver");
        const items = [];

        for (let index = 0; index < Math.min(evidenceCount, 3); index++) {
            items.push({
                id: index + 1,
                label: `${_t("Evidence")} ${String(index + 1).padStart(2, "0")}`,
                name: index === 0 ? _t("Latest Evidence Snapshot") : `${_t("Evidence Snapshot")} ${index + 1}`,
                traceLabel: data.latest_trace_type || _t("trace"),
                uploadedAt: latestTraceTime,
                uploader: index === 0 ? driverName : storeName,
                remark:
                    index === 0
                        ? data.latest_trace_summary || _t("Latest evidence context.")
                        : `${_t("Evidence placeholder")} ${index + 1} ${_t("for waybill review.")}`,
                isExceptionEvidence:
                    data.exception_status === "open" || data.exception_status === "processing",
                previewText: `${_t("Evidence")} ${index + 1}`,
            });
        }

        return items;
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

    mapTraceRecord(record) {
        return {
            id: record.id,
            time: this.formatTraceTime(record.trace_time),
            title: this.getEventTypeLabel(record.event_type),
            eventType: record.event_type,
            summary: record.remark || "",
            operator: record.submit_user_name || _t("Unknown"),
            evidenceCount: record.evidence_count || 0,
            hasException: !!record.is_exception,
            exceptionLabel:
                record.is_exception && (record.open_exception_count || 0) > 0
                    ? `${record.open_exception_count} exception(s)`
                    : record.is_exception
                      ? _t("exception")
                      : "",
        };
    }

    mapEvidenceRecord(record) {
        const traceRef = this.getRelationalRef(record.trace_event_id);
        return {
            id: record.id,
            label: record.name || `${_t("Evidence")} ${record.id}`,
            name: record.name || `${_t("Evidence")} ${record.id}`,
            traceEventId: traceRef.id,
            traceLabel: traceRef.label || _t("Trace Event"),
            uploadedAt: record.uploaded_at || "--",
            uploader: record.uploader_name || _t("Unknown"),
            remark: record.remark || "",
            isExceptionEvidence: !!record.is_exception_related,
            hasRelatedException: !!record.is_exception_related,
            previewText: record.name || _t("Evidence Preview"),
            imageAccessKey: record.image_access_key || "",
            previewUrl: record.preview_url || "",
            fullUrl: record.full_url || "",
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
            arrive_loading_point: _t("Arrive Loading Point"),
            start_loading: _t("Start Loading"),
            finish_loading: _t("Finish Loading"),
            departed: _t("Departed"),
            arrive_store: _t("Arrive Store"),
            deliver_finish: _t("Deliver Finish"),
            signoff: _t("Signoff"),
            exception_report: _t("Exception Report"),
        };
        return labels[eventType] || _t("Trace Event");
    }

    async onTraceClick(item) {
        if (!item?.id || typeof item.id !== "number") {
            return this.notifyPending(_t('Open trace is not available yet for "%s".').replace("%s", item.title));
        }
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: item.title || _t("Open Trace"),
            res_model: "logistics.trace.event",
            res_id: item.id,
            views: [[false, "form"]],
        });
    }

    async onTraceEvidenceClick(item) {
        if (!item?.id || typeof item.id !== "number") {
            return this.notifyPending(_t('Open evidence is not available yet for "%s".').replace("%s", item.title));
        }
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: `${_t("Open Evidence")} - ${item.title || _t("Trace Event")}`,
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
                name: `Open Exceptions - ${item.title || "Trace Event"}`,
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
            name: _t("Open Exceptions"),
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
            return this.notifyPending(_t("Open related trace is not available for this evidence item yet."));
        }
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: item.traceLabel || _t("Open Trace"),
            res_model: "logistics.trace.event",
            res_id: item.traceEventId,
            views: [[false, "form"]],
        });
    }

    async onEvidenceExceptionClick(item) {
        if (!item?.traceEventId) {
            return this.notifyPending(_t("Open related exceptions is not available for this evidence item yet."));
        }
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: _t("Open Related Exceptions"),
            res_model: "logistics.trace.exception",
            views: [
                [false, "list"],
                [false, "form"],
            ],
            domain: [["trace_event_id", "=", item.traceEventId]],
        });
    }

    onOpenFullImage(item) {
        if (item?.fullUrl) {
            window.open(item.fullUrl, "_blank", "noopener");
            return;
        }
        this.notifyPending(
            _t('Open full image is not available yet for "%s".').replace("%s", item.name || item.label)
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
