from odoo import api, models


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    @api.model
    def _has_lang(self, lang_code):
        return bool(self.env["res.lang"].sudo().search_count([("code", "=", lang_code)]))

    @api.model
    def _sync_menu(
        self,
        xmlid,
        *,
        label=None,
        parent_xmlid=None,
        sequence=None,
        active=None,
        action_xmlid=None,
        group_xmlids=None,
    ):
        menu = self.env.ref(xmlid, raise_if_not_found=False)
        if not menu:
            return None

        vals = {}
        if label is not None:
            vals["name"] = label
        if parent_xmlid is not None:
            if parent_xmlid:
                parent = self.env.ref(parent_xmlid, raise_if_not_found=False)
                if parent:
                    vals["parent_id"] = parent.id
            else:
                vals["parent_id"] = False
        if sequence is not None:
            vals["sequence"] = sequence
        if active is not None:
            vals["active"] = active
        if action_xmlid is not None:
            if action_xmlid:
                action = self.env.ref(action_xmlid, raise_if_not_found=False)
                if action:
                    vals["action"] = f"{action._name},{action.id}"
            else:
                vals["action"] = False
        if group_xmlids is not None:
            if group_xmlids:
                groups = []
                for group_xmlid in group_xmlids:
                    group = self.env.ref(group_xmlid, raise_if_not_found=False)
                    if group:
                        groups.append(group.id)
                vals["group_ids"] = [(6, 0, groups)]
            else:
                vals["group_ids"] = [(5, 0, 0)]

        if vals:
            menu.write(vals)
            if label is not None and self._has_lang("zh_CN"):
                menu.with_context(lang="zh_CN").write({"name": label})
        return menu

    @api.model
    def _sync_action(self, xmlid, label):
        action = self.env.ref(xmlid, raise_if_not_found=False)
        if not action:
            return None
        action.write({"name": label})
        if self._has_lang("zh_CN"):
            action.with_context(lang="zh_CN").write({"name": label})
        return action

    @api.model
    def _logistics_web_sync_localized_labels(self):
        enterprise_root_xmlid = "logistics_web.menu_tianshu_enterprise_root"
        root_xmlid = "logistics_dispatch.menu_logistics_dispatch_root"
        menu_specs = (
            {
                "xmlid": enterprise_root_xmlid,
                "label": "天枢科技企业系统",
                "parent_xmlid": False,
                "sequence": 5,
                "action_xmlid": "logistics_web.action_logistics_web_home",
            },
            {
                "xmlid": "logistics_web.menu_logistics_web_home",
                "label": "首页",
                "parent_xmlid": enterprise_root_xmlid,
                "sequence": 10,
            },
            {
                "xmlid": root_xmlid,
                "label": "物流",
                "parent_xmlid": False,
                "sequence": 20,
                "action_xmlid": False,
            },
            {
                "xmlid": "logistics_dispatch.menu_logistics_dispatch_enterprise_home",
                "label": "企业首页",
                "parent_xmlid": root_xmlid,
                "sequence": 5,
                "action_xmlid": "logistics_web.action_logistics_web_home",
                "active": False,
            },
            {
                "xmlid": "logistics_dispatch.menu_logistics_dispatch",
                "label": "物流工作区",
                "parent_xmlid": root_xmlid,
                "sequence": 10,
                "action_xmlid": "logistics_web.action_logistics_web_dashboard",
            },
            {
                "xmlid": "logistics_web.menu_logistics_web",
                "label": "所有统计图表",
                "parent_xmlid": enterprise_root_xmlid,
                "sequence": 60,
            },
            {
                "xmlid": "logistics_web.menu_logistics_web_stats_center",
                "label": "统计图表中心",
                "parent_xmlid": "logistics_web.menu_logistics_web",
                "action_xmlid": "logistics_web.action_logistics_web_stats_center",
                "sequence": 5,
            },
            {
                "xmlid": "logistics_dispatch.menu_logistics_dispatch_scheduling",
                "label": "调度",
                "parent_xmlid": root_xmlid,
                "sequence": 20,
            },
            {
                "xmlid": "logistics_dispatch.menu_logistics_dispatch_batch",
                "label": "批次",
                "parent_xmlid": "logistics_dispatch.menu_logistics_dispatch_scheduling",
                "sequence": 20,
            },
            {
                "xmlid": "logistics_dispatch.menu_logistics_dispatch_wave",
                "label": "波次",
                "parent_xmlid": "logistics_dispatch.menu_logistics_dispatch_scheduling",
                "sequence": 30,
            },
            {
                "xmlid": "logistics_dispatch.menu_logistics_dispatch_waybill_center",
                "label": "运单",
                "parent_xmlid": root_xmlid,
                "action_xmlid": "logistics_dispatch.action_logistics_dispatch_waybill",
                "sequence": 30,
            },
            {
                "xmlid": "logistics_dispatch.menu_logistics_dispatch_waybill",
                "label": "运单列表",
                "parent_xmlid": "logistics_dispatch.menu_logistics_dispatch_waybill_center",
                "sequence": 10,
            },
            {
                "xmlid": "logistics_dispatch.menu_logistics_dispatch_waybill_customer_line",
                "label": "配送节点明细",
                "parent_xmlid": "logistics_dispatch.menu_logistics_dispatch_waybill_center",
                "sequence": 20,
            },
            {
                "xmlid": "logistics_dispatch.menu_logistics_dispatch_waybill_customer_goods_line",
                "label": "货物明细",
                "parent_xmlid": "logistics_dispatch.menu_logistics_dispatch_waybill_center",
                "sequence": 30,
            },
            {
                "xmlid": "logistics_trace_core.menu_logistics_trace_event",
                "label": "留痕",
                "parent_xmlid": root_xmlid,
                "sequence": 40,
            },
            {
                "xmlid": "logistics_trace_evidence.menu_logistics_trace_evidence",
                "label": "证据",
                "parent_xmlid": root_xmlid,
                "sequence": 50,
            },
            {
                "xmlid": "logistics_trace_exception.menu_logistics_trace_exception",
                "label": "异常",
                "parent_xmlid": root_xmlid,
                "sequence": 60,
            },
            {
                "xmlid": "logistics_dispatch.menu_logistics_dispatch_import_center",
                "label": "导入中心",
                "parent_xmlid": root_xmlid,
                "action_xmlid": "logistics_dispatch.action_logistics_dispatch_waybill_import_center_direct",
                "sequence": 70,
            },
            {
                "xmlid": "logistics_dispatch.menu_logistics_dispatch_import_waybill",
                "label": "运单导入",
                "parent_xmlid": "logistics_dispatch.menu_logistics_dispatch_import_center",
                "active": False,
                "action_xmlid": "logistics_dispatch.action_logistics_dispatch_waybill_import_center_direct",
                "sequence": 10,
            },
            {
                "xmlid": "logistics_dispatch.menu_logistics_dispatch_import_customer_line",
                "label": "配送节点明细导入",
                "parent_xmlid": "logistics_dispatch.menu_logistics_dispatch_import_center",
                "active": False,
                "action_xmlid": "logistics_dispatch.action_logistics_dispatch_waybill_customer_line_import_center_direct",
                "sequence": 20,
            },
            {
                "xmlid": "logistics_dispatch.menu_logistics_dispatch_import_customer_goods_line",
                "label": "货物明细导入",
                "parent_xmlid": "logistics_dispatch.menu_logistics_dispatch_import_center",
                "active": False,
                "action_xmlid": "logistics_dispatch.action_logistics_dispatch_waybill_customer_goods_line_import_center_direct",
                "sequence": 30,
            },
            {
                "xmlid": "logistics_web.menu_logistics_web_dashboard",
                "label": "物流工作台",
                "parent_xmlid": "logistics_web.menu_logistics_web",
                "sequence": 10,
            },
            {
                "xmlid": "logistics_web.menu_logistics_web_boss_trace",
                "label": "管理看板",
                "parent_xmlid": "logistics_web.menu_logistics_web",
                "sequence": 20,
            },
            {
                "xmlid": "logistics_web.menu_logistics_web_driver_management",
                "label": "司机管理",
                "parent_xmlid": root_xmlid,
                "action_xmlid": "logistics_web.action_logistics_web_driver_management",
                "sequence": 80,
            },
            {
                "xmlid": "logistics_web.menu_logistics_web_vehicle_management",
                "label": "车辆管理",
                "parent_xmlid": root_xmlid,
                "action_xmlid": "logistics_web.action_logistics_web_vehicle_management",
                "sequence": 90,
            },
            {
                "xmlid": "logistics_web.menu_logistics_web_import_center_phase5",
                "label": "五期五表导入",
                "active": False,
            },
            {
                "xmlid": "logistics_web.menu_logistics_web_import_center_phase5_root",
                "label": "五期五表导入",
                "active": False,
            },
        )
        for spec in menu_specs:
            self._sync_menu(
                spec["xmlid"],
                label=spec.get("label"),
                parent_xmlid=spec.get("parent_xmlid"),
                sequence=spec.get("sequence"),
                active=spec.get("active"),
                action_xmlid=spec.get("action_xmlid"),
                group_xmlids=spec.get("group_xmlids"),
            )

        for xmlid in (
            "logistics_web.menu_tianshu_enterprise_logistics_shortcut",
            "logistics_web.menu_tianshu_enterprise_fleet_shortcut",
            "logistics_web.menu_tianshu_enterprise_employee_shortcut",
            "logistics_web.menu_tianshu_enterprise_inventory_shortcut",
            "logistics_web.menu_tianshu_enterprise_invoice_shortcut",
            "logistics_web.menu_tianshu_enterprise_settings_shortcut",
        ):
            self._sync_menu(xmlid, active=False)

        action_specs = {
            "logistics_dispatch.action_logistics_dispatch_waybill": "运单",
            "logistics_dispatch.action_logistics_dispatch_batch": "批次",
            "logistics_dispatch.action_logistics_dispatch_wave": "波次",
            "logistics_dispatch.action_logistics_dispatch_waybill_customer_line": "配送节点明细",
            "logistics_dispatch.action_logistics_dispatch_waybill_customer_goods_line": "货物明细",
            "logistics_dispatch.action_logistics_dispatch_waybill_import_center": "导入中心",
            "logistics_dispatch.action_logistics_dispatch_waybill_import_center_direct": "导入中心",
            "logistics_dispatch.action_logistics_dispatch_waybill_customer_line_import_center_direct": "配送节点明细导入",
            "logistics_dispatch.action_logistics_dispatch_waybill_customer_goods_line_import_center_direct": "货物明细导入",
            "logistics_trace_core.action_logistics_trace_event": "留痕",
            "logistics_trace_evidence.action_logistics_trace_evidence": "证据",
            "logistics_trace_exception.action_logistics_trace_exception": "异常",
            "logistics_web.action_logistics_web_home": "企业首页",
            "logistics_web.action_logistics_web_dashboard": "物流工作台",
            "logistics_web.action_logistics_web_stats_center": "统计图表中心",
            "logistics_web.action_logistics_web_boss_trace": "管理看板",
            "logistics_web.action_logistics_web_import_center": "导入中心",
            "logistics_web.action_logistics_web_import_result": "导入结果",
            "logistics_web.action_logistics_web_export_result": "导出结果",
            "logistics_web.action_logistics_web_driver_management": "司机管理",
            "logistics_web.action_logistics_web_vehicle_management": "车辆管理",
        }
        for xmlid, label in action_specs.items():
            self._sync_action(xmlid, label)
        return True
