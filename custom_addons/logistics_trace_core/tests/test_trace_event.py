# -*- coding: utf-8 -*-
"""logistics_trace_core 单元测试 — 留痕事件创建/约束/compute"""
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestTraceEventConstraints(TransactionCase):
    """留痕事件约束"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1)
        self.batch = self.env["logistics.dispatch.batch"].create({
            "name": "BATCH-TRACE-CONST", "warehouse_id": self.wh.id,
        })
        self.waybill = self.env["logistics.dispatch.waybill"].create({
            "name": "YD-TRACE-CONST", "warehouse_id": self.wh.id,
        })

    def test_create_trace_event(self):
        """创建留痕事件"""
        event = self.env["logistics.trace.event"].create({
            "object_type": "waybill",
            "waybill_id": self.waybill.id,
            "trace_type": "arrive",
            "state": "submitted",
        })
        self.assertEqual(event.state, "submitted")

    def test_object_type_waybill_without_waybill_id_raises(self):
        """object_type=waybill但waybill_id为空→ValidationError"""
        with self.assertRaises(ValidationError):
            self.env["logistics.trace.event"].create({
                "object_type": "waybill",
                "batch_id": self.batch.id,
                "trace_type": "arrive",
            })

    def test_object_type_batch_without_batch_id_raises(self):
        """object_type=batch但batch_id为空→ValidationError"""
        with self.assertRaises(ValidationError):
            self.env["logistics.trace.event"].create({
                "object_type": "batch",
                "trace_type": "arrive",
            })


class TestWaybillTraceCompute(TransactionCase):
    """运单留痕compute字段"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1)
        self.wb = self.env["logistics.dispatch.waybill"].create({
            "name": "YD-TRACE-COMP", "warehouse_id": self.wh.id,
        })

    def test_trace_count_increments(self):
        """创建留痕事件后trace_count应增加"""
        self.env["logistics.trace.event"].create({
            "object_type": "waybill", "waybill_id": self.wb.id,
            "trace_type": "arrive", "state": "submitted",
        })
        self.wb.invalidate_recordset()
        self.assertGreaterEqual(self.wb.trace_count, 1)
