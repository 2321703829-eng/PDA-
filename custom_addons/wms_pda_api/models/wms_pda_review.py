from odoo import fields, models
from odoo.exceptions import ValidationError


REVIEW_STATE_SELECTION = [
    ("normal", "正常"),
    ("pending_review", "待审核"),
    ("reviewed", "已审核"),
    ("force_completed", "强制完成"),
]


class WmsPdaReviewTaskMixin(models.AbstractModel):
    _name = "wms.pda.review.task.mixin"
    _description = "WMS PDA Review Task Mixin"

    review_state = fields.Selection(
        selection=REVIEW_STATE_SELECTION,
        string="审核状态",
        default="normal",
        required=True,
        tracking=True,
    )
    review_user_id = fields.Many2one("res.users", string="审核人", tracking=True)
    review_date = fields.Datetime(string="审核时间", tracking=True)
    review_note = fields.Text(string="审核备注")
    exception_note = fields.Text(string="异常说明")
    force_complete_reason = fields.Text(string="强制完成原因")

    def action_submit_pda_review(self, exception_note=None):
        for record in self:
            vals = {"review_state": "pending_review"}
            if exception_note:
                vals["exception_note"] = exception_note
            exception_state = record._pda_review_exception_state()
            if exception_state and record.state != exception_state:
                vals["state"] = exception_state
            record.write(vals)
        return True

    def pda_review_resolve(self, action, reason=None):
        self.ensure_one()
        reason = reason or ""
        if action not in ("approve", "reject", "force_complete"):
            raise ValidationError("不支持的审核动作。")
        if action in ("approve", "reject") and not self._pda_review_is_reviewable():
            raise ValidationError("当前任务不是待审核异常状态。")
        if action == "approve":
            self._pda_review_mark_done()
            self._pda_review_write_result("reviewed", reason)
        elif action == "reject":
            self._pda_review_reopen()
            self._pda_review_write_result("normal", reason)
        else:
            if not reason:
                raise ValidationError("强制完成必须填写原因。")
            self._pda_review_mark_done()
            self._pda_review_write_result("force_completed", reason, force=True)
        return True

    def _pda_review_write_result(self, state, reason, force=False):
        vals = {
            "review_state": state,
            "review_user_id": self.env.user.id,
            "review_date": fields.Datetime.now(),
            "review_note": reason,
        }
        if force:
            vals["force_complete_reason"] = reason
        self.write(vals)
        self.message_post(body=f"PDA异常审核：{state}。{reason}" if reason else f"PDA异常审核：{state}。")

    def _pda_review_is_reviewable(self):
        return self.review_state == "pending_review" or self.state == self._pda_review_exception_state()

    def _pda_review_exception_state(self):
        return {
            "wms.receipt.task": "receipt_exception",
            "wms.putaway.task": "putaway_exception",
            "wms.outbound.task": "task_exception",
            "wms.pick.task": "pick_exception",
            "wms.check.task": "check_exception",
            "wms.handover.order": "handover_exception",
        }.get(self._name)

    def _pda_review_active_state(self):
        return {
            "wms.receipt.task": "receiving",
            "wms.putaway.task": "putaway_ing",
            "wms.outbound.task": "task_processing",
            "wms.pick.task": "picking",
            "wms.check.task": "checking",
            "wms.handover.order": "handover_ing",
        }.get(self._name)

    def _pda_review_done_state(self):
        return {
            "wms.receipt.task": "received",
            "wms.putaway.task": "putaway_done",
            "wms.outbound.task": "task_done",
            "wms.pick.task": "picked",
            "wms.check.task": "checked",
            "wms.handover.order": "handover_done",
        }.get(self._name)

    def _pda_review_reopen(self):
        active_state = self._pda_review_active_state()
        if active_state:
            self.write({"state": active_state})

    def _pda_review_mark_done(self):
        if self._name == "wms.receipt.task":
            if self.state != "received":
                self.action_mark_received()
            return
        if self._name == "wms.putaway.task":
            if self.state != "putaway_done":
                self.action_mark_done()
            return
        if self._name == "wms.outbound.task":
            if self.state != "task_done":
                self.action_mark_done()
            return
        if self._name == "wms.pick.task":
            if self.state != "picked":
                self.write({"state": "picked"})
                if not self.outbound_task_id.check_task_ids:
                    self.action_create_check_task()
            return
        if self._name == "wms.check.task":
            if self.state != "checked":
                self.action_mark_checked()
            return
        if self._name == "wms.handover.order":
            if self.state != "handover_done":
                self.action_mark_done()
            return
        done_state = self._pda_review_done_state()
        if done_state:
            self.write({"state": done_state})


class WmsReceiptTaskPdaReview(models.Model):
    _inherit = ["wms.receipt.task", "wms.pda.review.task.mixin"]


class WmsPutawayTaskPdaReview(models.Model):
    _inherit = ["wms.putaway.task", "wms.pda.review.task.mixin"]


class WmsOutboundTaskPdaReview(models.Model):
    _inherit = ["wms.outbound.task", "wms.pda.review.task.mixin"]


class WmsPickTaskPdaReview(models.Model):
    _inherit = ["wms.pick.task", "wms.pda.review.task.mixin"]


class WmsCheckTaskPdaReview(models.Model):
    _inherit = ["wms.check.task", "wms.pda.review.task.mixin"]


class WmsHandoverOrderPdaReview(models.Model):
    _inherit = ["wms.handover.order", "wms.pda.review.task.mixin"]
