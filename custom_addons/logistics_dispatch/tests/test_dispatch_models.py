# -*- coding: utf-8 -*-
"""logistics_dispatch 单元测试 — 约束/compute/create归一化/write副作用"""
from datetime import timedelta
from unittest.mock import MagicMock, patch

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestWaybillConstraints(TransactionCase):
    """运单约束校验 — 每个constrains 1正常+1异常"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].create({"name": "WH-TEST", "code": "WHT"})
        self.wh2 = self.env["stock.warehouse"].create({"name": "WH-TEST2", "code": "WHT2"})
        self.batch = self.env["logistics.dispatch.batch"].create({
            "name": "BATCH-CONST", "warehouse_id": self.wh.id,
        })

    def test_waybill_warehouse_must_match_batch(self):
        """运单仓库与批次不一致 → ValidationError"""
        with self.assertRaises(ValidationError):
            self.env["logistics.dispatch.waybill"].create({
                "name": "YD-WH-MISMATCH", "batch_id": self.batch.id,
                "warehouse_id": self.wh2.id,
            })

    def test_waybill_warehouse_match_batch_ok(self):
        """运单仓库与批次一致 → 正常"""
        wb = self.env["logistics.dispatch.waybill"].create({
            "name": "YD-WH-OK", "batch_id": self.batch.id, "warehouse_id": self.wh.id,
        })
        self.assertEqual(wb.warehouse_id, self.wh)

    def test_waybill_no_duplicate(self):
        """重复运单号 → IntegrityError"""
        self.env["logistics.dispatch.waybill"].create({
            "name": "YD-DUP", "warehouse_id": self.wh.id,
        })
        with self.assertRaises(Exception):
            self.env["logistics.dispatch.waybill"].create({
                "name": "YD-DUP", "warehouse_id": self.wh.id,
            })

    def test_batch_warehouse_must_match_wave(self):
        """批次仓库与波次不一致 → ValidationError"""
        wave = self.env["logistics.dispatch.wave"].create({
            "name": "WAVE-CONST", "warehouse_id": self.wh.id,
        })
        with self.assertRaises(ValidationError):
            self.env["logistics.dispatch.batch"].create({
                "name": "BATCH-WAVE-MISMATCH", "wave_id": wave.id,
                "warehouse_id": self.wh2.id,
            })

    def test_batch_warehouse_match_wave_ok(self):
        """批次仓库与波次一致 → 正常"""
        wave = self.env["logistics.dispatch.wave"].create({
            "name": "WAVE-OK", "warehouse_id": self.wh.id,
        })
        batch = self.env["logistics.dispatch.batch"].create({
            "name": "BATCH-WAVE-OK", "wave_id": wave.id, "warehouse_id": self.wh.id,
        })
        self.assertEqual(batch.wave_id, wave)


class TestWaybillCompute(TransactionCase):
    """运单compute字段 — 设置依赖字段后断言计算结果"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].create({"name": "WH-COMP", "code": "WHC"})
        self.batch = self.env["logistics.dispatch.batch"].create({
            "name": "BATCH-COMP", "warehouse_id": self.wh.id,
        })
        self.wb = self.env["logistics.dispatch.waybill"].create({
            "name": "YD-COMP", "batch_id": self.batch.id, "warehouse_id": self.wh.id,
        })

    def test_detail_counts_sum_goods_quantity(self):
        """goods_line数量/重量/体积应汇总到运单"""
        cl = self.env["logistics.dispatch.waybill.customer.line"].create({
            "waybill_id": self.wb.id, "customer_no": "C001", "customer_name": "测试",
            "longitude": 113.5, "latitude": 23.1, "address_detail": "地址",
        })
        for i in range(3):
            self.env["logistics.dispatch.waybill.customer.goods.line"].create({
                "customer_line_id": cl.id, "waybill_no": "YD-COMP",
                "goods_name": "货%d" % i, "quantity": 10, "package_count": 2,
                "weight": 5, "volume": 1.5,
            })
        self.wb.invalidate_recordset()
        self.assertEqual(self.wb.total_goods_qty, 30)
        self.assertEqual(self.wb.total_package_count, 6)
        self.assertAlmostEqual(self.wb.total_goods_weight, 15)
        self.assertAlmostEqual(self.wb.total_goods_volume, 4.5)

    def test_detail_counts_empty(self):
        """无goods_line时汇总为0"""
        self.wb.invalidate_recordset()
        self.assertEqual(self.wb.total_goods_qty, 0)
        self.assertEqual(self.wb.total_package_count, 0)

    def test_order_line_count_compute(self):
        """order_line数量应正确计算"""
        ol = self.env["logistics.dispatch.waybill.order.line"].create({
            "waybill_id": self.wb.id, "sales_order_no": "SO001",
        })
        self.wb.invalidate_recordset()
        self.assertEqual(self.wb.order_line_count, 1)

    def test_batch_counts_compute(self):
        """批次数量和运单数应正确计算"""
        wave = self.env["logistics.dispatch.wave"].create({
            "name": "WAVE-COUNT", "warehouse_id": self.wh.id,
        })
        batch = self.env["logistics.dispatch.batch"].create({
            "name": "BATCH-SUB", "wave_id": wave.id, "warehouse_id": self.wh.id,
        })
        self.env["logistics.dispatch.waybill"].create({
            "name": "YD-SUB-1", "batch_id": batch.id, "warehouse_id": self.wh.id,
        })
        self.env["logistics.dispatch.waybill"].create({
            "name": "YD-SUB-2", "batch_id": batch.id, "warehouse_id": self.wh.id,
        })
        wave.invalidate_recordset()
        self.assertEqual(wave.total_batch, 1)
        self.assertEqual(wave.total_waybill, 2)

    def test_customer_no_compute_from_partner(self):
        """customer_no应从关联partner的字段计算"""
        partner = self.env["res.partner"].create({
            "name": "客户01", "external_customer_code": "EXT-001",
            "is_logistics_partner": True,
        })
        self.wb.write({"partner_id": partner.id})
        self.wb.invalidate_recordset()
        self.assertEqual(self.wb.customer_no, "EXT-001")


