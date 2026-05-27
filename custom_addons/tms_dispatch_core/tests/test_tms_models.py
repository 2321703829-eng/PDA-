# -*- coding: utf-8 -*-
"""tms_dispatch_core 单元测试 — 派车流程/状态同步/状态校验/推送派车"""
from odoo.tests.common import TransactionCase

_counter = [0]


def _uid(prefix="TMS"):
    _counter[0] += 1
    return "%s-%04d" % (prefix, _counter[0])


class TestDispatchOrderFlow(TransactionCase):
    """派车单核心流程"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1)
        self.batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": _uid("PC"), "delivery_date": "2026-06-01",
            "route_status": "route_planned", "warehouse_id": self.wh.id,
        })
        # 创建运单和停靠点(匹配)
        wn = _uid("YD-TMS")
        self.waybill = self.env["logistics.dispatch.waybill"].create({
            "name": wn, "warehouse_id": self.wh.id,
        })
        self.env["logistics.route.planning.stop.line"].create({
            "batch_id": self.batch.id, "stop_seq": 1,
            "store_name": "门店A", "waybill_no": wn,
            "longitude": 113.53, "latitude": 23.08, "address_detail": "广州",
        })
        self.dispatch = self.env["tms.dispatch.order"].create({
            "route_batch_id": self.batch.id,
        })

    def test_action_dispatch_creates_driver_tasks(self):
        """派车应创建司机任务"""
        self.dispatch.action_dispatch()
        self.assertEqual(self.dispatch.state, "dispatched")
        self.assertTrue(self.dispatch.driver_task_count >= 1)

    def test_action_dispatch_no_stops(self):
        """无停靠点→拦截"""
        batch2 = self.env["logistics.route.planning.batch"].create({
            "batch_no": _uid("PC-NS"), "delivery_date": "2026-06-01",
            "route_status": "route_planned", "warehouse_id": self.wh.id,
        })
        d2 = self.env["tms.dispatch.order"].create({"route_batch_id": batch2.id})
        result = d2.action_dispatch()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("没有停靠点", result["params"]["message"])

    def test_action_depart_state_change(self):
        """发车→in_transit(因自动推进司机任务)"""
        self.dispatch.action_dispatch()
        self.dispatch.action_depart()
        self.assertEqual(self.dispatch.state, "in_transit")

    def test_normal_state_flow(self):
        """完整流程: dispatch→depart→start→arrive→sign"""
        self.dispatch.action_dispatch()
        self.dispatch.action_depart()
        for task in self.dispatch.driver_task_ids:
            task.action_start_delivery()
            self.assertEqual(task.state, "in_transit")
            task.action_arrive_store()
            self.assertEqual(task.state, "arrived_store")
            task.action_mark_signed_full()
            self.assertEqual(task.state, "signed_full")


class TestSyncStateFromTasks(TransactionCase):
    """_sync_state_from_tasks"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1)
        self.batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": _uid("PC-SYNC"), "delivery_date": "2026-06-01",
            "route_status": "route_planned", "warehouse_id": self.wh.id,
        })
        self.dispatch = self.env["tms.dispatch.order"].create({
            "route_batch_id": self.batch.id,
        })

    def test_all_signed_full_syncs_dispatch(self):
        """全部签收→派车单signed_full"""
        self.env["tms.driver.task"].create({
            "dispatch_order_id": self.dispatch.id, "state": "signed_full",
        })
        self.env["tms.driver.task"].create({
            "dispatch_order_id": self.dispatch.id, "state": "signed_full",
        })
        self.dispatch._sync_state_from_tasks()
        self.assertEqual(self.dispatch.state, "signed_full")

    def test_mixed_syncs_signed_partial(self):
        """混合状态→signed_partial"""
        self.env["tms.driver.task"].create({
            "dispatch_order_id": self.dispatch.id, "state": "signed_full",
        })
        self.env["tms.driver.task"].create({
            "dispatch_order_id": self.dispatch.id, "state": "in_transit",
        })
        self.dispatch._sync_state_from_tasks()
        self.assertEqual(self.dispatch.state, "signed_partial")

    def test_exception_syncs_exception(self):
        """异常→delivery_exception"""
        self.env["tms.driver.task"].create({
            "dispatch_order_id": self.dispatch.id, "state": "delivery_exception",
        })
        self.dispatch._sync_state_from_tasks()
        self.assertEqual(self.dispatch.state, "delivery_exception")

    def test_departed_syncs_departed(self):
        """departed→departed"""
        self.env["tms.driver.task"].create({
            "dispatch_order_id": self.dispatch.id, "state": "departed",
        })
        self.dispatch._sync_state_from_tasks()
        self.assertEqual(self.dispatch.state, "departed")

    def test_no_tasks_unchanged(self):
        """无任务不变"""
        orig = self.dispatch.state
        self.dispatch._sync_state_from_tasks()
        self.assertEqual(self.dispatch.state, orig)


