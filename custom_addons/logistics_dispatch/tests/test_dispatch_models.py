"""logistics_dispatch 模块单测 — mock 模式，无需数据库。"""

import unittest
from datetime import datetime, timedelta
from test_helpers import MockRecord, MockRecordset, EMPTY
from odoo.exceptions import ValidationError

from custom_addons.logistics_dispatch.models.logistics_dispatch_waybill import (
    LogisticsDispatchWaybill,
)
from custom_addons.logistics_dispatch.models.logistics_dispatch_batch import (
    LogisticsDispatchBatch,
)
from custom_addons.logistics_dispatch.models.logistics_dispatch_wave import (
    LogisticsDispatchWave,
)
from custom_addons.logistics_dispatch.models.logistics_dispatch_waybill_order_line import (
    LogisticsDispatchWaybillOrderLine,
)
from custom_addons.logistics_dispatch.models.logistics_dispatch_waybill_customer_goods_line_v2 import (
    LogisticsDispatchWaybillCustomerGoodsLine,
)
from custom_addons.logistics_dispatch.models.logistics_import_batch import (
    LogisticsImportBatch,
)


# ── Waybill 约束 ──────────────────────────────────────────────────

class TestWaybillBatchWarehouseConstraint(unittest.TestCase):
    """_check_batch_warehouse_consistency"""

    def test_no_batch_no_check(self):
        """无批次 → 不触发校验"""
        r = MockRecord(batch_id=EMPTY, warehouse_id=MockRecord(_id=1))
        LogisticsDispatchWaybill._check_batch_warehouse_consistency(MockRecordset([r]))

    def test_batch_no_warehouse_raises(self):
        """有批次无仓库 → ValidationError"""
        r = MockRecord(batch_id=MockRecord(_id=10, warehouse_id=MockRecord(_id=1)), warehouse_id=EMPTY)
        with self.assertRaises(ValidationError):
            LogisticsDispatchWaybill._check_batch_warehouse_consistency(MockRecordset([r]))

    def test_batch_warehouse_mismatch_raises(self):
        """批次仓库 ≠ 运单仓库 → ValidationError"""
        r = MockRecord(
            batch_id=MockRecord(_id=10, warehouse_id=MockRecord(_id=1)),
            warehouse_id=MockRecord(_id=2),
        )
        with self.assertRaises(ValidationError):
            LogisticsDispatchWaybill._check_batch_warehouse_consistency(MockRecordset([r]))

    def test_batch_warehouse_match_ok(self):
        """批次仓库 == 运单仓库 → 通过"""
        wh = MockRecord(_id=5)
        r = MockRecord(batch_id=MockRecord(_id=10, warehouse_id=wh), warehouse_id=wh)
        LogisticsDispatchWaybill._check_batch_warehouse_consistency(MockRecordset([r]))


# ── Batch 约束 ────────────────────────────────────────────────────

class TestBatchWaveWarehouseConstraint(unittest.TestCase):
    """_check_wave_warehouse_consistency"""

    def test_no_wave_no_check(self):
        r = MockRecord(wave_id=EMPTY, warehouse_id=MockRecord(_id=1))
        LogisticsDispatchBatch._check_wave_warehouse_consistency(MockRecordset([r]))

    def test_wave_warehouse_mismatch_raises(self):
        r = MockRecord(
            wave_id=MockRecord(_id=20, warehouse_id=MockRecord(_id=1)),
            warehouse_id=MockRecord(_id=2),
        )
        with self.assertRaises(ValidationError):
            LogisticsDispatchBatch._check_wave_warehouse_consistency(MockRecordset([r]))

    def test_wave_warehouse_match_ok(self):
        wh = MockRecord(_id=5)
        r = MockRecord(wave_id=MockRecord(_id=20, warehouse_id=wh), warehouse_id=wh)
        LogisticsDispatchBatch._check_wave_warehouse_consistency(MockRecordset([r]))


# ── Order Line 约束 ───────────────────────────────────────────────