class TestWaybillCreateNormalization(TransactionCase):
    """create()归一化 — 传入导入字段应解析为标准字段"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].create({"name": "WH-NORM", "code": "WHN"})
        self.batch = self.env["logistics.dispatch.batch"].create({
            "name": "BATCH-NORM", "warehouse_id": self.wh.id,
        })
        self.partner = self.env["res.partner"].create({
            "name": "规范化测试客户", "external_customer_code": "NORM-001",
            "is_logistics_partner": True,
        })

    def test_create_resolves_batch_no(self):
        """batch_no应解析为batch_id并自动填warehouse_id"""
        self.batch.write({"batch_no": "PC-NORM-001"})
        wb = self.env["logistics.dispatch.waybill"].create({
            "name": "YD-BATCHNO", "batch_no": "PC-NORM-001", "warehouse_id": self.wh.id,
        })
        self.assertEqual(wb.batch_id, self.batch)
        self.assertEqual(wb.warehouse_id, self.batch.warehouse_id)

    def test_create_resolves_customer_no(self):
        """customer_no应解析为partner_id"""
        wb = self.env["logistics.dispatch.waybill"].create({
            "name": "YD-CUSTNO", "customer_no": "NORM-001",
            "warehouse_id": self.wh.id,
        })
        self.assertEqual(wb.partner_id, self.partner)

    def test_create_batch_no_not_found(self):
        """batch_no找不到 → ValidationError"""
        with self.assertRaises(ValidationError):
            self.env["logistics.dispatch.waybill"].create({
                "name": "YD-BADBATCH", "batch_no": "NONEXIST",
                "warehouse_id": self.wh.id,
            })

    def test_create_customer_no_not_found(self):
        """customer_no找不到 → ValidationError"""
        with self.assertRaises(ValidationError):
            self.env["logistics.dispatch.waybill"].create({
                "name": "YD-BADCUST", "customer_no": "NONEXIST",
                "warehouse_id": self.wh.id,
            })


class TestWaybillWriteSideEffects(TransactionCase):
    """write()副作用 — 状态变更触发跨模块联动"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].create({"name": "WH-SIDE", "code": "WHS"})
        self.wb = self.env["logistics.dispatch.waybill"].create({
            "name": "YD-SIDE", "warehouse_id": self.wh.id,
        })

    def test_write_state_ready_creates_trace_event(self):
        """状态变为ready → 创建arrive类型留痕事件"""
        mock_event = MagicMock()
        mock_event.sudo.return_value = mock_event
        mock_event.search.return_value = self.wb.browse()

        def fake_getitem(key):
            if key == "logistics.trace.event":
                return mock_event
            return self.env.__class__.__getitem__(self.env, key)

        mock_registry = dict(self.env.registry.models)
        mock_registry["logistics.trace.event"] = True
        with patch.dict(self.env.registry.models, mock_registry):
            with patch.object(type(self.env), '__getitem__', side_effect=fake_getitem):
                self.wb.write({"state": "ready"})
                mock_event.create.assert_called()
                call_args = mock_event.create.call_args[0][0]
                self.assertEqual(call_args.get("trace_type"), "arrive")

    def test_write_same_state_no_duplicate_event(self):
        """同一状态写两次不重复创建事件"""
        mock_event = MagicMock()
        mock_event.sudo.return_value = mock_event
        mock_event.search.return_value = self.wb.browse()

        def fake_getitem(key):
            if key == "logistics.trace.event":
                return mock_event
            return self.env.__class__.__getitem__(self.env, key)

        mock_registry = dict(self.env.registry.models)
        mock_registry["logistics.trace.event"] = True
        with patch.dict(self.env.registry.models, mock_registry):
            with patch.object(type(self.env), '__getitem__', side_effect=fake_getitem):
                self.wb.write({"state": "ready"})
                self.wb.write({"state": "ready"})
                self.assertLessEqual(mock_event.create.call_count, 1)


