"""logistics_trace_exception 模块单测 — mock 模式。"""

import unittest
from unittest.mock import MagicMock
from datetime import datetime, timedelta
from test_helpers import MockRecord, MockRecordset, EMPTY
from odoo.exceptions import ValidationError, AccessError

from custom_addons.logistics_trace_exception.models.logistics_trace_exception import (
    LogisticsTraceException,
)
from custom_addons.logistics_trace_exception.models.logistics_trace_exception_process_log import (
    LogisticsTraceExceptionProcessLog,
)


def _model_rs(records=None, env=None):
    """创建带有 LogisticsTraceException 类属性的 MockRecordset。"""
    rs = MockRecordset(records, env)
    rs.CREATE_ALLOWED_STATES = LogisticsTraceException.CREATE_ALLOWED_STATES
    rs.FINAL_STATES = LogisticsTraceException.FINAL_STATES
    rs.ALLOWED_STATE_TRANSITIONS = LogisticsTraceException.ALLOWED_STATE_TRANSITIONS
    return rs


# ── _validate_create_vals ─────────────────────────────────────────

class TestValidateCreateVals(unittest.TestCase):

    def test_open_allowed(self):
        LogisticsTraceException._validate_create_vals(_model_rs(), {"state": "open"})

    def test_draft_allowed(self):
        LogisticsTraceException._validate_create_vals(_model_rs(), {"state": "draft"})

    def test_processing_not_allowed(self):
        with self.assertRaises(ValidationError):
            LogisticsTraceException._validate_create_vals(_model_rs(), {"state": "processing"})

    def test_closed_not_allowed(self):
        with self.assertRaises(ValidationError):
            LogisticsTraceException._validate_create_vals(_model_rs(), {"state": "closed"})

    def test_closed_time_in_create_raises(self):
        with self.assertRaises(ValidationError):
            LogisticsTraceException._validate_create_vals(_model_rs(), {
                "state": "open", "closed_time": datetime.now()
            })

    def test_default_state_open(self):
        LogisticsTraceException._validate_create_vals(_model_rs(), {})


# ── _ensure_state_transition_allowed ──────────────────────────────

class TestStateTransitions(unittest.TestCase):

    def test_draft_to_open(self):
        r = MockRecord(_id=1, state="draft")
        LogisticsTraceException._ensure_state_transition_allowed(
            _model_rs([r]), "open", {1: "draft"}
        )

    def test_draft_to_processing_blocked(self):
        r = MockRecord(_id=1, state="draft")
        with self.assertRaises(ValidationError):
            LogisticsTraceException._ensure_state_transition_allowed(
                _model_rs([r]), "processing", {1: "draft"}
            )

    def test_open_to_processing(self):
        r = MockRecord(_id=1, state="open")
        LogisticsTraceException._ensure_state_transition_allowed(
            _model_rs([r]), "processing", {1: "open"}
        )

    def test_open_to_closed_blocked(self):
        r = MockRecord(_id=1, state="open")
        with self.assertRaises(ValidationError):
            LogisticsTraceException._ensure_state_transition_allowed(
                _model_rs([r]), "closed", {1: "open"}
            )

    def test_processing_to_resolved(self):
        r = MockRecord(_id=1, state="processing")
        LogisticsTraceException._ensure_state_transition_allowed(
            _model_rs([r]), "resolved", {1: "processing"}
        )

    def test_processing_to_closed(self):
        r = MockRecord(_id=1, state="processing")
        LogisticsTraceException._ensure_state_transition_allowed(
            _model_rs([r]), "closed", {1: "processing"}
        )

    def test_closed_to_anything_blocked(self):
        r = MockRecord(_id=1, state="closed")
        with self.assertRaises(ValidationError):
            LogisticsTraceException._ensure_state_transition_allowed(
                _model_rs([r]), "open", {1: "closed"}
            )

    def test_same_state_no_error(self):
        r = MockRecord(_id=1, state="processing")
        LogisticsTraceException._ensure_state_transition_allowed(
            _model_rs([r]), "processing", {1: "processing"}
        )

    def test_cancelled_to_anything_blocked(self):
        r = MockRecord(_id=1, state="cancelled")
        with self.assertRaises(ValidationError):
            LogisticsTraceException._ensure_state_transition_allowed(
                _model_rs([r]), "open", {1: "cancelled"}
            )

    def test_resolved_to_closed(self):
        r = MockRecord(_id=1, state="resolved")
        LogisticsTraceException._ensure_state_transition_allowed(
            _model_rs([r]), "closed", {1: "resolved"}
        )

    def test_resolved_to_processing(self):
        """resolved 可退回 processing"""
        r = MockRecord(_id=1, state="resolved")
        LogisticsTraceException._ensure_state_transition_allowed(
            _model_rs([r]), "processing", {1: "resolved"}
        )


# ── _ensure_final_state_requirements ──────────────────────────────