class TestOrderLineConstraints(unittest.TestCase):

    def test_negative_package_count_raises(self):
        """整件数 < 0 → ValidationError"""
        r = MockRecord(whole_package_count=-1, loose_package_count=0)
        with self.assertRaises(ValidationError):
            LogisticsDispatchWaybillOrderLine._check_non_negative_summary_values(MockRecordset([r]))

    def test_zero_package_counts_ok(self):
        r = MockRecord(whole_package_count=0, loose_package_count=0)
        LogisticsDispatchWaybillOrderLine._check_non_negative_summary_values(MockRecordset([r]))

    def test_no_business_key_raises(self):
        """所有业务键都为空 → ValidationError"""
        r = MockRecord(
            source_doc_no="", order_no="", sales_order_no="",
            source_ref_no="", third_party_doc_no="", external_order_no="",
        )
        with self.assertRaises(ValidationError):
            LogisticsDispatchWaybillOrderLine._check_business_key_presence(MockRecordset([r]))

    def test_one_business_key_ok(self):
        r = MockRecord(
            source_doc_no="", order_no="ORD-001", sales_order_no="",
            source_ref_no="", third_party_doc_no="", external_order_no="",
        )
        LogisticsDispatchWaybillOrderLine._check_business_key_presence(MockRecordset([r]))

    def test_customer_line_waybill_mismatch_raises(self):
        """订单行的 customer_line 不属于同一运单"""
        wb_a = MockRecord(_id=100)
        wb_b = MockRecord(_id=200)
        r = MockRecord(
            waybill_id=wb_a,
            customer_line_id=MockRecord(_id=50, waybill_id=wb_b),
        )
        with self.assertRaises(ValidationError):
            LogisticsDispatchWaybillOrderLine._check_customer_line_belongs_to_waybill(MockRecordset([r]))

    def test_customer_line_same_waybill_ok(self):
        wb = MockRecord(_id=100)
        r = MockRecord(
            waybill_id=wb,
            customer_line_id=MockRecord(_id=50, waybill_id=wb),
        )
        LogisticsDispatchWaybillOrderLine._check_customer_line_belongs_to_waybill(MockRecordset([r]))


# ── Goods Line 约束 ───────────────────────────────────────────────

class TestGoodsLineConstraints(unittest.TestCase):

    def test_order_line_waybill_mismatch_raises(self):
        """goods_line 的 order_line 和 customer_line 属于不同运单"""
        wb_a = MockRecord(_id=100)
        wb_b = MockRecord(_id=200)
        r = MockRecord(
            order_line_id=MockRecord(_id=10, waybill_id=wb_a, customer_line_id=EMPTY),
            customer_line_id=MockRecord(_id=20, waybill_id=wb_b),
        )
        with self.assertRaises(ValidationError):
            LogisticsDispatchWaybillCustomerGoodsLine._check_order_line_consistency(MockRecordset([r]))

    def test_no_order_line_ok(self):
        """无 order_line → 跳过"""
        r = MockRecord(order_line_id=EMPTY, customer_line_id=MockRecord(_id=20, waybill_id=MockRecord(_id=100)))
        LogisticsDispatchWaybillCustomerGoodsLine._check_order_line_consistency(MockRecordset([r]))


# ── Waybill Compute ───────────────────────────────────────────────

class TestWaybillCompute(unittest.TestCase):

    def test_compute_order_line_count(self):
        lines = MockRecordset([MockRecord(_id=i) for i in range(4)])
        r = MockRecord(order_line_ids=lines)
        LogisticsDispatchWaybill._compute_order_line_count(MockRecordset([r]))
        self.assertEqual(r.order_line_count, 4)

    def test_compute_order_summary_dedup(self):
        """sales_order_no 去重优先，order_no 补充，最多5个"""
        lines = MockRecordset([
            MockRecord(sales_order_no="SO1", order_no="O1"),
            MockRecord(sales_order_no="SO1", order_no="O2"),
            MockRecord(sales_order_no="SO2", order_no="O2"),
        ])
        r = MockRecord(order_line_ids=lines)
        LogisticsDispatchWaybill._compute_order_summary(MockRecordset([r]))
        self.assertEqual(r.order_refs_summary, "SO1 / O1 / O2 / SO2")

    def test_compute_order_summary_max_5(self):
        lines = MockRecordset([
            MockRecord(sales_order_no=f"S{i}", order_no="") for i in range(8)
        ])
        r = MockRecord(order_line_ids=lines)
        LogisticsDispatchWaybill._compute_order_summary(MockRecordset([r]))
        self.assertEqual(len(r.order_refs_summary.split(" / ")), 5)

    def test_compute_detail_counts(self):
        """货物明细汇总"""
        goods = MockRecordset([
            MockRecord(quantity=10, package_count=2, weight=5.0, volume=1.5),
            MockRecord(quantity=20, package_count=3, weight=8.0, volume=2.0),
        ])
        r = MockRecord(
            customer_line_ids=MockRecordset([MockRecord(), MockRecord()]),
            goods_line_ids=goods,
        )
        LogisticsDispatchWaybill._compute_detail_counts(MockRecordset([r]))
        self.assertEqual(r.customer_line_count, 2)
        self.assertEqual(r.goods_line_count, 2)
        self.assertAlmostEqual(r.total_goods_qty, 30.0)
        self.assertEqual(r.total_package_count, 5)
        self.assertAlmostEqual(r.total_goods_weight, 13.0)
        self.assertAlmostEqual(r.total_goods_volume, 3.5)

    def test_compute_customer_no_priority(self):
        """customer_no 优先级: external > logistics_customer > logistics_store"""
        cust = MockRecord(
            external_customer_code="E01",
            logistics_customer_code="C01",
            logistics_store_code="S01",
        )
        r = MockRecord(customer_id=cust)
        LogisticsDispatchWaybill._compute_customer_no(MockRecordset([r]))
        self.assertEqual(r.customer_no, "E01")

    def test_compute_customer_no_fallback(self):
        cust = MockRecord(
            external_customer_code="",
            logistics_customer_code="",
            logistics_store_code="S99",
        )
        r = MockRecord(customer_id=cust)
        LogisticsDispatchWaybill._compute_customer_no(MockRecordset([r]))
        self.assertEqual(r.customer_no, "S99")

    def test_compute_partner_fields_fallback(self):
        """partner_id 为空 → 回退到 customer_id"""
        cust = MockRecord(
            external_customer_code="E01",
            internal_customer_code="",
            logistics_customer_code="",
            logistics_store_code="",
            name="客户A",
        )
        r = MockRecord(partner_id=EMPTY, customer_id=cust, store_id=EMPTY)
        LogisticsDispatchWaybill._compute_partner_fields(MockRecordset([r]))
        self.assertEqual(r.partner_no, "E01")
        self.assertEqual(r.partner_name, "客户A")


