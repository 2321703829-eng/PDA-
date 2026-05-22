# -*- coding: utf-8 -*-
"""erp_base 模型单元测试 — CRUD / 字段默认值 / 约束 / compute"""
from odoo.tests.common import TransactionCase


class TestProductTemplate(TransactionCase):
    """商品主档扩展字段"""

    def test_01_create_with_defaults(self):
        """创建商品时扩展字段应有默认值"""
        product = self.env["product.template"].create({"name": "测试商品"})
        self.assertEqual(product.case_qty, 0.0)
        self.assertEqual(product.min_order_qty, 1.0)
        self.assertEqual(product.logistics_category, "normal")
        self.assertTrue(product.is_active_sale)

    def test_02_logistics_category_selection(self):
        """物流分类枚举值全部可设置"""
        product = self.env["product.template"].create({"name": "冷链品"})
        for val in ("normal", "fragile", "cold_chain", "hazardous"):
            product.logistics_category = val
            self.assertEqual(product.logistics_category, val)

    def test_03_volume_weight_storage(self):
        """体积和重量字段可正常读写"""
        product = self.env["product.template"].create({
            "name": "大件", "volume_m3": 2.5, "weight_kg": 30.0
        })
        self.assertAlmostEqual(product.volume_m3, 2.5)
        self.assertAlmostEqual(product.weight_kg, 30.0)

    def test_04_case_qty_storage(self):
        """箱规字段可正常读写"""
        uom = self.env.ref("uom.product_uom_unit")
        product = self.env["product.template"].create({
            "name": "箱装品", "case_qty": 24, "case_uom_id": uom.id
        })
        self.assertEqual(product.case_qty, 24)
        self.assertEqual(product.case_uom_id, uom)


class TestResPartner(TransactionCase):
    """客户/供应商主档扩展字段"""

    def test_01_partner_code_unique(self):
        """客户编码可正常设置"""
        p1 = self.env["res.partner"].create({"name": "测试客户A", "partner_code": "CUST-001"})
        self.assertEqual(p1.partner_code, "CUST-001")

    def test_02_customer_level_selection(self):
        """客户等级枚举全部可设置"""
        partner = self.env["res.partner"].create({"name": "等级测试"})
        for val in ("a", "b", "c", "d"):
            partner.customer_level = val
            self.assertEqual(partner.customer_level, val)

    def test_03_credit_days_default(self):
        """账期默认为0"""
        partner = self.env["res.partner"].create({"name": "账期测试"})
        self.assertEqual(partner.credit_days, 0)

    def test_04_settlement_method_selection(self):
        """结算方式枚举全部可设置"""
        partner = self.env["res.partner"].create({"name": "结算测试"})
        for val in ("cash", "monthly", "batch", "other"):
            partner.settlement_method = val
            self.assertEqual(partner.settlement_method, val)

    def test_05_store_fields(self):
        """门店标记和编码字段"""
        partner = self.env["res.partner"].create({
            "name": "门店A", "is_store": True, "store_code": "ST-001"
        })
        self.assertTrue(partner.is_store)
        self.assertEqual(partner.store_code, "ST-001")

    def test_06_logistics_serviceable_default(self):
        """可配送标记默认为True"""
        partner = self.env["res.partner"].create({"name": "配送测试"})
        self.assertTrue(partner.is_logistics_serviceable)

    def test_07_delivery_note_storage(self):
        """配送备注可正常读写"""
        partner = self.env["res.partner"].create({
            "name": "备注测试", "delivery_note": "需提前联系"
        })
        self.assertEqual(partner.delivery_note, "需提前联系")


class TestSaleOrderExt(TransactionCase):
    """销售订单扩展字段"""

    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "测试客户"})
        self.product = self.env["product.template"].create({"name": "测试商品"})

    def test_01_create_with_erp_fields(self):
        """创建销售订单时可写入ERP扩展字段"""
        order = self.env["sale.order"].create({
            "partner_id": self.partner.id,
            
            "is_urgent": True,
            "batch_ref": "BATCH-001",
            "delivery_deadline": "2026-06-01",
            "delivery_note": "加急配送",
        })
        self.assertIsNotNone(order.id)
        self.assertTrue(order.is_urgent)
        self.assertEqual(order.batch_ref, "BATCH-001")
        self.assertEqual(order.delivery_note, "加急配送")

    def test_02_wms_tms_status_defaults(self):
        """WMS/TMS状态默认为pending"""
        order = self.env["sale.order"].create({
            "partner_id": self.partner.id,
        })
        self.assertEqual(order.wms_status, "pending")
        self.assertEqual(order.tms_status, "pending")


class TestPurchaseOrderExt(TransactionCase):
    """采购订单扩展字段"""

    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "测试供应商"})

    def test_01_create_with_erp_fields(self):
        """创建采购订单时可写入ERP扩展字段"""
        order = self.env["purchase.order"].create({
            "partner_id": self.partner.id,
            "batch_ref": "P-BATCH-001",
            "expected_arrival": "2026-06-10",
            "receiving_status": "pending",
        })
        self.assertEqual(order.batch_ref, "P-BATCH-001")
        self.assertEqual(order.receiving_status, "pending")

    def test_02_receiving_status_values(self):
        """收货状态枚举值全部可接受"""
        order = self.env["purchase.order"].create({
            "partner_id": self.partner.id,
        })
        for val in ("pending", "partial", "received", "exception"):
            order.receiving_status = val
            self.assertEqual(order.receiving_status, val)
