from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .selection_options import (
    WMS_CHECK_TASK_STATUS_SELECTION,
    WMS_HANDOVER_STATUS_SELECTION,
    WMS_OUTBOUND_TASK_STATUS_SELECTION,
    WMS_PICK_TASK_STATUS_SELECTION,
    WMS_PUTAWAY_TASK_STATUS_SELECTION,
    WMS_RECEIPT_TASK_STATUS_SELECTION,
)


class WmsTaskMixin(models.AbstractModel):
    _name = "wms.task.mixin"
    _description = "WMS Task Mixin"

    @api.model
    def _next_sequence(self, code, fallback):
        return self.env["ir.sequence"].next_by_code(code) or fallback

    def _require_warehouse(self, warehouse_id):
        if not warehouse_id:
            raise ValidationError(_("Warehouse is required before generating the next task."))

    def action_print_barcode_label(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "name": _("Print Barcode Label"),
            "url": f"/wms/barcode/label/{self._name}/{self.id}",
            "target": "new",
        }


class WmsReceiptTask(models.Model):
    _name = "wms.receipt.task"
    _description = "WMS Receipt Task"
    _inherit = ["mail.thread", "mail.activity.mixin", "wms.task.mixin"]
    _order = "id desc"

    name = fields.Char(string="Task No", required=True, copy=False, tracking=True, default=lambda self: self._next_sequence("wms.receipt.task", "WMS-REC-NEW"))
    state = fields.Selection(
        selection=WMS_RECEIPT_TASK_STATUS_SELECTION,
        string="Status",
        default="waiting_receipt",
        required=True,
        tracking=True,
    )
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", required=True, index=True)
    stock_picking_id = fields.Many2one("stock.picking", string="Source Picking", ondelete="set null", index=True)
    partner_id = fields.Many2one("res.partner", string="Partner", ondelete="set null", index=True)
    scheduled_date = fields.Datetime(string="Scheduled Date")
    putaway_task_ids = fields.One2many("wms.putaway.task", "receipt_task_id", string="Putaway Tasks")
    note = fields.Text(string="Note")

    @api.model
    def create_from_picking(self, picking):
        warehouse = picking.picking_type_id.warehouse_id
        self._require_warehouse(warehouse.id if warehouse else False)
        receipt = self.search([("stock_picking_id", "=", picking.id)], limit=1)
        if receipt:
            return receipt
        receipt = self.create({
            "warehouse_id": warehouse.id,
            "stock_picking_id": picking.id,
            "partner_id": picking.partner_id.id,
            "scheduled_date": picking.scheduled_date,
            "note": picking.note,
        })
        picking.write({"wms_task_ref": receipt.name})
        return receipt

    def action_start_receipt(self):
        self.write({"state": "receiving"})
        return True

    def action_mark_received(self):
        for record in self:
            record.write({"state": "received"})
            if record.stock_picking_id:
                record.stock_picking_id.write({"wms_task_ref": record.name})
            if not record.putaway_task_ids:
                record.action_create_putaway_task()
        return True

    def action_create_putaway_task(self):
        self.ensure_one()
        putaway = self.env["wms.putaway.task"].search([("receipt_task_id", "=", self.id)], limit=1)
        if not putaway:
            putaway = self.env["wms.putaway.task"].create({
                "warehouse_id": self.warehouse_id.id,
                "stock_picking_id": self.stock_picking_id.id,
                "receipt_task_id": self.id,
                "source_location_id": self.stock_picking_id.location_dest_id.id,
                "note": self.note,
            })
        return putaway.action_open_record()

    def action_open_record(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Receipt Task"),
            "res_model": "wms.receipt.task",
            "view_mode": "form",
            "res_id": self.id,
        }


