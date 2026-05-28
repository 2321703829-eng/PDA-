"""logistics_trace_core 模块单测 — mock 模式。"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from test_helpers import MockRecord, MockRecordset, EMPTY
from odoo.exceptions import ValidationError
from odoo import fields

from custom_addons.logistics_trace_core.models.logistics_trace_event import (
    LogisticsTraceEvent,
)
from custom_addons.logistics_trace_core.models.logistics_dispatch_waybill import (
    LogisticsDispatchWaybill as WaybillTraceMixin,
)


def _event_rs(records=None, env=None, is_manager=True):
    """带有正确 _is_trace_manager 方法的 MockRecordset。"""
    rs = MockRecordset(records, env)
    rs._is_trace_manager = lambda: is_manager
    if hasattr(LogisticsTraceEvent, "EVENT_SELECTION"):
        rs.EVENT_SELECTION = LogisticsTraceEvent.EVENT_SELECTION
    return rs


# ── _check_object_link 约束 ───────────────────────────────────────

class TestTraceEventObjectLink(unittest.TestCase):

    def test_batch_event_no_batch_raises(self):
        r = MockRecord(object_type="batch", batch_id=EMPTY, waybill_id=EMPTY)
        with self.assertRaises(ValidationError):
            LogisticsTraceEvent._check_object_link(MockRecordset([r]))

    def test_batch_event_with_waybill_raises(self):
        r = MockRecord(
            object_type="batch",
            batch_id=MockRecord(_id=1),
            waybill_id=MockRecord(_id=2),
        )
        with self.assertRaises(ValidationError):
            LogisticsTraceEvent._check_object_link(MockRecordset([r]))

    def test_batch_event_ok(self):
        r = MockRecord(object_type="batch", batch_id=MockRecord(_id=1), waybill_id=EMPTY)
        LogisticsTraceEvent._check_object_link(MockRecordset([r]))

    def test_waybill_event_no_waybill_raises(self):
        r = MockRecord(object_type="waybill", batch_id=MockRecord(_id=1), waybill_id=EMPTY)
        with self.assertRaises(ValidationError):
            LogisticsTraceEvent._check_object_link(MockRecordset([r]))

    def test_waybill_event_batch_mismatch_raises(self):
        batch_a = MockRecord(_id=1)
        batch_b = MockRecord(_id=2)
        r = MockRecord(
            object_type="waybill",
            batch_id=batch_a,
            waybill_id=MockRecord(_id=10, batch_id=batch_b),
        )
        with self.assertRaises(ValidationError):
            LogisticsTraceEvent._check_object_link(MockRecordset([r]))

    def test_waybill_event_ok(self):
        batch = MockRecord(_id=1)
        r = MockRecord(
            object_type="waybill",
            batch_id=batch,
            waybill_id=MockRecord(_id=10, batch_id=batch),
        )
        LogisticsTraceEvent._check_object_link(MockRecordset([r]))


# ── _normalize_trace_vals ─────────────────────────────────────────

class TestNormalizeTraceVals(unittest.TestCase):

    def test_auto_fill_batch_from_waybill(self):
        env = MagicMock()
        waybill_mock = MagicMock()
        waybill_mock.batch_id.id = 99
        env.__getitem__ = MagicMock(
            return_value=MagicMock(browse=MagicMock(return_value=waybill_mock))
        )
        rs = _event_rs(env=env, is_manager=True)
        result = LogisticsTraceEvent._normalize_trace_vals(rs, {"waybill_id": 10})
        self.assertEqual(result["batch_id"], 99)

    def test_non_manager_cannot_create_draft(self):
        rs = _event_rs(is_manager=False)
        rs.env = MagicMock()
        rs.env.user.id = 42
        with self.assertRaises(ValidationError):
            LogisticsTraceEvent._normalize_trace_vals(rs, {"state": "draft"})

    def test_non_manager_defaults_to_submitted(self):
        rs = _event_rs(is_manager=False)
        rs.env = MagicMock()
        rs.env.user.id = 42
        result = LogisticsTraceEvent._normalize_trace_vals(rs, {})
        self.assertEqual(result["state"], "submitted")
        self.assertEqual(result["submit_user_id"], 42)

    def test_manager_can_create_draft(self):
        rs = _event_rs(is_manager=True)
        result = LogisticsTraceEvent._normalize_trace_vals(rs, {"state": "draft"})
        self.assertEqual(result["state"], "draft")


# ── write 权限 ────────────────────────────────────────────────────

class TestTraceEventWriteGuards(unittest.TestCase):

    def test_non_manager_change_submit_user_raises(self):
        rs = _event_rs([MockRecord()], is_manager=False)
        with self.assertRaises(ValidationError):
            LogisticsTraceEvent.write(rs, {"submit_user_id": 99})

    def test_non_manager_change_state_raises(self):
        rs = _event_rs([MockRecord()], is_manager=False)
        with self.assertRaises(ValidationError):
            LogisticsTraceEvent.write(rs, {"state": "invalid"})


# ── _compute_trace_metrics ────────────────────────────────────────

class TestTraceMetrics(unittest.TestCase):

    def test_no_events_all_pending(self):
        r = MockRecord(trace_event_ids=MockRecordset([]))
        WaybillTraceMixin._compute_trace_metrics(MockRecordset([r]))
        self.assertEqual(r.trace_count, 0)
        self.assertEqual(r.arrive_trace_status, "pending")
        self.assertEqual(r.signoff_trace_status, "pending")
        self.assertFalse(r.latest_trace_time)

    def test_arrive_event_sets_done(self):
        now = datetime.now()
        event = MockRecord(
            state="submitted", event_type="arrive_store",
            trace_time=now, create_date=now, remark="到店",
            submit_user_name="张三",
        )
        r = MockRecord(trace_event_ids=MockRecordset([event]))
        WaybillTraceMixin._compute_trace_metrics(MockRecordset([r]))
        self.assertEqual(r.trace_count, 1)
        self.assertEqual(r.arrive_trace_status, "done")
        self.assertEqual(r.signoff_trace_status, "partial")

    def test_signoff_event_sets_done(self):
        now = datetime.now()
        events = MockRecordset([
            MockRecord(state="submitted", event_type="signoff", trace_time=now,
                       create_date=now, remark="签收", submit_user_name=""),
            MockRecord(state="submitted", event_type="arrive_store",
                       trace_time=now - timedelta(hours=1), create_date=now,
                       remark="到店", submit_user_name=""),
        ])
        r = MockRecord(trace_event_ids=events)
        WaybillTraceMixin._compute_trace_metrics(MockRecordset([r]))
        self.assertEqual(r.arrive_trace_status, "done")
        self.assertEqual(r.signoff_trace_status, "done")

    def test_draft_events_excluded(self):
        event = MockRecord(
            state="draft", event_type="arrive_store",
            trace_time=datetime.now(), create_date=datetime.now(),
            remark="", submit_user_name="",
        )
        r = MockRecord(trace_event_ids=MockRecordset([event]))
        WaybillTraceMixin._compute_trace_metrics(MockRecordset([r]))
        self.assertEqual(r.trace_count, 0)
        self.assertEqual(r.arrive_trace_status, "pending")


# ── _get_trace_driven_dispatch_state ──────────────────────────────

class TestTraceDrivenState(unittest.TestCase):

    def test_signoff_returns_done(self):
        events = MockRecordset([MockRecord(state="submitted", event_type="signoff")])
        r = MockRecord(trace_event_ids=events)
        rs = MockRecordset([r])
        result = WaybillTraceMixin._get_trace_driven_dispatch_state(rs)
        self.assertEqual(result, "done")

    def test_arrive_returns_arrived(self):
        events = MockRecordset([MockRecord(state="submitted", event_type="arrive_store")])
        r = MockRecord(trace_event_ids=events)
        rs = MockRecordset([r])
        result = WaybillTraceMixin._get_trace_driven_dispatch_state(rs)
        self.assertEqual(result, "arrived")

    def test_other_events_returns_in_transit(self):
        events = MockRecordset([MockRecord(state="submitted", event_type="depart_warehouse")])
        r = MockRecord(trace_event_ids=events)
        rs = MockRecordset([r])
        result = WaybillTraceMixin._get_trace_driven_dispatch_state(rs)
        self.assertEqual(result, "in_transit")

    def test_no_submitted_returns_false(self):
        events = MockRecordset([MockRecord(state="draft", event_type="signoff")])
        r = MockRecord(trace_event_ids=events)
        rs = MockRecordset([r])
        result = WaybillTraceMixin._get_trace_driven_dispatch_state(rs)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
