from odoo import fields, models

from odoo.addons.logistics_dispatch.models.selection_options import (
    IMPORT_OBJECT_TYPE_SELECTION,
    IMPORT_TASK_LINE_STATUS_SELECTION,
    IMPORT_TASK_STATUS_SELECTION,
)


class LogisticsImportSourceFile(models.Model):
    _name = "logistics.import.source.file"
    _description = "导入源文件"
    _table = "import_source_file"
    _order = "uploaded_at desc, id desc"
    _rec_name = "source_file_no"

    _uniq_source_file_no = models.Constraint(
        "unique(source_file_no)",
        "源文件编号必须唯一。",
    )

    source_file_no = fields.Char(
        string="源文件编号",
        required=True,
        copy=False,
        index=True,
        default=lambda self: self.env["ir.sequence"].next_by_code("logistics.import.source.file") or "ISF-NEW",
    )
    file_name = fields.Char(string="文件名", required=True, size=256)
    file_ext = fields.Char(string="扩展名", size=16)
    file_sha256 = fields.Char(string="文件摘要", size=64)
    storage_path = fields.Text(string="存储路径")
    uploader_id = fields.Many2one("res.users", string="上传人", required=True, ondelete="restrict")
    uploaded_at = fields.Datetime(string="上传时间", required=True, default=fields.Datetime.now)


class LogisticsImportTask(models.Model):
    _name = "logistics.import.task"
    _description = "导入任务"
    _table = "import_task"
    _order = "create_date desc, id desc"
    _rec_name = "task_no"

    _uniq_import_task_no = models.Constraint(
        "unique(task_no)",
        "导入任务编号必须唯一。",
    )

    task_no = fields.Char(
        string="任务编号",
        required=True,
        copy=False,
        index=True,
        default=lambda self: self.env["ir.sequence"].next_by_code("logistics.import.task") or "IMP-TASK-NEW",
    )
    object_type = fields.Selection(
        selection=IMPORT_OBJECT_TYPE_SELECTION,
        string="导入对象类型",
        required=True,
        index=True,
    )
    source_file_id = fields.Many2one(
        "logistics.import.source.file",
        string="源文件",
        required=True,
        ondelete="restrict",
        index=True,
    )
    status = fields.Selection(
        selection=IMPORT_TASK_STATUS_SELECTION,
        string="任务状态",
        required=True,
        default="pending",
        index=True,
    )
    total_count = fields.Integer(string="总数", required=True, default=0)
    success_count = fields.Integer(string="成功数", required=True, default=0)
    fail_count = fields.Integer(string="失败数", required=True, default=0)
    started_at = fields.Datetime(string="开始时间")
    finished_at = fields.Datetime(string="结束时间")
    operator_id = fields.Many2one("res.users", string="操作人", ondelete="restrict")
    summary_message = fields.Text(string="任务摘要")
    task_line_ids = fields.One2many("logistics.import.task.line", "task_id", string="导入任务行")
    error_line_ids = fields.One2many("logistics.import.error.line", "task_id", string="导入错误行")


class LogisticsImportTaskLine(models.Model):
    _name = "logistics.import.task.line"
    _description = "导入任务行"
    _table = "import_task_line"
    _order = "task_id, line_no"

    _uniq_import_task_line = models.Constraint(
        "unique(task_id, line_no)",
        "同一导入任务内的任务行号必须唯一。",
    )

    task_id = fields.Many2one("logistics.import.task", string="导入任务", required=True, ondelete="cascade", index=True)
    line_no = fields.Integer(string="任务内行号", required=True)
    source_row_no = fields.Integer(string="原始文件行号", required=True, index=True)
    object_type = fields.Selection(
        selection=IMPORT_OBJECT_TYPE_SELECTION,
        string="对象类型",
        required=True,
    )
    status = fields.Selection(
        selection=IMPORT_TASK_LINE_STATUS_SELECTION,
        string="行状态",
        required=True,
        default="pending",
        index=True,
    )
    business_key = fields.Char(string="业务键摘要", size=128)
    target_model = fields.Char(string="目标模型", size=128)
    target_res_id = fields.Integer(string="目标主键")
    message = fields.Text(string="行结果说明")


class LogisticsImportErrorLine(models.Model):
    _name = "logistics.import.error.line"
    _description = "导入错误行"
    _table = "import_error_line"
    _order = "task_id, source_row_no, id"

    task_id = fields.Many2one("logistics.import.task", string="导入任务", required=True, ondelete="cascade", index=True)
    task_line_id = fields.Many2one("logistics.import.task.line", string="行结果", ondelete="set null")
    source_row_no = fields.Integer(string="原始行号", required=True, index=True)
    field_name = fields.Char(string="字段名", size=64, required=True)
    raw_value = fields.Text(string="原始值")
    mapped_value = fields.Text(string="映射值")
    error_code = fields.Char(string="错误码", size=64, required=True)
    error_message = fields.Text(string="错误说明", required=True)


class LogisticsMasterDataChangeLog(models.Model):
    _name = "logistics.master.data.change.log"
    _description = "主数据变更日志"
    _table = "logistics_master_data_change_log"
    _order = "create_date desc, id desc"

    object_model = fields.Char(string="目标模型", size=128, required=True, index=True)
    object_id = fields.Integer(string="目标主键", required=True, index=True)
    field_name = fields.Char(string="字段名", size=64, required=True)
    old_value = fields.Text(string="旧值", required=True)
    new_value = fields.Text(string="新值", required=True)
    operator_id = fields.Many2one("res.users", string="操作人", required=True, ondelete="restrict")
    source_type = fields.Char(string="来源类型", size=32, required=True)
    source_file_id = fields.Many2one("logistics.import.source.file", string="源文件", ondelete="set null")
    change_reason = fields.Text(string="变更原因")
