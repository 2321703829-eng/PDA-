from odoo import api, models


class WmsPdaBarcodeParser(models.AbstractModel):
    _name = "wms.pda.barcode.parser"
    _description = "WMS PDA Barcode Parser"

    @api.model
    def parse_barcode(self, barcode, warehouse=None):
        code = (barcode or "").strip()
        if not code:
            return {"type": "unknown"}
        warehouse = warehouse or self.env["stock.warehouse"]
        location = self._find_location(code, warehouse)
        if location:
            return {"type": "location", "record": self._format_location(location)}
        task = self._find_wms_task(code)
        if task:
            return {
                "type": "task",
                "task_type": task._name,
                "record": self._format_task(task),
            }
        product = self._find_product(code)
        if product:
            return {"type": "product", "record": self._format_product(product)}
        picking = self.env["stock.picking"].sudo().search([("name", "=", code)], limit=1)
        if picking:
            return {"type": "picking", "record": self._format_picking(picking)}
        return {"type": "unknown"}

    def _find_location(self, code, warehouse):
        Location = self.env["stock.location"].sudo()
        domain = [("barcode", "=", code)]
        if warehouse:
            domain = [
                ("barcode", "=", code),
                "|",
                ("id", "child_of", warehouse.view_location_id.id),
                ("id", "=", warehouse.lot_stock_id.id),
            ]
        location = Location.search(domain, limit=1)
        if location:
            return location
        if code.startswith("LOC-"):
            return Location.search([("name", "=", code[4:])], limit=1)
        return False

    def _find_wms_task(self, code):
        task_models = (
            "wms.receipt.task",
            "wms.putaway.task",
            "wms.outbound.task",
            "wms.pick.task",
            "wms.check.task",
            "wms.handover.order",
        )
        for model_name in task_models:
            if model_name in self.env:
                task = self.env[model_name].sudo().search([("name", "=", code)], limit=1)
                if task:
                    return task
        return False

    def _find_product(self, code):
        return self.env["product.product"].sudo().search(
            ["|", ("barcode", "=", code), ("default_code", "=", code)],
            limit=1,
        )

    def _format_product(self, product):
        template = product.product_tmpl_id
        return {
            "id": product.id,
            "name": product.display_name,
            "default_code": product.default_code or "",
            "barcode": product.barcode or "",
            "uom": product.uom_id.name or "",
            "spec": getattr(template, "specification", "") or "",
            "weight": product.weight or template.weight or 0.0,
            "volume": product.volume or template.volume or 0.0,
        }

    def _format_location(self, location):
        warehouse = self.env["stock.warehouse"].sudo().search(
            [
                "|",
                ("lot_stock_id", "=", location.id),
                ("view_location_id", "parent_of", location.id),
            ],
            limit=1,
        )
        return {
            "id": location.id,
            "name": location.display_name,
            "barcode": location.barcode or "",
            "usage_type": location.location_usage_type_ext or location.usage or "",
            "warehouse_id": warehouse.id if warehouse else False,
        }

    def _format_task(self, task):
        return {
            "id": task.id,
            "name": task.name,
            "state": getattr(task, "state", "") or "",
        }

    def _format_picking(self, picking):
        return {
            "id": picking.id,
            "name": picking.name,
            "state": picking.state,
            "picking_type_code": picking.picking_type_code,
            "partner_name": picking.partner_id.display_name or "",
        }
