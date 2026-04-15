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

    get totalItemCount() {
        return this.allItems.length;
    }

    get visibleItemCount() {
        return this.visibleItems.length;
    }

    get hasActiveFilters() {
        return this.state.onlyWithImages || this.state.onlyExceptions;
    }

    get activeFilterLabels() {
        const labels = [];
        if (this.state.onlyWithImages) {
            labels.push("只看有图");
        }
        if (this.state.onlyExceptions) {
            labels.push("只看异常");
        }
        return labels;
    }

    get summaryText() {
        const total = this.totalItemCount;
        const visible = this.visibleItemCount;
        if (!total) {
            return "当前运单还没有留痕记录，可先回到基础信息确认流转状态。";
        }
        if (!this.hasActiveFilters) {
            return `共 ${total} 条留痕，按时间顺序核对事件、证据和异常。`;
        }
        return `共 ${total} 条留痕，当前筛选出 ${visible} 条，可取消筛选继续查看完整过程。`;
    }

    get hasItems() {
        return this.visibleItems.length > 0;
    }

    get emptyText() {
        if (this.totalItemCount && this.hasActiveFilters) {
            return "当前筛选条件下没有匹配的留痕记录，可取消上方筛选后继续查看。";
        }
        return this.props.emptyText || "当前筛选条件下没有留痕记录。";
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
