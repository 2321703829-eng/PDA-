from odoo import fields, models

from odoo.addons.logistics_dispatch.models.selection_options import (
    EXPORT_ENTRY_TYPE_SELECTION,
    EXPORT_ERROR_STAGE_SELECTION,
    EXPORT_MODE_SELECTION,
    EXPORT_OBJECT_TYPE_SELECTION,
    EXPORT_PACKAGE_STRUCTURE_SELECTION,
    EXPORT_TARGET_OBJECT_TYPE_SELECTION,
    EXPORT_TASK_LINE_STATUS_SELECTION,
    EXPORT_TASK_STATUS_SELECTION,
)


class LogisticsExportSourceScope(models.Model):
    _name = "logistics.export.source.scope"
    _description = "物流导出范围快照"
    _table = "export_source_scope"
    _order = "create_date desc, id desc"
    _rec_name = "scope_no"

    _uniq_export_scope_no = models.Constraint(
        "unique(scope_no)",
        "导出范围编号必须唯一。",
    )

    scope_no = fields.Char(
        string="范围编号",
        required=True,
        copy=False,
        index=True,
        default=lambda self: self.env["ir.sequence"].next_by_code("logistics.export.source.scope") or "EXS-NEW",
    )
    object_type = fields.Selection(
        selection=EXPORT_OBJECT_TYPE_SELECTION,
        string="导出对象类型",
        required=True,
        index=True,
    )
    entry_type = fields.Selection(
        selection=EXPORT_ENTRY_TYPE_SELECTION,
        string="导出入口类型",
        required=True,
        index=True,
    )
    source_model = fields.Char(string="来源模型", required=True, size=128)
    source_page = fields.Char(string="来源页面", size=64)
    selected_ids_json = fields.Json(string="选中对象ID列表", required=True, default=lambda self: [])
    selected_count = fields.Integer(string="选中对象数", required=True, default=0)
    scope_snapshot_json = fields.Json(string="范围快照")
    request_payload_json = fields.Json(string="请求体快照")
    operator_id = fields.Many2one(
        "res.users",
        string="发起人",
        required=True,
        default=lambda self: self.env.user,
        ondelete="restrict",
        index=True,
    )
    task_ids = fields.One2many("logistics.export.task", "source_scope_id", string="导出任务")


class LogisticsExportTask(models.Model):
    _name = "logistics.export.task"
    _description = "物流导出任务"
    _table = "export_task"
    _order = "create_date desc, id desc"
    _rec_name = "task_no"

    _uniq_export_task_no = models.Constraint(
        "unique(task_no)",
        "导出任务编号必须唯一。",
    )

    task_no = fields.Char(
        string="任务编号",
        required=True,
        copy=False,
        index=True,
        default=lambda self: self.env["ir.sequence"].next_by_code("logistics.export.task") or "EXT-NEW",
    )
    object_type = fields.Selection(
        selection=EXPORT_OBJECT_TYPE_SELECTION,
        string="导出对象类型",
        required=True,
        index=True,
    )
    entry_type = fields.Selection(
        selection=EXPORT_ENTRY_TYPE_SELECTION,
        string="导出入口类型",
        required=True,
        index=True,
    )
    export_mode = fields.Selection(
        selection=EXPORT_MODE_SELECTION,
        string="导出模式",
        required=True,
        default="standard_xlsx",
        index=True,
    )
    package_structure = fields.Selection(
        selection=EXPORT_PACKAGE_STRUCTURE_SELECTION,
        string="导出包结构",
        required=True,
        default="dispatch_main_four_sheet",
    )
    source_scope_id = fields.Many2one(
        "logistics.export.source.scope",
        string="导出范围快照",
        required=True,
        ondelete="restrict",
        index=True,
    )
    status = fields.Selection(
        selection=EXPORT_TASK_STATUS_SELECTION,
        string="任务状态",
        required=True,
        default="pending",
        index=True,
    )
    total_count = fields.Integer(string="总数", required=True, default=0)
    success_count = fields.Integer(string="成功数", required=True, default=0)
    fail_count = fields.Integer(string="失败数", required=True, default=0)
    skipped_count = fields.Integer(string="跳过数", required=True, default=0)
    exported_waybill_count = fields.Integer(string="导出运单数", required=True, default=0)
    exported_customer_line_count = fields.Integer(string="导出客户节点数", required=True, default=0)
    exported_order_line_count = fields.Integer(string="导出订单数", required=True, default=0)
    exported_goods_line_count = fields.Integer(string="导出货物数", required=True, default=0)
    package_metrics_json = fields.Json(string="导出包结构化统计", default=lambda self: {})
    started_at = fields.Datetime(string="开始时间")
    finished_at = fields.Datetime(string="完成时间")
    download_ready_at = fields.Datetime(string="可下载时间")
    expires_at = fields.Datetime(string="过期时间", index=True)
    operator_id = fields.Many2one(
        "res.users",
        string="发起人",
        required=True,
        default=lambda self: self.env.user,
        ondelete="restrict",
        index=True,
    )
    summary_message = fields.Text(string="任务摘要")
    failure_error_code = fields.Char(string="任务头失败码", size=64)
    failure_reason = fields.Text(string="任务头失败说明")
    output_file_name = fields.Char(string="导出文件名", size=256)
    output_file_ext = fields.Char(string="导出文件扩展名", size=16)
    output_storage_path = fields.Text(string="导出文件存储路径")
    output_file_sha256 = fields.Char(string="导出文件摘要", size=64)
    output_file_size = fields.Integer(string="导出文件大小", default=0)
    task_line_ids = fields.One2many("logistics.export.task.line", "task_id", string="导出任务行")
    error_line_ids = fields.One2many("logistics.export.error.line", "task_id", string="导出错误明细")


