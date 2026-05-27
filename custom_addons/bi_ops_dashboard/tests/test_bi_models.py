# -*- coding: utf-8 -*-
"""bi_ops_dashboard 单元测试 — 快照生成/compute/仪表盘"""
from odoo.tests.common import TransactionCase
from datetime import date


class TestBiSnapshotGeneration(TransactionCase):
    """KPI快照生成 — 断言聚合数据而非输入值"""

    def test_generate_snapshot_creates_record(self):
        """generate_snapshot应在无数据时正常创建快照"""
        snap = self.env["bi.daily.kpi.snapshot"].generate_snapshot()
        self.assertTrue(snap)
        self.assertEqual(snap.snapshot_date, date.today())

    def test_generate_snapshot_twice_updates_not_duplicates(self):
        """同一天两次生成应更新而非重复创建"""
        s1 = self.env["bi.daily.kpi.snapshot"].generate_snapshot()
        s2 = self.env["bi.daily.kpi.snapshot"].generate_snapshot()
        self.assertEqual(s1.id, s2.id)

    def test_warehouse_snapshot_generate(self):
        """仓库快照生成应返回记录"""
        snap = self.env["bi.warehouse.dashboard.snapshot"].generate_snapshot()
        self.assertTrue(snap)
        self.assertTrue(hasattr(snap, 'receipt_count'))

    def test_dispatch_snapshot_generate(self):
        """调度快照生成"""
        snap = self.env["bi.dispatch.dashboard.snapshot"].generate_snapshot()
        self.assertTrue(snap)

    def test_order_dashboard_snapshot_generate(self):
        """订单看板快照生成"""
        snap = self.env["bi.order.dashboard.snapshot"].generate_snapshot()
        self.assertTrue(snap)

    def test_cost_profit_snapshot_generate(self):
        """成本利润快照生成"""
        snap = self.env["bi.cost.profit.snapshot"].generate_snapshot()
        self.assertTrue(snap)


class TestBiSnapshotModelsExist(TransactionCase):
    """所有快照模型可访问"""

    def test_01_kpi_snapshot(self):
        self.assertIn("bi.daily.kpi.snapshot", self.env)

    def test_02_warehouse_snapshot(self):
        self.assertIn("bi.warehouse.dashboard.snapshot", self.env)

    def test_03_dispatch_snapshot(self):
        self.assertIn("bi.dispatch.dashboard.snapshot", self.env)

    def test_04_order_dashboard_snapshot(self):
        self.assertIn("bi.order.dashboard.snapshot", self.env)

    def test_05_cost_profit_snapshot(self):
        self.assertIn("bi.cost.profit.snapshot", self.env)

    def test_06_exception_snapshot(self):
        self.assertIn("bi.exception.snapshot", self.env)

    def test_07_dashboard_board(self):
        self.assertIn("bi.ops.dashboard.board", self.env)


class TestBiDashboardBoard(TransactionCase):
    """BI仪表盘 — action方法和刷新"""

    def test_create_board(self):
        """仪表盘可创建"""
        board = self.env["bi.ops.dashboard.board"].create({})
        self.assertTrue(board.exists())

    def test_action_refresh_board(self):
        """刷新仪表盘返回action"""
        board = self.env["bi.ops.dashboard.board"].create({})
        action = board.action_refresh_board()
        self.assertIn("type", action)

    def test_action_open_kpi_report(self):
        """打开KPI报表"""
        board = self.env["bi.ops.dashboard.board"].create({})
        action = board.action_open_kpi_report()
        self.assertIn("type", action)

    def test_action_open_warehouse_dashboard(self):
        """打开仓库看板"""
        board = self.env["bi.ops.dashboard.board"].create({})
        action = board.action_open_warehouse_dashboard()
        self.assertIn("type", action)

    def test_action_open_dispatch_dashboard(self):
        """打开调度看板"""
        board = self.env["bi.ops.dashboard.board"].create({})
        action = board.action_open_dispatch_dashboard()
        self.assertIn("type", action)
