from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LogisticsTraceException(models.Model):
    _name = "logistics.trace.exception"
    _description = "物流异常"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "report_time desc, id desc"
    _rec_name = "name"

    EXCEPTION_TYPE_SELECTION = [
        ("delay", "延迟"),
        ("damage", "破损"),
        ("missing", "缺失"),
        ("rejected", "拒收"),
        ("store_closed", "门店关闭"),
        ("signoff_problem", "签收异常"),
        ("evidence_missing", "证据缺失"),
        ("other", "其他"),
    ]

    SEVERITY_SELECTION = [
        ("low", "低"),
        ("medium", "中"),
        ("high", "高"),
        ("critical", "严重"),
    ]

    STATE_SELECTION = [
        ("draft", "草稿"),
        ("open", "待处理"),
        ("processing", "处理中"),
        ("resolved", "已解决"),
        ("closed", "已关闭"),
        ("cancelled", "已取消"),
    ]

    name = fields.Char(string="异常单号", required=True, copy=False, default="新建", tracking=True)
    exception_no = fields.Char(
        string="异常单号（导入导出）",
        compute="_compute_exception_no",
        inverse="_inverse_exception_no",
    )
    exception_type = fields.Selection(
        EXCEPTION_TYPE_SELECTION,
        string="异常类型",
        required=True,
        tracking=True,
    )
    severity_level = fields.Selection(
        SEVERITY_SELECTION,
        string="严重等级",
        required=True,
        default="medium",
        tracking=True,
    )
    state = fields.Selection(
        STATE_SELECTION,
        string="状态",
        required=True,
        default="open",
        tracking=True,
    )
    waybill_id = fields.Many2one(
        "logistics.dispatch.waybill",
        string="运单",
        ondelete="cascade",
        index=True,
        tracking=True,
    )
    waybill_no = fields.Char(
        string="运单号（导入导出）",
        compute="_compute_waybill_no",
        inverse="_inverse_waybill_no",
    )
    batch_id = fields.Many2one(
        "logistics.dispatch.batch",
        string="批次",
        ondelete="set null",
        index=True,
        tracking=True,
    )
    batch_no = fields.Char(
        string="批次号（导入导出）",
        compute="_compute_batch_no",
        inverse="_inverse_batch_no",
    )
    trace_event_id = fields.Many2one(
        "logistics.trace.event",
        string="留痕事件",
        ondelete="set null",
        index=True,
        tracking=True,
    )
    trace_event_name = fields.Char(
        string="留痕事件（导入导出）",
        compute="_compute_trace_event_name",
        inverse="_inverse_trace_event_name",
    )
    report_time = fields.Datetime(
        string="上报时间",
        required=True,
        default=fields.Datetime.now,
        index=True,
        tracking=True,
    )
    reporter_user_id = fields.Many2one(
        "res.users",
        string="上报人",
        default=lambda self: self.env.user,
        tracking=True,
    )
    reporter_user_name = fields.Char(
        string="上报人姓名",
        compute="_compute_reporter_user_name",
        store=True,
    )
    process_owner_id = fields.Many2one(
        "hr.employee",
        string="处理负责人",
        tracking=True,
    )
    process_owner_name = fields.Char(
        string="处理负责人姓名",
        compute="_compute_process_owner_name",
        store=True,
        inverse="_inverse_process_owner_name",
    )
    description = fields.Text(string="异常说明", tracking=True)
    close_summary = fields.Text(string="处理结论")
    closed_time = fields.Datetime(string="关闭时间")
    is_overdue = fields.Boolean(
        string="是否超时",
        compute="_compute_is_overdue",
        store=True,
    )
    remark = fields.Text(string="备注")
    process_log_ids = fields.One2many(
        "logistics.trace.exception.process.log",
        "exception_id",
        string="处理日志",
    )
    evidence_count = fields.Integer(
        string="证据数",
        compute="_compute_evidence_count",
        store=True,
        readonly=True,
    )

    @api.depends("name")
    def _compute_exception_no(self):
        for record in self:
            record.exception_no = record.name or ""

    @api.depends("waybill_id.name")
    def _compute_waybill_no(self):
        for record in self:
            record.waybill_no = record.waybill_id.name or ""

    @api.depends("batch_id.name")
    def _compute_batch_no(self):
        for record in self:
            record.batch_no = record.batch_id.name or ""

    @api.depends("trace_event_id.name")
    def _compute_trace_event_name(self):
        for record in self:
            record.trace_event_name = record.trace_event_id.name or ""

    @api.depends("reporter_user_id")
    def _compute_reporter_user_name(self):
        for record in self:
            record.reporter_user_name = record.reporter_user_id.name or ""

    @api.depends("process_owner_id")
    def _compute_process_owner_name(self):
        for record in self:
            record.process_owner_name = record.process_owner_id.name or ""

    @api.depends("trace_event_id.evidence_count")
    def _compute_evidence_count(self):
        for record in self:
            record.evidence_count = record.trace_event_id.evidence_count or 0

    @api.depends("state", "report_time")
    def _compute_is_overdue(self):
        now = fields.Datetime.now()
        for record in self:
            record.is_overdue = (
                record.state in ("open", "processing")
                and bool(record.report_time)
                and (now - record.report_time).days >= 1
            )

    def _inverse_exception_no(self):
        for record in self:
            record.name = (record.exception_no or "").strip() or record.name or "新建"

    def _inverse_waybill_no(self):
        for record in self:
            waybill_no = (record.waybill_no or "").strip()
            record.waybill_id = self._resolve_waybill_by_no(waybill_no) if waybill_no else False

    def _inverse_batch_no(self):
        for record in self:
            batch_no = (record.batch_no or "").strip()
            record.batch_id = self._resolve_batch_by_no(batch_no) if batch_no else False

    def _inverse_trace_event_name(self):
        for record in self:
            trace_event_name = (record.trace_event_name or "").strip()
            record.trace_event_id = (
                self._resolve_trace_event_by_name(trace_event_name) if trace_event_name else False
            )

    def _inverse_process_owner_name(self):
        for record in self:
            process_owner_name = (record.process_owner_name or "").strip()
            record.process_owner_id = (
                self._resolve_employee_by_name(process_owner_name) if process_owner_name else False
            )

    @api.model
    def _ensure_unique_record(self, records, field_label, value):
        if not records:
            raise ValidationError(f"未找到{field_label}“{value}”对应的记录。")
        if len(records) > 1:
            raise ValidationError(f"{field_label}“{value}”匹配到多条记录，请先去重。")
        return records

    @api.model
    def _resolve_waybill_by_no(self, waybill_no):
        waybills = self.env["logistics.dispatch.waybill"].search([("name", "=", waybill_no)], limit=2)
        return self._ensure_unique_record(waybills, "运单号", waybill_no)

    @api.model
    def _resolve_batch_by_no(self, batch_no):
        batches = self.env["logistics.dispatch.batch"].search([("name", "=", batch_no)], limit=2)
        return self._ensure_unique_record(batches, "批次号", batch_no)

    @api.model
    def _resolve_trace_event_by_name(self, trace_event_name):
        events = self.env["logistics.trace.event"].search([("name", "=", trace_event_name)], limit=2)
        return self._ensure_unique_record(events, "留痕事件", trace_event_name)

    @api.model
    def _resolve_employee_by_name(self, employee_name):
        employees = self.env["hr.employee"].search([("name", "=", employee_name)], limit=2)
        return self._ensure_unique_record(employees, "处理负责人姓名", employee_name)

    @api.onchange("trace_event_id")
    def _onchange_trace_event_id(self):
        for record in self:
            if record.trace_event_id:
                if not record.waybill_id:
                    record.waybill_id = record.trace_event_id.waybill_id
                if not record.batch_id:
                    record.batch_id = record.trace_event_id.batch_id

    @api.onchange("waybill_id")
    def _onchange_waybill_id(self):
        for record in self:
            if record.waybill_id and not record.batch_id:
                record.batch_id = record.waybill_id.batch_id

    @api.model_create_multi
    def create(self, vals_list):
        records = self.browse()
        for vals in vals_list:
            if "exception_no" in vals:
                vals["name"] = (vals.pop("exception_no") or "").strip() or vals.get("name") or "新建"
            if "waybill_no" in vals and not vals.get("waybill_id"):
                waybill_no = (vals.pop("waybill_no") or "").strip()
                vals["waybill_id"] = self._resolve_waybill_by_no(waybill_no).id if waybill_no else False
            if "batch_no" in vals and not vals.get("batch_id"):
                batch_no = (vals.pop("batch_no") or "").strip()
                vals["batch_id"] = self._resolve_batch_by_no(batch_no).id if batch_no else False
            if "trace_event_name" in vals and not vals.get("trace_event_id"):
                trace_event_name = (vals.pop("trace_event_name") or "").strip()
                vals["trace_event_id"] = (
                    self._resolve_trace_event_by_name(trace_event_name).id if trace_event_name else False
                )
            if "process_owner_name" in vals and not vals.get("process_owner_id"):
                process_owner_name = (vals.pop("process_owner_name") or "").strip()
                vals["process_owner_id"] = (
                    self._resolve_employee_by_name(process_owner_name).id if process_owner_name else False
                )
            if vals.get("trace_event_id") and not vals.get("waybill_id"):
                trace_event = self.env["logistics.trace.event"].browse(vals["trace_event_id"])
                vals["waybill_id"] = trace_event.waybill_id.id
                vals["batch_id"] = vals.get("batch_id") or trace_event.batch_id.id
            elif vals.get("waybill_id") and not vals.get("batch_id"):
                waybill = self.env["logistics.dispatch.waybill"].browse(vals["waybill_id"])
                vals["batch_id"] = waybill.batch_id.id
            if vals.get("name", "新建") in ("New", "新建"):
                vals["name"] = self._build_exception_name(vals)
        records = super().create(vals_list)
        records._create_process_logs("create", from_state=False)
        return records

    def write(self, vals):
        vals = dict(vals)
        if "exception_no" in vals:
            exception_no = (vals.pop("exception_no") or "").strip()
            if exception_no:
                vals["name"] = exception_no
        if "waybill_no" in vals and "waybill_id" not in vals:
            waybill_no = (vals.pop("waybill_no") or "").strip()
            vals["waybill_id"] = self._resolve_waybill_by_no(waybill_no).id if waybill_no else False
        if "batch_no" in vals and "batch_id" not in vals:
            batch_no = (vals.pop("batch_no") or "").strip()
            vals["batch_id"] = self._resolve_batch_by_no(batch_no).id if batch_no else False
        if "trace_event_name" in vals and "trace_event_id" not in vals:
            trace_event_name = (vals.pop("trace_event_name") or "").strip()
            vals["trace_event_id"] = (
                self._resolve_trace_event_by_name(trace_event_name).id if trace_event_name else False
            )
        if "process_owner_name" in vals and "process_owner_id" not in vals:
            process_owner_name = (vals.pop("process_owner_name") or "").strip()
            vals["process_owner_id"] = (
                self._resolve_employee_by_name(process_owner_name).id if process_owner_name else False
            )
        previous_states = {record.id: record.state for record in self}
        result = super().write(vals)
        if "state" in vals or "remark" in vals or "close_summary" in vals:
            for record in self:
                from_state = previous_states.get(record.id)
                to_state = record.state
                if from_state != to_state:
                    record._create_process_logs(
                        "state_change",
                        from_state=from_state,
                        to_state=to_state,
                        note=vals.get("close_summary") or vals.get("remark") or "",
                    )
        if "state" in vals:
            for record in self.filtered(lambda rec: rec.state in ("closed", "cancelled")):
                if not record.closed_time:
                    record.closed_time = fields.Datetime.now()
        return result

    def _build_exception_name(self, vals):
        exception_type = vals.get("exception_type") or "other"
        report_time = vals.get("report_time")
        report_dt = fields.Datetime.to_datetime(report_time) if report_time else fields.Datetime.now()
        return f"EXC-{exception_type.upper()}-{report_dt.strftime('%Y%m%d%H%M%S')}"

    def _create_process_logs(self, action_type, from_state=False, to_state=False, note=""):
        log_model = self.env["logistics.trace.exception.process.log"]
        values_list = []
        for record in self:
            values_list.append(
                {
                    "exception_id": record.id,
                    "action_type": action_type,
                    "operator_id": self.env.user.id,
                    "from_state": from_state or False,
                    "to_state": to_state or record.state,
                    "note": note or "",
                }
            )
        if values_list:
            log_model.create(values_list)

    def action_mark_processing(self):
        self.write({"state": "processing"})

    def action_mark_resolved(self):
        self.write({"state": "resolved"})

    def action_mark_closed(self):
        self.write({"state": "closed", "closed_time": fields.Datetime.now()})

    def action_open_waybill(self):
        self.ensure_one()
        if not self.waybill_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": _("运单"),
            "res_model": "logistics.dispatch.waybill",
            "view_mode": "form",
            "res_id": self.waybill_id.id,
        }

    def action_open_trace_event(self):
        self.ensure_one()
        if not self.trace_event_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": _("留痕事件"),
            "res_model": "logistics.trace.event",
            "view_mode": "form",
            "res_id": self.trace_event_id.id,
        }

    def action_open_batch(self):
        self.ensure_one()
        if not self.batch_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": _("批次"),
            "res_model": "logistics.dispatch.batch",
            "view_mode": "form",
            "res_id": self.batch_id.id,
        }

    def action_open_evidence(self):
        self.ensure_one()
        if not self.trace_event_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": _("证据"),
            "res_model": "logistics.trace.evidence",
            "view_mode": "list,form",
            "domain": [("trace_event_id", "=", self.trace_event_id.id)],
            "context": {
                "default_trace_event_id": self.trace_event_id.id,
                "default_waybill_id": self.waybill_id.id,
                "default_batch_id": self.batch_id.id,
            },
        }
