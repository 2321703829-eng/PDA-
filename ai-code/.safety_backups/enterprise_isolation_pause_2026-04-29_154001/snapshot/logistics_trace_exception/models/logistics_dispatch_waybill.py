from odoo import _, api, fields, models


class LogisticsDispatchWaybill(models.Model):
    _inherit = "logistics.dispatch.waybill"

    exception_ids = fields.One2many(
        "logistics.trace.exception",
        "waybill_id",
        string="异常记录",
    )
    open_exception_count = fields.Integer(
        string="进行中异常数量",
        compute="_compute_exception_metrics",
        store=True,
        readonly=True,
    )
    exception_status = fields.Selection(
        [
            ("none", "None"),
            ("open", "Open"),
            ("processing", "Processing"),
            ("closed", "Closed"),
        ],
        string="异常状态",
        compute="_compute_exception_metrics",
        store=True,
        readonly=True,
    )
    risk_level = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        string="风险等级",
        compute="_compute_exception_metrics",
        store=True,
        readonly=True,
    )
    latest_exception_time = fields.Datetime(
        string="最新异常时间",
        compute="_compute_exception_metrics",
        store=True,
        readonly=True,
    )
    latest_exception_type = fields.Char(
        string="最新异常类型",
        compute="_compute_exception_metrics",
        store=True,
        readonly=True,
    )
    highest_exception_status = fields.Char(
        string="最高异常状态",
        compute="_compute_exception_metrics",
        store=True,
        readonly=True,
    )
    has_processing_exception = fields.Boolean(
        string="是否存在处理中异常",
        compute="_compute_exception_metrics",
        store=True,
        readonly=True,
    )

    @api.depends(
        "exception_ids.state",
        "exception_ids.severity_level",
        "exception_ids.report_time",
        "exception_ids.exception_type",
    )
    def _compute_exception_metrics(self):
        severity_rank = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        risk_map = {1: "low", 2: "medium", 3: "high", 4: "high"}
        status_rank = {"processing": 4, "open": 3, "resolved": 2, "closed": 1, "cancelled": 0, "draft": 0}

        for record in self:
            ordered_exceptions = record.exception_ids.sorted(
                key=lambda exc: exc.report_time or fields.Datetime.now(),
                reverse=True,
            )
            open_exceptions = ordered_exceptions.filtered(
                lambda exc: exc.state in ("open", "processing", "resolved")
            )
            latest_exception = ordered_exceptions[:1][0] if ordered_exceptions else False

            record.open_exception_count = len(
                ordered_exceptions.filtered(lambda exc: exc.state in ("open", "processing"))
            )
            record.latest_exception_time = latest_exception.report_time if latest_exception else False
            record.latest_exception_type = latest_exception.exception_type if latest_exception else False
            record.has_processing_exception = any(exc.state == "processing" for exc in ordered_exceptions)

            if not ordered_exceptions:
                record.exception_status = "none"
                record.risk_level = "low"
                record.highest_exception_status = False
                continue

            if record.has_processing_exception:
                record.exception_status = "processing"
            elif any(exc.state == "open" for exc in ordered_exceptions):
                record.exception_status = "open"
            else:
                record.exception_status = "closed"

            highest_rank = 1
            for exception in open_exceptions or ordered_exceptions:
                highest_rank = max(highest_rank, severity_rank.get(exception.severity_level, 1))
            record.risk_level = risk_map.get(highest_rank, "low")

            highest_status = False
            highest_status_value = -1
            for exception in ordered_exceptions:
                current_rank = status_rank.get(exception.state, -1)
                if current_rank > highest_status_value:
                    highest_status = exception.state
                    highest_status_value = current_rank
            record.highest_exception_status = highest_status or False

    def action_open_exceptions(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("运单异常"),
            "res_model": "logistics.trace.exception",
            "view_mode": "list,form",
            "domain": [("waybill_id", "=", self.id)],
            "context": {
                "default_waybill_id": self.id,
                "default_batch_id": self.batch_id.id,
            },
        }
