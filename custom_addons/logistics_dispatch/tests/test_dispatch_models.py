# -*- coding: utf-8 -*-
"""logistics_dispatch 单元测试 — 约束/compute/create归一化/write副作用"""
from datetime import timedelta
from unittest.mock import MagicMock, patch

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

_counter = [0]


def _uid(prefix="T"):
    _counter[0] += 1
    return "%s-%04d" % (prefix, _counter[0])


def _make_warehouse(env, name, code):
    """创建仓库,回退到 search 如果数据库有限制"""
    try:
        return env["stock.warehouse"].create({"name": name, "code": code})
    except Exception:
        return env["stock.warehouse"].search([], limit=1)


class TestWaybillConstraints(TransactionCase):
    """运单约束校验 — 自建两个仓库保证不匹配场景真实"""

    def setUp(self):
        super().setUp()
        self.wh = _make_warehouse(self.env, "WH-TEST-A", "WHA")
        self.wh2 = _make_warehouse(self.env, "WH-TEST-B", "WHB")
        # 确保两个仓库不同 (如果 create 回退到 search 可能相同)
        if self.wh == self.wh2:
            self.skipTest("无法创建两个不同仓库,跳过 warehouse mismatch 测试")

    def test_waybill_warehouse_must_match_batch(self):
        """运单仓库与批次不一致 → ValidationError"""
        batch = self.env["logistics.dispatch.batch"].create({
            "name": _uid("B-WH"), "warehouse_id": self.wh.id,
        })
        with self.assertRaises(ValidationError):
            self.env["logistics.dispatch.waybill"].create({
                "name": _uid("YD-WH-MIS"), "batch_id": batch.id,
                "warehouse_id": self.wh2.id,
            })

    def test_waybill_warehouse_match_batch_ok(self):
        """运单仓库与批次一致 → 正常"""
        batch = self.env["logistics.dispatch.batch"].create({
            "name": _uid("B-WH-OK"), "warehouse_id": self.wh.id,
        })
        wb = self.env["logistics.dispatch.waybill"].create({
            "name": _uid("YD-WH-OK"), "batch_id": batch.id, "warehouse_id": self.wh.id,
        })
        self.assertEqual(wb.warehouse_id, self.wh)

    def test_waybill_no_duplicate(self):
        """重复运单号 → IntegrityError"""
        name = _uid("YD-DUP")
        self.env["logistics.dispatch.waybill"].create({
            "name": name, "warehouse_id": self.wh.id,
        })
        with self.assertRaises(Exception):
            self.env["logistics.dispatch.waybill"].create({
                "name": name, "warehouse_id": self.wh.id,
            })

    def test_batch_warehouse_must_match_wave(self):
        """批次仓库与波次不一致 → ValidationError"""
        wave = self.env["logistics.dispatch.wave"].create({
            "name": _uid("WAVE-C"), "warehouse_id": self.wh.id,
        })
        with self.assertRaises(ValidationError):
            self.env["logistics.dispatch.batch"].create({
                "name": _uid("B-WM"), "wave_id": wave.id,
                "warehouse_id": self.wh2.id,
            })

    def test_batch_warehouse_match_wave_ok(self):
        """批次仓库与波次一致 → 正常"""
        wave = self.env["logistics.dispatch.wave"].create({
            "name": _uid("WAVE-OK"), "warehouse_id": self.wh.id,
        })
        batch = self.env["logistics.dispatch.batch"].create({
            "name": _uid("B-WO"), "wave_id": wave.id, "warehouse_id": self.wh.id,
        })
        self.assertEqual(batch.wave_id, wave)


