"""tms_dispatch_core 模块单测 — mock 模式。"""

import unittest
from unittest.mock import MagicMock
from test_helpers import MockRecord, MockRecordset, EMPTY

from custom_addons.tms_dispatch_core.models.tms_dispatch_models import (
    TmsDispatchOrder,
    TmsDriverTask,
)


# ── _sync_state_from_tasks ────────────────────────────────────────

class TestSyncStateFromTasks(unittest.TestCase):

    def test_no_tasks_unchanged(self):
        r = MockRecord(state="dispatched", driver_task_ids=MockRecordset([]))
        TmsDispatchOrder._sync_state_from_tasks(MockRecordset([r]))
        self.assertEqual(r.state, "dispatched")

    def test_exception_wins(self):
        tasks = MockRecordset([
            MockRecord(state="in_transit"),
            MockRecord(state="delivery_exception"),
        ])
        r = MockRecord(state="dispatched", driver_task_ids=tasks)
        TmsDispatchOrder._sync_state_from_tasks(MockRecordset([r]))
        self.assertEqual(r.state, "delivery_exception")

    def test_all_signed_full(self):
        tasks = MockRecordset([
            MockRecord(state="signed_full"),
            MockRecord(state="signed_full"),
        ])
        r = MockRecord(state="dispatched", driver_task_ids=tasks)
        TmsDispatchOrder._sync_state_from_tasks(MockRecordset([r]))
        self.assertEqual(r.state, "signed_full")

    def test_mixed_signed_partial(self):
        """一个签收一个在途 → signed_partial"""
        tasks = MockRecordset([
            MockRecord(state="signed_full"),
            MockRecord(state="in_transit"),
        ])
        r = MockRecord(state="dispatched", driver_task_ids=tasks)
        TmsDispatchOrder._sync_state_from_tasks(MockRecordset([r]))
        self.assertEqual(r.state, "signed_partial")

    def test_arrived_store(self):
        tasks = MockRecordset([
            MockRecord(state="arrived_store"),
            MockRecord(state="departed"),
        ])
        r = MockRecord(state="dispatched", driver_task_ids=tasks)
        TmsDispatchOrder._sync_state_from_tasks(MockRecordset([r]))
        self.assertEqual(r.state, "arrived_store")

    def test_in_transit(self):
        tasks = MockRecordset([
            MockRecord(state="in_transit"),
            MockRecord(state="departed"),
        ])
        r = MockRecord(state="dispatched", driver_task_ids=tasks)
        TmsDispatchOrder._sync_state_from_tasks(MockRecordset([r]))
        self.assertEqual(r.state, "in_transit")

    def test_departed(self):
        tasks = MockRecordset([MockRecord(state="departed")])
        r = MockRecord(state="dispatched", driver_task_ids=tasks)
        TmsDispatchOrder._sync_state_from_tasks(MockRecordset([r]))
        self.assertEqual(r.state, "departed")


# ── Dispatch compute counts ───────────────────────────────────────

class TestDispatchComputeCounts(unittest.TestCase):

    def test_counts(self):
        tasks = MockRecordset([
            MockRecord(_id=1, state="departed"),
            MockRecord(_id=2, state="in_transit"),
            MockRecord(_id=3, state="signed_full"),
        ])
        fees = MockRecordset([
            MockRecord(amount=100.0),
            MockRecord(amount=200.5),
        ])
        env = MagicMock()
        env.__getitem__ = MagicMock(return_value=MagicMock(
            search_count=MagicMock(return_value=0)
        ))
        r = MockRecord(driver_task_ids=tasks, freight_fee_line_ids=fees)
        rs = MockRecordset([r], env=env)
        TmsDispatchOrder._compute_counts(rs)
        self.assertEqual(r.driver_task_count, 3)
        self.assertAlmostEqual(r.freight_fee_total, 300.5)
        self.assertEqual(r.departed_task_count, 1)
        self.assertEqual(r.in_transit_task_count, 1)
        self.assertEqual(r.signed_task_count, 1)


# ── Driver task latest node ───────────────────────────────────────

class TestDriverTaskLatestNode(unittest.TestCase):

    def test_latest_node(self):
        from datetime import datetime
        early = datetime(2026, 5, 20, 10, 0)
        late = datetime(2026, 5, 20, 14, 0)
        nodes = MockRecordset([
            MockRecord(_id=1, event_time=early, state="departed", latitude=30.0, longitude=120.0),
            MockRecord(_id=2, event_time=late, state="arrived_store", latitude=31.0, longitude=121.0),
        ])
        r = MockRecord(node_ids=nodes)
        TmsDriverTask._compute_latest_node(MockRecordset([r]))
        self.assertEqual(r.latest_node_state, "arrived_store")
        self.assertEqual(r.latest_node_time, late)
        self.assertEqual(r.node_count, 2)

    def test_no_nodes(self):
        env = MagicMock()
        env.__getitem__ = MagicMock(return_value=MockRecordset([]))
        r = MockRecord(node_ids=MockRecordset([]))
        TmsDriverTask._compute_latest_node(MockRecordset([r], env=env))
        self.assertFalse(r.latest_node_state)
        self.assertFalse(r.latest_node_time)
        self.assertEqual(r.node_count, 0)


if __name__ == "__main__":
    unittest.main()
