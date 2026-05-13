import json
from odoo import http
from odoo.http import request


class B2bApi(http.Controller):

    # ========== B01: 商品列表接口 ==========
    @http.route("/api/open/logistics/b2b/products", type="http", auth="user", methods=["GET"], csrf=False)
    def b2b_products(self, **kw):
        domain = [("is_b2b_visible", "=", True), ("is_active_sale", "=", True)]
        if kw.get("keyword"):
            domain.append(("name", "ilike", kw["keyword"]))
        if kw.get("category_id"):
            domain.append(("categ_id", "=", int(kw["category_id"])))
        products = request.env["product.template"].sudo().search(domain, offset=int(kw.get("offset", 0)), limit=int(kw.get("limit", 20)))
        data = [{"id": p.id, "name": p.name, "list_price": p.list_price, "b2b_min_qty": p.b2b_min_qty, "b2b_saleable_desc": p.b2b_saleable_desc, "default_code": p.default_code} for p in products]
        return request.make_response(json.dumps({"ok": True, "data": data}), headers=[("Content-Type", "application/json")])

    # ========== B04: 购物车接口 ==========
    @http.route("/api/open/logistics/b2b/cart", type="http", auth="user", methods=["GET"], csrf=False)
    def b2b_cart_get(self, **kw):
        partner_id = request.env.user.partner_id.id
        cart = request.env["b2b.cart.draft"].sudo().search([("partner_id", "=", partner_id), ("state", "=", "draft")], limit=1)
        if not cart:
            return request.make_response(json.dumps({"ok": True, "data": {"lines": [], "total_amount": 0, "total_qty": 0}}), headers=[("Content-Type", "application/json")])
        lines = [{"id": l.id, "product_id": l.product_id.id, "product_name": l.product_id.name, "qty": l.qty, "unit_price": l.unit_price, "subtotal": l.subtotal} for l in cart.line_ids]
        return request.make_response(json.dumps({"ok": True, "data": {"id": cart.id, "store_id": cart.store_id.id, "lines": lines, "total_amount": cart.total_amount, "total_qty": cart.total_qty}}), headers=[("Content-Type", "application/json")])

    @http.route("/api/open/logistics/b2b/cart/add", type="http", auth="user", methods=["POST"], csrf=False)
    def b2b_cart_add(self, **kw):
        body = request.httprequest.get_json(silent=True) or {}
        partner_id = request.env.user.partner_id.id
        product_id = int(body.get("product_id", 0))
        qty = float(body.get("qty", 1))
        if not product_id:
            return request.make_response(json.dumps({"ok": False, "message": "product_id required"}), headers=[("Content-Type", "application/json")])
        cart = request.env["b2b.cart.draft"].sudo().search([("partner_id", "=", partner_id), ("state", "=", "draft")], limit=1)
        if not cart:
            cart = request.env["b2b.cart.draft"].sudo().create({"partner_id": partner_id})
        product = request.env["product.template"].sudo().browse(product_id)
        existing = cart.line_ids.filtered(lambda l: l.product_id.id == product_id)
        if existing:
            existing.qty += qty
        else:
            request.env["b2b.cart.draft.line"].sudo().create({"cart_id": cart.id, "product_id": product_id, "qty": qty, "unit_price": product.list_price})
        return request.make_response(json.dumps({"ok": True}), headers=[("Content-Type", "application/json")])

    @http.route("/api/open/logistics/b2b/cart/update", type="http", auth="user", methods=["POST"], csrf=False)
    def b2b_cart_update(self, **kw):
        body = request.httprequest.get_json(silent=True) or {}
        line_id = int(body.get("line_id", 0))
        qty = float(body.get("qty", 0))
        if line_id and qty > 0:
            request.env["b2b.cart.draft.line"].sudo().browse(line_id).write({"qty": qty})
        elif line_id and qty <= 0:
            request.env["b2b.cart.draft.line"].sudo().browse(line_id).unlink()
        return request.make_response(json.dumps({"ok": True}), headers=[("Content-Type", "application/json")])

    @http.route("/api/open/logistics/b2b/cart/clear", type="http", auth="user", methods=["POST"], csrf=False)
    def b2b_cart_clear(self, **kw):
        partner_id = request.env.user.partner_id.id
        cart = request.env["b2b.cart.draft"].sudo().search([("partner_id", "=", partner_id), ("state", "=", "draft")], limit=1)
        if cart:
            cart.line_ids.unlink()
        return request.make_response(json.dumps({"ok": True}), headers=[("Content-Type", "application/json")])

    # ========== C01 + C02: 下单确认与提交 ==========
    @http.route("/api/open/logistics/b2b/checkout", type="http", auth="user", methods=["GET"], csrf=False)
    def b2b_checkout(self, **kw):
        partner_id = request.env.user.partner_id.id
        partner = request.env["res.partner"].sudo().browse(partner_id)
        cart = request.env["b2b.cart.draft"].sudo().search([("partner_id", "=", partner_id), ("state", "=", "draft")], limit=1)
        if not cart or not cart.line_ids:
            return request.make_response(json.dumps({"ok": False, "message": "购物车为空"}), headers=[("Content-Type", "application/json")])
        stores = request.env["res.partner"].sudo().search([("is_b2b_store", "=", True)])
        return request.make_response(json.dumps({"ok": True, "data": {"cart_id": cart.id, "total_amount": cart.total_amount, "total_qty": cart.total_qty, "store_id": cart.store_id.id, "stores": [{"id": s.id, "name": s.name} for s in stores], "payment_method": partner.b2b_payment_method_default or "credit"}}), headers=[("Content-Type", "application/json")])

    @http.route("/api/open/logistics/b2b/orders/submit", type="http", auth="user", methods=["POST"], csrf=False)
    def b2b_order_submit(self, **kw):
        body = request.httprequest.get_json(silent=True) or {}
        partner_id = request.env.user.partner_id.id
        cart = request.env["b2b.cart.draft"].sudo().search([("partner_id", "=", partner_id), ("state", "=", "draft")], limit=1)
        if not cart or not cart.line_ids:
            return request.make_response(json.dumps({"ok": False, "message": "购物车为空"}), headers=[("Content-Type", "application/json")])
        store_id = int(body.get("store_id", 0))
        payment_method = body.get("payment_method", "credit")
        note = body.get("note", "")
        delivery_time = body.get("delivery_time", "")
        order_lines = [(0, 0, {"product_template_id": l.product_id.id, "product_id": l.product_id.product_variant_id.id, "product_uom_qty": l.qty, "price_unit": l.unit_price}) for l in cart.line_ids]
        order = request.env["sale.order"].sudo().create({
            "partner_id": partner_id,
            "source_channel": "b2b",
            "store_partner_id": store_id or None,
            "b2b_payment_method": payment_method,
            "b2b_submit_note": note,
            "b2b_submit_user_id": request.env.user.id,
            "delivery_time_required": delivery_time,
            "order_line": order_lines,
        })
        cart.write({"state": "submitted"})
        return request.make_response(json.dumps({"ok": True, "data": {"order_id": order.id, "order_name": order.name}}), headers=[("Content-Type", "application/json")])

    # ========== D01 + D02: 订单查询 ==========
    @http.route("/api/open/logistics/b2b/orders", type="http", auth="user", methods=["GET"], csrf=False)
    def b2b_orders(self, **kw):
        partner_id = request.env.user.partner_id.id
        domain = [("partner_id", "=", partner_id), ("source_channel", "=", "b2b")]
        if kw.get("state"):
            domain.append(("state", "=", kw["state"]))
        orders = request.env["sale.order"].sudo().search(domain, offset=int(kw.get("offset", 0)), limit=int(kw.get("limit", 20)), order="create_date desc")
        data = [{"id": o.id, "name": o.name, "state": o.state, "amount_total": o.amount_total, "store_name": o.store_partner_id.name, "create_date": str(o.create_date)} for o in orders]
        return request.make_response(json.dumps({"ok": True, "data": data}), headers=[("Content-Type", "application/json")])

    @http.route("/api/open/logistics/b2b/orders/<int:order_id>", type="http", auth="user", methods=["GET"], csrf=False)
    def b2b_order_detail(self, order_id, **kw):
        order = request.env["sale.order"].sudo().browse(order_id)
        if not order or order.partner_id.id != request.env.user.partner_id.id:
            return request.make_response(json.dumps({"ok": False, "message": "not found"}), headers=[("Content-Type", "application/json")])
        lines = [{"product_name": l.product_id.name, "qty": l.product_uom_qty, "price_unit": l.price_unit, "subtotal": l.price_subtotal} for l in order.order_line]
        data = {"id": order.id, "name": order.name, "state": order.state, "amount_total": order.amount_total, "store_name": order.store_partner_id.name, "delivery_time_required": order.delivery_time_required, "b2b_payment_method": order.b2b_payment_method, "b2b_submit_note": order.b2b_submit_note, "source_channel": order.source_channel, "wms_status": order.wms_status if hasattr(order, 'wms_status') else "", "tms_status": order.tms_status if hasattr(order, 'tms_status') else "", "lines": lines}
        return request.make_response(json.dumps({"ok": True, "data": data}), headers=[("Content-Type", "application/json")])

    # ========== E02: 售后提交 ==========
    @http.route("/api/open/logistics/b2b/after-sale", type="http", auth="user", methods=["POST"], csrf=False)
    def b2b_after_sale(self, **kw):
        body = request.httprequest.get_json(silent=True) or {}
        order_id = int(body.get("order_id", 0))
        ticket_type = body.get("ticket_type", "other")
        description = body.get("description", "")
        if not order_id:
            return request.make_response(json.dumps({"ok": False, "message": "order_id required"}), headers=[("Content-Type", "application/json")])
        ticket = request.env["b2b.after.sale.ticket"].sudo().create({
            "name": "售后-" + str(order_id),
            "order_id": order_id,
            "partner_id": request.env.user.partner_id.id,
            "ticket_type": ticket_type,
            "description": description,
        })
        return request.make_response(json.dumps({"ok": True, "data": {"ticket_id": ticket.id}}), headers=[("Content-Type", "application/json")])
