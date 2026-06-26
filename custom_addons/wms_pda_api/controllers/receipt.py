from odoo import fields, http
from odoo.exceptions import ValidationError
from odoo.http import request

from .base import WmsPdaBaseController


class WmsPdaReceiptController(WmsPdaBaseController):
    @http.route("/api/pda/wms/v1/receipt/tasks", type="http", auth="public", methods=["GET"], csrf=False)
    def list_receipt_tasks(self, **kwargs):
        payload = self._get_payload()
        return self._handle_request(lambda user, wh, token: self._receipt_list_tasks(user, wh, payload))

    @http.route(
        "/api/pda/wms/v1/receipt/tasks/<int:task_id>/lines",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_receipt_task_lines(self, task_id, **kwargs):
        payload = self._get_payload()
        lock = str(payload.get("lock", "1")).strip().lower() not in ("0", "false", "no")
        return self._handle_request(lambda user, wh, token: self._receipt_get_task_lines(user, wh, task_id, lock=lock))

    @http.route(
        "/api/pda/wms/v1/receipt/tasks/<int:task_id>/confirm-line",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def confirm_receipt_line(self, task_id, **kwargs):
        payload = self._get_payload()
        return self._handle_idempotent_request(payload, lambda user, wh, token: self._receipt_confirm_line(user, wh, task_id, payload))

    @http.route(
        "/api/pda/wms/v1/receipt/tasks/<int:task_id>/complete",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def complete_receipt_task(self, task_id, **kwargs):
        payload = self._get_payload()
        return self._handle_idempotent_request(payload, lambda user, wh, token: self._receipt_complete_task(user, wh, task_id))

    @http.route(
        "/api/pda/wms/v1/receipt/tasks/<int:task_id>/close",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def close_receipt_task(self, task_id, **kwargs):
        payload = self._get_payload()
        return self._handle_idempotent_request(payload, lambda user, wh, token: self._receipt_close_task(user, wh, task_id, payload))

    @http.route("/api/pda/wms/v1/receipt/manual/product", type="http", auth="public", methods=["GET"], csrf=False)
    def lookup_manual_receipt_product(self, **kwargs):
        payload = self._get_payload()
        return self._handle_request(lambda user, wh, token: self._receipt_lookup_product(user, payload))

    @http.route("/api/pda/wms/v1/receipt/manual/create", type="http", auth="public", methods=["POST"], csrf=False)
    def create_manual_receipt_task(self, **kwargs):
        payload = self._get_payload()
        return self._handle_idempotent_request(payload, lambda user, wh, token: self._receipt_create_manual_task(user, wh, payload))

    def _receipt_list_tasks(self, user, warehouse, payload):
        if not warehouse:
            raise ValidationError("请先选择仓库。")
        limit = min(int(payload.get("limit") or 50), 100)
        state = (payload.get("state") or "").strip()
        domain = [("warehouse_id", "=", warehouse.id)]
        if state:
            domain.append(("state", "=", state))
        else:
            domain.append(("state", "in", ["waiting_receipt", "receiving"]))
        tasks = request.env["wms.receipt.task"].with_user(user).sudo().search(domain, limit=limit, order="id desc")
        return {
            "warehouse_id": warehouse.id,
            "tasks": [self._receipt_format_task(task, include_progress=True) for task in tasks],
        }

    def _receipt_get_task_lines(self, user, warehouse, task_id, lock=False):
        task = self._receipt_get_task(user, warehouse, task_id)
        if lock:
            request.env["wms.task.lock"].sudo().acquire(
                task._name,
                task.id,
                user.id,
                warehouse_id=warehouse.id if warehouse else False,
            )
        return {
            "task": self._receipt_format_task(task, include_progress=True),
            "lines": [self._receipt_format_move(move) for move in self._receipt_task_moves(task)],
        }

    def _receipt_confirm_line(self, user, warehouse, task_id, payload):
        task = self._receipt_get_task(user, warehouse, task_id)
        if task.state == "received":
            return self._error(self.ERR_STATE_CONFLICT, "收货任务已完成，不能重复确认。", status=400, tts="任务已完成")
        request.env["wms.task.lock"].sudo().acquire(
            task._name,
            task.id,
            user.id,
            warehouse_id=warehouse.id if warehouse else False,
        )
        move = self._receipt_get_move(task, payload)
        done_qty = self._receipt_float_payload(payload, "done_qty")
        demand_qty = move.product_uom_qty or 0.0
        if done_qty < 0:
            raise ValidationError("实收数量不能小于 0。")
        if demand_qty and done_qty > demand_qty:
            return self._error(self.ERR_QTY_EXCEED, "实收数量不能超过应收数量。", status=400, tts="数量超出")
        barcode = (payload.get("barcode") or payload.get("product_barcode") or "").strip()
        if barcode and not self._receipt_product_matches_barcode(move.product_id, barcode):
            return self._error(self.ERR_BARCODE_UNKNOWN, "扫描商品与当前行不一致。", status=400, tts="商品不匹配")
        if task.state == "waiting_receipt":
            task.action_start_receipt()
        self._receipt_write_done_qty(move, done_qty)
        return {
            "task": self._receipt_format_task(task, include_progress=True),
            "line": self._receipt_format_move(move),
        }

    def _receipt_complete_task(self, user, warehouse, task_id):
        task = self._receipt_get_task(user, warehouse, task_id)
        if task.state == "received":
            return {
                "task": self._receipt_format_task(task, include_progress=True),
                "putaway_task_ids": task.putaway_task_ids.ids,
            }
        if task.state not in ("waiting_receipt", "receiving"):
            return self._error(self.ERR_STATE_CONFLICT, "当前状态不能完成收货。", status=400, tts="状态不允许")
        task.action_mark_received()
        request.env["wms.task.lock"].sudo().release(task._name, task.id, user_id=user.id)
        return self._success(
            {
                "task": self._receipt_format_task(task, include_progress=True),
                "putaway_task_ids": task.putaway_task_ids.ids,
            },
            tts="收货完成",
        )

    def _receipt_close_task(self, user, warehouse, task_id, payload):
        task = self._receipt_get_task(user, warehouse, task_id)
        if task.state == "received":
            return self._error(self.ERR_STATE_CONFLICT, "已完成的收货单不能关单。", status=400, tts="已完成不能关单")
        if task.state == "closed":
            return self._success({"task": self._receipt_format_task(task, include_progress=True)}, tts="收货单已关闭")
        if task.state not in ("waiting_receipt", "receiving", "receipt_exception"):
            return self._error(self.ERR_STATE_CONFLICT, "当前状态不能关单。", status=400, tts="状态不允许")
        reason = (payload.get("reason") or "PDA 关单").strip()
        note_parts = [part for part in (task.note, reason) if part]
        task.write({"state": "closed", "note": "\n".join(note_parts)})
        if task.stock_picking_id and "wms_task_ref" in task.stock_picking_id._fields:
            task.stock_picking_id.write({"wms_task_ref": task.name})
        request.env["wms.task.lock"].sudo().release(task._name, task.id, user_id=user.id)
        return self._success({"task": self._receipt_format_task(task, include_progress=True)}, tts="收货单已关闭")

    def _receipt_lookup_product(self, user, payload):
        code = (payload.get("code") or payload.get("barcode") or payload.get("keyword") or "").strip()
        if not code:
            raise ValidationError("请输入商品条码或 SKU。")
        product = self._receipt_find_product(user, code)
        if not product:
            return self._error(self.ERR_BARCODE_UNKNOWN, "未找到商品，请核对条码或 SKU。", status=404)
        return {"product": self._receipt_format_product(product)}

    def _receipt_create_manual_task(self, user, warehouse, payload):
        if not warehouse:
            raise ValidationError("请先选择仓库。")
        lines = payload.get("lines") or []
        if not isinstance(lines, list) or not lines:
            raise ValidationError("请至少添加一条商品。")
        picking_type = (
            request.env["stock.picking.type"]
            .with_user(user)
            .sudo()
            .search([("code", "=", "incoming"), ("warehouse_id", "=", warehouse.id)], limit=1)
        )
        if not picking_type:
            raise ValidationError("当前仓库没有可用的入库类型。")
        partner_name = (payload.get("partner_name") or "").strip() or "手动收货供应商"
        partner = request.env["res.partner"].sudo().search([("name", "=", partner_name)], limit=1)
        if not partner:
            partner_vals = {"name": partner_name}
            if "supplier_rank" in request.env["res.partner"]._fields:
                partner_vals["supplier_rank"] = 1
            partner = request.env["res.partner"].sudo().create(partner_vals)
        origin = (payload.get("origin") or payload.get("related_no") or "").strip() or self._receipt_manual_origin()
        picking_vals = {
            "picking_type_id": picking_type.id,
            "partner_id": partner.id,
            "origin": origin,
            "location_id": picking_type.default_location_src_id.id,
            "location_dest_id": picking_type.default_location_dest_id.id,
            "scheduled_date": fields.Datetime.now(),
            "company_id": warehouse.company_id.id,
        }
        if "note" in request.env["stock.picking"]._fields:
            picking_vals["note"] = (payload.get("note") or "PDA 手动新建收货单").strip()
        if "erp_source_type" in request.env["stock.picking"]._fields:
            picking_vals["erp_source_type"] = "purchase"
        tracking_no = (payload.get("logistics_no") or payload.get("tracking_no") or "").strip()
        if tracking_no:
            for field_name in ("carrier_tracking_ref", "tracking_ref", "waybill_no", "logistics_no"):
                if field_name in request.env["stock.picking"]._fields:
                    picking_vals[field_name] = tracking_no
                    break
        picking = request.env["stock.picking"].with_user(user).sudo().create(picking_vals)
        normalized_lines = self._receipt_manual_lines(user, lines)
        Move = request.env["stock.move"].with_user(user).sudo()
        for item in normalized_lines:
            product = item["product"]
            move_vals = {
                "product_id": product.id,
                "product_uom_qty": item["qty"],
                "product_uom": product.uom_id.id,
                "picking_id": picking.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
                "company_id": warehouse.company_id.id,
            }
            if "name" in Move._fields:
                move_vals["name"] = product.display_name
            if "description_picking" in Move._fields:
                move_vals["description_picking"] = product.display_name
            Move.create(move_vals)
        picking.action_confirm()
        for move in self._receipt_task_picking_moves(picking):
            self._receipt_write_done_qty(move, 0.0)
        receipt = request.env["wms.receipt.task"].sudo().create_from_picking(picking)
        return {
            "task": self._receipt_format_task(receipt, include_progress=True),
            "lines": [self._receipt_format_move(move) for move in self._receipt_task_moves(receipt)],
        }

    def _receipt_manual_lines(self, user, lines):
        grouped = {}
        for index, line in enumerate(lines, start=1):
            code = (line.get("barcode") or line.get("product_barcode") or line.get("default_code") or "").strip()
            if not code:
                raise ValidationError(f"第 {index} 行缺少商品条码或 SKU。")
            qty = float(line.get("qty") or line.get("demand_qty") or 0)
            if qty <= 0:
                raise ValidationError(f"第 {index} 行数量必须大于 0。")
            product = self._receipt_find_product(user, code)
            if not product:
                raise ValidationError(f"第 {index} 行商品不存在：{code}")
            if product.id not in grouped:
                grouped[product.id] = {"product": product, "qty": 0.0}
            grouped[product.id]["qty"] += qty
        return list(grouped.values())

    def _receipt_find_product(self, user, code):
        Product = request.env["product.product"].with_user(user).sudo()
        return Product.search(
            [
                "|",
                "|",
                ("barcode", "=", code),
                ("default_code", "=", code),
                ("product_tmpl_id.default_code", "=", code),
            ],
            limit=1,
        )

    def _receipt_format_product(self, product):
        return {
            "id": product.id,
            "product_name": product.display_name,
            "default_code": product.default_code or "",
            "barcode": product.barcode or "",
            "uom": product.uom_id.name if product.uom_id else "",
        }

    def _receipt_manual_origin(self):
        return "手动收货单-%s" % fields.Datetime.now().strftime("%Y%m%d%H%M")

    def _receipt_get_task(self, user, warehouse, task_id):
        domain = [("id", "=", task_id)]
        if warehouse:
            domain.append(("warehouse_id", "=", warehouse.id))
        task = request.env["wms.receipt.task"].with_user(user).sudo().search(domain, limit=1)
        if not task:
            raise ValidationError("收货任务不存在或不属于当前仓库。")
        return task

    def _receipt_get_move(self, task, payload):
        move_id = int(payload.get("move_id") or payload.get("line_id") or 0)
        moves = self._receipt_task_moves(task)
        if move_id:
            move = moves.filtered(lambda record: record.id == move_id)[:1]
            if move:
                return move
            raise ValidationError("收货明细不存在。")
        barcode = (payload.get("barcode") or payload.get("product_barcode") or "").strip()
        if not barcode:
            raise ValidationError("请传入收货明细或商品条码。")
        matched = moves.filtered(lambda record: self._receipt_product_matches_barcode(record.product_id, barcode))[:1]
        if not matched:
            raise ValidationError("未找到匹配的商品明细。")
        return matched

    def _receipt_task_moves(self, task):
        picking = task.stock_picking_id
        return self._receipt_task_picking_moves(picking)

    def _receipt_task_picking_moves(self, picking):
        if not picking:
            return request.env["stock.move"]
        moves = getattr(picking, "move_ids_without_package", False) or picking.move_ids
        return moves.filtered(lambda move: move.product_id)

    def _receipt_format_task(self, task, include_progress=False):
        picking = task.stock_picking_id
        result = {
            "id": task.id,
            "name": task.name,
            "state": task.state,
            "warehouse_id": task.warehouse_id.id,
            "warehouse_name": task.warehouse_id.display_name,
            "picking_id": picking.id if picking else False,
            "picking_name": picking.name if picking else "",
            "origin": picking.origin if picking else "",
            "partner_id": task.partner_id.id if task.partner_id else False,
            "partner_name": task.partner_id.display_name if task.partner_id else "",
            "scheduled_date": task.scheduled_date,
            "create_uid_name": task.create_uid.display_name if task.create_uid else "",
            "create_date": task.create_date,
            "source_type_label": self._receipt_source_type_label(picking),
            "related_no": picking.origin if picking and picking.origin else "",
            "logistics_no": self._receipt_tracking_no(picking),
        }
        if include_progress:
            moves = self._receipt_task_moves(task)
            done_moves = moves.filtered(lambda move: self._receipt_read_done_qty(move) > 0)
            result.update(
                {
                    "line_count": len(moves),
                    "done_line_count": len(done_moves),
                    "demand_qty": sum(moves.mapped("product_uom_qty")),
                    "done_qty": sum(self._receipt_read_done_qty(move) for move in moves),
                    "product_summary": self._receipt_product_summary(moves),
                }
            )
        return result

    def _receipt_source_type_label(self, picking):
        source_type = picking.erp_source_type if picking and "erp_source_type" in picking._fields else ""
        return {
            "purchase": "采购",
            "sale_return": "退货",
            "internal": "调拨",
            "purchase_return": "退供",
        }.get(source_type or "purchase", "采购")

    def _receipt_tracking_no(self, picking):
        if not picking:
            return ""
        for field_name in ("carrier_tracking_ref", "tracking_ref", "waybill_no", "logistics_no"):
            if field_name in picking._fields and picking[field_name]:
                return picking[field_name]
        return ""

    def _receipt_format_move(self, move):
        product = move.product_id
        return {
            "id": move.id,
            "product_id": product.id,
            "product_name": product.display_name,
            "default_code": product.default_code or "",
            "barcode": product.barcode or "",
            "demand_qty": move.product_uom_qty or 0.0,
            "done_qty": self._receipt_read_done_qty(move),
            "uom": move.product_uom.name if move.product_uom else "",
            "source_location_id": move.location_id.id if move.location_id else False,
            "source_location_name": move.location_id.display_name if move.location_id else "",
            "dest_location_id": move.location_dest_id.id if move.location_dest_id else False,
            "dest_location_name": move.location_dest_id.display_name if move.location_dest_id else "",
            "state": move.state,
        }

    def _receipt_read_done_qty(self, move):
        if "quantity" in move._fields:
            return move.quantity or 0.0
        if "quantity_done" in move._fields:
            return move.quantity_done or 0.0
        return 0.0

    def _receipt_product_summary(self, moves):
        products = moves.mapped("product_id")
        if not products:
            return ""
        first_name = products[:1].display_name
        return first_name if len(products) == 1 else f"{first_name} 等{len(products)}种商品"

    def _receipt_write_done_qty(self, move, qty):
        if "quantity" in move._fields:
            move.write({"quantity": qty})
            return
        if "quantity_done" in move._fields:
            move.write({"quantity_done": qty})
            return
        raise ValidationError("当前库存明细没有可写入的实收数量字段。")

    def _receipt_float_payload(self, payload, key):
        value = payload.get(key)
        if value in (None, ""):
            raise ValidationError("请填写实收数量。")
        return float(value)

    def _receipt_product_matches_barcode(self, product, barcode):
        return barcode in {product.barcode, product.default_code, product.product_tmpl_id.default_code}
