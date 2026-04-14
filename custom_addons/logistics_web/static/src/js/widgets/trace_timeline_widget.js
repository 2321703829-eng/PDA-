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
        return Array.isArray(this.props.items) ? this.props.items : [];
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
}
