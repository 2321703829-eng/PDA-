from odoo import http
from odoo.http import request


class B2bFrontend(http.Controller):

    def _get_cart(self):
        """获取当前用户的草稿购物车,没有就创建"""
        partner_id = request.env.user.partner_id.id
        cart = request.env["b2b.cart.draft"].sudo().search(
            [("partner_id", "=", partner_id), ("state", "=", "draft")], limit=1)
        if not cart:
            cart = request.env["b2b.cart.draft"].sudo().create({"partner_id": partner_id})
        return cart

    def _get_cart_values(self, cart):
        lines = []
        total_qty = 0
        total_amount = 0.0
        for l in cart.line_ids:
            subtotal = l.qty * l.unit_price
            total_qty += l.qty
            total_amount += subtotal
            lines.append({"id": l.id, "product_id": l.product_id.id,
                          "product_name": l.product_id.name,
                          "qty": int(l.qty), "unit_price": l.unit_price,
                          "subtotal": subtotal})
        return {"lines": lines, "total_qty": total_qty, "total_amount": total_amount}

    # ========== 商品列表页 ==========
    @http.route("/b2b/products", type="http", auth="user", website=True)
    def product_list(self, **kw):
        domain = [("is_b2b_visible", "=", True)]
        if kw.get("keyword"):
            domain.append(("name", "ilike", kw["keyword"]))
        if kw.get("category_id"):
            domain.append(("categ_id", "=", int(kw["category_id"])))
        products = request.env["product.template"].sudo().search(domain, limit=40)
        categories = request.env["product.category"].sudo().search([], limit=20)
        cart = self._get_cart()
        cv = self._get_cart_values(cart)
        return request.render("b2b_storefront.product_list_page", {
            "products": products,
            "categories": categories,
            "keyword": kw.get("keyword", ""),
            "cart_count": cv["total_qty"],
        })

    # ========== 加入购物车 ==========
    @http.route("/b2b/cart/add", type="http", auth="user", website=True, methods=["POST"], csrf=False)
    def cart_add(self, **kw):
        product_id = int(kw.get("product_id", 0))
        qty = float(kw.get("qty", 1))
        if qty < 1:
            qty = 1
        if product_id:
            cart = self._get_cart()
            product = request.env["product.template"].sudo().browse(product_id)
            existing = cart.line_ids.filtered(lambda l: l.product_id.id == product_id)
            if existing:
                existing.qty += qty
            else:
                request.env["b2b.cart.draft.line"].sudo().create({
                    "cart_id": cart.id, "product_id": product_id,
                    "qty": qty, "unit_price": product.list_price,
                })
        return request.redirect("/b2b/products?added=1")

    # ========== 购物车页 ==========
    @http.route("/b2b/cart", type="http", auth="user", website=True)
    def cart_page(self, **kw):
        cart = self._get_cart()
        cv = self._get_cart_values(cart)
        stores = request.env["res.partner"].sudo().search([("is_b2b_store", "=", True)])
        return request.render("b2b_storefront.cart_page", {
            "cart": cart, "stores": stores,
            "lines": cv["lines"], "total_qty": cv["total_qty"],
            "total_amount": cv["total_amount"],
        })

    # ========== 更新购物车数量 ==========
    @http.route("/b2b/cart/update", type="http", auth="user", website=True, methods=["POST"], csrf=False)
    def cart_update(self, **kw):
        line_id = int(kw.get("line_id", 0))
        qty = float(kw.get("qty", 0))
        action = kw.get("action", "")  # "delete" 直接删除
        if line_id:
            line = request.env["b2b.cart.draft.line"].sudo().browse(line_id)
            if action == "delete" or qty <= 0:
                line.unlink()
            elif qty > 0 and line.exists():
                line.qty = min(qty, 9999)
        return request.redirect("/b2b/cart")

    # ========== 更新购物车门 ==========
    @http.route("/b2b/cart/set-store", type="http", auth="user", website=True, methods=["POST"], csrf=False)
    def cart_set_store(self, **kw):
        store_id = int(kw.get("store_id", 0))
        cart = self._get_cart()
        if store_id:
            cart.store_id = store_id
        return request.redirect("/b2b/cart")

    # ========== 清空购物车 ==========
    @http.route("/b2b/cart/clear", type="http", auth="user", website=True, methods=["POST"], csrf=False)
    def cart_clear(self, **kw):
        cart = self._get_cart()
        cart.line_ids.unlink()
        return request.redirect("/b2b/cart")

    # ========== 下单页 ==========
    @http.route("/b2b/checkout", type="http", auth="user", website=True)
    def checkout_page(self, **kw):
        cart = self._get_cart()
        if not cart.line_ids:
            return request.redirect("/b2b/cart")
        cv = self._get_cart_values(cart)
        stores = request.env["res.partner"].sudo().search([("is_b2b_store", "=", True)])
        partner = request.env.user.partner_id
        return request.render("b2b_storefront.checkout_page", {
            "cart": cart, "stores": stores, "partner": partner,
            "lines": cv["lines"], "total_amount": cv["total_amount"],
            "total_qty": cv["total_qty"],
            "payment_method": partner.b2b_payment_method_default or "credit",
        })

    # ========== 提交订单 ==========
    @http.route("/b2b/orders/submit", type="http", auth="user", website=True, methods=["POST"], csrf=False)
    def order_submit(self, **kw):
        partner_id = request.env.user.partner_id.id
        cart = request.env["b2b.cart.draft"].sudo().search(
            [("partner_id", "=", partner_id), ("state", "=", "draft")], limit=1)
        if not cart or not cart.line_ids:
            return request.redirect("/b2b/cart")
        store_id = int(kw.get("store_id", 0))
        if not store_id:
            return request.render("b2b_storefront.checkout_page", {
                "error": "请选择收货门店", "cart": cart,
                "lines": self._get_cart_values(cart)["lines"],
                "total_amount": self._get_cart_values(cart)["total_amount"],
                "total_qty": self._get_cart_values(cart)["total_qty"],
                "stores": request.env["res.partner"].sudo().search([("is_b2b_store", "=", True)]),
                "partner": request.env.user.partner_id,
                "payment_method": kw.get("payment_method", "credit"),
            })
        # 先标记避免重复提交
        cart.write({"state": "submitted"})
        try:
            order_lines = []
            for l in cart.line_ids:
                variant = l.product_id.product_variant_id
                order_lines.append((0, 0, {
                    "product_template_id": l.product_id.id,
                    "product_id": variant.id if variant else False,
                    "product_uom_qty": l.qty,
                    "price_unit": l.unit_price,
                }))
            order = request.env["sale.order"].sudo().create({
                "partner_id": partner_id,
                "source_channel": "b2b",
                "store_partner_id": store_id,
                "b2b_payment_method": kw.get("payment_method", "credit"),
                "b2b_submit_note": kw.get("note", ""),
                "b2b_submit_user_id": request.env.user.id,
                "delivery_time_required": kw.get("delivery_time_required", ""),
                "order_line": order_lines,
            })
            cart.write({"state": "converted"})
            return request.redirect("/b2b/orders/%s" % order.id)
        except Exception as e:
            cart.write({"state": "draft"})
            return request.render("b2b_storefront.checkout_page", {
                "error": "提交失败: %s" % str(e),
                "cart": cart,
                "lines": self._get_cart_values(cart)["lines"],
                "total_amount": self._get_cart_values(cart)["total_amount"],
                "total_qty": self._get_cart_values(cart)["total_qty"],
                "stores": request.env["res.partner"].sudo().search([("is_b2b_store", "=", True)]),
                "partner": request.env.user.partner_id,
                "payment_method": kw.get("payment_method", "credit"),
            })

    # ========== 订单列表页 ==========
    @http.route("/b2b/orders", type="http", auth="user", website=True)
    def order_list(self, **kw):
        partner_id = request.env.user.partner_id.id
        orders = request.env["sale.order"].sudo().search(
            [("partner_id", "=", partner_id), ("source_channel", "=", "b2b")],
            order="create_date desc", limit=30)
        cart = self._get_cart()
        cv = self._get_cart_values(cart)
        return request.render("b2b_storefront.order_list_page", {
            "orders": orders, "cart_count": cv["total_qty"],
        })

    # ========== 订单详情页 ==========
    @http.route("/b2b/orders/<int:order_id>", type="http", auth="user", website=True)
    def order_detail(self, order_id, **kw):
        order = request.env["sale.order"].sudo().browse(order_id)
        if not order.exists() or order.partner_id.id != request.env.user.partner_id.id:
            return request.not_found()
        return request.render("b2b_storefront.order_detail_page", {
            "order": order,
            "wms_status": order.wms_status if hasattr(order, "wms_status") else "",
            "tms_status": order.tms_status if hasattr(order, "tms_status") else "",
        })

    # ========== 售后提交 ==========
    @http.route("/b2b/after-sale/submit", type="http", auth="user", website=True, methods=["POST"], csrf=False)
    def after_sale_submit(self, **kw):
        order_id = int(kw.get("order_id", 0))
        ticket_type = kw.get("ticket_type", "other")
        description = kw.get("description", "")
        if order_id:
            order = request.env["sale.order"].sudo().browse(order_id)
            if order.exists() and order.partner_id.id == request.env.user.partner_id.id:
                request.env["b2b.after.sale.ticket"].sudo().create({
                    "name": "售后-%s" % order.name,
                    "order_id": order_id,
                    "partner_id": request.env.user.partner_id.id,
                    "ticket_type": ticket_type,
                    "description": description,
                })
        return request.redirect("/b2b/orders/%s" % order_id)
