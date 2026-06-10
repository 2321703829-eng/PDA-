from odoo import http
from odoo.exceptions import AccessError, ValidationError
from odoo.http import request

from .base import WmsPdaBaseController


class WmsPdaWarehouseReturnController(WmsPdaBaseController):
    RETURN_REASON_LABELS = {
        "damaged": "破损",
        "expired": "过期",
        "oversupply": "补货过多",
        "slow_moving": "滞销",
        "other": "其他",
    }

    @http.route("/api/pda/wms/v1/return/create", type="http", auth="public", methods=["POST"], csrf=False)
    def create_return_operation(self, **kwargs):
        payload = self._get_payload()
        return self._handle_idempotent_request(payload, lambda user, wh, token: self._create_operation(user, wh, payload))

    @http.route(
        "/api/pda/wms/v1/return/<int:operation_id>/add-line",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def add_return_line(self, operation_id, **kwargs):
        payload = self._get_payload()
        return self._handle_idempotent_request(payload, lambda user, wh, token: self._add_line(user, wh, operation_id, payload))

    @http.route(
        "/api/pda/wms/v1/return/<int:operation_id>/confirm",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def confirm_return_operation(self, operation_id, **kwargs):
        payload = self._get_payload()
        return self._handle_idempotent_request(payload, lambda user, wh, token: self._confirm_operation(user, wh, operation_id))

    def _create_operation(self, user, warehouse, payload):
        self._require_warehouse(warehouse)
        self._require_return_permission(user)
        source_location = self._resolve_location(
            warehouse,
            payload.get("location_id"),
            payload.get("location_barcode") or payload.get("source_location_barcode"),
        ) or warehouse.lot_stock_id
        return_location = self._resolve_location(
            warehouse,
            payload.get("return_location_id"),
            payload.get("return_location_barcode") or payload.get("dest_location_barcode"),
            require_child=False,
        )
        if not source_location:
            raise ValidationError("当前仓库缺少默认库存库位，不能创建退库单。")
        vals = {
            "operation_type": "warehouse_return",
            "warehouse_id": warehouse.id,
            "location_id": source_location.id,
            "note": payload.get("note") or "",
        }
        if return_location:
            vals["return_location_id"] = return_location.id
        operation = request.env["wms.inventory.operation"].with_user(user).sudo().create(vals)
        return {
            "operation_id": operation.id,
            "name": operation.name,
            "state": operation.state,
            "warehouse_id": warehouse.id,
            "warehouse_name": warehouse.display_name,
            "location_id": source_location.id,
            "location_name": source_location.display_name,
            "return_location_id": return_location.id if return_location else False,
            "return_location_name": return_location.display_name if return_location else "",
        }

    def _add_line(self, user, warehouse, operation_id, payload):
        self._require_warehouse(warehouse)
        self._require_return_permission(user)
        operation = self._get_operation(user, warehouse, operation_id)
        if operation.state not in ("draft", "in_progress"):
            return self._error(self.ERR_STATE_CONFLICT, "当前退库单状态不能继续添加明细。", status=400, tts="状态不允许")
        product_code = (payload.get("product_barcode") or payload.get("barcode") or payload.get("default_code") or "").strip()
        if not product_code:
            raise ValidationError("请扫描商品条码或输入商品编码。")
        qty = self._float_payload(payload, "qty")
        if qty <= 0:
            raise ValidationError("退库数量必须大于 0。")
        product = self._find_product(user, product_code)
        if not product:
            return self._error(self.ERR_NOT_FOUND, "商品不存在。", status=404, tts="未找到商品")
        system_qty = self._location_product_qty(operation.location_id, product)
        reason = (payload.get("reason") or "other").strip()
        note = self._build_line_note(reason, payload.get("note") or "")
        line = request.env["wms.inventory.operation.line"].with_user(user).sudo().create(
            {
                "operation_id": operation.id,
                "product_id": product.id,
                "uom_id": product.uom_id.id,
                "system_qty": system_qty,
                "count_qty": qty,
                "note": note,
            }
        )
        return self._success(
            {
                "line_id": line.id,
                "product_id": product.id,
                "product_name": product.display_name,
                "qty": qty,
                "reason": reason,
                "reason_label": self.RETURN_REASON_LABELS.get(reason, reason),
                "current_line_count": len(operation.line_ids),
                "operation": self._format_operation(operation),
            },
            tts=f"{product.display_name}{qty:g}件，{self.RETURN_REASON_LABELS.get(reason, reason)}",
        )

    def _confirm_operation(self, user, warehouse, operation_id):
        self._require_warehouse(warehouse)
        self._require_return_permission(user)
        operation = self._get_operation(user, warehouse, operation_id)
        if operation.state in ("done", "cancelled"):
            return self._error(self.ERR_STATE_CONFLICT, "当前退库单已经结束，不能重复提交。", status=400, tts="退库单已结束")
        if not operation.line_ids:
            raise ValidationError("请先添加退库明细。")
        operation.action_mark_done()
        summary = self._operation_summary(operation)
        return self._success(
            {
                "operation_id": operation.id,
                "operation_name": operation.name,
                "operation_state": operation.state,
                "generated_picking_id": operation.generated_picking_id.id if operation.generated_picking_id else False,
                "generated_picking_name": operation.generated_picking_id.name if operation.generated_picking_id else "",
                "summary": summary,
            },
            tts=f"退库单已提交，共{summary['line_count']}种{summary['total_qty']:g}件",
        )

    def _get_operation(self, user, warehouse, operation_id):
        domain = [("id", "=", operation_id), ("operation_type", "=", "warehouse_return")]
        if warehouse:
            domain.append(("warehouse_id", "=", warehouse.id))
        operation = request.env["wms.inventory.operation"].with_user(user).sudo().search(domain, limit=1)
        if not operation:
            raise ValidationError("退库单不存在或不属于当前仓库。")
        return operation

    def _require_warehouse(self, warehouse):
        if not warehouse:
            raise ValidationError("请先选择仓库。")

    def _require_return_permission(self, user):
        if not (user.has_group("wms_pda_api.group_pda_leader") or user.has_group("wms_pda_api.group_pda_admin")):
            raise AccessError("当前账号没有退库操作权限。")

    def _resolve_location(self, warehouse, location_id=None, barcode=None, require_child=True):
        Location = request.env["stock.location"].sudo()
        location = Location.browse(int(location_id)) if location_id else Location.browse()
        if not location and barcode:
            location = Location.search([("barcode", "=", barcode)], limit=1)
        if location and require_child and warehouse:
            allowed = Location.search(
                [
                    ("id", "=", location.id),
                    "|",
                    ("id", "child_of", warehouse.view_location_id.id),
                    ("id", "=", warehouse.lot_stock_id.id),
                ],
                limit=1,
            )
            if not allowed:
                raise ValidationError("库位不属于当前仓库。")
        return location

    def _find_product(self, user, code):
        return (
            request.env["product.product"]
            .with_user(user)
            .sudo()
            .search(["|", ("barcode", "=", code), ("default_code", "=", code)], limit=1)
        )

    def _location_product_qty(self, location, product):
        quant = request.env["stock.quant"].sudo().search(
            [("location_id", "=", location.id), ("product_id", "=", product.id)],
            limit=1,
        )
        return quant.quantity if quant else 0.0

    def _build_line_note(self, reason, note):
        reason_label = self.RETURN_REASON_LABELS.get(reason, reason)
        return f"{reason_label}: {note}" if note else reason_label

    def _format_operation(self, operation):
        return {
            "operation_id": operation.id,
            "name": operation.name,
            "state": operation.state,
            "line_count": len(operation.line_ids),
            "total_qty": sum(operation.line_ids.mapped("count_qty")),
        }

    def _operation_summary(self, operation):
        return {
            "line_count": len(operation.line_ids),
            "total_qty": sum(operation.line_ids.mapped("count_qty")),
        }

    def _float_payload(self, payload, key):
        value = payload.get(key)
        if value in (None, ""):
            raise ValidationError("请填写数量。")
        return float(value)
