import json
import uuid
from datetime import timedelta

from odoo import api, fields, models


class LogisticsImportBatch(models.Model):
    _name = "logistics.import.batch"
    _description = "Logistics Import Batch"
    _order = "create_date desc, id desc"

    name = fields.Char(
        string="导入批次号",
        required=True,
        copy=False,
        index=True,
        default=lambda self: self._generate_import_batch_no(),
    )
    precheck_token = fields.Char(
        string="预校验令牌",
        required=True,
        copy=False,
        index=True,
        default=lambda self: self._generate_precheck_token(),
    )
    template_code = fields.Char(string="模板编码", required=True, index=True)
    template_version = fields.Char(string="模板版本", required=True)
    file_name = fields.Char(string="文件名")
    file_checksum = fields.Char(string="文件摘要", index=True)
    state = fields.Selection(
        [
            ("prechecked", "已预校验"),
            ("importing", "导入中"),
            ("finished", "已完成"),
            ("failed", "已失败"),
            ("expired", "已失效"),
        ],
        string="状态",
        default="prechecked",
        required=True,
        index=True,
    )
    expires_at = fields.Datetime(string="过期时间", index=True)
    can_confirm_import = fields.Boolean(string="允许正式导入", default=False)
    total_row_count = fields.Integer(string="总行数", default=0)
    passed_row_count = fields.Integer(string="通过行数", default=0)
    failed_row_count = fields.Integer(string="失败行数", default=0)
    source_rows_json = fields.Text(string="源数据快照")
    errors_json = fields.Text(string="预校验错误快照")
    confirmed_at = fields.Datetime(string="确认导入时间")
    finished_at = fields.Datetime(string="完成时间")
    created_waybill_count = fields.Integer(string="新增运单数", default=0)
    created_customer_line_count = fields.Integer(string="新增客户明细数", default=0)
    created_goods_line_count = fields.Integer(string="新增货物明细数", default=0)
    updated_record_count = fields.Integer(string="更新记录数", default=0)
    skipped_record_count = fields.Integer(string="跳过记录数", default=0)
    failed_record_count = fields.Integer(string="失败记录数", default=0)
    error_report_url = fields.Char(string="错误报告地址")
    failure_reason = fields.Text(string="失败原因")

    @api.model
    def _generate_import_batch_no(self):
        today = fields.Date.context_today(self)
        return f"IMP-{today.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    @api.model
    def _generate_precheck_token(self):
        return f"pre_{uuid.uuid4().hex[:16]}"

    @api.model
    def build_precheck_vals(
        self,
        *,
        template_code,
        template_version,
        file_name,
        file_checksum,
        total_row_count,
        passed_row_count,
        failed_row_count,
        can_confirm_import,
        source_rows,
        errors,
    ):
        now = fields.Datetime.now()
        return {
            "template_code": template_code,
            "template_version": template_version,
            "file_name": file_name,
            "file_checksum": file_checksum,
            "state": "prechecked",
            "expires_at": now + timedelta(hours=24),
            "can_confirm_import": can_confirm_import,
            "total_row_count": total_row_count,
            "passed_row_count": passed_row_count,
            "failed_row_count": failed_row_count,
            "source_rows_json": json.dumps(source_rows, ensure_ascii=False),
            "errors_json": json.dumps(errors, ensure_ascii=False),
            "confirmed_at": False,
            "finished_at": False,
            "created_waybill_count": 0,
            "created_customer_line_count": 0,
            "created_goods_line_count": 0,
            "updated_record_count": 0,
            "skipped_record_count": 0,
            "failed_record_count": 0,
            "error_report_url": False,
            "failure_reason": False,
        }

    def get_source_rows(self):
        self.ensure_one()
        return json.loads(self.source_rows_json or "[]")

    def get_errors(self):
        self.ensure_one()
        return json.loads(self.errors_json or "[]")

    def mark_expired_if_needed(self):
        for record in self:
            if record.state in ("finished", "failed", "expired"):
                continue
            if record.expires_at and record.expires_at < fields.Datetime.now():
                record.state = "expired"
