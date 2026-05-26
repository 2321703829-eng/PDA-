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

    def test_03_empty_input_guard_action_dispatch(self):
        """空输入派车返回通知而非异常"""
        result = self.env["tms.dispatch.order"].action_dispatch()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertEqual(result["tag"], "display_notification")
        self.assertIn("请先选择", result["params"]["message"])

    def test_04_empty_input_guard_action_depart(self):
        """空输入发车返回通知"""
        result = self.env["tms.dispatch.order"].action_depart()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("请先选择", result["params"]["message"])

    def test_05_empty_input_guard_action_generate_freight(self):
        """空输入生成运费返回通知"""
        result = self.env["tms.dispatch.order"].action_generate_freight_lines()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("请先选择", result["params"]["message"])

    def test_06_empty_input_guard_open_record(self):
        """空输入打开派车单记录返回通知"""
        result = self.env["tms.dispatch.order"].action_open_record()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("请先选择", result["params"]["message"])

    def test_07_action_dispatch_no_stops(self):
        """无停靠点时派车返回业务提示"""
        wh = self.env["stock.warehouse"].search([], limit=1)
        batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-NOSTOP", "delivery_date": "2026-06-01",
            "route_status": "route_planned", "warehouse_id": wh.id,
        })
        dispatch = self.env["tms.dispatch.order"].create({"route_batch_id": batch.id})
        result = dispatch.action_dispatch()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("没有停靠点", result["params"]["message"])


class TestTmsDriverTaskGuards(TransactionCase):
    """司机任务空输入守卫+状态校验"""

    def setUp(self):
        super().setUp()
        wh = self.env["stock.warehouse"].search([], limit=1)
        self.batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-GUARD", "delivery_date": "2026-06-01",
            "route_status": "route_planned", "warehouse_id": wh.id,
        })
        self.dispatch = self.env["tms.dispatch.order"].create({"route_batch_id": self.batch.id})
        self.task = self.env["tms.driver.task"].create({
            "dispatch_order_id": self.dispatch.id,
        })

    def test_01_empty_input_start_delivery(self):
        """空输入开始配送返回通知"""
        result = self.env["tms.driver.task"].action_start_delivery()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("请先选择", result["params"]["message"])

    def test_02_empty_input_arrive_store(self):
        """空输入到店返回通知"""
        result = self.env["tms.driver.task"].action_arrive_store()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("请先选择", result["params"]["message"])

    def test_03_empty_input_signed_full(self):
        """空输入全签返回通知"""
        result = self.env["tms.driver.task"].action_mark_signed_full()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("请先选择", result["params"]["message"])

    def test_04_empty_input_signed_partial(self):
        """空输入部分签收返回通知"""
        result = self.env["tms.driver.task"].action_mark_signed_partial()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("请先选择", result["params"]["message"])

    def test_05_empty_input_create_signoff(self):
        """空输入创建签收单返回通知"""
        result = self.env["tms.driver.task"].action_create_signoff_receipt()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("请先选择", result["params"]["message"])

    def test_06_empty_input_create_exception(self):
        """空输入创建异常返回通知"""
        result = self.env["tms.driver.task"].action_create_exception()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("请先选择", result["params"]["message"])

    def test_07_empty_input_open_record(self):
        """空输入打开司机任务记录返回通知"""
        result = self.env["tms.driver.task"].action_open_record()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("请先选择", result["params"]["message"])

    def test_08_empty_input_arrive_warehouse(self):
        """空输入到达仓库返回通知"""
        result = self.env["tms.driver.task"].action_arrive_warehouse()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("请先选择", result["params"]["message"])

    def test_09_empty_input_mark_delivering(self):
        """空输入标记配送中返回通知"""
        result = self.env["tms.driver.task"].action_mark_delivering()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("请先选择", result["params"]["message"])

    def test_10_empty_input_log_in_transit(self):
        """空输入记录在途返回通知"""
        result = self.env["tms.driver.task"].action_log_in_transit()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("请先选择", result["params"]["message"])

    def test_11_signed_task_cannot_start_delivery(self):
        """已签收任务不能重新开始配送"""
        self.task.state = "signed_full"
        result = self.task.action_start_delivery()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("已签收", result["params"]["message"])

    def test_12_not_in_transit_cannot_arrive_store(self):
        """未在途任务不能到店"""
        self.task.state = "waiting_dispatch"
        result = self.task.action_arrive_store()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("尚未开始配送", result["params"]["message"])

    def test_13_not_arrived_cannot_sign_full(self):
        """未到店任务不能全签"""
        self.task.state = "dispatched"
        result = self.task.action_mark_signed_full()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("尚未到店", result["params"]["message"])

    def test_14_not_arrived_cannot_sign_partial(self):
        """未到店任务不能部分签收"""
        self.task.state = "in_transit"
        result = self.task.action_mark_signed_partial()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("尚未到店", result["params"]["message"])

    def test_15_state_flow_arrive_then_sign(self):
        """正常到店→全签流程可通过状态校验"""
        self.task.state = "departed"
        r1 = self.task.action_start_delivery()
        self.assertNotEqual(r1.get("type"), "ir.actions.client")
        self.task.state = "arrived_store"
        r2 = self.task.action_mark_signed_full()
        self.assertNotEqual(r2.get("type"), "ir.actions.client")


