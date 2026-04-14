/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

import { Component, onWillStart, onWillUpdateProps, useState, xml } from "@odoo/owl";

import { EvidenceViewerWidget } from "./evidence_viewer_widget";
import { TraceTimelineWidget } from "./trace_timeline_widget";

class LogisticsWaybillBasePanel extends Component {
    static props = { ...standardFieldProps };

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.notificationService = useService("notification");
        this.state = useState({
            items: [],
            loading: true,
        });

        onWillStart(async () => {
            await this.loadItems(this.props);
        });

        onWillUpdateProps(async (nextProps) => {
            const currentResId = this.props.record?.resId;
            const nextResId = nextProps.record?.resId;
            const currentWriteDate = this.props.record?.data?.write_date;
            const nextWriteDate = nextProps.record?.data?.write_date;
            if (currentResId !== nextResId || currentWriteDate !== nextWriteDate) {
                await this.loadItems(nextProps);
            }
        });
    }

    get waybillId() {
        return this.props.record?.resId;
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

    notifyPending(message) {
        this.notificationService.add(message, { type: "info" });
    }
}

export class LogisticsTraceTimelineField extends LogisticsWaybillBasePanel {
    static template = xml`
        <div class="o_logistics_waybill_widget_field">
            <TraceTimelineWidget
                items="state.items"
                loading="state.loading"
                emptyText="'No trace events are available yet for this waybill.'"
                onTraceClick.bind="onTraceClick"
                onEvidenceClick.bind="onEvidenceClick"
                onExceptionClick.bind="onExceptionClick"
            />
        </div>
    `;
    static components = { TraceTimelineWidget };

    async loadItems(props = this.props) {
        const waybillId = props.record?.resId;
        if (!waybillId) {
            this.state.items = [];
            this.state.loading = false;
            return;
        }
        this.state.loading = true;
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
            this.state.items = records.map((record) => ({
                id: record.id,
                time: this.formatTraceTime(record.trace_time),
                title: this.getEventTypeLabel(record.event_type),
                eventType: record.event_type,
                summary: record.remark || "",
                operator: record.submit_user_name || "Unknown",
                evidenceCount: record.evidence_count || 0,
                hasException: !!record.is_exception,
                exceptionLabel:
                    record.is_exception && (record.open_exception_count || 0) > 0
                        ? `${record.open_exception_count} exception(s)`
                        : record.is_exception
                          ? "exception"
                          : "",
            }));
        } catch {
            this.state.items = [];
        } finally {
            this.state.loading = false;
        }
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
            arrive_loading_point: "Arrive Loading Point",
            start_loading: "Start Loading",
            finish_loading: "Finish Loading",
            departed: "Departed",
            arrive_store: "Arrive Store",
            deliver_finish: "Deliver Finish",
            signoff: "Signoff",
            exception_report: "Exception Report",
        };
        return labels[eventType] || "Trace Event";
    }

    async onTraceClick(item) {
        if (!item?.id) {
            return this.notifyPending("Open trace is not available yet.");
        }
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: item.title || "Open Trace",
            res_model: "logistics.trace.event",
            res_id: item.id,
            views: [[false, "form"]],
        });
    }

    async onEvidenceClick(item) {
        if (!item?.id) {
            return this.notifyPending("Open evidence is not available yet.");
        }
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: `Open Evidence - ${item.title || "Trace Event"}`,
            res_model: "logistics.trace.evidence",
            views: [
                [false, "list"],
                [false, "form"],
            ],
            domain: [["trace_event_id", "=", item.id]],
        });
    }

    async onExceptionClick(item) {
        if (!item?.id) {
            return this.notifyPending("Open exception is not available yet.");
        }
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
}

export const logisticsTraceTimelineField = {
    component: LogisticsTraceTimelineField,
    displayName: _t("Trace Timeline"),
    supportedTypes: ["char"],
};

registry.category("fields").add("logistics_trace_timeline", logisticsTraceTimelineField);

export class LogisticsEvidenceViewerField extends LogisticsWaybillBasePanel {
    static template = xml`
        <div class="o_logistics_waybill_widget_field">
            <EvidenceViewerWidget
                items="state.items"
                loading="state.loading"
                emptyText="'No evidence images are available yet for this waybill.'"
                onTraceClick.bind="onTraceClick"
                onExceptionClick.bind="onExceptionClick"
                onOpenFullImage.bind="onOpenFullImage"
            />
        </div>
    `;
    static components = { EvidenceViewerWidget };

    async loadItems(props = this.props) {
        const waybillId = props.record?.resId;
        if (!waybillId) {
            this.state.items = [];
            this.state.loading = false;
            return;
        }
        this.state.loading = true;
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
            this.state.items = records.map((record) => {
                const traceRef = this.getRelationalRef(record.trace_event_id);
                const imageAccessKey = this.cleanImageValue(record.image_access_key);
                const previewUrl = this.cleanImageValue(record.preview_url);
                const fullUrl = this.cleanImageValue(record.full_url);
                return {
                    id: record.id,
                    label: record.name || `Evidence ${record.id}`,
                    name: record.name || `Evidence ${record.id}`,
                    traceEventId: traceRef.id,
                    traceLabel: traceRef.label || "Trace Event",
                    uploadedAt: record.uploaded_at || "--",
                    uploader: record.uploader_name || "Unknown",
                    remark: record.remark || "",
                    isExceptionEvidence: !!record.is_exception_related,
                    hasRelatedException: !!record.is_exception_related,
                    previewText: record.name || "Evidence Preview",
                    imageAccessKey,
                    previewUrl,
                    fullUrl,
                    sequence: record.sequence || 10,
                };
            });
        } catch {
            this.state.items = [];
        } finally {
            this.state.loading = false;
        }
    }

    async onTraceClick(item) {
        if (!item?.traceEventId) {
            return this.notifyPending("Open related trace is not available for this evidence item yet.");
        }
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: item.traceLabel || "Open Trace",
            res_model: "logistics.trace.event",
            res_id: item.traceEventId,
            views: [[false, "form"]],
        });
    }

    async onExceptionClick(item) {
        if (!item?.traceEventId) {
            return this.notifyPending("Open related exceptions is not available for this evidence item yet.");
        }
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Open Related Exceptions",
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
        this.notifyPending(`Open full image is not available yet for "${item?.name || item?.label || "this evidence"}".`);
    }
}

export const logisticsEvidenceViewerField = {
    component: LogisticsEvidenceViewerField,
    displayName: _t("Evidence Viewer"),
    supportedTypes: ["char"],
};

registry.category("fields").add("logistics_evidence_viewer", logisticsEvidenceViewerField);
