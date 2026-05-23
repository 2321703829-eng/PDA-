# -*- coding: utf-8 -*-
"""wms_task_core 单元测试"""
from odoo.tests.common import TransactionCase


class TestWmsReceiptTask(TransactionCase):
    """收货任务"""

    def test_01_create_default(self):
        wh = self.env["stock.warehouse"].search([], limit=1)
        task = self.env["wms.receipt.task"].create({
            "warehouse_id": wh.id,
        })
        self.assertEqual(task.state, "waiting_receipt")

    def test_02_status_flow(self):
        """收货状态流转"""
        wh = self.env["stock.warehouse"].search([], limit=1)
        task = self.env["wms.receipt.task"].create({"warehouse_id": wh.id})
        task.action_start_receipt()
        self.assertEqual(task.state, "receiving")
        task.action_mark_received()
        self.assertEqual(task.state, "received")


class TestWmsPutawayTask(TransactionCase):
    """上架任务"""

    def test_01_create_default(self):
        wh = self.env["stock.warehouse"].search([], limit=1)
        task = self.env["wms.putaway.task"].create({"warehouse_id": wh.id})
        self.assertEqual(task.state, "waiting_putaway")

    def test_02_status_flow(self):
        wh = self.env["stock.warehouse"].search([], limit=1)
        task = self.env["wms.putaway.task"].create({"warehouse_id": wh.id})
        task.action_start_putaway()
        self.assertEqual(task.state, "putaway_ing")
        task.action_mark_done()
        self.assertEqual(task.state, "putaway_done")


class TestWmsOutboundTask(TransactionCase):
    """出库任务"""

    def test_01_create_default(self):
        wh = self.env["stock.warehouse"].search([], limit=1)
        task = self.env["wms.outbound.task"].create({"warehouse_id": wh.id})
        self.assertEqual(task.state, "waiting_outbound")

    def test_02_status_flow(self):
        wh = self.env["stock.warehouse"].search([], limit=1)
        task = self.env["wms.outbound.task"].create({"warehouse_id": wh.id})
        task.action_start_outbound()
        self.assertEqual(task.state, "task_processing")


class TestWmsPickTask(TransactionCase):
    """拣货任务"""

    def test_01_create_default(self):
        wh = self.env["stock.warehouse"].search([], limit=1)
        outbound = self.env["wms.outbound.task"].create({"warehouse_id": wh.id})
        task = self.env["wms.pick.task"].create({
            "warehouse_id": wh.id, "outbound_task_id": outbound.id,
            "source_location_id": wh.view_location_id.id
        })
        self.assertEqual(task.state, "waiting_pick")

    def test_02_status_flow(self):
        wh = self.env["stock.warehouse"].search([], limit=1)
        outbound = self.env["wms.outbound.task"].create({"warehouse_id": wh.id})
        task = self.env["wms.pick.task"].create({
            "warehouse_id": wh.id, "outbound_task_id": outbound.id,
            "source_location_id": wh.view_location_id.id
        })
        task.action_start_pick()
        self.assertEqual(task.state, "picking")
        task.action_mark_picked()
        self.assertEqual(task.state, "picked")


class TestWmsCheckTask(TransactionCase):
    """复核任务"""

    def test_01_create_default(self):
        wh = self.env["stock.warehouse"].search([], limit=1)
        task = self.env["wms.check.task"].create({"warehouse_id": wh.id})
        self.assertEqual(task.state, "waiting_check")


class TestWmsHandoverOrder(TransactionCase):
    """交接单"""

    def test_01_create_default(self):
        wh = self.env["stock.warehouse"].search([], limit=1)
        order = self.env["wms.handover.order"].create({"warehouse_id": wh.id})
        self.assertEqual(order.state, "waiting_handover")


class TestWmsInventoryOperation(TransactionCase):
    """库存操作"""

    def test_01_create_default(self):
        wh = self.env["stock.warehouse"].search([], limit=1)
        loc = self.env["stock.location"].search([("usage", "=", "internal")], limit=1)
        op = self.env["wms.inventory.operation"].create({
            "warehouse_id": wh.id, "location_id": loc.id,
        })
        self.assertEqual(op.state, "draft")

    def test_02_cancel_operation(self):
        wh = self.env["stock.warehouse"].search([], limit=1)
        loc = self.env["stock.location"].search([("usage", "=", "internal")], limit=1)
        op = self.env["wms.inventory.operation"].create({
            "warehouse_id": wh.id, "location_id": loc.id,
        })
        if hasattr(op, 'action_cancel'):
            op.action_cancel()
            self.assertEqual(op.state, "cancelled")


class TestWmsInventoryLedger(TransactionCase):
    """库存台账"""

    def test_01_create_entry(self):
        wh = self.env["stock.warehouse"].search([], limit=1)
        loc = self.env["stock.location"].search([("usage", "=", "internal")], limit=1)
        product = self.env["product.template"].create({"name": "台账测试品"})
        ledger = self.env["wms.inventory.ledger"].create({
            "warehouse_id": wh.id,
            "location_id": loc.id,
            "product_tmpl_id": product.id,
        })
        self.assertEqual(ledger.warehouse_id, wh)
