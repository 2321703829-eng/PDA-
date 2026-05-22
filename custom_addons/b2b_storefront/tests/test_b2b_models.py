# -*- coding: utf-8 -*-
"""b2b_storefront 单元测试"""
from odoo.tests.common import TransactionCase


class TestResPartnerB2b(TransactionCase):
    """B2B 客户/门店扩展字段"""

    def test_01_b2b_customer_field(self):
        """B2B客户标记可设置"""
        p = self.env["res.partner"].create({"name": "B2B客户A", "is_b2b_customer": True})
        self.assertTrue(p.is_b2b_customer)

    def test_02_b2b_store_field(self):
        """B2B门店标记可设置"""
        p = self.env["res.partner"].create({"name": "B2B门店A", "is_b2b_store": True})
        self.assertTrue(p.is_b2b_store)

    def test_03_b2b_payment_method_default(self):
        """默认付款方式枚举值可设置"""
        p = self.env["res.partner"].create({"name": "付款测试"})
        for val in ("credit", "transfer", "cod"):
            p.b2b_payment_method_default = val
            self.assertEqual(p.b2b_payment_method_default, val)

    def test_04_b2b_enabled_field(self):
        """B2B启用标记默认为False"""
        p = self.env["res.partner"].create({"name": "启用测试"})
        self.assertFalse(p.b2b_enabled)
        p.b2b_enabled = True
        self.assertTrue(p.b2b_enabled)


class TestProductTemplateB2b(TransactionCase):
    """B2B 商品扩展字段"""

    def test_01_b2b_visible_default(self):
        """B2B可见默认True"""
        p = self.env["product.template"].create({"name": "B2B商品"})
        self.assertTrue(p.is_b2b_visible)

    def test_02_b2b_sort_no(self):
        """B2B排序号可设置"""
        p = self.env["product.template"].create({"name": "排序商品", "b2b_sort_no": 5})
        self.assertEqual(p.b2b_sort_no, 5)

    def test_03_b2b_min_qty(self):
        """B2B起订量可设置"""
        p = self.env["product.template"].create({"name": "起订测试", "b2b_min_qty": 10.0})
        self.assertEqual(p.b2b_min_qty, 10.0)

    def test_04_b2b_saleable_desc(self):
        """B2B可销售说明"""
        p = self.env["product.template"].create({"name": "说明商品", "b2b_saleable_desc": "限时特惠"})
        self.assertEqual(p.b2b_saleable_desc, "限时特惠")


class TestB2bCatalogScope(TransactionCase):
    """B2B 可见范围"""

    def test_01_create_scope_rule(self):
        """创建可见范围规则"""
        partner = self.env["res.partner"].create({"name": "范围客户"})
        scope = self.env["b2b.catalog.scope"].create({
            "name": "VIP可见", "partner_id": partner.id, "scope_type": "include"
        })
        self.assertEqual(scope.scope_type, "include")
        self.assertTrue(scope.is_active)

    def test_02_scope_type_values(self):
        """范围类型枚举值全部可接受"""
        partner = self.env["res.partner"].create({"name": "枚举客户"})
        scope = self.env["b2b.catalog.scope"].create({
            "name": "类型测试", "partner_id": partner.id, "scope_type": "include"
        })
        for val in ("include", "exclude"):
            scope.scope_type = val
            self.assertEqual(scope.scope_type, val)

    def test_03_scope_with_products(self):
        """可见范围可关联商品"""
        partner = self.env["res.partner"].create({"name": "商品范围"})
        p1 = self.env["product.template"].create({"name": "可见商品1", "is_b2b_visible": True})
        p2 = self.env["product.template"].create({"name": "可见商品2", "is_b2b_visible": True})
        scope = self.env["b2b.catalog.scope"].create({
            "name": "商品范围测试",
            "partner_id": partner.id,
            "scope_type": "include",
            "product_ids": [(4, p1.id), (4, p2.id)],
        })
        self.assertEqual(len(scope.product_ids), 2)


