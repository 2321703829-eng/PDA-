from odoo import http
from odoo.http import request


class B2bFrontend(http.Controller):

    # ========== 商品列表页 ==========
    @http.route("/b2b/products", type="http", auth="user", website=True)
    def b2b_product_list_page(self, **kw):
        domain = [("is_b2b_visible", "=", True)]
        if kw.get("keyword"):
            domain.append(("name", "ilike", kw["keyword"]))
        if kw.get("category_id"):
            domain.append(("categ_id", "=", int(kw["category_id"])))
        products = request.env["product.template"].sudo().search(domain, limit=40)
        categories = request.env["product.category"].sudo().search([], limit=20)
        cart = request.env["b2b.cart.draft"].sudo().search(
            [("partner_id", "=", request.env.user.partner_id.id), ("state", "=", "draft")], limit=1)
        cart_count = sum(l.qty for l in cart.line_ids) if cart else 0
        values = {
            "products": products,
            "categories": categories,
            "keyword": kw.get("keyword", ""),
            "cart_count": int(cart_count),
        }
        return request.render("b2b_storefront.product_list_page", values)

    # ========== 购物车页 ==========
    @http.route("/b2b/cart", type="http", auth="user", website=True)
    def b2b_cart_page(self, **kw):
        partner_id = request.env.user.partner_id.id
        cart = request.env["b2b.cart.draft"].sudo().search(
            [("partner_id", "=", partner_id), ("state", "=", "draft")], limit=1)
        stores = request.env["res.partner"].sudo().search([("is_b2b_store", "=", True)])
        lines = []
        total = 0
        if cart:
            for l in cart.line_ids:
                lines.append({"id": l.id, "product": l.product_id, "qty": int(l.qty), "unit_price": l.unit_price, "subtotal": l.subtotal})
                total += l.subtotal
        values = {"cart": cart, "lines": lines, "stores": stores, "total_amount": total, "total_qty": sum(l["qty"] for l in lines)}
        return request.render("b2b_storefront.cart_page", values)

    # ========== 下单页 ==========
    @http.route("/b2b/checkout", type="http", auth="user", website=True)
    def b2b_checkout_page(self, **kw):
        partner_id = request.env.user.partner_id.id
        partner = request.env["res.partner"].sudo().browse(partner_id)
        cart = request.env["b2b.cart.draft"].sudo().search(
            [("partner_id", "=", partner_id), ("state", "=", "draft")], limit=1)
        if not cart or not cart.line_ids:
            return request.redirect("/b2b/cart")
        stores = request.env["res.partner"].sudo().search([("is_b2b_store", "=", True)])
        lines = []
        total = 0
        for l in cart.line_ids:
            lines.append({"product": l.product_id, "qty": int(l.qty), "unit_price": l.unit_price, "subtotal": l.subtotal})
            total += l.subtotal
        values = {"cart": cart, "lines": lines, "stores": stores, "total_amount": total, "partner": partner, "payment_method": partner.b2b_payment_method_default or "credit"}
        return request.render("b2b_storefront.checkout_page", values)

    # ========== 订单查询页 ==========
    @http.route("/b2b/orders", type="http", auth="user", website=True)
    def b2b_order_list_page(self, **kw):
        partner_id = request.env.user.partner_id.id
        domain = [("partner_id", "=", partner_id), ("source_channel", "=", "b2b")]
        orders = request.env["sale.order"].sudo().search(domain, order="create_date desc", limit=30)
        values = {"orders": orders}
        return request.render("b2b_storefront.order_list_page", values)

    # ========== 订单详情页 ==========
    @http.route("/b2b/orders/<int:order_id>", type="http", auth="user", website=True)
    def b2b_order_detail_page(self, order_id, **kw):
        order = request.env["sale.order"].sudo().browse(order_id)
        if not order or order.partner_id.id != request.env.user.partner_id.id:
            return request.not_found()
        values = {"order": order}
        return request.render("b2b_storefront.order_detail_page", values)

    # ========== 提交订单(HTML表单提交) ==========
    @http.route("/b2b/orders/submit", type="http", auth="user", website=True, methods=["POST"], csrf=False)
    def b2b_order_submit_page(self, **kw):
        partner_id = request.env.user.partner_id.id
        cart = request.env["b2b.cart.draft"].sudo().search(
            [("partner_id", "=", partner_id), ("state", "=", "draft")], limit=1)
        if not cart or not cart.line_ids:
            return request.redirect("/b2b/cart")
        store_id = int(kw.get("store_id", 0))
        payment_method = kw.get("payment_method", "credit")
        note = kw.get("note", "")
        delivery_time = kw.get("delivery_time_required", "")
        order_lines = []
        for l in cart.line_ids:
            order_lines.append((0, 0, {
                "product_template_id": l.product_id.id,
                "product_id": l.product_id.product_variant_id.id,
                "product_uom_qty": l.qty,
                "price_unit": l.unit_price,
            }))
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
        cart.write({"state": "converted"})
        return request.redirect("/b2b/orders/%s" % order.id)

    # ========== 加购(HTML表单, 从商品列表页提交) ==========
    @http.route("/b2b/cart/add", type="http", auth="user", website=True, methods=["POST"], csrf=False)
    def b2b_cart_add_page(self, **kw):
        partner_id = request.env.user.partner_id.id
        product_id = int(kw.get("product_id", 0))
        qty = float(kw.get("qty", 1))
        if product_id:
            cart = request.env["b2b.cart.draft"].sudo().search(
                [("partner_id", "=", partner_id), ("state", "=", "draft")], limit=1)
            if not cart:
                cart = request.env["b2b.cart.draft"].sudo().create({"partner_id": partner_id})
            product = request.env["product.template"].sudo().browse(product_id)
            existing = cart.line_ids.filtered(lambda l: l.product_id.id == product_id)
            if existing:
                existing.qty += qty
            else:
                request.env["b2b.cart.draft.line"].sudo().create({
                    "cart_id": cart.id, "product_id": product_id,
                    "qty": qty, "unit_price": product.list_price,
                })
        return request.redirect("/b2b/products")

    # ========== 购物车操作(HTML表单) ==========
    @http.route("/b2b/cart/update", type="http", auth="user", website=True, methods=["POST"], csrf=False)
    def b2b_cart_update_page(self, **kw):
        cart_id = int(kw.get("cart_id", 0))
        line_id = int(kw.get("line_id", 0))
        qty = float(kw.get("qty", 0))
        if cart_id:
            if line_id and qty > 0:
                request.env["b2b.cart.draft.line"].sudo().browse(line_id).write({"qty": qty})
            elif line_id and qty <= 0:
                request.env["b2b.cart.draft.line"].sudo().browse(line_id).unlink()
        return request.redirect("/b2b/cart")

    @http.route("/b2b/cart/clear", type="http", auth="user", website=True, methods=["POST"], csrf=False)
    def b2b_cart_clear_page(self, **kw):
        partner_id = request.env.user.partner_id.id
        cart = request.env["b2b.cart.draft"].sudo().search(
            [("partner_id", "=", partner_id), ("state", "=", "draft")], limit=1)
        if cart:
            cart.line_ids.unlink()
        return request.redirect("/b2b/cart")

    # ========== 售后提交(HTML表单) ==========
    @http.route("/b2b/after-sale/submit", type="http", auth="user", website=True, methods=["POST"], csrf=False)
    def b2b_after_sale_submit_page(self, **kw):
        order_id = int(kw.get("order_id", 0))
        ticket_type = kw.get("ticket_type", "other")
        description = kw.get("description", "")
        if order_id:
            request.env["b2b.after.sale.ticket"].sudo().create({
                "name": "售后-" + str(order_id),
                "order_id": order_id,
                "partner_id": request.env.user.partner_id.id,
                "ticket_type": ticket_type,
                "description": description,
            })
        return request.redirect("/b2b/orders/%s" % order_id)
