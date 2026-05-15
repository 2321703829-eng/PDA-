from odoo import _, models


class WmsHandoverOrder(models.Model):
    _inherit = "wms.handover.order"

    def action_create_dispatch_order(self):
        self.ensure_one()
        dispatch_order = self.env["tms.dispatch.order"].search([("handover_order_id", "=", self.id)], limit=1)
        if not dispatch_order:
            dispatch_order = self.env["tms.dispatch.order"].create_from_handover(self)
            self.env["core.operation.audit.log"].log_action(
                business_domain="tms",
                action_code="create_dispatch_order_from_handover",
                record=dispatch_order,
                note=_("Dispatch order created from handover order."),
                related_record=self,
            )
        return dispatch_order.action_open_record()

    def action_open_dispatch_orders(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Dispatch Orders"),
            "res_model": "tms.dispatch.order",
            "view_mode": "list,form",
            "domain": [("handover_order_id", "=", self.id)],
            "context": {"default_handover_order_id": self.id},
        }