class WmsPutawayTask(models.Model):
    _name = "wms.putaway.task"
    _description = "WMS Putaway Task"
    _inherit = ["mail.thread", "mail.activity.mixin", "wms.task.mixin"]
    _order = "id desc"

    name = fields.Char(string="Task No", required=True, copy=False, tracking=True, default=lambda self: self._next_sequence("wms.putaway.task", "WMS-PUT-NEW"))
    state = fields.Selection(
        selection=WMS_PUTAWAY_TASK_STATUS_SELECTION,
        string="Status",
        default="waiting_putaway",
        required=True,
        tracking=True,
    )
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", required=True, index=True)
    stock_picking_id = fields.Many2one("stock.picking", string="Source Picking", ondelete="set null", index=True)
    receipt_task_id = fields.Many2one("wms.receipt.task", string="Receipt Task", ondelete="set null", index=True)
    source_location_id = fields.Many2one("stock.location", string="Source Location", ondelete="set null")
    dest_location_id = fields.Many2one("stock.location", string="Destination Location", ondelete="set null")
    note = fields.Text(string="Note")

    def action_start_putaway(self):
        self.write({"state": "putaway_ing"})
        return True

    def action_mark_done(self):
        self.write({"state": "putaway_done"})
        return True

    def action_open_record(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Putaway Task"),
            "res_model": "wms.putaway.task",
            "view_mode": "form",
            "res_id": self.id,
        }


class WmsOutboundTask(models.Model):
    _name = "wms.outbound.task"
    _description = "WMS Outbound Task"
    _inherit = ["mail.thread", "mail.activity.mixin", "wms.task.mixin"]
    _order = "id desc"

    name = fields.Char(string="Task No", required=True, copy=False, tracking=True, default=lambda self: self._next_sequence("wms.outbound.task", "WMS-OUT-NEW"))
    state = fields.Selection(
        selection=WMS_OUTBOUND_TASK_STATUS_SELECTION,
        string="Status",
        default="waiting_outbound",
        required=True,
        tracking=True,
    )
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", required=True, index=True)
    stock_picking_id = fields.Many2one("stock.picking", string="Source Picking", ondelete="set null", index=True)
    store_partner_id = fields.Many2one("res.partner", string="Store Partner", ondelete="set null", index=True)
    move_line_count = fields.Integer(string="Move Line Count", compute="_compute_counts")
    pick_task_ids = fields.One2many("wms.pick.task", "outbound_task_id", string="Pick Tasks")
    check_task_ids = fields.One2many("wms.check.task", "outbound_task_id", string="Check Tasks")
    handover_order_ids = fields.One2many("wms.handover.order", "outbound_task_id", string="Handover Orders")
    note = fields.Text(string="Note")

    @api.depends("pick_task_ids")
    def _compute_counts(self):
        for record in self:
            record.move_line_count = len(record.pick_task_ids)

    @api.model
    def create_from_picking(self, picking):
        warehouse = picking.picking_type_id.warehouse_id
        self._require_warehouse(warehouse.id if warehouse else False)
        outbound = self.search([("stock_picking_id", "=", picking.id)], limit=1)
        if outbound:
            return outbound
        outbound = self.create({
            "warehouse_id": warehouse.id,
            "stock_picking_id": picking.id,
            "store_partner_id": picking.store_partner_id.id or picking.partner_id.id,
            "note": picking.note,
        })
        picking.write({
            "wms_task_ref": outbound.name,
            "wms_flow_stage": "task_created",
        })
        return outbound

    # #2: WMS出库任务状态变化 → 反写 sale.order.wms_status
    def write(self, vals):
        res = super().write(vals)
        if "state" in vals:
            for task in self:
                task._backfill_sale_wms_status()
        return res

    def _backfill_sale_wms_status(self):
        picking = self.stock_picking_id
        if not picking or not picking.sale_id:
            return
        state_map = {
            "waiting_outbound": "pending",
            "task_created": "pending",
            "task_processing": "picking",
            "task_done": "ready",
            "task_exception": "exception",
        }
        wms_status = state_map.get(self.state, "pending")
        picking.sale_id.write({"wms_status": wms_status})

    def action_start_outbound(self):
        for record in self:
            record.write({"state": "task_processing"})
            if record.stock_picking_id:
                record.stock_picking_id.write({"wms_flow_stage": "task_processing"})
        return True

    def action_generate_pick_task(self):
        self.ensure_one()
        pick_task = self.pick_task_ids[:1]
        if not pick_task:
            line_vals = []
            for move in self.stock_picking_id.move_ids.filtered(lambda m: m.product_id):
                lot_id = False
                if "restrict_lot_id" in move._fields and move.restrict_lot_id:
                    lot_id = move.restrict_lot_id.id
                line_vals.append(
                    {
                        "product_id": move.product_id.id,
                        "source_location_id": move.location_id.id,
                        "demand_qty": move.product_uom_qty,
                        "done_qty": 0.0,
                        "lot_id": lot_id,
                    }
                )
            pick_task = self.env["wms.pick.task"].create({
                "outbound_task_id": self.id,
                "note": self.note,
                "line_ids": [(0, 0, vals) for vals in line_vals],
            })
        return pick_task.action_open_record()

    def action_mark_done(self):
        for record in self:
            record.write({"state": "task_done"})
            if record.stock_picking_id:
                record.stock_picking_id.write({"wms_flow_stage": "task_done"})
        return True

    def action_open_record(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Outbound Task"),
            "res_model": "wms.outbound.task",
            "view_mode": "form",
            "res_id": self.id,
        }


