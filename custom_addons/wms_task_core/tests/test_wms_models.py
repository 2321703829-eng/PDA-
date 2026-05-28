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


class TestWmsOutboundFullChain(TransactionCase):
    """出库完整链路: picking→outbound→pick→check→handover"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1)
        self.product = self.env["product.product"].create({"name": "全链路品"})
        loc_src = self.env["stock.location"].search([("usage", "=", "internal")], limit=1)
        loc_dest = self.wh.lot_stock_id
        picking_type = self.env["stock.picking.type"].search([("code", "=", "outgoing")], limit=1)
        if not picking_type:
            self.skipTest("无出库作业类型")
            return
        self.picking = self.env["stock.picking"].create({
            "picking_type_id": picking_type.id,
            "location_id": loc_src.id,
            "location_dest_id": loc_dest.id,
            "origin": "TEST-OUTBOUND-FLOW",
        })
        self.env["stock.move"].create({
            "name": self.product.display_name,
            "product_id": self.product.id,
            "product_uom_qty": 5,
            "product_uom": self.product.uom_id.id,
            "picking_id": self.picking.id,
            "location_id": loc_src.id,
            "location_dest_id": loc_dest.id,
        })

    def test_full_outbound_chain(self):
        """出库→拣货→复核→交接完整链"""
        # 1. 创建出库任务
        outbound = self.env["wms.outbound.task"].create({
            "warehouse_id": self.wh.id, "stock_picking_id": self.picking.id,
        })
        outbound.action_start_outbound()
        self.assertEqual(outbound.state, "task_processing")

        # 2. 生成拣货任务 (action_generate_pick_task)
        result = outbound.action_generate_pick_task()
        self.assertEqual(result["type"], "ir.actions.act_window")
        pick_task = outbound.pick_task_ids[0]
        self.assertTrue(pick_task)
        self.assertTrue(len(pick_task.line_ids) >= 1)

        # 3. 拣货→完成
        pick_task.action_start_pick()
        self.assertEqual(pick_task.state, "picking")
        pick_task.action_mark_picked()
        self.assertEqual(pick_task.state, "picked")

        # 4. 复核→完成→交接单创建
        check_task = outbound.check_task_ids[0]
        self.assertTrue(check_task)
        check_task.action_mark_checked()
        self.assertEqual(check_task.state, "checked")
        self.assertTrue(outbound.handover_order_ids)

        # 5. 交接→完成→出库done
        handover = outbound.handover_order_ids[0]
        handover.action_start_handover()
        self.assertEqual(handover.state, "handover_ing")
        handover.action_mark_done()
        self.assertEqual(handover.state, "handover_done")
        self.assertEqual(outbound.state, "task_done")

