from odoo import api, fields, models


class LogisticsTraceEvidence(models.Model):
    _name = "logistics.trace.evidence"
    _description = "物流留痕证据"
    _order = "uploaded_at desc, sequence asc, id desc"
    _rec_name = "name"

    STATE_SELECTION = [
        ("available", "可用"),
        ("missing", "缺失"),
    ]

    name = fields.Char(string="证据名称", required=True, copy=False, default="New")
    trace_event_id = fields.Many2one(
        "logistics.trace.event",
        string="留痕事件",
        required=True,
        ondelete="cascade",
        index=True,
    )
    waybill_id = fields.Many2one(
        "logistics.dispatch.waybill",
        string="运单",
        related="trace_event_id.waybill_id",
        store=True,
        readonly=True,
        index=True,
    )
    batch_id = fields.Many2one(
        "logistics.dispatch.batch",
        string="批次",
        related="trace_event_id.batch_id",
        store=True,
        readonly=True,
        index=True,
    )
    image_access_key = fields.Char(string="图片访问 Key", index=True)
    preview_url = fields.Char(string="预览地址")
    full_url = fields.Char(string="原图地址")
    uploaded_at = fields.Datetime(
        string="上传时间",
        required=True,
        default=fields.Datetime.now,
        index=True,
    )
    uploader_id = fields.Many2one(
        "res.users",
        string="上传人",
        default=lambda self: self.env.user,
    )
    uploader_name = fields.Char(
        string="上传人姓名",
        compute="_compute_uploader_name",
        store=True,
    )
    remark = fields.Char(string="备注")
    is_exception_related = fields.Boolean(
        string="异常相关",
        compute="_compute_exception_flags",
        store=True,
    )
    sequence = fields.Integer(string="顺序", default=10)
    state = fields.Selection(
        STATE_SELECTION,
        string="状态",
        required=True,
        default="available",
    )

    @api.depends("uploader_id")
    def _compute_uploader_name(self):
        for record in self:
            record.uploader_name = record.uploader_id.name or ""

    @api.depends("trace_event_id.is_exception")
    def _compute_exception_flags(self):
        for record in self:
            record.is_exception_related = bool(record.trace_event_id.is_exception)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self._build_evidence_name(vals)
        return super().create(vals_list)

    def _build_evidence_name(self, vals):
        uploaded_at = vals.get("uploaded_at")
        uploaded_dt = fields.Datetime.to_datetime(uploaded_at) if uploaded_at else fields.Datetime.now()
        return f"Evidence - {fields.Datetime.to_string(uploaded_dt)}"
