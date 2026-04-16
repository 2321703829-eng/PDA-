/** @odoo-module */

import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";

const LOGISTICS_IMPORT_MODELS = new Set([
    "logistics.dispatch.wave",
    "logistics.dispatch.batch",
    "logistics.dispatch.waybill",
    "logistics.trace.event",
    "logistics.trace.evidence",
    "logistics.trace.exception",
]);

patch(ListController.prototype, {
    get showLogisticsImportButton() {
        return (
            !this.env.inDialog &&
            this.props.showButtons &&
            this.activeActions.create &&
            LOGISTICS_IMPORT_MODELS.has(this.props.resModel)
        );
    },

    onClickLogisticsImport() {
        this.actionService.doAction({
            type: "ir.actions.client",
            tag: "import",
            params: {
                active_model: this.props.resModel,
                context: this.model.root.context,
            },
        });
    },
});
