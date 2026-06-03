from odoo import _, fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    inventory_ledger_count = fields.Integer(
        string="Inventory Ledger Lines",
        compute="_compute_inventory_ledger_count",
    )

    def _compute_inventory_ledger_count(self):
        ledger_model = self.env["wms.inventory.ledger"]
        for record in self:
            record.inventory_ledger_count = ledger_model.search_count([("warehouse_id", "=", record.id)])

    def action_open_inventory_ledger(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Inventory Ledger"),
            "res_model": "wms.inventory.ledger",
            "view_mode": "list,pivot,graph",
            "domain": [("warehouse_id", "=", self.id)],
            "context": {"search_default_warehouse_id": self.id},
        }