class WmsPickTask(models.Model):
    _name = "wms.pick.task"
    _description = "WMS Pick Task"
    _inherit = ["mail.thread", "mail.activity.mixin", "wms.task.mixin"]
    _order = "id desc"

    name = fields.Char(string="Task No", required=True, copy=False, tracking=True, default=lambda self: self._next_sequence("wms.pick.task", "WMS-PICK-NEW"))
    state = fields.Selection(
        selection=WMS_PICK_TASK_STATUS_SELECTION,
        string="Status",
        default="waiting_pick",
        required=True,
        tracking=True,
    )
    outbound_task_id = fields.Many2one("wms.outbound.task", string="Outbound Task", required=True, ondelete="cascade", index=True)
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", related="outbound_task_id.warehouse_id", store=True)
    store_partner_id = fields.Many2one("res.partner", string="Store Partner", related="outbound_task_id.store_partner_id", store=True)
    line_ids = fields.One2many("wms.pick.task.line", "pick_task_id", string="Task Lines")
    note = fields.Text(string="Note")

    def action_start_pick(self):
        self.write({"state": "picking"})
        self.outbound_task_id.action_start_outbound()
        return True

    def action_mark_picked(self):
        for record in self:
            for line in record.line_ids.filtered(lambda l: not l.done_qty and l.demand_qty):
                line.done_qty = line.demand_qty
            record.write({"state": "picked"})
            if not record.outbound_task_id.check_task_ids:
                record.action_create_check_task()
        return True

    def action_create_check_task(self):
        self.ensure_one()
        check_task = self.env["wms.check.task"].search([("pick_task_id", "=", self.id)], limit=1)
        if not check_task:
            check_task = self.env["wms.check.task"].create({
                "outbound_task_id": self.outbound_task_id.id,
                "pick_task_id": self.id,
                "warehouse_id": self.warehouse_id.id,
                "note": self.note,
            })
        return check_task.action_open_record()

    def action_open_record(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Pick Task"),
            "res_model": "wms.pick.task",
            "view_mode": "form",
            "res_id": self.id,
        }


class WmsPickTaskLine(models.Model):
    _name = "wms.pick.task.line"
    _description = "WMS Pick Task Line"
    _order = "id asc"

    pick_task_id = fields.Many2one("wms.pick.task", string="Pick Task", required=True, ondelete="cascade", index=True)
    product_id = fields.Many2one("product.product", string="Product", required=True, ondelete="restrict", index=True)
    source_location_id = fields.Many2one("stock.location", string="Source Location", ondelete="set null")
    demand_qty = fields.Float(string="Demand Qty", default=0.0, digits=(16, 4))
    done_qty = fields.Float(string="Done Qty", default=0.0, digits=(16, 4))
    lot_id = fields.Many2one("stock.lot", string="Lot", ondelete="set null")


