"""logistics_trace_evidence 模块单测 — mock 模式。"""

import unittest
from unittest.mock import MagicMock
from test_helpers import MockRecord, MockRecordset, EMPTY
from odoo.exceptions import ValidationError

from custom_addons.logistics_trace_evidence.models.logistics_trace_evidence import (
    LogisticsTraceEvidence,
)


# ── upload_role 别名解析 ──────────────────────────────────────────

class TestUploadRoleResolve(unittest.TestCase):

    def test_store_maps_to_warehouse(self):
        result = LogisticsTraceEvidence._resolve_upload_role(None, {"upload_role": "store"})
        self.assertEqual(result, "warehouse")

    def test_keeper_maps_to_warehouse(self):
        result = LogisticsTraceEvidence._resolve_upload_role(None, {"upload_role": "keeper"})
        self.assertEqual(result, "warehouse")

    def test_truck_driver_maps_to_driver(self):
        result = LogisticsTraceEvidence._resolve_upload_role(None, {"upload_role": "truck_driver"})
        self.assertEqual(result, "driver")

    def test_driver_stays_driver(self):
        result = LogisticsTraceEvidence._resolve_upload_role(None, {"upload_role": "driver"})
        self.assertEqual(result, "driver")

    def test_unknown_maps_to_unknown(self):
        result = LogisticsTraceEvidence._resolve_upload_role(None, {"upload_role": "xyz"})
        self.assertEqual(result, "unknown")

    def test_empty_defaults_to_unknown(self):
        result = LogisticsTraceEvidence._resolve_upload_role(None, {})
        self.assertEqual(result, "unknown")


# ── compute: uploader_name ────────────────────────────────────────

class TestEvidenceCompute(unittest.TestCase):

    def test_uploader_name(self):
        r = MockRecord(uploader_id=MockRecord(name="上传人A"))
        LogisticsTraceEvidence._compute_uploader_name(MockRecordset([r]))
        self.assertEqual(r.uploader_name, "上传人A")

    def test_uploader_name_empty(self):
        r = MockRecord(uploader_id=EMPTY)
        LogisticsTraceEvidence._compute_uploader_name(MockRecordset([r]))
        self.assertEqual(r.uploader_name, "")


# ── compute: trace_event_fields ───────────────────────────────────

class TestEvidenceTraceEventFields(unittest.TestCase):

    def test_copies_event_fields(self):
        event = MockRecord(
            event_type="arrive_store",
            trace_time="2026-05-20 10:00:00",
            display_name="到店 - 2026-05-20",
        )
        r = MockRecord(trace_event_id=event)
        LogisticsTraceEvidence._compute_trace_event_fields(MockRecordset([r]))
        self.assertEqual(r.trace_event_type, "arrive_store")
        self.assertEqual(r.trace_event_time, "2026-05-20 10:00:00")

    def test_exception_flag(self):
        r = MockRecord(trace_event_id=MockRecord(event_type="exception_report"))
        LogisticsTraceEvidence._compute_exception_flags(MockRecordset([r]))
        self.assertTrue(r.is_exception_related)

    def test_non_exception_flag(self):
        r = MockRecord(trace_event_id=MockRecord(event_type="arrive_store"))
        LogisticsTraceEvidence._compute_exception_flags(MockRecordset([r]))
        self.assertFalse(r.is_exception_related)


# ── compute: evidence_count on trace_event ────────────────────────

class TestTraceEventEvidenceCount(unittest.TestCase):

    def test_evidence_count(self):
        from custom_addons.logistics_trace_evidence.models.logistics_trace_event import (
            LogisticsTraceEvent as EventEvidenceMixin,
        )
        r = MockRecord(evidence_ids=MockRecordset([MockRecord(), MockRecord(), MockRecord()]))
        EventEvidenceMixin._compute_evidence_count(MockRecordset([r]))
        self.assertEqual(r.evidence_count, 3)

    def test_evidence_count_zero(self):
        from custom_addons.logistics_trace_evidence.models.logistics_trace_event import (
            LogisticsTraceEvent as EventEvidenceMixin,
        )
        r = MockRecord(evidence_ids=MockRecordset([]))
        EventEvidenceMixin._compute_evidence_count(MockRecordset([r]))
        self.assertEqual(r.evidence_count, 0)


if __name__ == "__main__":
    unittest.main()
