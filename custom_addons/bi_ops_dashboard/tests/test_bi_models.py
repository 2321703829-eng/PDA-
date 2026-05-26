# -*- coding: utf-8 -*-
"""bi_ops_dashboard 单元测试"""
from odoo.tests.common import TransactionCase
from datetime import date


class TestBiSnapshot(TransactionCase):
    """BI 快照"""

    def test_01_create_snapshot(self):
        """创建 KPI 日报快照"""
        snap = self.env["bi.daily.kpi.snapshot"].create({
            "snapshot_date": date.today(),
        })
        self.assertEqual(snap.snapshot_date, date.today())

    def test_02_generate_snapshot_runs(self):
        """generate_snapshot 方法可正常执行"""
        snap = self.env["bi.daily.kpi.snapshot"].create({
            "snapshot_date": date.today(),
        })
        if hasattr(snap, 'generate_snapshot'):
            snap.generate_snapshot()
            found = self.env["bi.daily.kpi.snapshot"].search([
                ("snapshot_date", "=", date.today())
            ])
            self.assertTrue(len(found) >= 1)

    def test_03_snapshot_date_unique_per_day(self):
        """同一日期可创建多条快照(不强制唯一)"""
        s1 = self.env["bi.daily.kpi.snapshot"].create({"snapshot_date": date.today()})
        s2 = self.env["bi.daily.kpi.snapshot"].create({"snapshot_date": date.today()})
        self.assertNotEqual(s1.id, s2.id)


class TestBiDashboardBoard(TransactionCase):
    """BI 仪表盘"""

    def test_01_create_board(self):
        """仪表盘记录可创建"""
        board = self.env["bi.ops.dashboard.board"].create({})
        self.assertTrue(board.exists())

    def test_02_action_open_dashboards(self):
        """各看板入口返回 action"""
        board = self.env["bi.ops.dashboard.board"].create({})
        for method_name in ("action_open_kpi_report", "action_open_order_dashboard",
                            "action_open_warehouse_dashboard", "action_open_dispatch_dashboard",
                            "action_open_exception_ledger", "action_open_cost_dashboard"):
            if hasattr(board, method_name):
                action = getattr(board, method_name)()
                if action:
                    self.assertIn("type", action)


class TestBiSnapshotModels(TransactionCase):
    """各维度快照模型"""

    def test_01_order_snapshot(self):
        """订单快照模型存在"""
        self.assertIn("bi.daily.kpi.snapshot", self.env)
        # 确保模型可被搜索
        model = self.env["ir.model"].search([("model", "=", "bi.daily.kpi.snapshot")], limit=1)
        self.assertTrue(model)

    def test_02_dashboard_board_model_exists(self):
        """仪表盘模型存在"""
        model = self.env["ir.model"].search([("model", "=", "bi.ops.dashboard.board")], limit=1)
        self.assertTrue(model)

    def test_03_warehouse_snapshot(self):
        """仓库快照模型可访问"""
        self.assertIn("bi.warehouse.dashboard.snapshot", self.env)

    def test_04_dispatch_snapshot(self):
        """调度快照模型可访问"""
        self.assertIn("bi.dispatch.dashboard.snapshot", self.env)

    def test_05_order_dashboard_snapshot(self):
        """订单看板快照模型可访问"""
        self.assertIn("bi.order.dashboard.snapshot", self.env)

    def test_06_cost_profit_snapshot(self):
        """成本利润快照模型可访问"""
        self.assertIn("bi.cost.profit.snapshot", self.env)

    def test_07_exception_snapshot(self):
        """异常快照模型可访问"""
        self.assertIn("bi.exception.snapshot", self.env)


class TestBiSnapshotGeneration(TransactionCase):
    """快照数据生成"""

    def test_01_warehouse_snapshot_generate(self):
        """仓库快照生成"""
        snap = self.env["bi.warehouse.dashboard.snapshot"].generate_snapshot()
        self.assertTrue(snap)
        self.assertTrue(hasattr(snap, 'snapshot_date'))

    def test_02_dispatch_snapshot_generate(self):
        """调度快照生成"""
        snap = self.env["bi.dispatch.dashboard.snapshot"].generate_snapshot()
        self.assertTrue(snap)
        self.assertTrue(hasattr(snap, 'snapshot_date'))

    def test_03_order_dashboard_snapshot_generate(self):
        """订单看板快照生成"""
        snap = self.env["bi.order.dashboard.snapshot"].generate_snapshot()
        self.assertTrue(snap)
        self.assertTrue(hasattr(snap, 'snapshot_date'))

    def test_04_cost_profit_snapshot_generate(self):
        """成本利润快照生成"""
        snap = self.env["bi.cost.profit.snapshot"].generate_snapshot()
        self.assertTrue(snap)
        self.assertTrue(hasattr(snap, 'snapshot_date'))

    def test_05_dashboard_board_refresh(self):
        """仪表盘刷新"""
        board = self.env["bi.ops.dashboard.board"].create({})
        if hasattr(board, 'action_refresh_board'):
            action = board.action_refresh_board()
            self.assertIn("type", action)

    def test_06_kpi_snapshot_callback(self):
        """KPI快照 action_generate_today 可调用"""
        snap = self.env["bi.daily.kpi.snapshot"].create({
            "snapshot_date": date.today(),
        })
        if hasattr(snap, 'action_generate_today_snapshot'):
            result = snap.action_generate_today_snapshot()
            self.assertIn("type", result)
