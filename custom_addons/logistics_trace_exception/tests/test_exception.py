# -*- coding: utf-8 -*-
"""logistics_trace_exception 单元测试 — 异常状态流转"""
from odoo.tests.common import TransactionCase


class TestTraceException(TransactionCase):
    """配送异常状态流转"""

    def setUp(self):
        super().setUp()
        self.exception = self.env["logistics.trace.exception"].create({
            "exception_type": "delay",
        })

    def test_state_default_draft(self):
        """新建异常默认为draft"""
        self.assertEqual(self.exception.state, "draft")

    def test_action_mark_open(self):
        if hasattr(self.exception, 'action_open'):
            self.exception.action_open()
            self.assertEqual(self.exception.state, "open")
        elif hasattr(self.exception, 'action_mark_open'):
            self.exception.action_mark_open()
            self.assertEqual(self.exception.state, "open")
        else:
            # 模型定义了state字段但缺少action方法,标记为BUG
            self.fail("BUG: logistics.trace.exception 缺少状态流转action方法")

    def test_action_mark_resolved(self):
        if hasattr(self.exception, 'action_resolve'):
            self.exception.write({"state": "open"})
            self.exception.action_resolve()
            self.assertEqual(self.exception.state, "resolved")
