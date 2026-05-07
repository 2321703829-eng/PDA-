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
                emptyText="'当前运单还没有留痕记录。'"
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
                operator: record.submit_user_name || "未知",
                evidenceCount: record.evidence_count || 0,
                hasException: !!record.is_exception,
                exceptionLabel:
                    record.is_exception && (record.open_exception_count || 0) > 0
                        ? `${record.open_exception_count} 条异常`
                        : record.is_exception
                          ? "异常相关"
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
            arrive_loading_point: "到达装货点",
            start_loading: "开始装车",
            finish_loading: "装车完成",
            departed: "仓库发车",
            arrive_store: "到店",
            deliver_finish: "交付完成",
            signoff: "签收",
            exception_report: "异常上报",
        };
        return labels[eventType] || "留痕事件";
    }

    async onTraceClick(item) {
        if (!item?.id) {
            return this.notifyPending("暂时还不能打开留痕详情。");
        }
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: item.title || "查看留痕",
            res_model: "logistics.trace.event",
            res_id: item.id,
            views: [[false, "form"]],
        });
    }

    async onEvidenceClick(item) {
        if (!item?.id) {
            return this.notifyPending("暂时还不能打开证据列表。");
        }
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: `查看证据 - ${item.title || "留痕事件"}`,
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
            return this.notifyPending("暂时还不能打开异常列表。");
        }
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
}

export const logisticsTraceTimelineField = {
    component: LogisticsTraceTimelineField,
    displayName: _t("留痕时间线"),
    supportedTypes: ["char"],
};

registry.category("fields").add("logistics_trace_timeline", logisticsTraceTimelineField);

export class LogisticsEvidenceViewerField extends LogisticsWaybillBasePanel {
    static template = xml`
        <div class="o_logistics_waybill_widget_field">
            <EvidenceViewerWidget
                items="state.items"
                loading="state.loading"
                emptyText="'当前运单还没有证据。'"
                onTraceClick.bind="onTraceClick"
                onExceptionClick.bind="onExceptionClick"
                onOpenFullImage.bind="onOpenFullImage"
                onDownloadImage.bind="onDownloadImage"
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
                    label: record.name || `证据 ${record.id}`,
                    name: record.name || `证据 ${record.id}`,
                    traceEventId: traceRef.id,
                    traceLabel: traceRef.label || "留痕事件",
                    uploadedAt: record.uploaded_at || "--",
                    uploader: record.uploader_name || "未知",
                    remark: record.remark || "",
                    isExceptionEvidence: !!record.is_exception_related,
                    hasRelatedException: !!record.is_exception_related,
                    previewText: record.name || "证据预览",
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
            return this.notifyPending("当前证据暂时还不能打开关联留痕。");
        }
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: item.traceLabel || "查看留痕",
            res_model: "logistics.trace.event",
            res_id: item.traceEventId,
            views: [[false, "form"]],
        });
    }

    async onExceptionClick(item) {
        if (!item?.traceEventId) {
            return this.notifyPending("当前证据暂时还不能打开关联异常。");
        }
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "查看关联异常",
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
        this.notifyPending(`暂时还不能打开“${item?.name || item?.label || "当前证据"}”的原图。`);
    }

    onDownloadImage(item) {
        const sourceUrl = this.normalizeImageUrl(item?.fullUrl || item?.previewUrl || "");
        if (!sourceUrl) {
            this.notifyPending("暂时还不能下载当前证据图片。");
            return;
        }
        const downloadUrl = sourceUrl.includes("?")
            ? `${sourceUrl}&download=1`
            : `${sourceUrl}?download=1`;
        window.open(downloadUrl, "_blank", "noopener");
    }
}

export const logisticsEvidenceViewerField = {
    component: LogisticsEvidenceViewerField,
    displayName: _t("证据查看"),
    supportedTypes: ["char"],
};

registry.category("fields").add("logistics_evidence_viewer", logisticsEvidenceViewerField);
