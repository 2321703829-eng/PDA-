# -*- coding: utf-8 -*-
"""logistics_base 单元测试 — 车辆/司机画像约束"""
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestVehicleProfileConstraints(TransactionCase):
    """车辆画像约束校验"""

    def test_approved_load_ton_negative_raises(self):
        """核准载重为负→ValidationError"""
        with self.assertRaises(ValidationError):
            self.env["logistics.vehicle.profile"].create({
                "plate_no": "TEST-VEH-NEG",
                "approved_load_ton": -1,
            })

    def test_approved_volume_negative_raises(self):
        """核准体积为负→ValidationError"""
        with self.assertRaises(ValidationError):
            self.env["logistics.vehicle.profile"].create({
                "plate_no": "TEST-VEH-VOL",
                "approved_volume_m3": -5,
            })

    def test_normal_vehicle_creation(self):
        """正常车辆创建"""
        v = self.env["logistics.vehicle.profile"].create({
            "plate_no": "粤A-TEST-001",
            "approved_load_ton": 10,
            "approved_volume_m3": 30,
        })
        self.assertEqual(v.plate_no, "粤A-TEST-001")


class TestDriverProfileConstraints(TransactionCase):
    """司机画像约束"""

    def test_contract_start_after_end_raises(self):
        """合同开始日期晚于结束日期→ValidationError"""
        with self.assertRaises(ValidationError):
            self.env["logistics.driver.profile"].create({
                "name": "TEST-DRV",
                "contract_start_date": "2026-12-01",
                "contract_end_date": "2026-01-01",
            })

    def test_normal_driver_creation(self):
        """正常司机创建"""
        d = self.env["logistics.driver.profile"].create({
            "name": "测试司机",
            "contract_start_date": "2026-01-01",
            "contract_end_date": "2026-12-31",
        })
        self.assertEqual(d.name, "测试司机")
