from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LogisticsTraceEvent(models.Model):
    _name = "logistics.trace.event"
    _description = "Logistics Trace Event"
    _order = "occurred_at desc, id desc"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ("new", "New"),
            ("done", "Done"),
            ("void", "Void"),
        ],
        default="new",
        required=True,
    )
    biz_type = fields.Selection(
        [
            ("batch", "Batch"),
            ("waybill", "Waybill"),
        ],
        required=True,
        default="waybill",
    )
    trace_type = fields.Selection(
        [
            ("load", "Load"),
            ("arrive", "Arrive"),
            ("sign", "Sign"),
            ("exception", "Exception"),
        ],
        default="arrive",
        required=True,
    )
    occurred_at = fields.Datetime(default=fields.Datetime.now, required=True)
    trace_source = fields.Selection(
        [
            ("admin", "Admin"),
            ("mini", "Mini Program"),
            ("system", "System"),
            ("open", "Open API"),
        ],
        default="admin",
        required=True,
    )
    batch_no = fields.Char(index=True)
    waybill_no = fields.Char(index=True)
    stock_picking_id = fields.Many2one("stock.picking", string="Related Odoo Delivery Record", index=True)
    partner_id = fields.Many2one("res.partner", string="Store / Contact", index=True)
    operator_id = fields.Many2one(
        "res.users",
        string="Operator",
        default=lambda self: self.env.user,
        index=True,
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    driver_name = fields.Char()
    vehicle_no = fields.Char()
    location_text = fields.Char(string="Location")
    route_sequence = fields.Integer()
    is_exception = fields.Boolean(default=False)
    remark = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name"):
                vals["name"] = self.env["ir.sequence"].next_by_code("logistics.trace.event") or "TR"
        return super().create(vals_list)

    @api.constrains("biz_type", "batch_no", "waybill_no")
    def _check_biz_identifier(self):
        for record in self:
            if record.biz_type == "batch" and not record.batch_no:
                raise ValidationError("Batch trace events must have a batch number.")
            if record.biz_type == "waybill" and not record.waybill_no:
                raise ValidationError("Waybill trace events must have a waybill number.")
            if record.biz_type == "batch" and record.waybill_no:
                raise ValidationError("Batch trace events cannot carry a waybill number.")
            if record.biz_type == "waybill" and record.batch_no:
                raise ValidationError("Waybill trace events cannot carry a batch number.")

    def action_mark_done(self):
        self.write({"state": "done"})

    def action_mark_exception(self):
        self.write({"state": "done", "trace_type": "exception", "is_exception": True})

    def action_reset_new(self):
        self.write({"state": "new", "is_exception": False})

    def action_mark_void(self):
        self.write({"state": "void"})
