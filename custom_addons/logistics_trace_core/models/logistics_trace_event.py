from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LogisticsTraceEvent(models.Model):
    _name = "logistics.trace.event"
    _description = "物流留痕事件"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "trace_time desc, id desc"
    _rec_name = "name"

    EVENT_SELECTION = [
        ("arrive_loading_point", "到达装车点"),
        ("start_loading", "开始装车"),
        ("finish_loading", "完成装车"),
        ("departed", "已发车"),
        ("arrive_store", "到达门店"),
        ("deliver_finish", "完成配送"),
        ("signoff", "完成签收"),
        ("exception_report", "异常上报"),
    ]

    OBJECT_SELECTION = [
        ("batch", "批次"),
        ("waybill", "运单"),
    ]

    SUBMIT_SOURCE_SELECTION = [
        ("manual", "人工"),
        ("system", "系统"),
        ("mobile", "移动端"),
    ]

    STATE_SELECTION = [
        ("draft", "草稿"),
        ("submitted", "已提交"),
        ("invalid", "无效"),
    ]

    name = fields.Char(string="留痕事件", required=True, copy=False, default="New", tracking=True)
    event_type = fields.Selection(EVENT_SELECTION, string="留痕类型", required=True, tracking=True)
    object_type = fields.Selection(
        OBJECT_SELECTION,
        string="对象类型",
        required=True,
        default="waybill",
        tracking=True,
    )
    batch_id = fields.Many2one("logistics.dispatch.batch", string="批次", ondelete="cascade", index=True)
    waybill_id = fields.Many2one(
        "logistics.dispatch.waybill",
        string="运单",
        ondelete="cascade",
        index=True,
    )
    trace_time = fields.Datetime(
        string="留痕时间",
        required=True,
        default=fields.Datetime.now,
        tracking=True,
        index=True,
    )
    submit_user_id = fields.Many2one(
        "res.users",
        string="提交人",
        default=lambda self: self.env.user,
        tracking=True,
    )
    submit_user_name = fields.Char(
        string="提交人姓名",
        compute="_compute_submit_user_name",
        store=True,
    )
    submit_source = fields.Selection(
        SUBMIT_SOURCE_SELECTION,
        string="提交来源",
        default="manual",
    )
    location_text = fields.Char(string="现场位置")
    plate_no = fields.Char(string="车牌号")
    driver_name = fields.Char(string="司机姓名")
    remark = fields.Text(string="备注", tracking=True)
    evidence_count = fields.Integer(string="证据数", default=0)
    is_exception = fields.Boolean(string="异常事件", tracking=True)
    source_channel = fields.Char(string="来源渠道")
    source_record_id = fields.Char(string="来源记录号")
    state = fields.Selection(
        STATE_SELECTION,
        string="状态",
        required=True,
        default="submitted",
        tracking=True,
    )

    @api.depends("submit_user_id")
    def _compute_submit_user_name(self):
        for record in self:
            record.submit_user_name = record.submit_user_id.name or ""

    @api.constrains("object_type", "batch_id", "waybill_id")
    def _check_object_link(self):
        for record in self:
            if record.object_type == "batch" and not record.batch_id:
                raise ValidationError("批次留痕事件必须关联到一个批次。")
            if record.object_type == "waybill" and not record.waybill_id:
                raise ValidationError("运单留痕事件必须关联到一张运单。")

    @api.onchange("waybill_id")
    def _onchange_waybill_id(self):
        for record in self:
            if record.waybill_id:
                record.object_type = "waybill"
                if not record.batch_id:
                    record.batch_id = record.waybill_id.batch_id
                if not record.plate_no and record.waybill_id.vehicle_id:
                    record.plate_no = record.waybill_id.vehicle_id.license_plate
                if not record.driver_name and record.waybill_id.driver_employee_id:
                    record.driver_name = record.waybill_id.driver_employee_id.name

    @api.onchange("batch_id")
    def _onchange_batch_id(self):
        for record in self:
            if record.object_type == "batch" and record.batch_id:
                if not record.plate_no and record.batch_id.vehicle_id:
                    record.plate_no = record.batch_id.vehicle_id.license_plate
                if not record.driver_name and record.batch_id.driver_employee_id:
                    record.driver_name = record.batch_id.driver_employee_id.name

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            waybill_id = vals.get("waybill_id")
            if waybill_id and not vals.get("batch_id"):
                waybill = self.env["logistics.dispatch.waybill"].browse(waybill_id)
                vals["batch_id"] = waybill.batch_id.id
            if vals.get("name", "New") == "New":
                vals["name"] = self._build_event_name(vals)
        return super().create(vals_list)

    def _build_event_name(self, vals):
        event_type = vals.get("event_type") or "trace"
        trace_time = vals.get("trace_time")
        trace_dt = fields.Datetime.to_datetime(trace_time) if trace_time else fields.Datetime.now()
        return f"{event_type.replace('_', ' ').title()} - {fields.Datetime.to_string(trace_dt)}"