class TestWaybillCompute(TransactionCase):
    """运单compute字段"""

    def setUp(self):
        super().setUp()
        self.wh = _make_warehouse(self.env, "WH-AUTO", "WHA")
        self.batch = self.env["logistics.dispatch.batch"].create({
            "name": _uid("B-COMP"), "warehouse_id": self.wh.id,
        })
        self.wb = self.env["logistics.dispatch.waybill"].create({
            "name": _uid("YD-COMP"), "batch_id": self.batch.id, "warehouse_id": self.wh.id,
        })

    def test_detail_counts_sum_goods_quantity(self):
        """goods_line数量/重量/体积应汇总到运单"""
        cl = self.env["logistics.dispatch.waybill.customer.line"].create({
            "waybill_id": self.wb.id, "customer_no": _uid("C"), "customer_name": "TC",
            "longitude": 113.5, "latitude": 23.1, "address_detail": "A",
        })
        for i in range(3):
            self.env["logistics.dispatch.waybill.customer.goods.line"].create({
                "customer_line_id": cl.id, "waybill_no": self.wb.name,
                "goods_name": "G%d" % i, "quantity": 10, "package_count": 2,
                "weight": 5, "volume": 1.5,
            })
        self.wb.invalidate_recordset()
        self.assertEqual(self.wb.total_goods_qty, 30)
        self.assertEqual(self.wb.total_package_count, 6)
        self.assertAlmostEqual(self.wb.total_goods_weight, 15)
        self.assertAlmostEqual(self.wb.total_goods_volume, 4.5)

    def test_batch_counts_compute(self):
        """波次下批次和运单计数"""
        wave = self.env["logistics.dispatch.wave"].create({
            "name": _uid("W-COUNT"), "warehouse_id": self.wh.id,
        })
        b = self.env["logistics.dispatch.batch"].create({
            "name": _uid("B-SUB"), "wave_id": wave.id, "warehouse_id": self.wh.id,
        })
        self.env["logistics.dispatch.waybill"].create({
            "name": _uid("YD-SUB"), "batch_id": b.id, "warehouse_id": self.wh.id,
        })
        self.env["logistics.dispatch.waybill"].create({
            "name": _uid("YD-SUB2"), "batch_id": b.id, "warehouse_id": self.wh.id,
        })
        wave.invalidate_recordset()
        self.assertEqual(wave.total_batch, 1)
        self.assertEqual(wave.total_waybill, 2)

    def test_customer_no_compute_from_partner(self):
        """customer_no从partner的code字段计算"""
        partner = self.env["res.partner"].create({
            "name": _uid("P"), "external_customer_code": _uid("EXT"),
            "is_logistics_partner": True,
        })
        self.wb.write({"partner_id": partner.id})
        self.wb.invalidate_recordset()
        self.assertEqual(self.wb.customer_no, partner.external_customer_code)


class TestWaybillCreateNormalization(TransactionCase):
    """create()归一化"""

    def setUp(self):
        super().setUp()
        self.wh = _make_warehouse(self.env, "WH-AUTO", "WHA")
        self.partner = self.env["res.partner"].create({
            "name": _uid("P-NORM"), "external_customer_code": _uid("EC"),
            "is_logistics_partner": True,
        })
        self.bn = _uid("PC-NORM")
        self.batch = self.env["logistics.dispatch.batch"].create({
            "name": _uid("B-NORM"), "warehouse_id": self.wh.id, "batch_no": self.bn,
        })

    def test_create_resolves_batch_no(self):
        """batch_no应解析为batch_id"""
        wb = self.env["logistics.dispatch.waybill"].create({
            "name": _uid("YD-BNO"), "batch_no": self.bn, "warehouse_id": self.wh.id,
        })
        self.assertEqual(wb.batch_id, self.batch)
        self.assertEqual(wb.warehouse_id, self.batch.warehouse_id)

    def test_create_resolves_customer_no(self):
        """customer_no应解析为partner_id"""
        wb = self.env["logistics.dispatch.waybill"].create({
            "name": _uid("YD-CNO"), "customer_no": self.partner.external_customer_code,
            "warehouse_id": self.wh.id,
        })
        self.assertEqual(wb.partner_id, self.partner)

    def test_create_batch_no_not_found(self):
        """batch_no找不到 → ValidationError"""
        with self.assertRaises(ValidationError):
            self.env["logistics.dispatch.waybill"].create({
                "name": _uid("YD-BAD"), "batch_no": "NONEXIST99",
                "warehouse_id": self.wh.id,
            })


class TestOrderLineConstraints(TransactionCase):
    """订单行约束"""

    def setUp(self):
        super().setUp()
        self.wh = _make_warehouse(self.env, "WH-AUTO", "WHA")
        self.wb = self.env["logistics.dispatch.waybill"].create({
            "name": _uid("YD-ORD"), "warehouse_id": self.wh.id,
        })

    def test_whole_package_count_negative_raises(self):
        """整件数为负 → ValidationError"""
        with self.assertRaises(ValidationError):
            self.env["logistics.dispatch.waybill.order.line"].create({
                "waybill_id": self.wb.id, "sales_order_no": _uid("SO"),
                "whole_package_count": -1,
            })

    def test_order_line_requires_sales_order(self):
        """有sales_order_no时正常创建"""
        ol = self.env["logistics.dispatch.waybill.order.line"].create({
            "waybill_id": self.wb.id, "sales_order_no": _uid("SO"),
        })
        self.assertTrue(ol.id)


