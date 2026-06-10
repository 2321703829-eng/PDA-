from odoo import fields, models


class WmsPdaRequestLog(models.Model):
    _name = "wms.pda.request.log"
    _description = "WMS PDA Idempotent Request Log"
    _order = "id desc"

    _uniq_request_id = models.Constraint(
        "unique(request_id)",
        "request_id must be unique.",
    )

    request_id = fields.Char(required=True, index=True)
    endpoint = fields.Char(required=True, index=True)
    method = fields.Char(required=True, default="POST")
    user_id = fields.Many2one("res.users", string="User", ondelete="set null", index=True)
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", ondelete="set null", index=True)
    device_id = fields.Char(index=True)
    payload_hash = fields.Char(required=True, index=True)
    response_json = fields.Text()
    state = fields.Selection(
        [
            ("processing", "Processing"),
            ("done", "Done"),
            ("failed", "Failed"),
        ],
        default="processing",
        required=True,
        index=True,
    )
    error_message = fields.Text()
    created_at = fields.Datetime(default=fields.Datetime.now, required=True, index=True)

