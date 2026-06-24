from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from .base import WmsPdaBaseController


class WmsPdaBarcodeController(WmsPdaBaseController):
    @http.route("/api/pda/wms/v1/barcode/parse", type="http", auth="public", methods=["POST"], csrf=False)
    def parse_barcode(self, **kwargs):
        payload = self._get_payload()
        return self._handle_request(lambda user, wh, token: self._parse_barcode(wh, payload))

    @http.route("/api/pda/wms/v1/scan/resolve", type="http", auth="public", methods=["POST"], csrf=False)
    def resolve_scan(self, **kwargs):
        payload = self._get_payload()
        return self._handle_request(lambda user, wh, token: self._resolve_scan(user, wh, payload))

    def _parse_barcode(self, warehouse, payload):
        barcode = (payload.get("barcode") or "").strip()
        if not barcode:
            raise ValidationError("请扫描或输入条码。")
        result = request.env["wms.pda.barcode.parser"].sudo().parse_barcode(barcode, warehouse=warehouse)
        if result.get("type") == "unknown":
            return self._error(
                self.ERR_BARCODE_UNKNOWN,
                "条码无法识别。",
                status=400,
                data={"barcode": barcode},
                tts="未识别",
            )
        return result

    def _resolve_scan(self, user, warehouse, payload):
        barcode = (payload.get("barcode") or "").strip()
        if not barcode:
            raise ValidationError("请扫描或输入条码。")
        parsed = request.env["wms.pda.barcode.parser"].sudo().parse_barcode(barcode, warehouse=warehouse)
        scan_type = parsed.get("type")
        record = parsed.get("record") or {}
        if scan_type == "task":
            return self._resolve_task(record, parsed)
        if scan_type == "location":
            return {
                "type": "location",
                "route": "inventory",
                "inventory_mode": "location",
                "barcode": record.get("barcode") or barcode,
                "title": record.get("name") or barcode,
                "message": "已识别库位，进入库位库存。",
            }
        if scan_type == "product":
            match = self._find_product_task(user, warehouse, record.get("id"))
            if match:
                match.update({
                    "type": "product_task",
                    "barcode": record.get("barcode") or record.get("default_code") or barcode,
                    "product": record,
                    "message": "已找到该商品关联的待执行任务。",
                })
                return match
            return {
                "type": "product",
                "route": "inventory",
                "inventory_mode": "product",
                "barcode": record.get("barcode") or record.get("default_code") or barcode,
                "title": record.get("name") or barcode,
                "message": "未找到关联待办，进入商品库存。",
            }
        if scan_type == "picking":
            route = "inbound-flow" if record.get("picking_type_code") == "incoming" else "outbound-flow"
            return {
                "type": "picking",
                "route": route,
                "barcode": barcode,
                "title": record.get("name") or barcode,
                "message": "已识别单据，请在对应履约链路中处理。",
            }
        return self._error(
            self.ERR_BARCODE_UNKNOWN,
            "条码无法识别。",
            status=400,
            data={"barcode": barcode},
            tts="未识别",
        )

    def _resolve_task(self, record, parsed):
        model_name = parsed.get("task_type") or ""
        mapping = {
            "wms.receipt.task": ("inbound-flow", "inbound", "入库上架"),
            "wms.putaway.task": ("inbound-flow", "putaway", "入库上架"),
            "wms.pick.task": ("outbound-flow", "pick", "出库履约"),
            "wms.check.task": ("outbound-flow", "outbound", "出库履约"),
            "wms.handover.order": ("outbound-flow", "handover", "出库履约"),
        }
        route, mode, title = mapping.get(model_name, ("home", "", "工作台"))
        return {
            "type": "task",
            "route": route,
            "mode": mode,
            "target_id": record.get("id"),
            "task_type": model_name,
            "title": title,
            "record": record,
            "message": "已识别任务，正在打开。",
        }

    def _find_product_task(self, user, warehouse, product_id):
        if not product_id:
            return {}
        product_id = int(product_id)
        specs = (
            ("wms.receipt.task", "inbound-flow", "inbound", ["waiting_receipt", "receiving"]),
            ("wms.putaway.task", "inbound-flow", "putaway", ["waiting_putaway", "putaway_ing"]),
            ("wms.pick.task", "outbound-flow", "pick", ["waiting_pick", "picking"]),
            ("wms.check.task", "outbound-flow", "outbound", ["waiting_check", "checking"]),
        )
        for model_name, route, mode, states in specs:
            task = self._first_task_with_product(user, warehouse, model_name, states, product_id)
            if task:
                return {
                    "route": route,
                    "mode": mode,
                    "target_id": task.id,
                    "record": {"id": task.id, "name": task.name, "state": task.state},
                }
        return {}

    def _first_task_with_product(self, user, warehouse, model_name, states, product_id):
        if model_name not in request.env.registry:
            return False
        domain = [("state", "in", states)]
        if warehouse:
            domain.append(("warehouse_id", "=", warehouse.id))
        tasks = request.env[model_name].with_user(user).sudo().search(domain, limit=30, order="id asc")
        for task in tasks:
            if model_name in ("wms.receipt.task", "wms.putaway.task"):
                picking = task.stock_picking_id
                moves = (getattr(picking, "move_ids_without_package", False) or picking.move_ids) if picking else request.env["stock.move"]
                if moves.filtered(lambda move: move.product_id.id == product_id):
                    return task
            elif model_name == "wms.pick.task":
                if task.line_ids.filtered(lambda line: line.product_id.id == product_id):
                    return task
            elif model_name == "wms.check.task" and task.pick_task_id:
                if task.pick_task_id.line_ids.filtered(lambda line: line.product_id.id == product_id):
                    return task
        return request.env[model_name]