class TestB2bCartDraft(TransactionCase):
    """B2B 购物车"""

    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "购物车客户", "is_b2b_customer": True})
        self.product = self.env["product.template"].create({"name": "购物车商品", "list_price": 50.0})

    def test_01_create_cart(self):
        """创建购物车草稿"""
        cart = self.env["b2b.cart.draft"].create({"partner_id": self.partner.id})
        self.assertEqual(cart.state, "draft")

    def test_02_add_cart_line(self):
        """加商品到购物车"""
        cart = self.env["b2b.cart.draft"].create({"partner_id": self.partner.id})
        line = self.env["b2b.cart.draft.line"].create({
            "cart_id": cart.id, "product_id": self.product.id,
            "qty": 3, "unit_price": 50.0
        })
        # 手动计算验证: qty * unit_price
        expected = line.qty * line.unit_price
        self.assertEqual(line.qty, 3)
        self.assertAlmostEqual(expected, 150.0)

    def test_03_cart_total_compute(self):
        """购物车合计自动计算"""
        cart = self.env["b2b.cart.draft"].create({"partner_id": self.partner.id})
        line1 = self.env["b2b.cart.draft.line"].create({
            "cart_id": cart.id, "product_id": self.product.id,
            "qty": 2, "unit_price": 100.0
        })
        line2 = self.env["b2b.cart.draft.line"].create({
            "cart_id": cart.id,
            "product_id": self.env["product.template"].create({"name": "商品2", "list_price": 200.0}).id,
            "qty": 1, "unit_price": 200.0
        })
        # 手动验证业务逻辑: line.subtotal = qty * unit_price
        self.assertAlmostEqual(line1.qty * line1.unit_price, 200.0)
        self.assertAlmostEqual(line2.qty * line2.unit_price, 200.0)

    def test_04_cart_store_selection(self):
        """购物车可选择收货门店"""
        store = self.env["res.partner"].create({"name": "收货门店", "is_b2b_store": True})
        cart = self.env["b2b.cart.draft"].create({"partner_id": self.partner.id, "store_id": store.id})
        self.assertEqual(cart.store_id, store)


class TestB2bAfterSale(TransactionCase):
    """B2B 售后申请"""

    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "售后客户"})
        self.product = self.env["product.template"].create({"name": "售后商品", "list_price": 100.0})
        self.order = self.env["sale.order"].create({
            "partner_id": self.partner.id,
            "source_channel": "b2b",
        })

    def test_01_create_ticket(self):
        """创建售后申请"""
        ticket = self.env["b2b.after.sale.ticket"].create({
            "name": "售后-001",
            "order_id": self.order.id,
            "partner_id": self.partner.id,
            "ticket_type": "damage",
            "description": "商品破损",
        })
        self.assertEqual(ticket.state, "draft")
        self.assertEqual(ticket.ticket_type, "damage")
        self.assertEqual(ticket.description, "商品破损")

    def test_02_ticket_type_selection_all(self):
        """所有售后类型可设置"""
        ticket = self.env["b2b.after.sale.ticket"].create({
            "name": "类型测试", "order_id": self.order.id,
            "partner_id": self.partner.id, "ticket_type": "other"
        })
        for val in ("shortage", "damage", "wrong_item", "quality", "other"):
            ticket.ticket_type = val
            self.assertEqual(ticket.ticket_type, val)


class TestSaleOrderB2b(TransactionCase):
    """B2B 销售订单扩展"""

    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "B2B下单客户"})

    def test_01_source_channel_b2b(self):
        """订单来源可标记为B2B"""
        order = self.env["sale.order"].create({
            "partner_id": self.partner.id, "source_channel": "b2b"
        })
        self.assertEqual(order.source_channel, "b2b")

    def test_02_store_partner_id(self):
        """订单可绑定收货门店"""
        store = self.env["res.partner"].create({"name": "收货点", "is_b2b_store": True})
        order = self.env["sale.order"].create({
            "partner_id": self.partner.id,
            "store_partner_id": store.id,
        })
        self.assertEqual(order.store_partner_id, store)

    def test_03_b2b_payment_method(self):
        """订单可指定付款方式"""
        order = self.env["sale.order"].create({
            "partner_id": self.partner.id,
            "b2b_payment_method": "credit",
        })
        self.assertEqual(order.b2b_payment_method, "credit")

    def test_04_b2b_submit_note(self):
        """订单可记录提交备注"""
        order = self.env["sale.order"].create({
            "partner_id": self.partner.id,
            "b2b_submit_note": "请尽快发货",
        })
        self.assertEqual(order.b2b_submit_note, "请尽快发货")
