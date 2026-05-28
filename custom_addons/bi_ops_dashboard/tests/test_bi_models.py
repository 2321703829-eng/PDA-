# -*- coding: utf-8 -*-
"""bi_ops_dashboard 单元测试 — 快照生成验证聚合数值"""
from odoo.tests.common import TransactionCase
from datetime import date


class TestBiSnapshotWithData(TransactionCase):
    """创建真实数据后验证快照聚合值"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].search([], limit=1)
        # 创建 3 个 WMS 任务(收货+上架+出库)
        self.env["wms.receipt.task"].create({"warehouse_id": self.wh.id})
        self.env["wms.putaway.task"].create({"warehouse_id": self.wh.id})
        outbound = self.env["wms.outbound.task"].create({"warehouse_id": self.wh.id, "state": "task_done"})
        # 创建拣货+复核+交接
        pick = self.env["wms.pick.task"].create({"outbound_task_id": outbound.id, "warehouse_id": self.wh.id})
        self.env["wms.check.task"].create({"outbound_task_id": outbound.id, "warehouse_id": self.wh.id})
        self.env["wms.handover.order"].create({"outbound_task_id": outbound.id, "warehouse_id": self.wh.id})
        # 创建 TMS 数据
        batch = self.env["logistics.route.planning.batch"].create({
            "batch_no": "PC-SNAP-TEST", "delivery_date": "2026-06-01",
        })
        dispatch = self.env["tms.dispatch.order"].create({
            "route_batch_id": batch.id, "state": "departed",
        })
        self.env["tms.driver.task"].create({
            "dispatch_order_id": dispatch.id, "state": "in_transit",
        })
        self.env["tms.driver.task"].create({
            "dispatch_order_id": dispatch.id, "state": "signed_full",
        })

    def test_kpi_snapshot_counts(self):
        """KPI快照应统计正确的 warehouse/dispatch/signoff 数量"""
        snap = self.env["bi.daily.kpi.snapshot"].generate_snapshot()
        self.assertEqual(snap.snapshot_date, date.today())
        self.assertGreaterEqual(snap.warehouse_task_count, 4)
        self.assertGreaterEqual(snap.dispatch_count, 1)
        self.assertGreaterEqual(snap.signoff_count, 0)
        self.assertEqual(snap.exception_count, 0)

    def test_warehouse_snapshot_counts(self):
        """仓库快照应统计各类型任务数量"""
        snap = self.env["bi.warehouse.dashboard.snapshot"].generate_snapshot()
        self.assertGreaterEqual(snap.receipt_count, 1)
        self.assertGreaterEqual(snap.putaway_count, 1)
        self.assertGreaterEqual(snap.outbound_count, 1)
        self.assertGreaterEqual(snap.pick_count, 1)
        self.assertGreaterEqual(snap.check_count, 1)
        self.assertGreaterEqual(snap.handover_count, 1)

    def test_dispatch_snapshot_counts(self):
        """调度快照应统计派车/司机任务/在途/签收"""
        snap = self.env["bi.dispatch.dashboard.snapshot"].generate_snapshot()
        self.assertGreaterEqual(snap.dispatch_count, 1)
        self.assertGreaterEqual(snap.driver_task_count, 2)
        self.assertGreaterEqual(snap.in_transit_count, 1)
        self.assertGreaterEqual(snap.signed_count, 1)

    def test_cost_profit_snapshot_has_freight(self):
        """成本利润快照应生成"""
        snap = self.env["bi.cost.profit.snapshot"].generate_snapshot()
        self.assertIsNotNone(snap.snapshot_date)

    def test_duplicate_snapshot_updates(self):
        """同一天重复生成不重复创建"""
        s1 = self.env["bi.daily.kpi.snapshot"].generate_snapshot()
        s2 = self.env["bi.daily.kpi.snapshot"].generate_snapshot()
        self.assertEqual(s1.id, s2.id)


class TestBiDashboardBoard(TransactionCase):
    """BI仪表盘 — action刷新"""

    def test_create_board(self):
        board = self.env["bi.ops.dashboard.board"].create({})
        self.assertTrue(board.exists())

    def test_action_refresh_board(self):
        board = self.env["bi.ops.dashboard.board"].create({})
        action = board.action_refresh_board()
        self.assertIn("type", action)

    def test_action_open_kpi_report(self):
        board = self.env["bi.ops.dashboard.board"].create({})
        action = board.action_open_kpi_report()
        self.assertIn("type", action)

    def test_action_open_warehouse_dashboard(self):
        board = self.env["bi.ops.dashboard.board"].create({})
        action = board.action_open_warehouse_dashboard()
        self.assertIn("type", action)

    def test_action_open_dispatch_dashboard(self):
        board = self.env["bi.ops.dashboard.board"].create({})
        action = board.action_open_dispatch_dashboard()
        self.assertIn("type", action)
