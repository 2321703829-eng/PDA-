/** @odoo-module */

import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";

patch(FormController.prototype, {
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
