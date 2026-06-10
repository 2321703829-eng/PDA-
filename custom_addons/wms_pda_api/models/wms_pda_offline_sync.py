from odoo import fields, models


class WmsPdaOfflineSync(models.Model):
    _name = "wms.pda.offline.sync"
    _description = "WMS PDA Offline Sync Log"
    _order = "id desc"

    _uniq_sync_id = models.Constraint(
        "unique(sync_id)",
        "sync_id must be unique.",
    )

    sync_id = fields.Char(required=True, index=True)
    user_id = fields.Many2one("res.users", string="User", ondelete="set null", index=True)
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", ondelete="set null", index=True)
    device_id = fields.Char(index=True)
    request_count = fields.Integer(default=0)
    success_count = fields.Integer(default=0)
    failed_count = fields.Integer(default=0)
    results_json = fields.Text()
    state = fields.Selection(
        [
            ("done", "Done"),
            ("partial", "Partial"),
            ("failed", "Failed"),
        ],
        default="done",
        required=True,
        index=True,
    )
    created_at = fields.Datetime(default=fields.Datetime.now, required=True, index=True)