class LogisticsExportTaskLine(models.Model):
    _name = "logistics.export.task.line"
    _description = "物流导出任务行"
    _table = "export_task_line"
    _order = "task_id, line_no"

    _uniq_export_task_line = models.Constraint(
        "unique(task_id, line_no)",
        "同一导出任务内的任务行号必须唯一。",
    )

    task_id = fields.Many2one("logistics.export.task", string="导出任务", required=True, ondelete="cascade", index=True)
    line_no = fields.Integer(string="任务内行号", required=True)
    target_object_type = fields.Selection(
        selection=EXPORT_TARGET_OBJECT_TYPE_SELECTION,
        string="目标对象类型",
        required=True,
        index=True,
    )
    target_res_model = fields.Char(string="目标模型", size=128)
    target_res_id = fields.Integer(string="目标主键", index=True)
    business_key = fields.Char(string="业务键摘要", required=True, size=128)
    display_name = fields.Char(string="展示名称", size=128)
    status = fields.Selection(
        selection=EXPORT_TASK_LINE_STATUS_SELECTION,
        string="行状态",
        required=True,
        default="pending",
        index=True,
    )
    exported_waybill_count = fields.Integer(string="导出运单数", required=True, default=0)
    exported_customer_line_count = fields.Integer(string="导出客户节点数", required=True, default=0)
    exported_order_line_count = fields.Integer(string="导出订单数", required=True, default=0)
    exported_goods_line_count = fields.Integer(string="导出货物数", required=True, default=0)
    line_metrics_json = fields.Json(string="行级结构化统计", default=lambda self: {})
    message = fields.Text(string="行结果说明")


class LogisticsExportErrorLine(models.Model):
    _name = "logistics.export.error.line"
    _description = "物流导出错误明细"
    _table = "export_error_line"
    _order = "task_id, id"

    task_id = fields.Many2one("logistics.export.task", string="导出任务", required=True, ondelete="cascade", index=True)
    task_line_id = fields.Many2one(
        "logistics.export.task.line",
        string="导出任务行",
        ondelete="set null",
        index=True,
    )
    error_stage = fields.Selection(
        selection=EXPORT_ERROR_STAGE_SELECTION,
        string="失败阶段",
        required=True,
        index=True,
    )
    field_name = fields.Char(string="字段名", required=True, size=64)
    raw_value = fields.Text(string="原始值")
    mapped_value = fields.Text(string="映射值")
    error_code = fields.Char(string="错误码", required=True, size=64, index=True)
    error_message = fields.Text(string="错误说明", required=True)
