from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from .base import WmsPdaBaseController


class WmsPdaInboundController(WmsPdaBaseController):
    @http.route("/api/pda/wms/v1/inbound/tasks", type="http", auth="public", methods=["GET"], csrf=False)
    def list_inbound_tasks(self, **kwargs):
        payload = self._get_payload()
        return self._handle_request(lambda user, wh, token: self._inbound_list_tasks(user, wh, payload))

    @http.route(
        "/api/pda/wms/v1/inbound/arrival/<int:picking_id>/checkin",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def checkin_arrival(self, picking_id, **kwargs):
        payload = self._get_payload()
        return self._handle_idempotent_request(
            payload,
            lambda user, wh, token: self._inbound_checkin_arrival(user, wh, picking_id),
        )

    @http.route(
        "/api/pda/wms/v1/inbound/arrival/<int:picking_id>/cancel",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def cancel_arrival(self, picking_id, **kwargs):
        payload = self._get_payload()
        return self._handle_idempotent_request(
            payload,
            lambda user, wh, token: self._inbound_cancel_arrival(user, wh, picking_id),
        )

    def _inbound_list_tasks(self, user, warehouse, payload):
        if not warehouse:
            raise ValidationError("请先选择仓库。")
        stage = (payload.get("stage") or "arrival").strip()
        limit = min(int(payload.get("limit") or 50), 100)
        if stage == "arrival":
            arrival_status = (payload.get("arrival_status") or "unsigned").strip()
            return self._arrival_list_tasks(user, warehouse, arrival_status, limit)
        if stage == "done":
            records = (
                request.env["wms.putaway.task"]
                .with_user(user)
                .sudo()
                .search([("warehouse_id", "=", warehouse.id), ("state", "=", "putaway_done")], limit=limit, order="id desc")
            )
            return {"stage": stage, "records": [self._format_done_putaway(task) for task in records]}
        raise ValidationError("不支持的入库状态。")

    def _arrival_list_tasks(self, user, warehouse, arrival_status, limit):
        if arrival_status == "unsigned":
            records = self._arrival_pickings(user, warehouse, limit)
            return {
                "stage": "arrival",
                "arrival_status": arrival_status,
                "records": [self._format_arrival(picking, arrival_status="unsigned", state_label="未签到") for picking in records],
            }
        if arrival_status == "signed":
            records = (
                request.env["wms.receipt.task"]
                .with_user(user)
                .sudo()
                .search(
                    [
                        ("warehouse_id", "=", warehouse.id),
                        ("stock_picking_id", "!=", False),
                        ("stock_picking_id.picking_type_code", "=", "incoming"),
                        ("stock_picking_id.state", "!=", "cancel"),
                    ],
                    limit=limit,
                    order="id desc",
                )
            )
            return {
                "stage": "arrival",
                "arrival_status": arrival_status,
                "records": [self._format_signed_arrival(receipt) for receipt in records],
            }
        if arrival_status == "cancelled":
            records = (
                request.env["stock.picking"]
                .with_user(user)
                .sudo()
                .search(
                    [
                        ("picking_type_code", "=", "incoming"),
                        ("picking_type_id.warehouse_id", "=", warehouse.id),
                        ("state", "=", "cancel"),
                    ],
                    limit=limit,
                    order="write_date desc, id desc",
                )
            )
            return {
                "stage": "arrival",
                "arrival_status": arrival_status,
                "records": [
                    self._format_arrival(
                        picking,
                        arrival_status="cancelled",
                        state="arrival_cancelled",
                        state_label="已取消",
                    )
                    for picking in records
                ],
            }
        raise ValidationError("不支持的到货签到状态。")

    def _arrival_pickings(self, user, warehouse, limit):
        receipt_pickings = (
            request.env["wms.receipt.task"]
            .sudo()
            .search([("warehouse_id", "=", warehouse.id), ("stock_picking_id", "!=", False)])
            .mapped("stock_picking_id")
            .ids
        )
        putaway_pickings = (
            request.env["wms.putaway.task"]
            .sudo()
            .search([("warehouse_id", "=", warehouse.id), ("stock_picking_id", "!=", False)])
            .mapped("stock_picking_id")
            .ids
        )
        handled_picking_ids = list(set(receipt_pickings + putaway_pickings))
        domain = [
            ("picking_type_code", "=", "incoming"),
            ("picking_type_id.warehouse_id", "=", warehouse.id),
            ("state", "not in", ["done", "cancel"]),
        ]
        if handled_picking_ids:
            domain.append(("id", "not in", handled_picking_ids))
        return request.env["stock.picking"].with_user(user).sudo().search(domain, limit=limit, order="scheduled_date asc, id asc")

    def _inbound_checkin_arrival(self, user, warehouse, picking_id):
        picking = self._arrival_get_picking(user, warehouse, picking_id)
        if self._arrival_has_receipt_or_putaway(warehouse, picking):
            return self._error(self.ERR_STATE_CONFLICT, "当前到货单已签到，不能重复签到。", status=400, tts="已签到")
        if "erp_source_type" in picking._fields and not picking.erp_source_type:
            picking.write({"erp_source_type": "purchase"})
        receipt = request.env["wms.receipt.task"].sudo().create_from_picking(picking)
        return self._success(
            {
                "arrival": self._format_arrival(picking),
                "task": self._format_receipt_task(receipt),
                "next_step": "receipt",
            },
            tts="到货已签到",
        )

    def _inbound_cancel_arrival(self, user, warehouse, picking_id):
        picking = self._arrival_get_picking(user, warehouse, picking_id)
        if self._arrival_has_receipt_or_putaway(warehouse, picking):
            return self._error(self.ERR_STATE_CONFLICT, "当前到货单已签到，不能取消。", status=400, tts="已签到不能取消")
        picking.action_cancel()
        return self._success(
            {
                "arrival": self._format_arrival(
                    picking,
                    arrival_status="cancelled",
                    state="arrival_cancelled",
                    state_label="已取消",
                ),
                "next_step": "arrival",
            },
            tts="到货已取消",
        )

    def _arrival_has_receipt_or_putaway(self, warehouse, picking):
        if not picking:
            return False
        receipt_count = request.env["wms.receipt.task"].sudo().search_count(
            [
                ("warehouse_id", "=", warehouse.id),
                ("stock_picking_id", "=", picking.id),
            ]
        )
        putaway_count = request.env["wms.putaway.task"].sudo().search_count(
            [
                ("warehouse_id", "=", warehouse.id),
                ("stock_picking_id", "=", picking.id),
            ]
        )
        return bool(receipt_count or putaway_count)

    def _arrival_get_picking(self, user, warehouse, picking_id):
        domain = [
            ("id", "=", picking_id),
            ("picking_type_code", "=", "incoming"),
            ("picking_type_id.warehouse_id", "=", warehouse.id),
            ("state", "not in", ["done", "cancel"]),
        ]
        picking = request.env["stock.picking"].with_user(user).sudo().search(domain, limit=1)
        if not picking:
            raise ValidationError("待到货单不存在或不属于当前仓库。")
        return picking

    def _format_arrival(self, picking, arrival_status="unsigned", state="waiting_arrival", state_label="待到货"):
        moves = self._picking_moves(picking)
        return {
            "id": picking.id,
            "name": picking.origin or picking.name,
            "state": state,
            "state_label": state_label,
            "mode": "arrival",
            "arrival_status": arrival_status,
            "arrival_status_label": state_label,
            "picking_id": picking.id,
            "picking_name": picking.name,
            "partner_id": picking.partner_id.id if picking.partner_id else False,
            "partner_name": picking.partner_id.display_name if picking.partner_id else "",
            "warehouse_name": picking.picking_type_id.warehouse_id.display_name if picking.picking_type_id.warehouse_id else "",
            "source_location": picking.location_id.display_name if picking.location_id else "",
            "dest_location": picking.location_dest_id.display_name if picking.location_dest_id else "",
            "scheduled_date": picking.scheduled_date,
            "create_date": picking.create_date,
            "line_count": len(moves),
            "product_summary": self._product_summary(moves),
            "demand_qty": sum(moves.mapped("product_uom_qty")),
            "done_qty": 0.0,
            "lines": [self._format_arrival_line(move) for move in moves],
        }

    def _format_signed_arrival(self, receipt):
        picking = receipt.stock_picking_id
        moves = self._picking_moves(picking)
        demand_qty = sum(moves.mapped("product_uom_qty"))
        return {
            "id": receipt.id,
            "name": picking.origin or picking.name or receipt.name,
            "state": "arrival_signed",
            "state_label": "已签到",
            "mode": "arrival",
            "arrival_status": "signed",
            "arrival_status_label": "已签到",
            "receipt_task_id": receipt.id,
            "receipt_task_name": receipt.name,
            "receipt_state": receipt.state,
            "picking_id": picking.id if picking else False,
            "picking_name": picking.name if picking else "",
            "partner_id": receipt.partner_id.id if receipt.partner_id else False,
            "partner_name": receipt.partner_id.display_name if receipt.partner_id else "",
            "warehouse_name": receipt.warehouse_id.display_name if receipt.warehouse_id else "",
            "source_location": picking.location_id.display_name if picking and picking.location_id else "",
            "dest_location": picking.location_dest_id.display_name if picking and picking.location_dest_id else "",
            "scheduled_date": receipt.scheduled_date,
            "create_date": receipt.create_date,
            "line_count": len(moves),
            "product_summary": self._product_summary(moves),
            "demand_qty": demand_qty,
            "done_qty": demand_qty,
            "lines": [self._format_arrival_line(move) for move in moves],
        }

    def _format_done_putaway(self, task):
        moves = self._picking_moves(task.stock_picking_id)
        total_qty = sum(moves.mapped("product_uom_qty"))
        putaway_qty = sum(self._putaway_qty(task, move.product_id) for move in moves)
        return {
            "id": task.id,
            "name": task.name,
            "state": task.state,
            "state_label": "已完成",
            "mode": "inbound_done",
            "receipt_task_id": task.receipt_task_id.id if task.receipt_task_id else False,
            "receipt_task_name": task.receipt_task_id.name if task.receipt_task_id else "",
            "picking_id": task.stock_picking_id.id if task.stock_picking_id else False,
            "picking_name": task.stock_picking_id.name if task.stock_picking_id else "",
            "partner_name": task.receipt_task_id.partner_id.display_name if task.receipt_task_id and task.receipt_task_id.partner_id else "",
            "source_location": task.source_location_id.display_name if task.source_location_id else "",
            "dest_location": task.dest_location_id.display_name if task.dest_location_id else "",
            "create_date": task.create_date,
            "line_count": len(moves),
            "product_summary": self._product_summary(moves),
            "total_qty": total_qty,
            "putaway_qty": putaway_qty,
        }

    def _format_receipt_task(self, receipt):
        return {
            "id": receipt.id,
            "name": receipt.name,
            "state": receipt.state,
            "picking_id": receipt.stock_picking_id.id if receipt.stock_picking_id else False,
            "picking_name": receipt.stock_picking_id.name if receipt.stock_picking_id else "",
        }

    def _picking_moves(self, picking):
        if not picking:
            return request.env["stock.move"]
        moves = getattr(picking, "move_ids_without_package", False) or picking.move_ids
        return moves.filtered(lambda move: move.product_id)

    def _format_arrival_line(self, move):
        product = move.product_id
        return {
            "id": move.id,
            "product_id": product.id,
            "product_name": product.display_name,
            "default_code": product.default_code or "",
            "barcode": product.barcode or "",
            "demand_qty": move.product_uom_qty or 0.0,
            "done_qty": 0.0,
            "uom": move.product_uom.name if move.product_uom else "",
            "source_location": move.location_id.display_name if move.location_id else "",
            "dest_location": move.location_dest_id.display_name if move.location_dest_id else "",
            "state": move.state,
        }

    def _product_summary(self, moves):
        products = moves.mapped("product_id")
        if not products:
            return ""
        first_name = products[:1].display_name
        return first_name if len(products) == 1 else f"{first_name} 等{len(products)}种商品"

    def _putaway_qty(self, task, product):
        moves = request.env["stock.move"].sudo().search([("origin", "=", task.name), ("state", "=", "done")])
        product_moves = moves.filtered(lambda move: move.product_id.id == product.id)
        total = 0.0
        for move in product_moves:
            if "quantity" in move._fields:
                total += move.quantity or 0.0
            elif "quantity_done" in move._fields:
                total += move.quantity_done or 0.0
            else:
                total += move.product_uom_qty or 0.0
        return total
