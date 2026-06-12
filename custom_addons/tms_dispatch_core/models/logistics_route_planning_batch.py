from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .selection_options import TMS_ROUTE_STATUS_SELECTION


class LogisticsRoutePlanningBatch(models.Model):
    _inherit = "logistics.route.planning.batch"

    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", ondelete="set null", index=True)
    driver_profile_id = fields.Many2one("logistics.driver.profile", string="Driver Profile", ondelete="set null")
    vehicle_profile_id = fields.Many2one("logistics.vehicle.profile", string="Vehicle Profile", ondelete="set null")
    source_handover_order_id = fields.Many2one("wms.handover.order", string="Source Handover Order", ondelete="set null", index=True)
    route_status = fields.Selection(
        selection=TMS_ROUTE_STATUS_SELECTION,
        string="Route Status",
        default="waiting_route",
        required=True,
    )
    handover_order_count = fields.Integer(string="Handover Orders", compute="_compute_tms_link_counts")
    dispatch_order_count = fields.Integer(string="Dispatch Orders", compute="_compute_tms_link_counts")
    driver_task_count = fields.Integer(string="Driver Tasks", compute="_compute_tms_link_counts")
    order_refs_summary = fields.Char(string="订单号", compute="_compute_chain_trace_fields", store=True)
    store_names_summary = fields.Char(string="门店", compute="_compute_chain_trace_fields", store=True)
    waybill_nos_summary = fields.Char(string="运单号", compute="_compute_chain_trace_fields", store=True)

    @api.depends("stop_line_ids.order_refs_summary", "stop_line_ids.store_name", "stop_line_ids.waybill_no")
    def _compute_chain_trace_fields(self):
        for record in self:
            stop_lines = record.stop_line_ids
            record.order_refs_summary = " / ".join(dict.fromkeys([value for value in stop_lines.mapped("order_refs_summary") if value]))
            record.store_names_summary = " / ".join(dict.fromkeys([value for value in stop_lines.mapped("store_name") if value]))
            record.waybill_nos_summary = " / ".join(dict.fromkeys([value for value in stop_lines.mapped("waybill_no") if value]))

    def _compute_tms_link_counts(self):
        handover_model = self.env["wms.handover.order"]
        dispatch_model = self.env["tms.dispatch.order"]
        for record in self:
            handovers = handover_model.search([("route_batch_id", "=", record.id)])
            dispatch_orders = dispatch_model.search([("route_batch_id", "=", record.id)])
            record.handover_order_count = len(handovers)
            record.dispatch_order_count = len(dispatch_orders)
            record.driver_task_count = len(dispatch_orders.mapped("driver_task_ids"))

    def action_open_handover_orders(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条排线批次记录"),
                    "type": "warning",
                },
            }
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Related Handover Orders",
            "res_model": "wms.handover.order",
            "view_mode": "list,form",
            "domain": [("route_batch_id", "=", self.id)],
        }

    def action_open_dispatch_orders(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条排线批次记录"),
                    "type": "warning",
                },
            }
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Related Dispatch Orders",
            "res_model": "tms.dispatch.order",
            "view_mode": "list,form",
            "domain": [("route_batch_id", "=", self.id)],
        }

    def action_open_driver_tasks(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条排线批次记录"),
                    "type": "warning",
                },
            }
        self.ensure_one()
        dispatch_orders = self.env["tms.dispatch.order"].search([("route_batch_id", "=", self.id)])
        return {
            "type": "ir.actions.act_window",
            "name": "Related Driver Tasks",
            "res_model": "tms.driver.task",
            "view_mode": "list,form",
            "domain": [("dispatch_order_id", "in", dispatch_orders.ids)],
        }

    def _route_waybills(self):
        self.ensure_one()
        names = [name for name in self.stop_line_ids.mapped("waybill_no") if name]
        if not names:
            return self.env["logistics.dispatch.waybill"].browse()
        return self.env["logistics.dispatch.waybill"].sudo().search([("name", "in", names)])

    def _action_open_chain_records(self, title, model_name, records):
        records = records.exists()
        if not records:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("当前批次暂未找到可打开的%s。") % title,
                    "type": "warning",
                },
            }
        action = {
            "type": "ir.actions.act_window",
            "name": title,
            "res_model": model_name,
            "target": "current",
        }
        if len(records) == 1:
            action.update({"view_mode": "form", "res_id": records.id})
        else:
            action.update({"view_mode": "list,form", "domain": [("id", "in", records.ids)]})
        return action

    def action_open_chain_sale_orders(self):
        self.ensure_one()
        sale_orders = self.env["sale.order"].browse()
        waybills = self._route_waybills()
        if waybills and "logistics.dispatch.waybill.order.line" in self.env.registry:
            sale_orders |= self.env["logistics.dispatch.waybill.order.line"].sudo().search(
                [("waybill_id", "in", waybills.ids)]
            ).mapped("sale_order_id")
        return self._action_open_chain_records(_("销售订单"), "sale.order", sale_orders)

    def action_open_chain_waybills(self):
        self.ensure_one()
        return self._action_open_chain_records(_("运单"), "logistics.dispatch.waybill", self._route_waybills())

    def _route_batch_adjustment_unavailable(self):
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("提示"),
                "message": _("批次人工调整向导暂未启用，请先完成模块升级或联系管理员。"),
                "type": "warning",
            },
        }

    def action_rebatch_by_limit(self):
        return self._route_batch_adjustment_unavailable()

    def action_open_move_waybill_wizard(self):
        return self._route_batch_adjustment_unavailable()

    def action_open_merge_batch_wizard(self):
        return self._route_batch_adjustment_unavailable()

    def action_open_split_batch_wizard(self):
        return self._route_batch_adjustment_unavailable()

    def action_open_route_map(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条排线批次记录"),
                    "type": "warning",
                },
            }
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": "/tms/route/%s/map" % self.id,
            "target": "self",
        }

    def action_push_to_dispatch(self):
        if not self:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("请先选择一条排线批次记录"),
                    "type": "warning",
                },
            }
        self.ensure_one()
        if not self.stop_line_ids:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("提示"),
                    "message": _("排线批次 %s 没有停靠点，无法生成派车单") % self.display_name,
                    "type": "warning",
                    "sticky": True,
                },
            }
        dispatch_order = self.env["tms.dispatch.order"].search(
            [("route_batch_id", "=", self.id)], limit=1
        )
        if not dispatch_order:
            if not self.warehouse_id:
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("提示"),
                        "message": _("排线批次 %s 未关联仓库，无法生成派车单") % self.display_name,
                        "type": "warning",
                        "sticky": True,
                    },
                }
            dispatch_order = self.env["tms.dispatch.order"].create({
                "route_batch_id": self.id,
                "warehouse_id": self.warehouse_id.id,
                "driver_profile_id": self.driver_profile_id.id,
                "vehicle_profile_id": self.vehicle_profile_id.id,
            })
            stop_lines = self.stop_line_ids.sorted(key=lambda line: (line.stop_seq, line.id))
            failed_messages = []
            for stop_line in stop_lines:
                try:
                    self.env["tms.driver.task"].create(
                        dispatch_order._prepare_driver_task_vals(stop_line)
                    )
                except Exception as exc:
                    failed_messages.append("%s: %s" % (stop_line.display_name, exc))
            if failed_messages:
                raise UserError(
                    _("司机任务创建失败，派车单未完成推送：\n%s")
                    % "\n".join(failed_messages[:10])
                )
            dispatch_order.write({"state": "dispatched"})
            self.env["core.operation.audit.log"].log_action(
                business_domain="tms",
                action_code="route_batch_push_to_dispatch",
                record=dispatch_order,
                note=_("排线批次推送到派车单"),
                related_record=self,
                payload={"driver_task_count": dispatch_order.driver_task_count},
            )
        return dispatch_order.action_open_record()


class LogisticsRoutePlanningStopLine(models.Model):
    _inherit = "logistics.route.planning.stop.line"

    order_refs_summary = fields.Char(string="订单号", compute="_compute_order_refs_summary", store=True)

    @api.depends("waybill_no")
    def _compute_order_refs_summary(self):
        Waybill = self.env["logistics.dispatch.waybill"].sudo()
        for record in self:
            waybill = Waybill.search([("name", "=", record.waybill_no)], limit=1) if record.waybill_no else False
            record.order_refs_summary = waybill.order_refs_summary if waybill else ""
