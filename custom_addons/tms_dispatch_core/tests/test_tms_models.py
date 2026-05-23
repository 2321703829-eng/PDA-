# -*- coding: utf-8 -*-
"""tms_dispatch_core 排线调度单元测试"""
from odoo.tests.common import TransactionCase


class TestRoutePlanningBatch(TransactionCase):
    """排线批次"""

    def test_01_create_batch(self):
        """创建排线批次"""
        batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-TEST-001",
            "delivery_date": "2026-06-01",
            "route_status": "waiting_route",
        })
        self.assertEqual(batch.batch_no, "PC-TEST-001")
        self.assertEqual(batch.route_status, "waiting_route")

    def test_02_route_status_selection(self):
        """路线状态枚举"""
        batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-ROUTE-TEST",
            "delivery_date": "2026-06-01",
            "route_status": "waiting_route",
        })
        for status in ("waiting_route", "route_planned", "route_confirmed"):
            batch.route_status = status
            self.assertEqual(batch.route_status, status)

    def test_03_vehicle_and_driver_binding(self):
        """排线批次绑定车牌和司机"""
        batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-DRIVER-TEST",
            "delivery_date": "2026-06-01",
            "route_status": "route_planned",
            "vehicle_no": "粤AAJ2702",
            "driver_name": "测试司机",
            "driver_phone": "13800138000",
        })
        self.assertEqual(batch.vehicle_no, "粤AAJ2702")
        self.assertEqual(batch.driver_name, "测试司机")


class TestRouteStopLine(TransactionCase):
    """排线停靠站点"""

    def setUp(self):
        super().setUp()
        self.batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-STOPLINE",
            "delivery_date": "2026-06-01",
            "route_status": "waiting_route",
        })

    def test_01_create_stop_line(self):
        """创建停靠站点"""
        stop = self.env["logistics.route.planning.stop.line"].create({
            "batch_id": self.batch.id,
            "stop_seq": 1,
            "store_name": "测试门店",
            "waybill_no": "YD-TEST-001",
            "longitude": 113.53,
            "latitude": 23.08,
            "address_detail": "测试地址",
        })
        self.assertEqual(stop.store_name, "测试门店")
        self.assertEqual(stop.stop_seq, 1)

    def test_02_multiple_stops_ordering(self):
        """多站点按stop_seq排序"""
        s1 = self.env["logistics.route.planning.stop.line"].create({
            "batch_id": self.batch.id, "stop_seq": 3,
            "store_name": "门店C", "waybill_no": "YD-C",
            "longitude": 113.5, "latitude": 23.1, "address_detail": "地址C",
        })
        s2 = self.env["logistics.route.planning.stop.line"].create({
            "batch_id": self.batch.id, "stop_seq": 1,
            "store_name": "门店A", "waybill_no": "YD-A",
            "longitude": 113.5, "latitude": 23.1, "address_detail": "地址A",
        })
        s3 = self.env["logistics.route.planning.stop.line"].create({
            "batch_id": self.batch.id, "stop_seq": 2,
            "store_name": "门店B", "waybill_no": "YD-B",
            "longitude": 113.5, "latitude": 23.1, "address_detail": "地址B",
        })
        sorted_stops = self.batch.stop_line_ids.sorted(key=lambda s: s.stop_seq)
        self.assertEqual(sorted_stops[0].store_name, "门店A")
        self.assertEqual(sorted_stops[1].store_name, "门店B")
        self.assertEqual(sorted_stops[2].store_name, "门店C")

    def test_03_stop_line_coordinates(self):
        """经纬度可正常存储"""
        stop = self.env["logistics.route.planning.stop.line"].create({
            "batch_id": self.batch.id, "stop_seq": 1,
            "store_name": "坐标点", "waybill_no": "YD-COORD",
            "longitude": 116.40, "latitude": 39.90,
            "address_detail": "北京",
        })
        self.assertAlmostEqual(stop.longitude, 116.40)
        self.assertAlmostEqual(stop.latitude, 39.90)


class TestRouteBatchActions(TransactionCase):
    """排线批次 action 方法"""

    def setUp(self):
        super().setUp()
        self.batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-ACT-TEST",
            "delivery_date": "2026-06-01",
            "route_status": "route_planned",
        })

    def test_01_action_open_route_map_returns_action(self):
        """路线地图 action 返回正确的窗口动作"""
        action = self.batch.action_open_route_map()
        self.assertEqual(action["type"], "ir.actions.act_url")
        self.assertIn("/tms/route/", action["url"])

    def test_02_action_open_handover_orders_returns_action(self):
        """Open Handover Orders 返回窗口动作"""
        action = self.batch.action_open_handover_orders()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "wms.handover.order")

    def test_03_action_open_dispatch_orders_returns_action(self):
        """Open Dispatch Orders 返回窗口动作"""
        action = self.batch.action_open_dispatch_orders()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "tms.dispatch.order")

    def test_04_action_open_driver_tasks_returns_action(self):
        """Open Driver Tasks 返回窗口动作"""
        action = self.batch.action_open_driver_tasks()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "tms.driver.task")


class TestWaybillTmsLinks(TransactionCase):
    """运单 TMS 联动查询"""

    def setUp(self):
        super().setUp()
        self.waybill = self.env["logistics.dispatch.waybill"].search([], limit=1)
        if not self.waybill:
            self.skipTest("无运单数据,跳过")

    def test_01_action_open_dispatch_orders(self):
        """运单→派车单查询动作"""
        action = self.waybill.action_open_related_dispatch_orders()
        if action:  # 可能返回空
            self.assertIn("type", action)

    def test_02_action_open_driver_tasks(self):
        """运单→司机任务查询动作"""
        action = self.waybill.action_open_related_driver_tasks()
        if action:
            self.assertIn("type", action)

    def test_03_action_open_signoff_receipts(self):
        """运单→签收回单查询动作"""
        action = self.waybill.action_open_related_signoff_receipts()
        if action:
            self.assertIn("type", action)


class TestTmsDispatchOrder(TransactionCase):
    """TMS 派车单"""

    def setUp(self):
        super().setUp()
        self.batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-DISPATCH",
            "delivery_date": "2026-06-01",
            "route_status": "route_planned",
        })

    def test_01_create_dispatch_order(self):
        """创建派车单"""
        dispatch = self.env["tms.dispatch.order"].create({
            "route_batch_id": self.batch.id,
        })
        self.assertEqual(dispatch.state, "waiting_dispatch")

    def test_02_dispatch_state_selection(self):
        """派车状态枚举全部可接受"""
        dispatch = self.env["tms.dispatch.order"].create({
            "route_batch_id": self.batch.id,
        })
        valid_states = ["waiting_dispatch", "dispatched", "departed",
                        "in_transit", "arrived_store", "signed_full",
                        "signed_partial", "delivery_exception"]
        for state in valid_states:
            dispatch.state = state
            self.assertEqual(dispatch.state, state)
