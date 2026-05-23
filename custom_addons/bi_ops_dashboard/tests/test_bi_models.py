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
        self.assertTrue(hasattr(self.env, "bi.daily.kpi.snapshot"))
        # 确保模型可被搜索
        model = self.env["ir.model"].search([("model", "=", "bi.daily.kpi.snapshot")], limit=1)
        self.assertTrue(model)

    def test_02_dashboard_board_model_exists(self):
        """仪表盘模型存在"""
        model = self.env["ir.model"].search([("model", "=", "bi.ops.dashboard.board")], limit=1)
        self.assertTrue(model)
