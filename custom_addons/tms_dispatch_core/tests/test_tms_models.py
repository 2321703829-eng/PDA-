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
            "entry_mode": "manual",
            "planning_state": "waiting_route",
            "route_status": "waiting_route",
        })
        self.assertEqual(batch.batch_no, "PC-TEST-001")
        self.assertEqual(batch.planning_state, "waiting_route")

    def test_02_planning_state_selection(self):
        """排线计划状态枚举"""
        batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-STATE-TEST",
            "delivery_date": "2026-06-01",
            "entry_mode": "manual",
            "planning_state": "waiting_route",
            "route_status": "waiting_route",
        })
        valid_states = ["waiting_route", "result_ready", "first_reviewed",
                        "backfilled", "second_reviewed", "resource_assigned",
                        "pushed_dispatch", "returned_replan"]
        for state in valid_states:
            batch.planning_state = state
            self.assertEqual(batch.planning_state, state)

    def test_03_route_status_selection(self):
        """路线状态枚举"""
        batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-ROUTE-TEST",
            "delivery_date": "2026-06-01",
            "entry_mode": "manual",
            "planning_state": "waiting_route",
            "route_status": "waiting_route",
        })
        for status in ("waiting_route", "route_planned", "route_confirmed"):
            batch.route_status = status
            self.assertEqual(batch.route_status, status)

    def test_04_entry_mode_selection(self):
        """入口模式枚举"""
        batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-ENTRY-TEST",
            "delivery_date": "2026-06-01",
            "entry_mode": "manual",
            "planning_state": "waiting_route",
            "route_status": "waiting_route",
        })
        for mode in ("handover_pool", "import_sheet", "manual"):
            batch.entry_mode = mode
            self.assertEqual(batch.entry_mode, mode)

    def test_05_vehicle_and_driver_binding(self):
        """排线批次绑定车牌和司机"""
        batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-DRIVER-TEST",
            "delivery_date": "2026-06-01",
            "entry_mode": "manual",
            "planning_state": "result_ready",
            "route_status": "route_planned",
            "vehicle_no": "粤AAJ2702",
            "driver_name": "测试司机",
            "driver_phone": "13800138000",
        })
        self.assertEqual(batch.vehicle_no, "粤AAJ2702")
        self.assertEqual(batch.driver_name, "测试司机")

    def test_06_stop_count_field(self):
        """站点数可正常存储"""
        batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-STOP-TEST",
            "delivery_date": "2026-06-01",
            "entry_mode": "manual",
            "planning_state": "waiting_route",
            "route_status": "waiting_route",
            "stop_count": 8,
        })
        self.assertEqual(batch.stop_count, 8)


class TestRouteStopLine(TransactionCase):
    """排线停靠站点"""

    def setUp(self):
        super().setUp()
        self.batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-STOPLINE",
            "delivery_date": "2026-06-01",
            "entry_mode": "manual",
            "planning_state": "waiting_route",
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


class TestTmsDispatchOrder(TransactionCase):
    """TMS 派车单"""

    def setUp(self):
        super().setUp()
        self.batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-DISPATCH",
            "delivery_date": "2026-06-01",
            "entry_mode": "manual",
            "planning_state": "result_ready",
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

    def test_03_action_dispatch(self):
        """执行派车操作"""
        dispatch = self.env["tms.dispatch.order"].create({
            "route_batch_id": self.batch.id,
        })
        dispatch.action_dispatch()
        self.assertEqual(dispatch.state, "dispatched")


class TestTmsDriverTask(TransactionCase):
    """TMS 司机任务"""

    def setUp(self):
        super().setUp()
        self.batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-DRIVER-TASK",
            "delivery_date": "2026-06-01",
            "entry_mode": "manual",
            "planning_state": "result_ready",
            "route_status": "route_planned",
        })
        self.dispatch = self.env["tms.dispatch.order"].create({
            "route_batch_id": self.batch.id,
        })

    def test_01_create_driver_task(self):
        """创建司机任务"""
        task = self.env["tms.driver.task"].create({
            "dispatch_order_id": self.dispatch.id,
        })
        self.assertIsNotNone(task)

    def test_02_create_task_node(self):
        """创建司机任务节点"""
        task = self.env["tms.driver.task"].create({
            "dispatch_order_id": self.dispatch.id,
        })
        partner = self.env["res.partner"].create({"name": "节点门店"})
        node = self.env["tms.driver.task.node"].create({
            "driver_task_id": task.id,
            "store_id": partner.id,
            "sequence": 1,
            "state": "departed",
        })
        self.assertEqual(node.state, "departed")

    def test_03_node_state_selection(self):
        """节点状态枚举全部可接受"""
        task = self.env["tms.driver.task"].create({
            "dispatch_order_id": self.dispatch.id,
        })
        partner = self.env["res.partner"].create({"name": "状态测试"})
        node = self.env["tms.driver.task.node"].create({
            "driver_task_id": task.id,
            "store_id": partner.id,
            "sequence": 1,
            "state": "driver_arrived_warehouse",
        })
        for state in ("driver_arrived_warehouse", "departed", "in_transit",
                      "arrived_store", "delivering"):
            node.state = state
            self.assertEqual(node.state, state)
