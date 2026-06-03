from odoo import _, fields, models
from odoo.exceptions import UserError

from .selection_options import TMS_ROUTE_STATUS_SELECTION


class LogisticsRoutePlanningBatch(models.Model):
    _inherit = "logistics.route.planning.batch"

    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", ondelete="set null", index=True)
    driver_profile_id = fields.Many2one("logistics.driver.profile", string="Driver Profile", ondelete="set null")
    vehicle_profile_id = fields.Many2one("logistics.vehicle.profile", string="Vehicle Profile", ondelete="set null")
    route_status = fields.Selection(
        selection=TMS_ROUTE_STATUS_SELECTION,
        string="Route Status",
        default="waiting_route",
        required=True,
    )
    handover_order_count = fields.Integer(string="Handover Orders", compute="_compute_tms_link_counts")
    dispatch_order_count = fields.Integer(string="Dispatch Orders", compute="_compute_tms_link_counts")
    driver_task_count = fields.Integer(string="Driver Tasks", compute="_compute_tms_link_counts")

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
