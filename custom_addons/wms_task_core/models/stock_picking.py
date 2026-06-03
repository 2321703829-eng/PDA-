from odoo import _, fields, models
from odoo.exceptions import ValidationError

from .selection_options import (
    ERP_SOURCE_TYPE_SELECTION,
    WMS_HANDOVER_STATUS_SELECTION,
    WMS_OUTBOUND_TASK_STATUS_SELECTION,
)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    erp_source_type = fields.Selection(
        selection=ERP_SOURCE_TYPE_SELECTION,
        string="ERP Source Type",
    )
    wms_flow_stage = fields.Selection(
        selection=WMS_OUTBOUND_TASK_STATUS_SELECTION,
        string="WMS Flow Stage",
    )
    tms_handover_status = fields.Selection(
        selection=WMS_HANDOVER_STATUS_SELECTION,
        string="TMS Handover Status",
    )
    store_partner_id = fields.Many2one(
        "res.partner",
        string="Store Partner",
        index=True,
    )
    wms_task_ref = fields.Char(string="WMS Task Ref")

    def _get_wms_warehouse(self):
        self.ensure_one()
        warehouse = self.picking_type_id.warehouse_id
        if not warehouse:
            raise ValidationError(_("Picking must belong to a warehouse before creating WMS tasks."))
        return warehouse

    def action_create_receipt_task(self):
        self.ensure_one()
        self.write({"erp_source_type": self.erp_source_type or "purchase"})
        receipt = self.env["wms.receipt.task"].create_from_picking(self)
        if hasattr(self.env.registry, "core.operation.audit.log"):
            self.env["core.operation.audit.log"].log_action(
                business_domain="wms", action_code="create_receipt_task_from_picking",
                record=receipt, note=_("Receipt task created from stock picking."), related_record=self)
        return receipt.action_open_record()

    def action_create_outbound_task(self):
        self.ensure_one()
        self.write({"erp_source_type": self.erp_source_type or "sale"})
        outbound = self.env["wms.outbound.task"].create_from_picking(self)
        if hasattr(self.env.registry, "core.operation.audit.log"):
            self.env["core.operation.audit.log"].log_action(
                business_domain="wms", action_code="create_outbound_task_from_picking",
                record=outbound, note=_("Outbound task created from stock picking."), related_record=self)
        return outbound.action_open_record()

    def action_create_wms_task(self):
        self.ensure_one()
        if self.picking_type_code == "incoming":
            return self.action_create_receipt_task()
        return self.action_create_outbound_task()

    def action_open_wms_tasks(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("WMS Tasks"),
            "res_model": "wms.outbound.task" if self.picking_type_code != "incoming" else "wms.receipt.task",
            "view_mode": "list,form",
            "domain": [("stock_picking_id", "=", self.id)],
        }

    # ========== P1: 自动创建 WMS 任务 + 反写 wms_status ==========
    def write(self, vals):
        res = super().write(vals)
        if vals.get("state") == "assigned":
            for picking in self:
                if picking.picking_type_code in ("incoming", "outgoing"):
                    picking._auto_create_wms_task()
        return res

    def _auto_create_wms_task(self):
        """stock.picking 确认后自动创建 WMS 任务（已存在则跳过）"""
        self.ensure_one()
        if self.picking_type_code == "incoming":
            existing = self.env["wms.receipt.task"].search([("stock_picking_id", "=", self.id)], limit=1)
            if not existing:
                receipt = self.env["wms.receipt.task"].create_from_picking(self)
                receipt.action_start_receipt()
        else:
            existing = self.env["wms.outbound.task"].search([("stock_picking_id", "=", self.id)], limit=1)
            if not existing:
                outbound = self.env["wms.outbound.task"].create_from_picking(self)
                # 回写 sale.order 门店信息
                sale = self.sale_id
                if sale and outbound.store_partner_id:
                    sale.write({"store_partner_id": outbound.store_partner_id.id})
                # 同步运单订单明细
                self._link_waybill_order_lines(outbound)

    def _link_waybill_order_lines(self, outbound_task):
        """P2: 出库完成后,关联运单订单明���到 stock.picking"""
        sale = self.sale_id
        if not sale:
            return
        waybill_lines = self.env["logistics.dispatch.waybill.order.line"].sudo().search([
            ("sale_order_id", "=", False),
        ])
        if waybill_lines:
            waybill_lines.filtered(lambda l: not l.stock_picking_id).write({
                "stock_picking_id": self.id,
            })
