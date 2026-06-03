from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


WMS_INVENTORY_OPERATION_TYPE_SELECTION = [
    ("inventory_count", "Inventory Count"),
    ("stock_adjustment", "Stock Adjustment"),
    ("warehouse_return", "Warehouse Return"),
]

WMS_INVENTORY_OPERATION_STATUS_SELECTION = [
    ("draft", "Draft"),
    ("in_progress", "In Progress"),
    ("done", "Done"),
    ("cancelled", "Cancelled"),
]


class WmsInventoryOperation(models.Model):
    _name = "wms.inventory.operation"
    _description = "WMS Inventory Operation"
    _inherit = ["mail.thread", "mail.activity.mixin", "wms.task.mixin"]
    _order = "id desc"

    name = fields.Char(
        string="Operation No",
        required=True,
        copy=False,
        tracking=True,
        default=lambda self: self._next_sequence("wms.inventory.operation", "WMS-INV-NEW"),
    )
    state = fields.Selection(
        selection=WMS_INVENTORY_OPERATION_STATUS_SELECTION,
        string="Status",
        default="draft",
        required=True,
        tracking=True,
    )
    operation_type = fields.Selection(
        selection=WMS_INVENTORY_OPERATION_TYPE_SELECTION,
        string="Operation Type",
        required=True,
        default="inventory_count",
        tracking=True,
    )
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", required=True, index=True)
    location_id = fields.Many2one("stock.location", string="Location", required=True, index=True)
    return_location_id = fields.Many2one("stock.location", string="Return To", index=True)
    partner_id = fields.Many2one("res.partner", string="Counterparty", ondelete="set null", index=True)
    scheduled_date = fields.Datetime(string="Scheduled Date", default=fields.Datetime.now)
    line_ids = fields.One2many("wms.inventory.operation.line", "operation_id", string="Lines")
    source_picking_id = fields.Many2one("stock.picking", string="Source Picking", ondelete="set null", index=True)
    generated_picking_id = fields.Many2one("stock.picking", string="Generated Picking", ondelete="set null", index=True, readonly=True)
    note = fields.Text(string="Note")
    line_count = fields.Integer(string="Line Count", compute="_compute_totals")
    total_system_qty = fields.Float(string="System Qty", compute="_compute_totals", digits=(16, 4))
    total_count_qty = fields.Float(string="Count Qty", compute="_compute_totals", digits=(16, 4))
    total_diff_qty = fields.Float(string="Diff Qty", compute="_compute_totals", digits=(16, 4))
    has_generated_picking = fields.Boolean(
        string="Has Generated Picking",
        compute="_compute_generated_picking_flags",
    )
    has_source_picking = fields.Boolean(
        string="Has Source Picking",
        compute="_compute_generated_picking_flags",
    )

    @api.depends("line_ids.system_qty", "line_ids.count_qty", "line_ids.diff_qty")
    def _compute_totals(self):
        for record in self:
            record.line_count = len(record.line_ids)
            record.total_system_qty = sum(record.line_ids.mapped("system_qty"))
            record.total_count_qty = sum(record.line_ids.mapped("count_qty"))
            record.total_diff_qty = sum(record.line_ids.mapped("diff_qty"))

    @api.depends("generated_picking_id", "source_picking_id")
    def _compute_generated_picking_flags(self):
        for record in self:
            record.has_generated_picking = bool(record.generated_picking_id)
            record.has_source_picking = bool(record.source_picking_id)

    def action_start(self):
        for record in self:
            record.write({"state": "in_progress"})
            self.env["core.operation.audit.log"].log_action(
                business_domain="wms",
                action_code="inventory_operation_start",
                record=record,
                note=_("Inventory operation started."),
            )
        return True

    def action_cancel(self):
        for record in self:
            record.write({"state": "cancelled"})
            if "core.operation.audit.log" in self.env.registry:
                self.env["core.operation.audit.log"].log_action(
                    business_domain="wms",
                    action_code="inventory_operation_cancel",
                    action_result="cancelled",
                    record=record,
                    note=_("Inventory operation cancelled."),
                )
        return True

    def action_load_location_quants(self):
        for record in self:
            record.line_ids.unlink()
            quants = self.env["stock.quant"].search(
                [
                    ("location_id", "=", record.location_id.id),
                    ("product_id", "!=", False),
                ]
            )
            line_commands = []
            for quant in quants:
                line_commands.append(
                    (
                        0,
                        0,
                        {
                            "product_id": quant.product_id.id,
                            "lot_id": quant.lot_id.id,
                            "uom_id": quant.product_id.uom_id.id,
                            "system_qty": quant.quantity,
                            "count_qty": quant.quantity,
                        },
                    )
                )
            record.write({"line_ids": line_commands})
            self.env["core.operation.audit.log"].log_action(
                business_domain="wms",
                action_code="inventory_operation_load_quants",
                record=record,
                note=_("Location quants loaded into inventory operation."),
                payload={"line_count": len(line_commands)},
            )
        return True

    def _find_internal_picking_type(self):
        self.ensure_one()
        picking_type = self.env["stock.picking.type"].search(
            [("warehouse_id", "=", self.warehouse_id.id), ("code", "=", "internal")],
            order="id asc",
            limit=1,
        )
        if not picking_type:
            raise ValidationError(_("Internal picking type is required before processing warehouse returns."))
        return picking_type

    def _apply_quant_count(self, line):
        quant = self.env["stock.quant"].search(
            [
                ("location_id", "=", self.location_id.id),
                ("product_id", "=", line.product_id.id),
                ("lot_id", "=", line.lot_id.id or False),
            ],
            limit=1,
        )
        if quant and "inventory_quantity" in quant._fields and hasattr(quant, "action_apply_inventory"):
            quant.inventory_quantity = line.count_qty
            quant.action_apply_inventory()

    def _create_return_picking(self):
        self.ensure_one()
        picking_type = self._find_internal_picking_type()
        destination = self.return_location_id or self.warehouse_id.lot_stock_id
        if not destination:
            raise ValidationError(_("Return destination location is required before processing warehouse returns."))
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": self.location_id.id,
                "location_dest_id": destination.id,
                "origin": self.name,
                "note": self.note,
            }
        )
        move_commands = []
        for line in self.line_ids.filtered(lambda l: l.count_qty):
            move_commands.append(
                (
                    0,
                    0,
                    {
                        "name": line.product_id.display_name,
                        "product_id": line.product_id.id,
                        "product_uom_qty": line.count_qty,
                        "product_uom": line.uom_id.id or line.product_id.uom_id.id,
                        "location_id": self.location_id.id,
                        "location_dest_id": destination.id,
                    },
                )
            )
        if not move_commands:
            raise ValidationError(_("At least one line with quantity is required before creating a warehouse return picking."))
        picking.write({"move_ids_without_package": move_commands})
        return picking

    def action_mark_done(self):
        for record in self:
            if not record.line_ids:
                raise ValidationError(_("At least one inventory line is required before completing the operation."))
            if record.operation_type == "warehouse_return":
                picking = record._create_return_picking()
                if hasattr(picking, "action_confirm"):
                    picking.action_confirm()
                record.generated_picking_id = picking.id
            else:
                for line in record.line_ids:
                    record._apply_quant_count(line)
            record.state = "done"
            self.env["core.operation.audit.log"].log_action(
                business_domain="wms",
                action_code="inventory_operation_done",
                record=record,
                note=_("Inventory operation completed."),
                related_record=record.generated_picking_id or record.source_picking_id,
                payload={
                    "operation_type": record.operation_type,
                    "line_count": record.line_count,
                    "total_diff_qty": record.total_diff_qty,
                },
            )
        return True

    def action_open_operation_logs(self):
        self.ensure_one()
        return self.env["core.operation.audit.log"].action_open_logs_for_record(self)

    def action_open_source_picking(self):
        self.ensure_one()
        if not self.source_picking_id:
            raise ValidationError(_("Source picking is not available for this inventory operation."))
        return {
            "type": "ir.actions.act_window",
            "name": _("Source Picking"),
            "res_model": "stock.picking",
            "view_mode": "form",
            "res_id": self.source_picking_id.id,
        }

    def action_open_generated_picking(self):
        self.ensure_one()
        if not self.generated_picking_id:
            raise ValidationError(_("No return picking has been generated for this inventory operation yet."))
        return {
            "type": "ir.actions.act_window",
            "name": _("Generated Picking"),
            "res_model": "stock.picking",
            "view_mode": "form",
            "res_id": self.generated_picking_id.id,
        }

    def action_open_record(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Inventory Operation"),
            "res_model": "wms.inventory.operation",
            "view_mode": "form",
            "res_id": self.id,
        }


class WmsInventoryOperationLine(models.Model):
    _name = "wms.inventory.operation.line"
    _description = "WMS Inventory Operation Line"
    _order = "id asc"

    operation_id = fields.Many2one("wms.inventory.operation", string="Operation", required=True, ondelete="cascade", index=True)
    product_id = fields.Many2one("product.product", string="Product", required=True, ondelete="restrict", index=True)
    lot_id = fields.Many2one("stock.lot", string="Lot", ondelete="set null")
    uom_id = fields.Many2one("uom.uom", string="UoM", ondelete="set null")
    system_qty = fields.Float(string="System Qty", digits=(16, 4), default=0.0)
    count_qty = fields.Float(string="Count Qty", digits=(16, 4), default=0.0)
    diff_qty = fields.Float(string="Diff Qty", digits=(16, 4), compute="_compute_diff", store=True)
    note = fields.Char(string="Remark")

    @api.depends("system_qty", "count_qty")
    def _compute_diff(self):
        for record in self:
            record.diff_qty = record.count_qty - record.system_qty
