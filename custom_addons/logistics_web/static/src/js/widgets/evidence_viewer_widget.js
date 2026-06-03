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
        onDownloadImage: { type: Function, optional: true },
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

    get totalItemCount() {
        return this.allItems.length;
    }

    get uniqueEvidenceCount() {
        const evidenceIds = new Set(
            this.allItems
                .map((item) => item.evidenceId || item.evidence_id || false)
                .filter((value) => value)
        );
        return evidenceIds.size || this.totalItemCount;
    }

    get exceptionEvidenceCount() {
        return this.allItems.filter((item) => item.isExceptionEvidence).length;
    }

    get emptyText() {
        return this.props.emptyText || "当前还没有证据。";
    }

    getInitialActiveIndex() {
        const items = this.props.items || [];
        if (!items.length || !this.props.activeEvidenceId) {
            return 0;
        }
        const matchedIndex = items.findIndex((item) => item.evidenceId === this.props.activeEvidenceId || item.id === this.props.activeEvidenceId);
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

    get hasActiveOpenUrl() {
        return Boolean(this.activeOpenUrl);
    }

    get hasActivePreview() {
        return Boolean(this.activePreviewUrl) && !this.hasPreviewFailed(this.activeItem);
    }

    get activeSummaryText() {
        const item = this.activeItem;
        if (!item) {
            return "当前还没有可查看的证据。";
        }
        const parts = [
            `当前查看第 ${this.state.activeIndex + 1} / ${this.totalItemCount} 张图片`,
            `关联留痕 ${item.traceLabel || item.trace_label || "--"}`,
        ];
        if (item.imageIndex && item.imageCountInEvidence) {
            parts.push(`该证据内第 ${item.imageIndex} / ${item.imageCountInEvidence} 张`);
        }
        if (item.uploadedAt || item.uploaded_at) {
            parts.push(`上传时间 ${item.uploadedAt || item.uploaded_at}`);
        }
        if (item.isExceptionEvidence) {
            parts.push("与异常处理相关");
        }
        if (!this.hasActiveOpenUrl) {
            parts.push("当前仅支持预览");
        }
        return `${parts.join("，")}。`;
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
        return item?.key || item?.imageId || item?.id || item?.imageAccessKey || item?.name || item?.label || "";
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
        return this.normalizeUrl(item?.downloadUrl || item?.fullUrl || item?.previewUrl || item?.imageAccessKey || "");
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

    onDownloadImage() {
        if (this.activeItem && this.props.onDownloadImage) {
            this.props.onDownloadImage(this.activeItem);
        }
    }
}
