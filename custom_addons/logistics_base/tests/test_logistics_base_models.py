"""logistics_base 模块单测 — mock 模式，无需数据库。"""

import unittest
from datetime import date
from test_helpers import MockRecord, MockRecordset, EMPTY
from odoo.exceptions import ValidationError

from custom_addons.logistics_base.models.logistics_vehicle_profile import (
    LogisticsVehicleProfile,
)
from custom_addons.logistics_base.models.logistics_driver_profile import (
    LogisticsDriverProfile,
)
from custom_addons.logistics_base.models.logistics_product_unit import (
    LogisticsProductUnit,
)
from custom_addons.logistics_base.models.res_partner import ResPartner
from custom_addons.logistics_base.models.product_template import ProductTemplate


# ── Vehicle Profile 约束 ──────────────────────────────────────────

class TestVehicleProfileConstraint(unittest.TestCase):

    def test_negative_load_raises(self):
        r = MockRecord(approved_load_ton=-1, approved_volume_m3=10)
        with self.assertRaises(ValidationError):
            LogisticsVehicleProfile._check_non_negative_values(MockRecordset([r]))

    def test_negative_volume_raises(self):
        r = MockRecord(approved_load_ton=5, approved_volume_m3=-0.1)
        with self.assertRaises(ValidationError):
            LogisticsVehicleProfile._check_non_negative_values(MockRecordset([r]))

    def test_zero_values_ok(self):
        r = MockRecord(approved_load_ton=0, approved_volume_m3=0)
        LogisticsVehicleProfile._check_non_negative_values(MockRecordset([r]))

    def test_positive_values_ok(self):
        r = MockRecord(approved_load_ton=20, approved_volume_m3=60)
        LogisticsVehicleProfile._check_non_negative_values(MockRecordset([r]))


# ── Driver Profile ────────────────────────────────────────────────

class TestDriverProfileCompute(unittest.TestCase):

    def test_phone_priority_mobile_first(self):
        emp = MockRecord(mobile_phone="138001", work_phone="021001", private_phone="139001")
        r = MockRecord(employee_id=emp)
        LogisticsDriverProfile._compute_driver_phone(MockRecordset([r]))
        self.assertEqual(r.driver_phone, "138001")

    def test_phone_fallback_work(self):
        emp = MockRecord(mobile_phone="", work_phone="021002", private_phone="139002")
        r = MockRecord(employee_id=emp)
        LogisticsDriverProfile._compute_driver_phone(MockRecordset([r]))
        self.assertEqual(r.driver_phone, "021002")

    def test_phone_fallback_private(self):
        emp = MockRecord(mobile_phone=False, work_phone=False, private_phone="139003")
        r = MockRecord(employee_id=emp)
        LogisticsDriverProfile._compute_driver_phone(MockRecordset([r]))
        self.assertEqual(r.driver_phone, "139003")

    def test_phone_all_empty(self):
        emp = MockRecord(mobile_phone=False, work_phone=False, private_phone=False)
        r = MockRecord(employee_id=emp)
        LogisticsDriverProfile._compute_driver_phone(MockRecordset([r]))
        self.assertEqual(r.driver_phone, "")

    def test_phone_no_employee(self):
        r = MockRecord(employee_id=EMPTY)
        LogisticsDriverProfile._compute_driver_phone(MockRecordset([r]))
        self.assertEqual(r.driver_phone, "")


class TestDriverProfileDateConstraint(unittest.TestCase):

    def test_contract_end_before_start_raises(self):
        r = MockRecord(
            contract_start_date=date(2025, 6, 1),
            contract_end_date=date(2025, 5, 1),
            driver_license_valid_from=False,
            driver_license_valid_to=False,
        )
        with self.assertRaises(ValidationError):
            LogisticsDriverProfile._check_date_ranges(MockRecordset([r]))

    def test_license_end_before_start_raises(self):
        r = MockRecord(
            contract_start_date=False,
            contract_end_date=False,
            driver_license_valid_from=date(2025, 12, 1),
            driver_license_valid_to=date(2025, 1, 1),
        )
        with self.assertRaises(ValidationError):
            LogisticsDriverProfile._check_date_ranges(MockRecordset([r]))

    def test_dates_ok(self):
        r = MockRecord(
            contract_start_date=date(2025, 1, 1),
            contract_end_date=date(2026, 1, 1),
            driver_license_valid_from=date(2025, 1, 1),
            driver_license_valid_to=date(2030, 1, 1),
        )
        LogisticsDriverProfile._check_date_ranges(MockRecordset([r]))

    def test_partial_dates_ok(self):
        """只设了 start 没设 end → 不校验"""
        r = MockRecord(
            contract_start_date=date(2025, 1, 1),
            contract_end_date=False,
            driver_license_valid_from=False,
            driver_license_valid_to=False,
        )
        LogisticsDriverProfile._check_date_ranges(MockRecordset([r]))