class TestDriverTaskStateValidation(TransactionCase):
    """状态校验 — 不允许倒退/跳步"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1)
        self.batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": _uid("PC-VAL"), "delivery_date": "2026-06-01",
            "route_status": "route_planned", "warehouse_id": self.wh.id,
        })
        self.dispatch = self.env["tms.dispatch.order"].create({
            "route_batch_id": self.batch.id,
        })
        self.task = self.env["tms.driver.task"].create({
            "dispatch_order_id": self.dispatch.id,
        })

    def test_signed_cannot_start_delivery(self):
        """已签收不能重新开始配送"""
        self.task.state = "signed_full"
        result = self.task.action_start_delivery()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("已签收", result["params"]["message"])

    def test_not_departed_cannot_arrive_store(self):
        """未在途不能到店"""
        self.task.state = "waiting_dispatch"
        result = self.task.action_arrive_store()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("尚未开始配送", result["params"]["message"])

    def test_not_arrived_cannot_sign_full(self):
        """未到店不能全签"""
        self.task.state = "dispatched"
        result = self.task.action_mark_signed_full()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("尚未到店", result["params"]["message"])

    def test_not_arrived_cannot_sign_partial(self):
        """未到店不能部分签收"""
        self.task.state = "in_transit"
        result = self.task.action_mark_signed_partial()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("尚未到店", result["params"]["message"])

    def test_arrived_can_sign_full(self):
        """到店后正常签收"""
        self.task.state = "arrived_store"
        result = self.task.action_mark_signed_full()
        if isinstance(result, dict):
            self.assertNotEqual(result.get("type"), "ir.actions.client")


class TestPushToDispatch(TransactionCase):
    """推送派车"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1)

    def test_push_creates_dispatch(self):
        """推送→创建派车单"""
        wn = _uid("YD-PUSH")
        wb = self.env["logistics.dispatch.waybill"].create({
            "name": wn, "warehouse_id": self.wh.id,
        })
        batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": _uid("PC-PUSH"), "delivery_date": "2026-06-01",
            "route_status": "route_planned", "warehouse_id": self.wh.id,
        })
        self.env["logistics.route.planning.stop.line"].create({
            "batch_id": batch.id, "stop_seq": 1,
            "store_name": "A", "waybill_no": wn,
            "longitude": 113.5, "latitude": 23.1, "address_detail": "X",
        })
        result = batch.action_push_to_dispatch()
        self.assertEqual(result["type"], "ir.actions.act_window")
        d = self.env["tms.dispatch.order"].search([("route_batch_id", "=", batch.id)], limit=1)
        self.assertTrue(d)

    def test_push_no_stops(self):
        """无停靠点→拦截"""
        batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": _uid("PC-NS-PUSH"), "delivery_date": "2026-06-01",
            "route_status": "route_planned", "warehouse_id": self.wh.id,
        })
        result = batch.action_push_to_dispatch()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("没有停靠点", result["params"]["message"])

    def test_push_idempotent(self):
        """重复推送不重复创建"""
        wn = _uid("YD-DUP")
        wb = self.env["logistics.dispatch.waybill"].create({
            "name": wn, "warehouse_id": self.wh.id,
        })
        batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": _uid("PC-DUP"), "delivery_date": "2026-06-01",
            "route_status": "route_planned", "warehouse_id": self.wh.id,
        })
        self.env["logistics.route.planning.stop.line"].create({
            "batch_id": batch.id, "stop_seq": 1,
            "store_name": "B", "waybill_no": wn,
            "longitude": 113.5, "latitude": 23.1, "address_detail": "X",
        })
        batch.action_push_to_dispatch()
        batch.action_push_to_dispatch()
        self.assertEqual(
            self.env["tms.dispatch.order"].search_count([("route_batch_id", "=", batch.id)]), 1
        )


class TestRouteBatchOpenMethods(TransactionCase):
    """排线批次open方法"""

    def setUp(self):
        super().setUp()
        self.batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": _uid("PC-OPEN"), "delivery_date": "2026-06-01",
            "route_status": "route_planned",
        })

    def test_action_open_route_map(self):
        action = self.batch.action_open_route_map()
        self.assertEqual(action["type"], "ir.actions.act_url")
        self.assertIn("/tms/route/", action["url"])

    def test_action_open_dispatch_orders(self):
        action = self.batch.action_open_dispatch_orders()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "tms.dispatch.order")
