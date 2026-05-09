/** @odoo-module */

import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";

const LOGISTICS_OPERATION_MODELS = new Set([
    "logistics.dispatch.wave",
    "logistics.dispatch.batch",
    "logistics.dispatch.waybill",
    "logistics.dispatch.waybill.customer.line",
    "logistics.dispatch.waybill.customer.goods.line",
    "logistics.dispatch.waybill.order.line",
    "logistics.route.planning.batch",
    "logistics.trace.event",
    "logistics.trace.evidence",
    "logistics.trace.evidence.summary",
    "logistics.trace.exception",
]);

patch(FormController.prototype, {
    get showLogisticsCreateSiblingButton() {
        return (
            !this.env.inDialog &&
            this.props.resModel &&
            LOGISTICS_OPERATION_MODELS.has(this.props.resModel) &&
            this.activeActions?.create
        );
    },

    get showLogisticsDeleteButton() {
        return (
            !this.env.inDialog &&
            this.props.resModel &&
            LOGISTICS_OPERATION_MODELS.has(this.props.resModel) &&
            Boolean(this.model?.root?.resId)
        );
    },

    async onClickLogisticsCreateSibling(ev) {
        ev?.preventDefault?.();
        ev?.stopPropagation?.();
        await this.actionService?.doAction?.({
            type: "ir.actions.act_window",
            name: "新建",
            res_model: this.props.resModel,
            views: [[false, "form"]],
            target: "current",
            context: { ...(this.model?.root?.context || {}) },
        });
    },

    async onClickLogisticsDelete(ev) {
        ev?.preventDefault?.();
        ev?.stopPropagation?.();
        const resId = this.model?.root?.resId;
        if (!resId) {
            return;
        }
        const confirmed = window.confirm("确定删除当前记录吗？删除后不可恢复。");
        if (!confirmed) {
            return;
        }
        try {
            await this.env.services.orm.call(this.props.resModel, "action_logistics_delete", [[resId]], {
                context: this.model?.root?.context,
            });
            this.env.services.notification.add("删除成功。", {
                type: "success",
            });
            if (window.history.length > 1) {
                window.history.back();
                return;
            }
            this.actionService?.doAction?.({
                type: "ir.actions.act_window_close",
            });
        } catch (error) {
            this.env.services.notification.add(
                String(error?.message || "删除失败，请稍后重试。"),
                { type: "danger" }
            );
        }
    },

    onLogisticsBackButtonClick(ev) {
        ev?.preventDefault?.();
        ev?.stopPropagation?.();
        if (window.history.length > 1) {
            window.history.back();
            return;
        }
        this.actionService?.doAction?.({
            type: "ir.actions.act_window_close",
        });
    },
});