class TestGoodsLineConstraints(TransactionCase):
    """货物明细约束"""

    def setUp(self):
        super().setUp()
        self.wh = _make_warehouse(self.env, "WH-AUTO", "WHA")
        self.wb = self.env["logistics.dispatch.waybill"].create({
            "name": _uid("YD-GL"), "warehouse_id": self.wh.id,
        })
        self.cl = self.env["logistics.dispatch.waybill.customer.line"].create({
            "waybill_id": self.wb.id, "customer_no": _uid("CL"), "customer_name": "CL",
            "longitude": 113.5, "latitude": 23.1, "address_detail": "A",
        })

    def test_goods_quantity_negative_raises(self):
        """货物数量为负 → ValidationError"""
        with self.assertRaises(ValidationError):
            self.env["logistics.dispatch.waybill.customer.goods.line"].create({
                "customer_line_id": self.cl.id, "waybill_no": self.wb.name,
                "goods_name": "NEG", "quantity": -10,
            })

    def test_goods_zero_ok(self):
        """零值正常"""
        gl = self.env["logistics.dispatch.waybill.customer.goods.line"].create({
            "customer_line_id": self.cl.id, "waybill_no": self.wb.name,
            "goods_name": "ZERO", "quantity": 0, "weight": 0,
        })
        self.assertTrue(gl.id)


class TestImportBatchExpiry(TransactionCase):
    """导入批次过期"""

    def test_mark_expired_changes_state(self):
        """过期→标记为expired"""
        b = self.env["logistics.import.batch"].create({
            "template_code": _uid("TPL"),
            "template_version": "v1",
            "expires_at": fields.Datetime.now() - timedelta(hours=1),
        })
        b.mark_expired_if_needed()
        b.invalidate_recordset()
        self.assertEqual(b.state, "expired")

    def test_not_expired_unchanged(self):
        """未过期不变"""
        b = self.env["logistics.import.batch"].create({
            "template_code": _uid("TPL"),
            "template_version": "v1",
            "expires_at": fields.Datetime.now() + timedelta(hours=24),
        })
        b.mark_expired_if_needed()
        b.invalidate_recordset()
        self.assertNotEqual(b.state, "expired")

    def test_finished_not_marked_expired(self):
        """已完成不会被标过期"""
        b = self.env["logistics.import.batch"].create({
            "template_code": _uid("TPL"),
            "template_version": "v1",
            "expires_at": fields.Datetime.now() - timedelta(hours=1),
        })
        b.write({"state": "finished"})
        b.mark_expired_if_needed()
        b.invalidate_recordset()
        self.assertEqual(b.state, "finished")


class TestDeleteChain(TransactionCase):
    """删除链路"""

    def setUp(self):
        super().setUp()
        self.wh = _make_warehouse(self.env, "WH-AUTO", "WHA")

    def test_batch_delete_cleans_waybills(self):
        """批次删除→级联运单"""
        b = self.env["logistics.dispatch.batch"].create({
            "name": _uid("B-DEL"), "warehouse_id": self.wh.id,
        })
        wb = self.env["logistics.dispatch.waybill"].create({
            "name": _uid("YD-DEL"), "batch_id": b.id, "warehouse_id": self.wh.id,
        })
        b.action_logistics_delete()
        self.assertFalse(self.env["logistics.dispatch.batch"].search([("id", "=", b.id)]))
        self.assertFalse(self.env["logistics.dispatch.waybill"].search([("id", "=", wb.id)]))


class TestBatchOpenRecord(TransactionCase):
    """批次打开记录"""

    def setUp(self):
        super().setUp()
        self.wh = _make_warehouse(self.env, "WH-AUTO", "WHA")

    def test_action_open_record(self):
        b = self.env["logistics.dispatch.batch"].create({
            "name": _uid("B-OPEN"), "warehouse_id": self.wh.id,
        })
        action = b.action_open_record()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_id"], b.id)