# ── Batch Compute ─────────────────────────────────────────────────

class TestBatchCompute(unittest.TestCase):

    def test_compute_counts(self):
        waybills = MockRecordset([
            MockRecord(state="draft", exception_status="none"),
            MockRecord(state="done", exception_status="none"),
            MockRecord(state="done", exception_status="open"),
        ])
        r = MockRecord(waybill_ids=waybills)
        LogisticsDispatchBatch._compute_counts(MockRecordset([r]))
        self.assertEqual(r.total_waybill_count, 3)
        self.assertEqual(r.finished_waybill_count, 2)
        self.assertEqual(r.exception_waybill_count, 1)


# ── Wave Compute ──────────────────────────────────────────────────

class TestWaveCompute(unittest.TestCase):

    def test_compute_counts(self):
        wb1_a = MockRecord(_id=1, order_line_ids=MockRecordset([MockRecord(), MockRecord()]))
        wb1_b = MockRecord(_id=2, order_line_ids=MockRecordset([MockRecord()]))
        wb2_a = MockRecord(_id=3, order_line_ids=MockRecordset([MockRecord()]))
        batch1 = MockRecord(total_waybill_count=2, waybill_ids=MockRecordset([wb1_a, wb1_b]))
        batch2 = MockRecord(total_waybill_count=1, waybill_ids=MockRecordset([wb2_a]))
        r = MockRecord(batch_ids=MockRecordset([batch1, batch2]))
        LogisticsDispatchWave._compute_counts(MockRecordset([r]))
        self.assertEqual(r.total_batch_count, 2)
        self.assertEqual(r.total_waybill_count, 3)
        # mapped("order_line_ids") returns [MockRecordset, MockRecordset, MockRecordset]
        # len of each MockRecordset = 2, 1, 1 → total = 3 (sum of mapped items)
        # But code does: len(batch.waybill_ids.mapped("order_line_ids"))
        # mapped returns list of MockRecordset objects, len counts those
        self.assertEqual(r.total_order_count, 3)


# ── Import Batch ──────────────────────────────────────────────────

class TestImportBatch(unittest.TestCase):

    def test_mark_expired_skips_finished(self):
        r = MockRecord(state="finished", expires_at=datetime.now() - timedelta(hours=2))
        LogisticsImportBatch.mark_expired_if_needed(MockRecordset([r]))
        self.assertEqual(r.state, "finished")

    def test_mark_expired_changes_state(self):
        r = MockRecord(state="prechecked", expires_at=datetime.now() - timedelta(hours=1))
        LogisticsImportBatch.mark_expired_if_needed(MockRecordset([r]))
        self.assertEqual(r.state, "expired")

    def test_mark_expired_not_yet_expired(self):
        r = MockRecord(state="prechecked", expires_at=datetime.now() + timedelta(hours=1))
        LogisticsImportBatch.mark_expired_if_needed(MockRecordset([r]))
        self.assertEqual(r.state, "prechecked")

    def test_get_source_rows_parses_json(self):
        import json
        data = [{"a": 1}, {"b": 2}]
        r = MockRecord(source_rows_json=json.dumps(data))
        rs = MockRecordset([r])
        result = LogisticsImportBatch.get_source_rows(rs)
        self.assertEqual(result, data)

    def test_get_source_rows_empty(self):
        r = MockRecord(source_rows_json="")
        rs = MockRecordset([r])
        result = LogisticsImportBatch.get_source_rows(rs)
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
