import uuid
from datetime import timedelta

from odoo import api, fields, models


class WmsApiToken(models.Model):
    _name = "wms.api.token"
    _description = "WMS PDA API Token"
    _order = "id desc"

    user_id = fields.Many2one("res.users", string="用户", required=True, index=True, ondelete="cascade")
    token = fields.Char(string="Token", required=True, index=True, copy=False)
    device_id = fields.Char(string="设备号", index=True)
    warehouse_id = fields.Many2one("stock.warehouse", string="当前仓库", index=True)
    expires_at = fields.Datetime(string="过期时间", index=True)
    is_active = fields.Boolean(string="有效", default=True, index=True)
    last_used_at = fields.Datetime(string="最后使用时间")
    is_expired = fields.Boolean(string="已过期", compute="_compute_is_expired")

    _sql_constraints = [
        ("token_unique", "unique(token)", "PDA Token 必须唯一。"),
    ]

    @api.depends("expires_at")
    def _compute_is_expired(self):
        now = fields.Datetime.now()
        for record in self:
            record.is_expired = bool(record.expires_at and record.expires_at < now)

    @api.model
    def generate_token(self, user_id, device_id=None, warehouse_id=None, hours=24):
        domain = [("user_id", "=", user_id), ("is_active", "=", True)]
        if device_id:
            domain.append(("device_id", "=", device_id))
        self.search(domain).write({"is_active": False})
        return self.create(
            {
                "user_id": user_id,
                "device_id": device_id,
                "warehouse_id": warehouse_id,
                "token": str(uuid.uuid4()),
                "expires_at": fields.Datetime.now() + timedelta(hours=hours),
                "is_active": True,
            }
        )

    def touch(self):
        self.write({"last_used_at": fields.Datetime.now()})

    def action_revoke(self):
        self.write({"is_active": False})
        return True
