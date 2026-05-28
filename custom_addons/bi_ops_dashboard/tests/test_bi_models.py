"""bi_ops_dashboard 模块单测 — mock 模式。"""

import unittest
from datetime import date
from unittest.mock import MagicMock
from test_helpers import MockRecord, MockRecordset, EMPTY

from custom_addons.bi_ops_dashboard.models.bi_snapshot_models import (
    BiSnapshotMixin,
)


# ── _day_range ────────────────────────────────────────────────────

class TestDayRange(unittest.TestCase):

    def test_returns_start_and_end(self):
        start, end = BiSnapshotMixin._day_range(None, date(2026, 5, 20))
        self.assertIn("2026-05-20", start)
        self.assertIn("2026-05-20", end)

    def test_string_date_input(self):
        start, end = BiSnapshotMixin._day_range(None, "2026-01-15")
        self.assertIn("2026-01-15", start)
        self.assertIn("2026-01-15", end)


if __name__ == "__main__":
    unittest.main()
