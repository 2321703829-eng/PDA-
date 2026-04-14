/** @odoo-module */

import { Component, useState } from "@odoo/owl";

export class TraceTimelineWidget extends Component {
    static template = "logistics_web.TraceTimelineWidget";
    static props = {
        items: { type: Array, optional: true },
        waybillId: { type: Number, optional: true },
        loading: { type: Boolean, optional: true },
        emptyText: { type: String, optional: true },
        readonly: { type: Boolean, optional: true },
        onTraceClick: { type: Function, optional: true },
        onEvidenceClick: { type: Function, optional: true },
        onExceptionClick: { type: Function, optional: true },
    };

    setup() {
        this.state = useState({
            onlyWithImages: false,
            onlyExceptions: false,
        });
    }

    get isLoading() {
        return Boolean(this.props.loading);
    }

    get allItems() {
        return Array.isArray(this.props.items) ? this.props.items : this.defaultItems;
    }

    get visibleItems() {
        return this.allItems.filter((item) => {
            if (this.state.onlyWithImages && !item.evidenceCount) {
                return false;
            }
            if (this.state.onlyExceptions && !item.hasException) {
                return false;
            }
            return true;
        });
    }

    get hasItems() {
        return this.visibleItems.length > 0;
    }

    get emptyText() {
        return this.props.emptyText || "No trace items match the current filters.";
    }

    toggleOnlyWithImages() {
        this.state.onlyWithImages = !this.state.onlyWithImages;
    }

    toggleOnlyExceptions() {
        this.state.onlyExceptions = !this.state.onlyExceptions;
    }

    onTraceClick(item) {
        this.props.onTraceClick?.(item);
    }

    onEvidenceClick(item, ev) {
        ev.stopPropagation();
        this.props.onEvidenceClick?.(item);
    }

    onExceptionClick(item, ev) {
        ev.stopPropagation();
        this.props.onExceptionClick?.(item);
    }

    get defaultItems() {
        return [
            {
                id: 1,
                time: "09:18",
                eventType: "exception_report",
                title: "Exception reported on store arrival",
                summary: "Store-side damage issue reported with missing signoff proof.",
                operator: "Li Si",
                evidenceCount: 2,
                hasException: true,
                exceptionLabel: "damage",
            },
            {
                id: 2,
                time: "08:42",
                eventType: "arrive_store",
                title: "Arrived at store",
                summary: "Driver checked in at the delivery location and uploaded arrival proof.",
                operator: "Wang Wu",
                evidenceCount: 1,
                hasException: false,
            },
            {
                id: 3,
                time: "07:55",
                eventType: "loading_finish",
                title: "Loading completed",
                summary: "Batch loading finished at the warehouse dock and the waybill entered transit stage.",
                operator: "Warehouse Team",
                evidenceCount: 3,
                hasException: false,
            },
        ];
    }
}
