from odoo import _, api, fields, models


class LogisticsDispatchWaybill(models.Model):
    _inherit = "logistics.dispatch.waybill"

    exception_ids = fields.One2many(
        "logistics.trace.exception",
        "waybill_id",
        string="Exceptions",
    )
    open_exception_count = fields.Integer(
        string="Open Exception Count",
        compute="_compute_exception_metrics",
        store=True,
        readonly=True,
    )
    exception_status = fields.Selection(
        [
            ("none", "No Exception"),
            ("open", "Open"),
            ("processing", "Processing"),
            ("closed", "Closed"),
        ],
        string="Exception Status",
        compute="_compute_exception_metrics",
        store=True,
        readonly=True,
    )
    risk_level = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        string="Risk Level",
        compute="_compute_exception_metrics",
        store=True,
        readonly=True,
    )

    @api.depends("exception_ids.state", "exception_ids.severity_level")
    def _compute_exception_metrics(self):
        severity_rank = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        risk_map = {1: "low", 2: "medium", 3: "high", 4: "high"}
        for record in self:
            open_exceptions = record.exception_ids.filtered(
                lambda exc: exc.state in ("open", "processing", "resolved")
            )
            record.open_exception_count = len(
                record.exception_ids.filtered(lambda exc: exc.state in ("open", "processing"))
            )
            if not record.exception_ids:
                record.exception_status = "none"
                record.risk_level = "low"
                continue
            if any(exc.state == "processing" for exc in record.exception_ids):
                record.exception_status = "processing"
            elif any(exc.state == "open" for exc in record.exception_ids):
                record.exception_status = "open"
            else:
                record.exception_status = "closed"

            highest_rank = 1
            for exception in open_exceptions or record.exception_ids:
                highest_rank = max(highest_rank, severity_rank.get(exception.severity_level, 1))
            record.risk_level = risk_map.get(highest_rank, "low")

    def action_open_exceptions(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Waybill Exceptions"),
            "res_model": "logistics.trace.exception",
            "view_mode": "list,form",
            "domain": [("waybill_id", "=", self.id)],
            "context": {
                "default_waybill_id": self.id,
                "default_batch_id": self.batch_id.id,
            },
        }