class TestOrderLineConstraints(TransactionCase):
    """订单行约束校验"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].create({"name": "WH-ORD", "code": "WHO"})
        self.wb = self.env["logistics.dispatch.waybill"].create({
            "name": "YD-ORD", "warehouse_id": self.wh.id,
        })

    def test_whole_package_count_negative_raises(self):
        """整件数为负 → ValidationError"""
        with self.assertRaises(ValidationError):
            self.env["logistics.dispatch.waybill.order.line"].create({
                "waybill_id": self.wb.id, "sales_order_no": "SO001",
                "whole_package_count": -1,
            })

    def test_loose_package_count_negative_raises(self):
        """散件数为负 → ValidationError"""
        with self.assertRaises(ValidationError):
            self.env["logistics.dispatch.waybill.order.line"].create({
                "waybill_id": self.wb.id, "sales_order_no": "SO002",
                "loose_package_count": -5,
            })

    def test_order_line_requires_business_key(self):
        """无业务键字段 → ValidationError"""
        with self.assertRaises(ValidationError):
            self.env["logistics.dispatch.waybill.order.line"].create({
                "waybill_id": self.wb.id,
            })

    def test_order_line_normal_creation(self):
        """正常order_line创建"""
        ol = self.env["logistics.dispatch.waybill.order.line"].create({
            "waybill_id": self.wb.id, "sales_order_no": "SO003",
            "whole_package_count": 3, "loose_package_count": 1,
        })
        self.assertTrue(ol.id)


class TestGoodsLineConstraints(TransactionCase):
    """货物明细约束校验"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].create({"name": "WH-GL", "code": "WHG"})
        self.wb = self.env["logistics.dispatch.waybill"].create({
            "name": "YD-GL", "warehouse_id": self.wh.id,
        })
        self.cl = self.env["logistics.dispatch.waybill.customer.line"].create({
            "waybill_id": self.wb.id, "customer_no": "C01", "customer_name": "C",
            "longitude": 113.5, "latitude": 23.1, "address_detail": "A",
        })

    def test_goods_quantity_negative_raises(self):
        """货物数量为负 → ValidationError"""
        with self.assertRaises(ValidationError):
            self.env["logistics.dispatch.waybill.customer.goods.line"].create({
                "customer_line_id": self.cl.id, "waybill_no": "YD-GL",
                "goods_name": "负数量测试", "quantity": -10,
            })

    def test_goods_weight_negative_raises(self):
        """货物重量为负 → ValidationError"""
        with self.assertRaises(ValidationError):
            self.env["logistics.dispatch.waybill.customer.goods.line"].create({
                "customer_line_id": self.cl.id, "waybill_no": "YD-GL",
                "goods_name": "负重量测试", "quantity": 10, "weight": -5,
            })

    def test_goods_zero_values_ok(self):
        """零值正常通过"""
        gl = self.env["logistics.dispatch.waybill.customer.goods.line"].create({
            "customer_line_id": self.cl.id, "waybill_no": "YD-GL",
            "goods_name": "零值测试", "quantity": 0, "weight": 0,
        })
        self.assertTrue(gl.id)
        self.assertEqual(gl.quantity, 0)


