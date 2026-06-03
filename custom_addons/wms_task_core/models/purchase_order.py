from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


WMS_RECEIPT_SUMMARY_SELECTION = [
    ("not_started", "Not Started"),
    ("waiting_receipt", "Waiting Receipt"),
    ("receiving", "Receiving"),
    ("received", "Received"),
    ("receipt_exception", "Receipt Exception"),
]


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    arrival_plan_date = fields.Date(string="Arrival Plan Date", tracking=True)
    wms_receipt_status = fields.Selection(
        selection=WMS_RECEIPT_SUMMARY_SELECTION,
        string="WMS Receipt Status",
        compute="_compute_wms_receipt_summary",
        store=False,
    )
    receipt_task_count = fields.Integer(
        string="Receipt Task Count",
        compute="_compute_wms_receipt_summary",
    )

    def _get_related_receipt_tasks(self):
        picking_ids = self.picking_ids.filtered(lambda picking: picking.picking_type_code == "incoming").ids
        if not picking_ids:
            return self.env["wms.receipt.task"]
        return self.env["wms.receipt.task"].search([("stock_picking_id", "in", picking_ids)])

    @api.depends("picking_ids")
    def _compute_wms_receipt_summary(self):
        receipt_model = self.env["wms.receipt.task"]
        for record in self:
            incoming_picking_ids = record.picking_ids.filtered(lambda picking: picking.picking_type_code == "incoming").ids
            if not incoming_picking_ids:
                record.receipt_task_count = 0
                record.wms_receipt_status = "not_started"
                continue
            receipt_tasks = receipt_model.search([("stock_picking_id", "in", incoming_picking_ids)])
            record.receipt_task_count = len(receipt_tasks)
            states = set(receipt_tasks.mapped("state"))
            if not states:
                record.wms_receipt_status = "not_started"
            elif "receipt_exception" in states:
                record.wms_receipt_status = "receipt_exception"
            elif states == {"received"}:
                record.wms_receipt_status = "received"
            elif "receiving" in states:
                record.wms_receipt_status = "receiving"
            else:
                record.wms_receipt_status = "waiting_receipt"

    def action_create_receipt_tasks(self):
        receipt_model = self.env["wms.receipt.task"]
        created_tasks = receipt_model
        for record in self:
            incoming_pickings = record.picking_ids.filtered(lambda picking: picking.picking_type_code == "incoming")
            if not incoming_pickings:
                raise ValidationError(_("Purchase order must have at least one incoming picking before creating receipt tasks."))
            for picking in incoming_pickings:
                created_tasks |= receipt_model.create_from_picking(picking)
        if len(created_tasks) == 1:
            return created_tasks.action_open_record()
        return {
            "type": "ir.actions.act_window",
            "name": _("Receipt Tasks"),
            "res_model": "wms.receipt.task",
            "view_mode": "list,form",
            "domain": [("id", "in", created_tasks.ids)],
        }

    def action_open_receipt_tasks(self):
        self.ensure_one()
        receipt_tasks = self._get_related_receipt_tasks()
        return {
            "type": "ir.actions.act_window",
            "name": _("Receipt Tasks"),
            "res_model": "wms.receipt.task",
            "view_mode": "list,form",
            "domain": [("id", "in", receipt_tasks.ids)],
            "context": {
                "search_default_stock_picking_id": self.picking_ids.filtered(lambda picking: picking.picking_type_code == "incoming").ids[:1],
            },
        }