class TestTmsSignoffExceptionGuards(TransactionCase):
    """签收单+配送异常空输入守卫"""

    def test_01_empty_input_confirm_signoff(self):
        """空输入确认签收返回通知"""
        result = self.env["tms.signoff.receipt"].action_confirm_signoff()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("请先选择", result["params"]["message"])

    def test_02_empty_input_signoff_open_record(self):
        """空输入打开签收单返回通知"""
        result = self.env["tms.signoff.receipt"].action_open_record()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("请先选择", result["params"]["message"])

    def test_03_empty_input_exception_open_record(self):
        """空输入打开配送异常返回通知"""
        result = self.env["tms.delivery.exception"].action_open_record()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("请先选择", result["params"]["message"])


class TestTmsPushToDispatch(TransactionCase):
    """排线批次推送派车"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1)

    def test_01_empty_input_push(self):
        """空输入推送返回通知"""
        result = self.env["logistics.route.planning.batch"].action_push_to_dispatch()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("请先选择", result["params"]["message"])

    def test_02_push_no_stops(self):
        """无停靠点推送返回提示"""
        batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-PUSH-NOSTOP", "delivery_date": "2026-06-01",
            "route_status": "route_planned", "warehouse_id": self.wh.id,
        })
        result = batch.action_push_to_dispatch()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("没有停靠点", result["params"]["message"])

    def test_03_push_creates_dispatch_order(self):
        """正常推送创建派车单"""
        batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-PUSH-OK", "delivery_date": "2026-06-01",
            "route_status": "route_planned", "warehouse_id": self.wh.id,
        })
        self.env["logistics.route.planning.stop.line"].create({
            "batch_id": batch.id, "stop_seq": 1,
            "store_name": "门店A", "waybill_no": "YD-PUSH-001",
            "longitude": 113.5, "latitude": 23.1, "address_detail": "测试",
        })
        result = batch.action_push_to_dispatch()
        self.assertEqual(result["type"], "ir.actions.act_window")
        dispatch_order = self.env["tms.dispatch.order"].search([("route_batch_id", "=", batch.id)], limit=1)
        self.assertTrue(dispatch_order)
        self.assertEqual(dispatch_order.state, "dispatched")

    def test_04_push_idempotent(self):
        """重复推送返回已有派车单"""
        batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-PUSH-DUP", "delivery_date": "2026-06-01",
            "route_status": "route_planned", "warehouse_id": self.wh.id,
        })
        self.env["logistics.route.planning.stop.line"].create({
            "batch_id": batch.id, "stop_seq": 1,
            "store_name": "门店B", "waybill_no": "YD-PUSH-DUP",
            "longitude": 113.5, "latitude": 23.1, "address_detail": "测试",
        })
        r1 = batch.action_push_to_dispatch()
        r2 = batch.action_push_to_dispatch()
        self.assertEqual(r1["type"], "ir.actions.act_window")
        self.assertEqual(r2["type"], "ir.actions.act_window")
        dispatch_count = self.env["tms.dispatch.order"].search_count([("route_batch_id", "=", batch.id)])
        self.assertEqual(dispatch_count, 1)