class TestFinalStateRequirements(unittest.TestCase):

    def test_close_without_summary_raises(self):
        r = MockRecord(_id=1, close_summary="")
        with self.assertRaises(ValidationError):
            LogisticsTraceException._ensure_final_state_requirements(
                _model_rs([r]), "closed", {}
            )

    def test_close_with_summary_in_vals_ok(self):
        r = MockRecord(_id=1, close_summary="")
        LogisticsTraceException._ensure_final_state_requirements(
            _model_rs([r]), "closed", {"close_summary": "问题已解决"}
        )

    def test_close_with_summary_on_record_ok(self):
        r = MockRecord(_id=1, close_summary="已处理")
        LogisticsTraceException._ensure_final_state_requirements(
            _model_rs([r]), "closed", {}
        )

    def test_cancel_without_summary_raises(self):
        r = MockRecord(_id=1, close_summary="")
        with self.assertRaises(ValidationError):
            LogisticsTraceException._ensure_final_state_requirements(
                _model_rs([r]), "cancelled", {}
            )

    def test_non_final_state_no_check(self):
        r = MockRecord(_id=1, close_summary="")
        LogisticsTraceException._ensure_final_state_requirements(
            _model_rs([r]), "processing", {}
        )


# ── _compute_is_overdue ──────────────────────────────────────────

class TestComputeIsOverdue(unittest.TestCase):

    def test_open_and_old_is_overdue(self):
        r = MockRecord(state="open", report_time=datetime.now() - timedelta(days=2))
        LogisticsTraceException._compute_is_overdue(MockRecordset([r]))
        self.assertTrue(r.is_overdue)

    def test_open_and_recent_not_overdue(self):
        r = MockRecord(state="open", report_time=datetime.now() - timedelta(hours=12))
        LogisticsTraceException._compute_is_overdue(MockRecordset([r]))
        self.assertFalse(r.is_overdue)

    def test_closed_not_overdue(self):
        r = MockRecord(state="closed", report_time=datetime.now() - timedelta(days=5))
        LogisticsTraceException._compute_is_overdue(MockRecordset([r]))
        self.assertFalse(r.is_overdue)

    def test_no_report_time_not_overdue(self):
        r = MockRecord(state="open", report_time=False)
        LogisticsTraceException._compute_is_overdue(MockRecordset([r]))
        self.assertFalse(r.is_overdue)

    def test_processing_and_old_is_overdue(self):
        r = MockRecord(state="processing", report_time=datetime.now() - timedelta(days=3))
        LogisticsTraceException._compute_is_overdue(MockRecordset([r]))
        self.assertTrue(r.is_overdue)


# ── compute: exception_no / waybill_no ────────────────────────────

class TestExceptionCompute(unittest.TestCase):

    def test_exception_no_from_name(self):
        r = MockRecord(name="EXC-001")
        LogisticsTraceException._compute_exception_no(MockRecordset([r]))
        self.assertEqual(r.exception_no, "EXC-001")

    def test_waybill_no_from_waybill(self):
        r = MockRecord(waybill_id=MockRecord(name="YD-001"))
        LogisticsTraceException._compute_waybill_no(MockRecordset([r]))
        self.assertEqual(r.waybill_no, "YD-001")

    def test_waybill_no_empty(self):
        r = MockRecord(waybill_id=EMPTY)
        LogisticsTraceException._compute_waybill_no(MockRecordset([r]))
        self.assertEqual(r.waybill_no, "")


# ── waybill exception metrics ────────────────────────────────────

class TestWaybillExceptionMetrics(unittest.TestCase):

    def test_no_exceptions(self):
        from custom_addons.logistics_trace_exception.models.logistics_dispatch_waybill import (
            LogisticsDispatchWaybill as WaybillExcMixin,
        )
        r = MockRecord(exception_ids=MockRecordset([]))
        WaybillExcMixin._compute_exception_metrics(MockRecordset([r]))
        self.assertEqual(r.open_exception_count, 0)
        self.assertEqual(r.exception_status, "none")

    def test_open_exception(self):
        from custom_addons.logistics_trace_exception.models.logistics_dispatch_waybill import (
            LogisticsDispatchWaybill as WaybillExcMixin,
        )
        exc = MockRecord(state="open", severity_level="high")
        r = MockRecord(exception_ids=MockRecordset([exc]))
        WaybillExcMixin._compute_exception_metrics(MockRecordset([r]))
        self.assertEqual(r.open_exception_count, 1)
        self.assertEqual(r.exception_status, "open")


# ── Process Log 访问控制 ──────────────────────────────────────────

class TestProcessLogAccessControl(unittest.TestCase):

    def test_create_without_sudo_raises(self):
        env = MagicMock()
        env.su = False
        rs = MockRecordset([], env=env)
        with self.assertRaises(AccessError):
            LogisticsTraceExceptionProcessLog.create(rs, [{"note": "test"}])

    def test_write_without_sudo_raises(self):
        env = MagicMock()
        env.su = False
        rs = MockRecordset([MockRecord()], env=env)
        with self.assertRaises(AccessError):
            LogisticsTraceExceptionProcessLog.write(rs, {"note": "updated"})

    def test_unlink_without_sudo_raises(self):
        env = MagicMock()
        env.su = False
        rs = MockRecordset([MockRecord()], env=env)
        with self.assertRaises(AccessError):
            LogisticsTraceExceptionProcessLog.unlink(rs)


if __name__ == "__main__":
    unittest.main()
