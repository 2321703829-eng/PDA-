"""b2b_storefront 模块单测 — mock 模式。"""

import unittest
from test_helpers import MockRecord, MockRecordset, EMPTY

from custom_addons.b2b_storefront.models.b2b_cart_draft import (
    B2bCartDraft,
    B2bCartDraftLine,
)


# ── Cart compute ──────────────────────────────────────────────────

class TestCartCompute(unittest.TestCase):

    def test_total_qty_sums_lines(self):
        lines = [
            MockRecord(qty=3, subtotal=300),
            MockRecord(qty=2, subtotal=400),
        ]
        r = MockRecord(line_ids=lines)
        B2bCartDraft._compute_total(MockRecordset([r]))
        self.assertAlmostEqual(r.total_qty, 5.0)
        self.assertAlmostEqual(r.total_amount, 700.0)

    def test_total_empty_cart(self):
        r = MockRecord(line_ids=[])
        B2bCartDraft._compute_total(MockRecordset([r]))
        self.assertAlmostEqual(r.total_qty, 0.0)
        self.assertAlmostEqual(r.total_amount, 0.0)


class TestCartLineCompute(unittest.TestCase):

    def test_subtotal(self):
        r = MockRecord(qty=5, unit_price=30.0)
        B2bCartDraftLine._compute_subtotal(MockRecordset([r]))
        self.assertAlmostEqual(r.subtotal, 150.0)

    def test_subtotal_zero_qty(self):
        r = MockRecord(qty=0, unit_price=100.0)
        B2bCartDraftLine._compute_subtotal(MockRecordset([r]))
        self.assertAlmostEqual(r.subtotal, 0.0)


if __name__ == "__main__":
    unittest.main()
