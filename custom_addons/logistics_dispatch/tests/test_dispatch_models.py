# -*- coding: utf-8 -*-
"""logistics_dispatch 单元测试 — 波次/批次/运单"""
from odoo.tests.common import TransactionCase


class TestDispatchBatch(TransactionCase):
    """物流批次"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1)

    def test_01_create_batch(self):
        batch = self.env["logistics.dispatch.batch"].create({
            "name": "TEST-BATCH-001", "state": "draft", "warehouse_id": self.wh.id,
        })
        self.assertEqual(batch.state, "draft")

    def test_02_state_flow(self):
        """批次状态流转"""
        batch = self.env["logistics.dispatch.batch"].create({
            "name": "FLOW-BATCH", "state": "draft", "warehouse_id": self.wh.id,
        })
        states = ["draft", "ready", "loading", "in_transit", "done"]
        for s in states:
            batch.state = s
            self.assertEqual(batch.state, s)

    def test_03_batch_no_required(self):
        """batch_no可正常存储"""
        batch = self.env["logistics.dispatch.batch"].create({
            "name": "BN-TEST", "state": "draft", "warehouse_id": self.wh.id,
            "batch_no": "PC202605220001",
        })
        self.assertEqual(batch.batch_no, "PC202605220001")


class TestDispatchWave(TransactionCase):
    """物流波次"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1)

    def test_01_create_wave(self):
        wave = self.env["logistics.dispatch.wave"].create({
            "name": "WAVE-TEST-001", "state": "draft", "warehouse_id": self.wh.id,
        })
        self.assertEqual(wave.state, "draft")

    def test_02_state_flow(self):
        """波次状态流转"""
        wave = self.env["logistics.dispatch.wave"].create({
            "name": "FLOW-WAVE", "state": "draft", "warehouse_id": self.wh.id,
        })
        for s in ("draft", "ready", "in_progress", "done"):
            wave.state = s
            self.assertEqual(wave.state, s)


class TestDispatchWaybill(TransactionCase):
    """物流运单"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1)

    def test_01_create_waybill(self):
        wb = self.env["logistics.dispatch.waybill"].create({
            "name": "YD-TEST-001", "state": "draft", "warehouse_id": self.wh.id,
        })
        self.assertEqual(wb.state, "draft")

    def test_02_state_flow_all(self):
        """运单全部状态枚举可设置"""
        wb = self.env["logistics.dispatch.waybill"].create({
            "name": "YD-STATES", "state": "draft", "warehouse_id": self.wh.id,
        })
        for s in ("draft", "ready", "in_transit", "arrived", "signed", "done"):
            wb.state = s
            self.assertEqual(wb.state, s)

    def test_03_waybill_no_storage(self):
        """waybill_no可存储"""
        wb = self.env["logistics.dispatch.waybill"].create({
            "name": "YD-NO-TEST", "state": "draft", "warehouse_id": self.wh.id,
            "waybill_no": "YD202605220001",
        })
        self.assertEqual(wb.waybill_no, "YD202605220001")

    def test_04_action_open_batch(self):
        """打开所属批次返回action或False"""
        wb = self.env["logistics.dispatch.waybill"].create({
            "name": "YD-OPEN-BATCH", "state": "draft", "warehouse_id": self.wh.id,
        })
        result = wb.action_open_batch()
        self.assertTrue(result is False or result.get("type"))

    def test_05_action_open_wave(self):
        """打开所属波次返回action或False"""
        wb = self.env["logistics.dispatch.waybill"].create({
            "name": "YD-OPEN-WAVE", "state": "draft", "warehouse_id": self.wh.id,
        })
        result = wb.action_open_wave()
        self.assertTrue(result is False or result.get("type"))


class TestDispatchBatchActions(TransactionCase):
    """批次action方法"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1)

    def test_01_action_open_record(self):
        """打开批次记录"""
        batch = self.env["logistics.dispatch.batch"].create({
            "name": "BATCH-OPEN", "state": "draft", "warehouse_id": self.wh.id,
        })
        action = batch.action_open_record()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_id"], batch.id)

    def test_02_action_logistics_delete(self):
        """批次删除"""
        batch = self.env["logistics.dispatch.batch"].create({
            "name": "BATCH-DEL", "state": "draft", "warehouse_id": self.wh.id,
        })
        batch_id = batch.id
        batch.action_logistics_delete()
        found = self.env["logistics.dispatch.batch"].search([("id", "=", batch_id)])
        self.assertFalse(found)

    def test_03_wave_delete_cascades_to_batch(self):
        """波次删除级联删除批次"""
        batch = self.env["logistics.dispatch.batch"].create({
            "name": "BATCH-CASCADE", "state": "draft", "warehouse_id": self.wh.id,
        })
        wave = self.env["logistics.dispatch.wave"].create({
            "name": "WAVE-CASCADE", "state": "draft", "warehouse_id": self.wh.id,
        })
        if hasattr(wave, 'batch_ids'):
            wave.batch_ids = [(6, 0, [batch.id])]
        wave_id = wave.id
        batch_id = batch.id
        wave.action_logistics_delete()
        self.assertFalse(self.env["logistics.dispatch.wave"].search([("id", "=", wave_id)]))
        self.assertFalse(self.env["logistics.dispatch.batch"].search([("id", "=", batch_id)]))


