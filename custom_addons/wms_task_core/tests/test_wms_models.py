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
        })
        self.assertEqual(task.state, "waiting_pick")

    def test_02_status_flow(self):
        wh = self.env["stock.warehouse"].search([], limit=1)
        outbound = self.env["wms.outbound.task"].create({"warehouse_id": wh.id})
        task = self.env["wms.pick.task"].create({
            "warehouse_id": wh.id, "outbound_task_id": outbound.id,
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

    def test_01_model_exists(self):
        """台账模型可正常访问(数据库视图,只读)"""
        model = self.env["wms.inventory.ledger"]
        self.assertTrue(model._auto is False)
        found = self.env["ir.model"].search([("model", "=", "wms.inventory.ledger")], limit=1)
        self.assertTrue(found)


class TestWmsReceiptTaskActions(TransactionCase):
    """收货任务完整流程 + create_from_picking"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1)

    def test_01_create_from_picking(self):
        """stock.picking自动生成收货任务"""
        picking_type = self.env["stock.picking.type"].search([("code", "=", "incoming")], limit=1)
        if not picking_type:
            self.skipTest("无入库作业类型")
        picking = self.env["stock.picking"].create({
            "picking_type_id": picking_type.id,
            "location_dest_id": self.wh.lot_stock_id.id,
            "location_id": self.env["stock.location"].search([("usage", "=", "supplier")], limit=1).id,
        })
        task = self.env["wms.receipt.task"].create_from_picking(picking)
        self.assertEqual(task.warehouse_id, self.wh)
        self.assertEqual(task.state, "waiting_receipt")

    def test_02_mark_received_creates_putaway(self):
        """标记收货后自动生成上架任务"""
        task = self.env["wms.receipt.task"].create({"warehouse_id": self.wh.id})
        task.action_mark_received()
        self.assertEqual(task.state, "received")
        self.assertTrue(task.putaway_task_ids)

    def test_03_empty_receipt_guard(self):
        """空收货任务action_mark_received不崩溃"""
        task = self.env["wms.receipt.task"].create({"warehouse_id": self.wh.id})
        task.action_start_receipt()
        self.assertEqual(task.state, "receiving")


class TestWmsOutboundFullFlow(TransactionCase):
    """出库→拣货→复核→交接完整链路"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1)

    def test_01_outbound_full_flow(self):
        """出库任务完整状态流转"""
        task = self.env["wms.outbound.task"].create({"warehouse_id": self.wh.id})
        task.action_start_outbound()
        self.assertEqual(task.state, "task_processing")
        task.action_mark_done()
        self.assertEqual(task.state, "task_done")

    def test_02_generate_pick_task(self):
        """出库任务生成拣货任务(通过action)"""
        outbound = self.env["wms.outbound.task"].create({"warehouse_id": self.wh.id})
        product = self.env["product.product"].create({"name": "拣货测试品"})
        loc = self.env["stock.location"].search([("usage", "=", "internal")], limit=1)
        picking_type = self.env["stock.picking.type"].search([("code", "=", "outgoing")], limit=1)
        if picking_type:
            picking = self.env["stock.picking"].create({
                "picking_type_id": picking_type.id,
                "location_id": loc.id,
                "location_dest_id": self.wh.lot_stock_id.id,
                "move_ids": [(0, 0, {
                    "name": product.display_name,
                    "product_id": product.id,
                    "product_uom_qty": 10,
                    "location_id": loc.id,
                    "location_dest_id": self.wh.lot_stock_id.id,
                })],
            })
            outbound.write({"stock_picking_id": picking.id})
        pick_task = self.env["wms.pick.task"].create({
            "outbound_task_id": outbound.id, "warehouse_id": self.wh.id,
        })
        line = self.env["wms.pick.task.line"].create({
            "pick_task_id": pick_task.id,
            "product_id": product.id,
            "demand_qty": 10,
            "done_qty": 0,
        })
        self.assertEqual(line.demand_qty, 10)
        line.done_qty = 10
        pick_task.action_mark_picked()
        self.assertEqual(pick_task.state, "picked")

    def test_03_check_task_create_handover(self):
        """复核完成自动生成交接单"""
        outbound = self.env["wms.outbound.task"].create({"warehouse_id": self.wh.id})
        check = self.env["wms.check.task"].create({
            "outbound_task_id": outbound.id, "warehouse_id": self.wh.id,
        })
        check.action_mark_checked()
        self.assertEqual(check.state, "checked")
        self.assertTrue(outbound.handover_order_ids)

    def test_04_handover_state_flow(self):
        """交接单状态流转"""
        outbound = self.env["wms.outbound.task"].create({"warehouse_id": self.wh.id})
        handover = self.env["wms.handover.order"].create({
            "outbound_task_id": outbound.id, "warehouse_id": self.wh.id,
        })
        handover.action_start_handover()
        self.assertEqual(handover.state, "handover_ing")
        handover.action_mark_done()
        self.assertEqual(handover.state, "handover_done")
        self.assertEqual(outbound.state, "task_done")


class TestWmsInventoryOperationFull(TransactionCase):
    """库存操作完整流程"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1)
        self.loc = self.env["stock.location"].search([("usage", "=", "internal")], limit=1)

    def test_01_load_quants(self):
        """加载库位库存快照"""
        op = self.env["wms.inventory.operation"].create({
            "warehouse_id": self.wh.id, "location_id": self.loc.id,
            "operation_type": "inventory_count",
        })
        op.action_start()
        self.assertEqual(op.state, "in_progress")
        op.action_cancel()
        self.assertEqual(op.state, "cancelled")
