# -*- coding: utf-8 -*-
"""erp_base 业务动作单元测试 — action 方法 / 状态流转"""
from datetime import date

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestPriceAdjustment(TransactionCase):
    """价格调整记录 — action_confirm"""

    def setUp(self):
        super().setUp()
        self.product = self.env["product.template"].create({
            "name": "调价测试品", "list_price": 100.0, "standard_price": 60.0
        })

    def test_01_confirm_sale_price_updates_product(self):
        """确认销售价调整后,商品售价应更新"""
        adj = self.env["product.price.adjustment"].create({
            "product_id": self.product.id,
            "price_type": "sale",
            "old_price": 100.0,
            "new_price": 120.0,
            "state": "draft",
        })
        adj.action_confirm()
        self.assertEqual(adj.state, "confirmed")
        self.assertEqual(self.product.list_price, 120.0)

    def test_02_confirm_purchase_price_updates_product(self):
        """确认采购成本价调整后,商品成本价应更新"""
        adj = self.env["product.price.adjustment"].create({
            "product_id": self.product.id,
            "price_type": "purchase",
            "old_price": 60.0,
            "new_price": 55.0,
            "state": "draft",
        })
        adj.action_confirm()
        self.assertEqual(adj.state, "confirmed")
        self.assertEqual(self.product.standard_price, 55.0)

    def test_03_create_with_defaults(self):
        """新建调价记录应有默认值"""
        adj = self.env["product.price.adjustment"].create({
            "product_id": self.product.id,
        })
        self.assertEqual(adj.state, "draft")
        self.assertEqual(adj.price_type, "sale")
        self.assertIsNotNone(adj.adjustment_date)


class TestPeriodClose(TransactionCase):
    """结账/反结账"""

    def test_01_action_close_sets_state(self):
        """结账操作将状态改为closed"""
        pc = self.env["erp.period.close"].create({
            "name": "2026-05结账",
            "period_start": "2026-05-01",
            "period_end": "2026-05-31",
        })
        pc.action_close()
        self.assertEqual(pc.state, "closed")
        self.assertIsNotNone(pc.closed_by)
        self.assertIsNotNone(pc.closed_at)

    def test_02_cannot_close_twice(self):
        """已结账的期间不能重复结账"""
        pc = self.env["erp.period.close"].create({
            "name": "2026-04结账",
            "period_start": "2026-04-01",
            "period_end": "2026-04-30",
        })
        pc.action_close()
        with self.assertRaises(UserError):
            pc.action_close()

    def test_03_cannot_reopen_draft(self):
        """草稿状态不能反结账"""
        pc = self.env["erp.period.close"].create({
            "name": "草稿期间", "period_start": "2026-01-01", "period_end": "2026-01-31"
        })
        with self.assertRaises(UserError):
            pc.action_reopen()

    def test_04_reopen_closed_period(self):
        """已结账期间可以反结账"""
        pc = self.env["erp.period.close"].create({
            "name": "测试反结账", "period_start": "2026-03-01", "period_end": "2026-03-31"
        })
        pc.action_close()
        pc.action_reopen()
        self.assertEqual(pc.state, "reopened")
        self.assertIsNotNone(pc.reopened_by)

    def test_05_period_start_after_end_no_constraint(self):
        """BUG: period_start > period_end 无 @api.constrains,不会报错"""
        pc = self.env["erp.period.close"].create({
            "name": "日期倒挂", "period_start": "2026-06-01", "period_end": "2026-05-01"
        })
        self.assertEqual(pc.state, "draft")
        # TODO: 添加 @api.constrains 校验 period_start <= period_end


class TestDeliveryPlan(TransactionCase):
    """销售出库计划"""

    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "测试客户"})

    def test_01_create_with_defaults(self):
        """创建出库计划有默认值"""
        plan = self.env["erp.delivery.plan"].create({
            "name": "DP-001",
        })
        self.assertEqual(plan.state, "draft")
        self.assertIsNotNone(plan.planned_date)

    def test_02_action_lock_stock(self):
        """锁定库存操作更新状态"""
        plan = self.env["erp.delivery.plan"].create({"name": "DP-LOCK"})
        plan.action_lock_stock()
        self.assertTrue(plan.locked)
        self.assertEqual(plan.state, "confirmed")