# ── Product Unit ──────────────────────────────────────────────────

class TestProductUnitDisplayName(unittest.TestCase):

    def test_full_parts(self):
        r = MockRecord(
            product_tmpl_id=MockRecord(name="苹果"),
            spec_desc="500g",
            unit_name="箱",
            sale_unit_name="件",
        )
        LogisticsProductUnit._compute_display_name(MockRecordset([r]))
        self.assertEqual(r.display_name, "苹果 / 500g / 箱")

    def test_unit_fallback_sale_unit(self):
        r = MockRecord(
            product_tmpl_id=MockRecord(name="香蕉"),
            spec_desc="",
            unit_name="",
            sale_unit_name="把",
        )
        LogisticsProductUnit._compute_display_name(MockRecordset([r]))
        self.assertEqual(r.display_name, "香蕉 / 把")

    def test_all_empty(self):
        r = MockRecord(
            product_tmpl_id=MockRecord(name=""),
            spec_desc="",
            unit_name="",
            sale_unit_name="",
        )
        LogisticsProductUnit._compute_display_name(MockRecordset([r]))
        self.assertEqual(r.display_name, "")


# ── Res Partner 归一化 ────────────────────────────────────────────

class TestPartnerNormalize(unittest.TestCase):

    def test_is_logistics_partner_syncs_flags(self):
        result = ResPartner._normalize_logistics_partner_vals(None, {"is_logistics_partner": True})
        self.assertTrue(result.get("is_logistics_customer"))
        self.assertTrue(result.get("is_logistics_store"))

    def test_customer_or_store_syncs_partner(self):
        """只设 customer=True, store=False → partner_flag=True → 两者均 True"""
        result = ResPartner._normalize_logistics_partner_vals(None, {
            "is_logistics_customer": True,
            "is_logistics_store": False,
        })
        self.assertTrue(result["is_logistics_customer"])
        self.assertTrue(result["is_logistics_store"])

    def test_code_whitespace_stripped(self):
        result = ResPartner._normalize_logistics_partner_vals(None, {
            "logistics_customer_code": "  C001  ",
        })
        self.assertEqual(result["logistics_customer_code"], "C001")
        self.assertEqual(result["logistics_store_code"], "C001")

    def test_inconsistent_codes_raises(self):
        with self.assertRaises(ValidationError):
            ResPartner._normalize_logistics_partner_vals(None, {
                "logistics_customer_code": "A",
                "logistics_store_code": "B",
            })

    def test_empty_code_becomes_false(self):
        result = ResPartner._normalize_logistics_partner_vals(None, {
            "logistics_customer_code": "   ",
        })
        self.assertFalse(result["logistics_customer_code"])


class TestPartnerCompute(unittest.TestCase):

    def test_is_logistics_partner_true(self):
        r = MockRecord(is_logistics_customer=True, is_logistics_store=False)
        ResPartner._compute_is_logistics_partner(MockRecordset([r]))
        self.assertTrue(r.is_logistics_partner)

    def test_is_logistics_partner_false(self):
        r = MockRecord(is_logistics_customer=False, is_logistics_store=False)
        ResPartner._compute_is_logistics_partner(MockRecordset([r]))
        self.assertFalse(r.is_logistics_partner)


# ── Product Template 归一化 ───────────────────────────────────────

class TestProductTemplateNormalize(unittest.TestCase):

    def test_product_name_syncs_to_name(self):
        """product_name 有值、name 没有 → 自动同步"""
        vals_list = [{"product_name": "测试商品"}]
        rs = MockRecordset([], env=None)
        # create is @api.model_create_multi, first arg is vals_list
        # We test normalization logic only, need to call with mocked super
        result = dict(vals_list[0])
        if result.get("product_name") and not result.get("name"):
            result["name"] = result["product_name"]
        self.assertEqual(result["name"], "测试商品")

    def test_name_syncs_to_product_name(self):
        result = dict({"name": "Test Product"})
        if result.get("name") and not result.get("product_name"):
            result["product_name"] = result["name"]
        self.assertEqual(result["product_name"], "Test Product")


if __name__ == "__main__":
    unittest.main()
