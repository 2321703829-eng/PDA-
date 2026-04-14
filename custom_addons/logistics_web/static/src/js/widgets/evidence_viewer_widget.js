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
            failedPreviewKeys: {},
        });
    }

    get isLoading() {
        return this.props.loading || false;
    }

    get allItems() {
        return Array.isArray(this.props.items) ? this.props.items : [];
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

    get activePreviewUrl() {
        return this.getItemPreviewUrl(this.activeItem);
    }

    get activeOpenUrl() {
        return this.getItemOpenUrl(this.activeItem);
    }

    get hasActivePreview() {
        return Boolean(this.activePreviewUrl) && !this.hasPreviewFailed(this.activeItem);
    }

    normalizeUrl(url) {
        if (!url || typeof url !== "string") {
            return "";
        }
        let normalized = url.trim();
        if (
            (normalized.startsWith('"') && normalized.endsWith('"')) ||
            (normalized.startsWith("'") && normalized.endsWith("'"))
        ) {
            normalized = normalized.slice(1, -1).trim();
        }
        if (!normalized) {
            return "";
        }
        if (
            normalized.startsWith("http://") ||
            normalized.startsWith("https://") ||
            normalized.startsWith("file://") ||
            normalized.startsWith("blob:") ||
            normalized.startsWith("data:") ||
            normalized.startsWith("/")
        ) {
            return normalized;
        }
        if (/^[A-Za-z]:[\\/]/.test(normalized)) {
            return `file:///${normalized.replace(/\\/g, "/")}`;
        }
        return normalized;
    }

    getPreviewKey(item) {
        return item?.id || item?.imageAccessKey || item?.name || item?.label || "";
    }

    hasPreviewFailed(item) {
        const key = this.getPreviewKey(item);
        return Boolean(key && this.state.failedPreviewKeys[key]);
    }

    markPreviewFailed(item) {
        const key = this.getPreviewKey(item);
        if (!key || this.state.failedPreviewKeys[key]) {
            return;
        }
        this.state.failedPreviewKeys = {
            ...this.state.failedPreviewKeys,
            [key]: true,
        };
    }

    getItemPreviewUrl(item) {
        return this.normalizeUrl(item?.previewUrl || item?.fullUrl || item?.imageAccessKey || "");
    }

    getItemOpenUrl(item) {
        return this.normalizeUrl(item?.fullUrl || item?.previewUrl || item?.imageAccessKey || "");
    }

    onStageImageError() {
        if (this.activeItem) {
            this.markPreviewFailed(this.activeItem);
        }
    }

    onThumbImageError(item) {
        this.markPreviewFailed(item);
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
}
