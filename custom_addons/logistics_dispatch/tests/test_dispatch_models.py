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
