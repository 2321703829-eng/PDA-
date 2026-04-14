/** @odoo-module */

import { Component, useState } from "@odoo/owl";

export class EvidenceViewerWidget extends Component {
    static template = "logistics_web.EvidenceViewerWidget";
    static props = {
        items: { type: Array, optional: true },
        waybillId: { type: Number, optional: true },
        activeEvidenceId: { type: Number, optional: true },
        loading: { type: Boolean, optional: true },
        emptyText: { type: String, optional: true },
        readonly: { type: Boolean, optional: true },
        onEvidenceChange: { type: Function, optional: true },
        onTraceClick: { type: Function, optional: true },
        onExceptionClick: { type: Function, optional: true },
        onOpenFullImage: { type: Function, optional: true },
    };

    setup() {
        this.state = useState({
            activeIndex: this.getInitialActiveIndex(),
        });
    }

    get isLoading() {
        return this.props.loading || false;
    }

    get allItems() {
        return Array.isArray(this.props.items) ? this.props.items : this.defaultItems;
    }

    get hasItems() {
        return this.allItems.length > 0;
    }

    get activeItem() {
        return this.allItems[this.state.activeIndex] || null;
    }

    get emptyText() {
        return this.props.emptyText || "No evidence items yet.";
    }

    getInitialActiveIndex() {
        const items = this.props.items || [];
        if (!items.length || !this.props.activeEvidenceId) {
            return 0;
        }
        const matchedIndex = items.findIndex(
            (item) => item.id === this.props.activeEvidenceId
        );
        return matchedIndex >= 0 ? matchedIndex : 0;
    }

    setActiveIndex(index) {
        if (index < 0 || index >= this.allItems.length) {
            return;
        }
        this.state.activeIndex = index;
        const activeItem = this.activeItem;
        if (activeItem && this.props.onEvidenceChange) {
            this.props.onEvidenceChange(activeItem);
        }
    }

    onThumbClick(item, index) {
        this.setActiveIndex(index);
    }

    onPrevClick() {
        this.setActiveIndex(this.state.activeIndex - 1);
    }

    onNextClick() {
        this.setActiveIndex(this.state.activeIndex + 1);
    }

    onTraceClick() {
        if (this.activeItem && this.props.onTraceClick) {
            this.props.onTraceClick(this.activeItem);
        }
    }

    onExceptionClick() {
        if (this.activeItem && this.props.onExceptionClick) {
            this.props.onExceptionClick(this.activeItem);
        }
    }

    onOpenFullImage() {
        if (this.activeItem && this.props.onOpenFullImage) {
            this.props.onOpenFullImage(this.activeItem);
        }
    }

    get defaultItems() {
        return [
            {
                id: 1,
                label: "Evidence 01",
                name: "Door Damage Photo",
                traceLabel: "Exception Report",
                uploadedAt: "2026-04-13 09:19",
                uploader: "Li Si",
                remark: "Front-left outer box visibly damaged.",
                isExceptionEvidence: true,
                previewText: "Damage Photo",
            },
            {
                id: 2,
                label: "Evidence 02",
                name: "Arrival Receipt Photo",
                traceLabel: "Arrive Store",
                uploadedAt: "2026-04-13 08:43",
                uploader: "Zhang San",
                remark: "Arrival proof before unloading.",
                isExceptionEvidence: false,
                previewText: "Arrival Photo",
            },
            {
                id: 3,
                label: "Evidence 03",
                name: "Loading Confirmation Photo",
                traceLabel: "Loading Finish",
                uploadedAt: "2026-04-13 07:56",
                uploader: "Wang Wu",
                remark: "Vehicle loaded and sealed.",
                isExceptionEvidence: false,
                previewText: "Loading Photo",
            },
        ];
    }
}
