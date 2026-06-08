from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class WmsTaskLock(models.Model):
    _name = "wms.task.lock"
    _description = "WMS PDA Task Lock"
    _order = "id desc"

    task_model = fields.Char(string="任务模型", required=True, index=True)
    task_id = fields.Integer(string="任务 ID", required=True, index=True)
    user_id = fields.Many2one("res.users", string="锁定人", required=True, ondelete="cascade")
    warehouse_id = fields.Many2one("stock.warehouse", string="仓库", ondelete="set null")
    locked_at = fields.Datetime(string="锁定时间", default=fields.Datetime.now, required=True)
    expires_at = fields.Datetime(string="过期时间", index=True)
    is_active = fields.Boolean(string="有效", default=True, index=True)

    @api.model
    def acquire(self, task_model, task_id, user_id, warehouse_id=False, timeout_minutes=30):
        now = fields.Datetime.now()
        locks = self.search(
            [
                ("task_model", "=", task_model),
                ("task_id", "=", task_id),
                ("is_active", "=", True),
            ]
        )
        expired = locks.filtered(lambda lock: lock.expires_at and lock.expires_at <= now)
        if expired:
            expired.write({"is_active": False})
        active = locks - expired
        if active and active.user_id.id != user_id:
            raise ValidationError(_("任务已被 %s 锁定，请稍后再试。") % active.user_id.display_name)
        if active:
            active.write(
                {
                    "locked_at": now,
                    "expires_at": now + timedelta(minutes=timeout_minutes),
                    "warehouse_id": warehouse_id or active.warehouse_id.id,
                }
            )
            return active
        return self.create(
            {
                "task_model": task_model,
                "task_id": task_id,
                "user_id": user_id,
                "warehouse_id": warehouse_id,
                "locked_at": now,
                "expires_at": now + timedelta(minutes=timeout_minutes),
                "is_active": True,
            }
        )

    @api.model
    def release(self, task_model, task_id, user_id=False):
        domain = [
            ("task_model", "=", task_model),
            ("task_id", "=", task_id),
            ("is_active", "=", True),
        ]
        if user_id:
            domain.append(("user_id", "=", user_id))
        self.search(domain).write({"is_active": False})
        return True

    @api.model
    def get_lock_holder(self, task_model, task_id):
        now = fields.Datetime.now()
        lock = self.search(
            [
                ("task_model", "=", task_model),
                ("task_id", "=", task_id),
                ("is_active", "=", True),
            ],
            limit=1,
        )
        if lock and lock.expires_at and lock.expires_at <= now:
            lock.write({"is_active": False})
            return False
        return lock.user_id.display_name if lock else False