class TestImportBatchExpiry(TransactionCase):
    """导入批次过期标记"""

    def test_mark_expired_changes_state(self):
        """过期导入批次应标记为expired"""
        batch = self.env["logistics.import.batch"].create({
            "template_code": "TSL-TEST",
            "template_version": "v1",
            "expires_at": fields.Datetime.now() - timedelta(hours=1),
        })
        batch.mark_expired_if_needed()
        batch.invalidate_recordset()
        self.assertEqual(batch.state, "expired")

    def test_not_expired_stays_unchanged(self):
        """未过期批次状态不变"""
        batch = self.env["logistics.import.batch"].create({
            "template_code": "TSL-TEST2",
            "template_version": "v1",
            "expires_at": fields.Datetime.now() + timedelta(hours=1),
        })
        batch.mark_expired_if_needed()
        batch.invalidate_recordset()
        self.assertNotEqual(batch.state, "expired")

    def test_finished_stays_finished(self):
        """已完成批次不会被标过期"""
        batch = self.env["logistics.import.batch"].create({
            "template_code": "TSL-TEST3",
            "template_version": "v1",
            "expires_at": fields.Datetime.now() - timedelta(hours=1),
        })
        batch.write({"state": "finished"})
        batch.mark_expired_if_needed()
        batch.invalidate_recordset()
        self.assertEqual(batch.state, "finished")


class TestDeleteChain(TransactionCase):
    """删除链路 — 确保级联删除生效"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].create({"name": "WH-DEL", "code": "WHD"})

    def test_batch_delete_cleans_waybills(self):
        """批次删除时应级联删除运单"""
        batch = self.env["logistics.dispatch.batch"].create({
            "name": "BATCH-TO-DEL", "warehouse_id": self.wh.id,
        })
        wb = self.env["logistics.dispatch.waybill"].create({
            "name": "YD-TO-DEL", "batch_id": batch.id, "warehouse_id": self.wh.id,
        })
        batch.action_logistics_delete()
        self.assertFalse(self.env["logistics.dispatch.batch"].search([("id", "=", batch.id)]))
        self.assertFalse(self.env["logistics.dispatch.waybill"].search([("id", "=", wb.id)]))

    def test_waybill_delete_cleans_customer_lines_and_goods(self):
        """运单删除时级联删除配送节点和货物"""
        wb = self.env["logistics.dispatch.waybill"].create({
            "name": "YD-CASCADE", "warehouse_id": self.wh.id,
        })
        cl = self.env["logistics.dispatch.waybill.customer.line"].create({
            "waybill_id": wb.id, "customer_no": "C1", "customer_name": "C",
            "longitude": 113.5, "latitude": 23.1, "address_detail": "A",
        })
        gl = self.env["logistics.dispatch.waybill.customer.goods.line"].create({
            "customer_line_id": cl.id, "waybill_no": "YD-CASCADE",
            "goods_name": "G", "quantity": 1,
        })
        wb.action_logistics_delete()
        self.assertFalse(self.env["logistics.dispatch.waybill"].search([("id", "=", wb.id)]))
        self.assertFalse(self.env["logistics.dispatch.waybill.customer.line"].search([("id", "=", cl.id)]))
        self.assertFalse(self.env["logistics.dispatch.waybill.customer.goods.line"].search([("id", "=", gl.id)]))


class TestBatchOpenRecord(TransactionCase):
    """批次打开记录"""

    def setUp(self):
        super().setUp()
        self.wh = self.env["stock.warehouse"].create({"name": "WH-OPEN", "code": "WHO"})

    def test_action_open_record(self):
        """打开批次记录返回form视图"""
        batch = self.env["logistics.dispatch.batch"].create({
            "name": "BATCH-OPEN", "warehouse_id": self.wh.id,
        })
        action = batch.action_open_record()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_id"], batch.id)
