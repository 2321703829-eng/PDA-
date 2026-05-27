# -*- coding: utf-8 -*-
"""tms_dispatch_core 单元测试 — 派车流程/状态同步/状态校验/推送派车"""
from unittest.mock import MagicMock, patch

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestDispatchOrderFlow(TransactionCase):
    """派车单核心流程: dispatch→depart→sync"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1) or self.env["stock.warehouse"].create({"name": "WH-TMS", "code": "WT"})
        self.batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-TMS-FLOW", "delivery_date": "2026-06-01",
            "route_status": "route_planned", "warehouse_id": self.wh.id,
        })
        # 创建2个停靠点
        self.stop1 = self.env["logistics.route.planning.stop.line"].create({
            "batch_id": self.batch.id, "stop_seq": 1,
            "store_name": "门店A", "waybill_no": "YD-TMS-001",
            "longitude": 113.53, "latitude": 23.08, "address_detail": "广州",
        })
        self.stop2 = self.env["logistics.route.planning.stop.line"].create({
            "batch_id": self.batch.id, "stop_seq": 2,
            "store_name": "门店B", "waybill_no": "YD-TMS-002",  # 运单不存在,用于测stop→waybill解析失败
            "longitude": 113.45, "latitude": 23.12, "address_detail": "佛山",
        })
        # 创建与stop1匹配的运单
        self.wh2 = self.env["stock.warehouse"].search([], limit=1) or self.env["stock.warehouse"].create({"name": "WH-WAYBILL", "code": "WW"})
        self.waybill = self.env["logistics.dispatch.waybill"].create({
            "name": "YD-TMS-001", "warehouse_id": self.wh2.id,
        })
        self.dispatch = self.env["tms.dispatch.order"].create({
            "route_batch_id": self.batch.id,
        })

    def test_action_dispatch_creates_driver_tasks(self):
        """派车应创建司机任务(只对匹配到运单的停靠点)"""
        self.dispatch.action_dispatch()
        self.assertEqual(self.dispatch.state, "dispatched")
        # 只有stop1能成功(waybill存在),stop2会报ValidationError被跳过
        self.assertTrue(self.dispatch.driver_task_count >= 1)

    def test_action_dispatch_no_stops(self):
        """无停靠点时派车应拦截"""
        empty_batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-NOSTOP", "delivery_date": "2026-06-01",
            "route_status": "route_planned", "warehouse_id": self.wh.id,
        })
        empty_dispatch = self.env["tms.dispatch.order"].create({"route_batch_id": empty_batch.id})
        result = empty_dispatch.action_dispatch()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("没有停靠点", result["params"]["message"])

    def test_action_depart_state_change(self):
        """发车后状态变departed"""
        self.dispatch.action_dispatch()
        self.dispatch.action_depart()
        self.assertEqual(self.dispatch.state, "departed")

    def test_normal_state_flow(self):
        """完整状态流: waiting→dispatch→depart→in_transit→arrived→signed"""
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
    """_sync_state_from_tasks — 派车单状态应与司机任务同步"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1) or self.env["stock.warehouse"].create({"name": "WH-SYNC", "code": "WS"})
        self.batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-SYNC", "delivery_date": "2026-06-01",
            "route_status": "route_planned", "warehouse_id": self.wh.id,
        })
        self.dispatch = self.env["tms.dispatch.order"].create({
            "route_batch_id": self.batch.id,
        })

    def test_all_tasks_signed_full_then_dispatch_signed(self):
        """所有任务签收后派车单应变signed_full"""
        task1 = self.env["tms.driver.task"].create({
            "dispatch_order_id": self.dispatch.id, "state": "signed_full",
        })
        task2 = self.env["tms.driver.task"].create({
            "dispatch_order_id": self.dispatch.id, "state": "signed_full",
        })
        self.dispatch._sync_state_from_tasks()
        self.assertEqual(self.dispatch.state, "signed_full")

    def test_mixed_states_then_dispatch_stays_partial(self):
        """任务状态混合时派车单应变signed_partial"""
        self.env["tms.driver.task"].create({
            "dispatch_order_id": self.dispatch.id, "state": "signed_full",
        })
        self.env["tms.driver.task"].create({
            "dispatch_order_id": self.dispatch.id, "state": "in_transit",
        })
        self.dispatch._sync_state_from_tasks()
        self.assertEqual(self.dispatch.state, "signed_partial")

    def test_one_exception_then_dispatch_exception(self):
        """有一个异常任务时派车单应变delivery_exception"""
        self.env["tms.driver.task"].create({
            "dispatch_order_id": self.dispatch.id, "state": "delivery_exception",
        })
        self.dispatch._sync_state_from_tasks()
        self.assertEqual(self.dispatch.state, "delivery_exception")

    def test_departed_tasks_then_dispatch_departed(self):
        """任务departed时派车单应变departed"""
        self.env["tms.driver.task"].create({
            "dispatch_order_id": self.dispatch.id, "state": "departed",
        })
        self.dispatch._sync_state_from_tasks()
        self.assertEqual(self.dispatch.state, "departed")

    def test_no_tasks_state_unchanged(self):
        """无任务时状态不变"""
        original = self.dispatch.state
        self.dispatch._sync_state_from_tasks()
        self.assertEqual(self.dispatch.state, original)