class TestDispatchWaybillActions(TransactionCase):
    """运单action方法"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1)

    def test_01_waybill_delete(self):
        """运单删除"""
        wb = self.env["logistics.dispatch.waybill"].create({
            "name": "YD-DEL", "state": "draft", "warehouse_id": self.wh.id,
        })
        wb_id = wb.id
        wb.action_logistics_delete()
        found = self.env["logistics.dispatch.waybill"].search([("id", "=", wb_id)])
        self.assertFalse(found)

    def test_02_action_open_order_lines(self):
        """打开订单明细"""
        wb = self.env["logistics.dispatch.waybill"].create({
            "name": "YD-ORD", "state": "draft", "warehouse_id": self.wh.id,
        })
        result = wb.action_open_order_lines()
        self.assertEqual(result["type"], "ir.actions.act_window")

    def test_03_action_open_customer_lines(self):
        """打开配送节点"""
        wb = self.env["logistics.dispatch.waybill"].create({
            "name": "YD-CUST", "state": "draft", "warehouse_id": self.wh.id,
        })
        result = wb.action_open_customer_lines()
        self.assertEqual(result["type"], "ir.actions.act_window")

    def test_04_action_open_goods_lines(self):
        """打开货物明细"""
        wb = self.env["logistics.dispatch.waybill"].create({
            "name": "YD-GOODS", "state": "draft", "warehouse_id": self.wh.id,
        })
        result = wb.action_open_goods_lines()
        self.assertEqual(result["type"], "ir.actions.act_window")


class TestDispatchCustomerLineDelete(TransactionCase):
    """配送节点删除链路"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1)
        self.wb = self.env["logistics.dispatch.waybill"].create({
            "name": "YD-DELCHAIN", "state": "draft", "warehouse_id": self.wh.id,
        })

    def test_01_customer_line_delete(self):
        """配送节点删除(调用v2模型action_logistics_delete)"""
        cl = self.env["logistics.dispatch.waybill.customer.line"].create({
            "waybill_id": self.wb.id, "customer_no": "C001", "customer_name": "测试客户",
            "longitude": 113.5, "latitude": 23.1, "address_detail": "测试",
        })
        cl_id = cl.id
        if hasattr(cl, 'action_logistics_delete'):
            cl.action_logistics_delete()
            found = self.env["logistics.dispatch.waybill.customer.line"].search([("id", "=", cl_id)])
            self.assertFalse(found)

    def test_02_goods_line_delete(self):
        """货物明细删除"""
        cl = self.env["logistics.dispatch.waybill.customer.line"].create({
            "waybill_id": self.wb.id, "customer_no": "C002", "customer_name": "测试客户2",
            "longitude": 113.5, "latitude": 23.1, "address_detail": "测试",
        })
        product = self.env["product.product"].create({"name": "测试品"})
        gl = self.env["logistics.dispatch.waybill.customer.goods.line"].create({
            "customer_line_id": cl.id, "product_id": product.id,
            "waybill_no": self.wb.name, "quantity": 10,
        })
        gl_id = gl.id
        if hasattr(gl, 'action_logistics_delete'):
            gl.action_logistics_delete()
            found = self.env["logistics.dispatch.waybill.customer.goods.line"].search([("id", "=", gl_id)])
            self.assertFalse(found)
