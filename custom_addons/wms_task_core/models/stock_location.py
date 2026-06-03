from odoo import _, fields, models
from odoo.exceptions import ValidationError

from .selection_options import WMS_LOCATION_USAGE_TYPE_EXT_SELECTION


class StockLocation(models.Model):
    _inherit = "stock.location"

    location_usage_type_ext = fields.Selection(
        selection=WMS_LOCATION_USAGE_TYPE_EXT_SELECTION,
        string="WMS Extended Usage",
    )
    pick_path_sequence = fields.Integer(string="Pick Path Sequence", default=0)
    is_staging_zone = fields.Boolean(string="Staging Zone", default=False)
    is_handover_zone = fields.Boolean(string="Handover Zone", default=False)
    inventory_operation_count = fields.Integer(
        string="Inventory Operations",
        compute="_compute_inventory_operation_count",
    )
    inventory_ledger_count = fields.Integer(
        string="Inventory Ledger Lines",
        compute="_compute_inventory_ledger_count",
    )

    def _compute_inventory_operation_count(self):
        operation_model = self.env["wms.inventory.operation"]
        for record in self:
            record.inventory_operation_count = operation_model.search_count(
                [("location_id", "=", record.id)]
            )

    def _compute_inventory_ledger_count(self):
        ledger_model = self.env["wms.inventory.ledger"]
        for record in self:
            record.inventory_ledger_count = ledger_model.search_count(
                [("location_id", "=", record.id)]
            )

    def action_create_inventory_operation(self):
        self.ensure_one()
        warehouse = self.env["stock.warehouse"].search(
            [
                "|",
                ("lot_stock_id", "=", self.id),
                ("view_location_id", "parent_of", self.id),
            ],
            order="id asc",
            limit=1,
        )
        if not warehouse:
            raise ValidationError(_("Warehouse must be linked before creating an inventory operation from this location."))
        operation = self.env["wms.inventory.operation"].create(
            {
                "warehouse_id": warehouse.id,
                "location_id": self.id,
            }
        )
        self.env["core.operation.audit.log"].log_action(
            business_domain="wms",
            action_code="create_inventory_operation_from_location",
            record=operation,
            note=_("Inventory operation created from stock location."),
            related_record=self,
        )
        return operation.action_open_record()

    def action_open_inventory_operations(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Inventory Operations"),
            "res_model": "wms.inventory.operation",
            "view_mode": "list,form",
            "domain": [("location_id", "=", self.id)],
            "context": {"default_location_id": self.id},
        }

    def action_open_inventory_ledger(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Inventory Ledger"),
            "res_model": "wms.inventory.ledger",
            "view_mode": "list,pivot,graph",
            "domain": [("location_id", "=", self.id)],
            "context": {"search_default_location_id": self.id},
        }