class WmsCheckTask(models.Model):
    _name = "wms.check.task"
    _description = "WMS Check Task"
    _inherit = ["mail.thread", "mail.activity.mixin", "wms.task.mixin"]
    _order = "id desc"

    name = fields.Char(string="Task No", required=True, copy=False, tracking=True, default=lambda self: self._next_sequence("wms.check.task", "WMS-CHK-NEW"))
    state = fields.Selection(
        selection=WMS_CHECK_TASK_STATUS_SELECTION,
        string="Status",
        default="waiting_check",
        required=True,
        tracking=True,
    )
    outbound_task_id = fields.Many2one("wms.outbound.task", string="Outbound Task", ondelete="set null", index=True)
    pick_task_id = fields.Many2one("wms.pick.task", string="Pick Task", ondelete="set null", index=True)
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", ondelete="set null", index=True)
    note = fields.Text(string="Note")

    def action_start_check(self):
        self.write({"state": "checking"})
        return True

    def action_mark_checked(self):
        for record in self:
            record.write({"state": "checked"})
            if not record.outbound_task_id.handover_order_ids:
                record.action_create_handover_order()
        return True

    def action_create_handover_order(self):
        self.ensure_one()
        handover = self.env["wms.handover.order"].search([("outbound_task_id", "=", self.outbound_task_id.id)], limit=1)
        if not handover:
            handover = self.env["wms.handover.order"].create({
                "warehouse_id": self.warehouse_id.id,
                "outbound_task_id": self.outbound_task_id.id,
                "route_batch_id": False,
                "note": self.note,
            })
            if self.outbound_task_id.stock_picking_id:
                self.outbound_task_id.stock_picking_id.write({"tms_handover_status": "waiting_handover"})
        return handover.action_open_record()

    def action_open_record(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Check Task"),
            "res_model": "wms.check.task",
            "view_mode": "form",
            "res_id": self.id,
        }


class WmsHandoverOrder(models.Model):
    _name = "wms.handover.order"
    _description = "WMS Handover Order"
    _inherit = ["mail.thread", "mail.activity.mixin", "wms.task.mixin"]
    _order = "id desc"

    name = fields.Char(string="Handover No", required=True, copy=False, tracking=True, default=lambda self: self._next_sequence("wms.handover.order", "WMS-HO-NEW"))
    state = fields.Selection(
        selection=WMS_HANDOVER_STATUS_SELECTION,
        string="Status",
        default="waiting_handover",
        required=True,
        tracking=True,
    )
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", required=True, index=True)
    outbound_task_id = fields.Many2one("wms.outbound.task", string="Outbound Task", ondelete="set null", index=True)
    route_batch_id = fields.Many2one("logistics.route.planning.batch", string="Route Batch", ondelete="set null", index=True)
    driver_profile_id = fields.Many2one("logistics.driver.profile", string="Driver Profile", ondelete="set null")
    vehicle_profile_id = fields.Many2one("logistics.vehicle.profile", string="Vehicle Profile", ondelete="set null")
    weight_total = fields.Float(string="Weight Total", digits=(16, 4), default=0.0)
    volume_total = fields.Float(string="Volume Total", digits=(16, 6), default=0.0)
    note = fields.Text(string="Note")

    def action_start_handover(self):
        for record in self:
            record.write({"state": "handover_ing"})
            if record.outbound_task_id.stock_picking_id:
                record.outbound_task_id.stock_picking_id.write({"tms_handover_status": "handover_ing"})
        return True

    def action_mark_done(self):
        for record in self:
            record.write({"state": "handover_done"})
            record.outbound_task_id.action_mark_done()
            if record.outbound_task_id.stock_picking_id:
                record.outbound_task_id.stock_picking_id.write({"tms_handover_status": "handover_done"})
        return True

    def action_open_record(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Handover Order"),
            "res_model": "wms.handover.order",
            "view_mode": "form",
            "res_id": self.id,
        }