class TestDriverTaskStateValidation(TransactionCase):
    """司机任务状态校验 — 不允许倒退/跳步"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1) or self.env["stock.warehouse"].create({"name": "WH-VAL", "code": "WV"})
        self.batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-VAL", "delivery_date": "2026-06-01",
            "route_status": "route_planned", "warehouse_id": self.wh.id,
        })
        self.dispatch = self.env["tms.dispatch.order"].create({
            "route_batch_id": self.batch.id,
        })
        self.task = self.env["tms.driver.task"].create({
            "dispatch_order_id": self.dispatch.id,
        })

    def test_signed_task_cannot_start_delivery(self):
        """已签收任务不能重新开始配送"""
        self.task.state = "signed_full"
        result = self.task.action_start_delivery()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("已签收", result["params"]["message"])

    def test_exception_task_cannot_start_delivery(self):
        """异常任务不能开始配送"""
        self.task.state = "delivery_exception"
        result = self.task.action_start_delivery()
        self.assertEqual(result["type"], "ir.actions.client")

    def test_not_departed_cannot_arrive_store(self):
        """未在途/出发的任务不能标记到店"""
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

    def test_normal_flow_arrived_to_signed(self):
        """正常到店→签收可通过"""
        self.task.state = "arrived_store"
        result = self.task.action_mark_signed_full()
        self.assertNotEqual(result.get("type"), "ir.actions.client")


class TestPushToDispatch(TransactionCase):
    """排线批次推送派车"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1) or self.env["stock.warehouse"].create({"name": "WH-PUSH", "code": "WP"})

    def test_push_creates_dispatch_with_driver_tasks(self):
        """推送应创建派车单+司机任务"""
        batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-PUSH-OK", "delivery_date": "2026-06-01",
            "route_status": "route_planned", "warehouse_id": self.wh.id,
        })
        wb = self.env["logistics.dispatch.waybill"].create({
            "name": "YD-PUSH", "warehouse_id": self.wh.id,
        })
        self.env["logistics.route.planning.stop.line"].create({
            "batch_id": batch.id, "stop_seq": 1,
            "store_name": "A", "waybill_no": "YD-PUSH",
            "longitude": 113.5, "latitude": 23.1, "address_detail": "测试",
        })
        result = batch.action_push_to_dispatch()
        self.assertEqual(result["type"], "ir.actions.act_window")
        d = self.env["tms.dispatch.order"].search([("route_batch_id", "=", batch.id)], limit=1)
        self.assertTrue(d)
        self.assertEqual(d.state, "dispatched")

    def test_push_no_stops_blocked(self):
        """无停靠点推送应拦截"""
        batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-PUSH-NO", "delivery_date": "2026-06-01",
            "route_status": "route_planned", "warehouse_id": self.wh.id,
        })
        result = batch.action_push_to_dispatch()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("没有停靠点", result["params"]["message"])

    def test_push_idempotent_no_duplicate(self):
        """重复推送不创建重复派车单"""
        batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-PUSH-DUP", "delivery_date": "2026-06-01",
            "route_status": "route_planned", "warehouse_id": self.wh.id,
        })
        wb = self.env["logistics.dispatch.waybill"].create({
            "name": "YD-PUSH-DUP", "warehouse_id": self.wh.id,
        })
        self.env["logistics.route.planning.stop.line"].create({
            "batch_id": batch.id, "stop_seq": 1,
            "store_name": "B", "waybill_no": "YD-PUSH-DUP",
            "longitude": 113.5, "latitude": 23.1, "address_detail": "测试",
        })
        batch.action_push_to_dispatch()
        batch.action_push_to_dispatch()
        count = self.env["tms.dispatch.order"].search_count([("route_batch_id", "=", batch.id)])
        self.assertEqual(count, 1)


class TestRouteBatchOpenMethods(TransactionCase):
    """排线批次open方法"""

    def setUp(self):
        super().setUp()
        self.batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-OPEN", "delivery_date": "2026-06-01",
            "route_status": "route_planned",
        })

    def test_action_open_route_map(self):
        """路线地图返回URL动作"""
        action = self.batch.action_open_route_map()
        self.assertEqual(action["type"], "ir.actions.act_url")
        self.assertIn("/tms/route/", action["url"])

    def test_action_open_dispatch_orders(self):
        """打开派车单返回窗口动作"""
        action = self.batch.action_open_dispatch_orders()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "tms.dispatch.order")

    def test_action_open_handover_orders(self):
        """打开交接单返回窗口动作"""
        action = self.batch.action_open_handover_orders()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "wms.handover.order")