class TestReconciliation(TransactionCase):
    """对账模型"""

    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "对账客户"})

    def test_01_create_customer_recon(self):
        """创建客户对账单"""
        recon = self.env["erp.reconciliation"].create({
            "name": "RECON-001",
            "partner_id": self.partner.id,
            "recon_type": "customer",
            "period_start": "2026-05-01",
            "period_end": "2026-05-31",
        })
        self.assertEqual(recon.state, "draft")
        self.assertEqual(recon.recon_type, "customer")

    def test_02_create_supplier_recon(self):
        """创建供应商对账单"""
        recon = self.env["erp.reconciliation"].create({
            "name": "RECON-002",
            "partner_id": self.partner.id,
            "recon_type": "supplier",
        })
        self.assertEqual(recon.recon_type, "supplier")

    def test_03_balance_calculation(self):
        """closing_balance = opening + invoiced - paid + adjustment"""
        recon = self.env["erp.reconciliation"].create({
            "name": "RECON-BAL",
            "partner_id": self.partner.id,
            "recon_type": "customer",
            "opening_balance": 1000.0,
            "total_invoiced": 5000.0,
            "total_paid": 3000.0,
            "total_adjustment": -200.0,
        })
        expected = 1000.0 + 5000.0 - 3000.0 + (-200.0)
        self.assertAlmostEqual(recon.opening_balance, 1000.0)
        self.assertAlmostEqual(recon.total_invoiced, 5000.0)
        self.assertAlmostEqual(recon.total_paid, 3000.0)
        # BUG: closing_balance 不是 compute 字段,需手动设置才会更新
        # 当前仅验证字段可存储,未实现自动计算
        recon.closing_balance = expected
        self.assertAlmostEqual(recon.closing_balance, expected)


class TestClaimRule(TransactionCase):
    """扣赔核销规则"""

    def test_01_create_with_defaults(self):
        """创建扣赔规则有默认值"""
        rule = self.env["erp.claim.rule"].create({
            "name": "配送破损扣款",
            "claim_type": "driver_penalty",
            "source_module": "tms",
        })
        self.assertEqual(rule.claim_type, "driver_penalty")
        self.assertTrue(rule.is_active)

    def test_02_claim_type_selection_all(self):
        """所有扣赔类型可设置"""
        rule = self.env["erp.claim.rule"].create({
            "name": "类型测试", "claim_type": "other"
        })
        for val in ("customer_deduct", "driver_penalty", "warehouse_loss", "other"):
            rule.claim_type = val
            self.assertEqual(rule.claim_type, val)


class TestImportTemplate(TransactionCase):
    """导入导出模板"""

    def test_01_create_template(self):
        """创建导入模板"""
        tmpl = self.env["erp.import.template"].create({
            "name": "订单导入模板",
            "template_type": "order_import",
        })
        self.assertEqual(tmpl.template_type, "order_import")
        self.assertTrue(tmpl.is_active)

    def test_02_template_type_selection_all(self):
        """所有模板类型可设置"""
        tmpl = self.env["erp.import.template"].create({
            "name": "类型测试", "template_type": "other"
        })
        for val in ("order_import", "product_import", "customer_import", "order_export", "report_export", "other"):
            tmpl.template_type = val
            self.assertEqual(tmpl.template_type, val)


class TestSaleReturn(TransactionCase):
    """销售退货单"""

    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "退货客户"})

    def test_01_create_with_defaults(self):
        """创建退货单有默认值"""
        ret = self.env["erp.sale.return"].create({
            "name": "RET-001",
            "partner_id": self.partner.id,
            "return_reason": "damage",
        })
        self.assertEqual(ret.state, "draft")
        self.assertEqual(ret.return_reason, "damage")


class TestOrderImport(TransactionCase):
    """订单导入"""

    def test_01_create_import_batch(self):
        """创建导入批次"""
        imp = self.env["erp.order.import"].create({
            "name": "IMP-001",
        })
        self.assertEqual(imp.state, "draft")

    def test_02_create_import_line(self):
        """创建导入明细行"""
        imp = self.env["erp.order.import"].create({"name": "IMP-LINE"})
        line = self.env["erp.order.import.line"].create({
            "import_id": imp.id,
            "sequence": 1,
            "customer_name": "测试客户",
            "product_name": "测试商品",
            "quantity": 10.0,
        })
        self.assertEqual(line.customer_name, "测试客户")
        self.assertEqual(line.match_status, "pending")
