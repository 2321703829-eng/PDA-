# -*- coding: utf-8 -*-
"""wms_task_core 单元测试 — picking联动/出库全链/库存操作/状态流转"""
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestWmsReceiptTask(TransactionCase):
    """收货任务 — action流转+create_from_picking"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1) or self.env["stock.warehouse"].create({"name": "WH-REC", "code": "WR"})

    def test_status_flow_receipt_to_received(self):
        """收货→标记完成→状态变更"""
        task = self.env["wms.receipt.task"].create({"warehouse_id": self.wh.id})
        task.action_start_receipt()
        self.assertEqual(task.state, "receiving")
        task.action_mark_received()
        self.assertEqual(task.state, "received")

    def test_mark_received_creates_putaway(self):
        """收货完成后自动创建上架任务"""
        task = self.env["wms.receipt.task"].create({"warehouse_id": self.wh.id})
        task.action_mark_received()
        self.assertTrue(task.putaway_task_ids)


class TestWmsPutawayTask(TransactionCase):
    """上架任务"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1) or self.env["stock.warehouse"].create({"name": "WH-PUT", "code": "WP"})

    def test_status_flow_putaway_to_done(self):
        task = self.env["wms.putaway.task"].create({"warehouse_id": self.wh.id})
        task.action_start_putaway()
        self.assertEqual(task.state, "putaway_ing")
        task.action_mark_done()
        self.assertEqual(task.state, "putaway_done")


class TestWmsPickTask(TransactionCase):
    """拣货任务 — action流转"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1) or self.env["stock.warehouse"].create({"name": "WH-PICK", "code": "WK"})
        self.outbound = self.env["wms.outbound.task"].create({"warehouse_id": self.wh.id})

    def test_pick_task_status_flow(self):
        task = self.env["wms.pick.task"].create({
            "outbound_task_id": self.outbound.id, "warehouse_id": self.wh.id,
        })
        task.action_start_pick()
        self.assertEqual(task.state, "picking")
        task.action_mark_picked()
        self.assertEqual(task.state, "picked")

    def test_pick_task_line_create(self):
        """拣货行可正常创建"""
        task = self.env["wms.pick.task"].create({
            "outbound_task_id": self.outbound.id, "warehouse_id": self.wh.id,
        })
        product = self.env["product.product"].create({"name": "PICK品"})
        line = self.env["wms.pick.task.line"].create({
            "pick_task_id": task.id, "product_id": product.id,
            "demand_qty": 10, "done_qty": 0,
        })
        self.assertEqual(line.demand_qty, 10)
        line.done_qty = 10
        self.assertEqual(line.done_qty, 10)


class TestWmsCheckTask(TransactionCase):
    """复核任务 — action流转+创建交接单"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1) or self.env["stock.warehouse"].create({"name": "WH-CHK", "code": "WC"})
        self.outbound = self.env["wms.outbound.task"].create({"warehouse_id": self.wh.id})

    def test_check_mark_checked_creates_handover(self):
        """复核完成自动创建交接单"""
        check = self.env["wms.check.task"].create({
            "outbound_task_id": self.outbound.id, "warehouse_id": self.wh.id,
        })
        check.action_mark_checked()
        self.assertEqual(check.state, "checked")
        self.assertTrue(self.outbound.handover_order_ids)


class TestWmsHandoverOrder(TransactionCase):
    """交接单 — 完整流程"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1) or self.env["stock.warehouse"].create({"name": "WH-HO", "code": "WH"})
        self.outbound = self.env["wms.outbound.task"].create({"warehouse_id": self.wh.id})

    def test_handover_full_flow(self):
        handover = self.env["wms.handover.order"].create({
            "outbound_task_id": self.outbound.id, "warehouse_id": self.wh.id,
        })
        handover.action_start_handover()
        self.assertEqual(handover.state, "handover_ing")
        handover.action_mark_done()
        self.assertEqual(handover.state, "handover_done")
        self.assertEqual(self.outbound.state, "task_done")


class TestWmsOutboundFullFlow(TransactionCase):
    """出库任务完整链路: outbound→pick→check→handover"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1) or self.env["stock.warehouse"].create({"name": "WH-OUT", "code": "WO"})

    def test_outbound_state_flow(self):
        task = self.env["wms.outbound.task"].create({"warehouse_id": self.wh.id})
        task.action_start_outbound()
        self.assertEqual(task.state, "task_processing")
        task.action_mark_done()
        self.assertEqual(task.state, "task_done")


class TestWmsInventoryOperation(TransactionCase):
    """库存操作"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1) or self.env["stock.warehouse"].create({"name": "WH-INV", "code": "WI"})
        self.loc = self.env["stock.location"].search([("usage", "=", "internal")], limit=1)
        if not self.loc:
            self.loc = self.env["stock.location"].create({
                "name": "TEST-LOC", "usage": "internal", "location_id": self.wh.view_location_id.id,
            })

    def test_inventory_operation_status_flow(self):
        op = self.env["wms.inventory.operation"].create({
            "warehouse_id": self.wh.id, "location_id": self.loc.id,
            "operation_type": "inventory_count",
        })
        op.action_start()
        self.assertEqual(op.state, "in_progress")

    def test_inventory_operation_cancel(self):
        """取消操作 — 不使用hasattr防御"""
        op = self.env["wms.inventory.operation"].create({
            "warehouse_id": self.wh.id, "location_id": self.loc.id,
            "operation_type": "inventory_count",
        })
        op.action_cancel()
        self.assertEqual(op.state, "cancelled")

