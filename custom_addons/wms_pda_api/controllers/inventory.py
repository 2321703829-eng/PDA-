from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from .base import WmsPdaBaseController


class WmsPdaInventoryController(WmsPdaBaseController):
    @http.route(
        ["/api/pda/wms/v1/inventory/product", "/api/pda/wms/v1/inventory/by-product"],
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_product_inventory(self, **kwargs):
        payload = self._get_payload()
        return self._handle_request(lambda user, wh, token: self._product_inventory(user, wh, payload))

    @http.route(
        ["/api/pda/wms/v1/inventory/location", "/api/pda/wms/v1/inventory/by-location"],
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_location_inventory(self, **kwargs):
        payload = self._get_payload()
        return self._handle_request(lambda user, wh, token: self._location_inventory(user, wh, payload))

    @http.route("/api/pda/wms/v1/inventory/search", type="http", auth="public", methods=["POST"], csrf=False)
    def search_inventory(self, **kwargs):
        payload = self._get_payload()
        return self._handle_request(lambda user, wh, token: self._search_inventory(user, wh, payload))

    def _product_inventory(self, user, warehouse, payload):
        self._require_warehouse(warehouse)
        code = (payload.get("barcode") or payload.get("default_code") or "").strip()
        if not code:
            raise ValidationError("请扫描商品条码或输入商品编码。")
        product = self._find_product(user, code)
        if not product:
            return self._error(self.ERR_NOT_FOUND, "商品不存在。", status=404, tts="未找到商品")
        ledger_lines = self._ledger_model(user).search(
            [
                ("warehouse_id", "=", warehouse.id),
                ("product_id", "=", product.id),
            ],
            order="location_id asc, id asc",
        )
        summary = self._summary(ledger_lines)
        return {
            "product": self._format_product(product, summary=summary),
            "warehouse": self._format_warehouse(warehouse),
            "summary": summary,
            "locations": [self._format_product_location(line) for line in ledger_lines],
            "records": [self._format_ledger_line(line) for line in ledger_lines],
        }

    def _location_inventory(self, user, warehouse, payload):
        self._require_warehouse(warehouse)
        barcode = (payload.get("location_barcode") or payload.get("barcode") or "").strip()
        if not barcode:
            raise ValidationError("请扫描库位条码。")
        location = self._find_location(user, warehouse, barcode)
        if not location:
            return self._error(self.ERR_NOT_FOUND, "库位不存在或不属于当前仓库。", status=404, tts="未找到库位")
        ledger_lines = self._ledger_model(user).search(
            [
                ("warehouse_id", "=", warehouse.id),
                ("location_id", "=", location.id),
            ],
            order="product_id asc, id asc",
        )
        return {
            "location": self._format_location(location),
            "warehouse": self._format_warehouse(warehouse),
            "summary": self._summary(ledger_lines),
            "products": [self._format_location_product(line) for line in ledger_lines],
            "records": [self._format_ledger_line(line) for line in ledger_lines],
        }

    def _search_inventory(self, user, warehouse, payload):
        self._require_warehouse(warehouse)
        offset = int(payload.get("offset") or 0)
        limit = min(int(payload.get("limit") or 20), 100)
        keyword = (payload.get("keyword") or payload.get("q") or "").strip()
        domain = [("warehouse_id", "=", warehouse.id)]
        if keyword:
            domain += [
                "|",
                "|",
                "|",
                "|",
                ("product_id.name", "ilike", keyword),
                ("product_id.default_code", "ilike", keyword),
                ("product_id.barcode", "ilike", keyword),
                ("location_id.name", "ilike", keyword),
                ("location_id.barcode", "ilike", keyword),
            ]
        Ledger = self._ledger_model(user)
        total = Ledger.search_count(domain)
        ledger_lines = Ledger.search(domain, offset=offset, limit=limit, order="location_id asc, product_id asc, id asc")
        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "keyword": keyword,
            "warehouse": self._format_warehouse(warehouse),
            "records": [self._format_ledger_line(line) for line in ledger_lines],
        }

    def _require_warehouse(self, warehouse):
        if not warehouse:
            raise ValidationError("请先选择仓库。")

    def _ledger_model(self, user):
        return request.env["wms.inventory.ledger"].with_user(user).sudo()

    def _find_product(self, user, code):
        return (
            request.env["product.product"]
            .with_user(user)
            .sudo()
            .search(["|", ("barcode", "=", code), ("default_code", "=", code)], limit=1)
        )

    def _find_location(self, user, warehouse, barcode):
        domain = [
            ("barcode", "=", barcode),
            "|",
            ("id", "child_of", warehouse.view_location_id.id),
            ("id", "=", warehouse.lot_stock_id.id),
        ]
        return request.env["stock.location"].with_user(user).sudo().search(domain, limit=1)

    def _summary(self, ledger_lines):
        return {
            "line_count": len(ledger_lines),
            "quantity_on_hand": sum(ledger_lines.mapped("quantity_on_hand")),
            "reserved_quantity": sum(ledger_lines.mapped("reserved_quantity")),
            "available_quantity": sum(ledger_lines.mapped("available_quantity")),
        }

    def _format_ledger_line(self, line):
        product = line.product_id
        location = line.location_id
        warehouse = line.warehouse_id
        uom = line.product_uom_id or product.uom_id
        return {
            "product_id": product.id,
            "product_name": product.display_name,
            "default_code": product.default_code or "",
            "barcode": product.barcode or "",
            "location_id": location.id,
            "location_name": location.display_name,
            "location_barcode": location.barcode or "",
            "quantity_on_hand": line.quantity_on_hand,
            "reserved_quantity": line.reserved_quantity,
            "available_quantity": line.available_quantity,
            "uom": uom.name if uom else "",
            "warehouse_id": warehouse.id if warehouse else False,
            "warehouse_name": warehouse.display_name if warehouse else "",
        }

    def _format_product_location(self, line):
        location = line.location_id
        return {
            "location_id": location.id,
            "location": location.display_name,
            "location_barcode": location.barcode or "",
            "qty": line.quantity_on_hand,
            "reserved": line.reserved_quantity,
            "available": line.available_quantity,
        }

    def _format_location_product(self, line):
        product = line.product_id
        return {
            "product_id": product.id,
            "product_name": product.display_name,
            "default_code": product.default_code or "",
            "barcode": product.barcode or "",
            "qty": line.quantity_on_hand,
            "reserved": line.reserved_quantity,
            "available": line.available_quantity,
            "uom": (line.product_uom_id or product.uom_id).name if (line.product_uom_id or product.uom_id) else "",
        }

    def _format_product(self, product, summary=None):
        summary = summary or {}
        result = {
            "id": product.id,
            "name": product.display_name,
            "default_code": product.default_code or "",
            "barcode": product.barcode or "",
            "uom": product.uom_id.name if product.uom_id else "",
        }
        if summary:
            result.update(
                {
                    "total_qty": summary.get("quantity_on_hand", 0.0),
                    "reserved_qty": summary.get("reserved_quantity", 0.0),
                    "available_qty": summary.get("available_quantity", 0.0),
                }
            )
        return result

    def _format_location(self, location):
        return {
            "id": location.id,
            "name": location.display_name,
            "barcode": location.barcode or "",
            "usage": location.usage or "",
            "usage_type": location.location_usage_type_ext if "location_usage_type_ext" in location._fields else "",
        }

    def _format_warehouse(self, warehouse):
        return {
            "id": warehouse.id,
            "name": warehouse.display_name,
        }
