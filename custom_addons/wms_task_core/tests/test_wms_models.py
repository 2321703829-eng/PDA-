"""wms_task_core 模块单测 — mock 模式。"""

import unittest
from unittest.mock import MagicMock
from test_helpers import MockRecord, MockRecordset, EMPTY

from custom_addons.wms_task_core.models.wms_inventory_models import (
    WmsInventoryOperation,
    WmsInventoryOperationLine,
)
from custom_addons.wms_task_core.models.wms_task_models import (
    WmsOutboundTask,
)


# ── Inventory compute ─────────────────────────────────────────────

class TestInventoryCompute(unittest.TestCase):

    def test_diff_qty(self):
        r = MockRecord(system_qty=100, count_qty=95)
        WmsInventoryOperationLine._compute_diff(MockRecordset([r]))
        self.assertEqual(r.diff_qty, -5)

    def test_diff_qty_zero(self):
        r = MockRecord(system_qty=50, count_qty=50)
        WmsInventoryOperationLine._compute_diff(MockRecordset([r]))
        self.assertEqual(r.diff_qty, 0)


class TestInventoryTotals(unittest.TestCase):

    def test_totals(self):
        lines = MockRecordset([
            MockRecord(system_qty=100, count_qty=90, diff_qty=-10),
            MockRecord(system_qty=200, count_qty=210, diff_qty=10),
        ])
        r = MockRecord(line_ids=lines)
        WmsInventoryOperation._compute_totals(MockRecordset([r]))
        self.assertEqual(r.line_count, 2)
        self.assertEqual(r.total_system_qty, 300)
        self.assertEqual(r.total_count_qty, 300)
        self.assertEqual(r.total_diff_qty, 0)

    def test_totals_empty(self):
        r = MockRecord(line_ids=MockRecordset([]))
        WmsInventoryOperation._compute_totals(MockRecordset([r]))
        self.assertEqual(r.line_count, 0)
        self.assertEqual(r.total_system_qty, 0)


class TestInventoryPickingFlags(unittest.TestCase):

    def test_has_generated_picking(self):
        r = MockRecord(generated_picking_id=MockRecord(_id=1), source_picking_id=EMPTY)
        WmsInventoryOperation._compute_generated_picking_flags(MockRecordset([r]))
        self.assertTrue(r.has_generated_picking)
        self.assertFalse(r.has_source_picking)

    def test_no_pickings(self):
        r = MockRecord(generated_picking_id=EMPTY, source_picking_id=EMPTY)
        WmsInventoryOperation._compute_generated_picking_flags(MockRecordset([r]))
        self.assertFalse(r.has_generated_picking)
        self.assertFalse(r.has_source_picking)


# ── Outbound 状态回写 ─────────────────────────────────────────────

class TestOutboundBackfillStatus(unittest.TestCase):

    def test_task_processing_sets_picking(self):
        """outbound state=task_processing → sale.wms_status=picking"""
        sale = MockRecord(wms_status="pending")
        picking = MockRecord(sale_id=sale)
        r = MockRecord(
            state="task_processing",
            stock_picking_id=picking,
        )
        WmsOutboundTask._backfill_sale_wms_status(MockRecordset([r]))
        self.assertEqual(sale.wms_status, "picking")

    def test_task_done_sets_ready(self):
        sale = MockRecord(wms_status="pending")
        picking = MockRecord(sale_id=sale)
        r = MockRecord(state="task_done", stock_picking_id=picking)
        WmsOutboundTask._backfill_sale_wms_status(MockRecordset([r]))
        self.assertEqual(sale.wms_status, "ready")

    def test_task_exception_sets_exception(self):
        sale = MockRecord(wms_status="pending")
        picking = MockRecord(sale_id=sale)
        r = MockRecord(state="task_exception", stock_picking_id=picking)
        WmsOutboundTask._backfill_sale_wms_status(MockRecordset([r]))
        self.assertEqual(sale.wms_status, "exception")

    def test_no_sale_no_error(self):
        """无关联 sale → 不报错"""
        picking = MockRecord(sale_id=EMPTY)
        r = MockRecord(state="task_done", stock_picking_id=picking)
        WmsOutboundTask._backfill_sale_wms_status(MockRecordset([r]))


if __name__ == "__main__":
    unittest.main()
