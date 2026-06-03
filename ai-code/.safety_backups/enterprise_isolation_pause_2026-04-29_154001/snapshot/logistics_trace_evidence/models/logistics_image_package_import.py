import base64

from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError

from ..services.image_package_import_service import ImagePackageImportService


class LogisticsImportTask(models.Model):
    _inherit = "logistics.import.task"

    matched_count = fields.Integer(string="已命中数量", compute="_compute_image_package_metrics", store=True)
    unmatched_count = fields.Integer(string="未命中数量", compute="_compute_image_package_metrics", store=True)
    ambiguous_count = fields.Integer(string="命中歧义数量", compute="_compute_image_package_metrics", store=True)
    linked_count = fields.Integer(string="已补链数量", compute="_compute_image_package_metrics", store=True)
    link_failed_count = fields.Integer(string="补链失败数量", compute="_compute_image_package_metrics", store=True)
    manual_review_count = fields.Integer(string="待人工复核数量", compute="_compute_image_package_metrics", store=True)

    @api.depends(
        "task_line_ids.object_type",
        "task_line_ids.match_status",
        "task_line_ids.link_status",
    )
    def _compute_image_package_metrics(self):
        for record in self:
            lines = record.task_line_ids.filtered(lambda rec: rec.object_type == ImagePackageImportService.OBJECT_TYPE)
            record.matched_count = len(lines.filtered(lambda rec: rec.match_status == "matched"))
            record.unmatched_count = len(lines.filtered(lambda rec: rec.match_status == "unmatched"))
            record.ambiguous_count = len(lines.filtered(lambda rec: rec.match_status == "ambiguous"))
            record.linked_count = len(lines.filtered(lambda rec: rec.link_status == "linked"))
            record.link_failed_count = len(lines.filtered(lambda rec: rec.link_status == "failed"))
            record.manual_review_count = len(lines.filtered(lambda rec: rec.link_status == "manual_review"))

    def action_retry_image_package_lines(self):
        self.ensure_one()
        return ImagePackageImportService.retry_failed_lines(self.env, self)

    def action_open_linked_evidences(self):
        self.ensure_one()
        evidence_ids = self.task_line_ids.filtered(
            lambda rec: rec.object_type == ImagePackageImportService.OBJECT_TYPE and rec.linked_evidence_id
        ).mapped("linked_evidence_id").ids
        return {
            "type": "ir.actions.act_window",
            "name": "图片包导入证据",
            "res_model": "logistics.trace.evidence",
            "view_mode": "list,form",
            "domain": [("id", "in", evidence_ids)],
        }


class LogisticsImportTaskLine(models.Model):
    _inherit = "logistics.import.task.line"

    package_entry_name = fields.Char(string="包内文件路径")
    source_filename = fields.Char(string="原始文件名")
    scene_code = fields.Char(string="场景编码")
    capture_time = fields.Datetime(string="采集时间")
    mime_type = fields.Char(string="MIME 类型")
    waybill_no = fields.Char(string="运单号")
    customer_line_no = fields.Char(string="配送节点编号")
    store_no = fields.Char(string="门店编码")
    matched_waybill_id = fields.Many2one("logistics.dispatch.waybill", string="命中运单")
    matched_customer_line_id = fields.Many2one(
        "logistics.dispatch.waybill.customer.line",
        string="命中配送节点",
    )
    match_status = fields.Selection(
        selection=ImagePackageImportService.MATCH_STATUS_SELECTION,
        string="命中状态",
        default="pending",
    )
    match_method = fields.Selection(
        selection=ImagePackageImportService.MATCH_METHOD_SELECTION,
        string="命中方式",
    )
    match_remark = fields.Text(string="命中说明")
    selected_trace_event_id = fields.Many2one("logistics.trace.event", string="目标留痕事件")
    linked_evidence_id = fields.Many2one("logistics.trace.evidence", string="正式证据")
    image_access_key = fields.Char(string="图片访问键")
    link_status = fields.Selection(
        selection=ImagePackageImportService.LINK_STATUS_SELECTION,
        string="补链状态",
        default="pending",
    )
    link_mode = fields.Selection(
        [("auto", "自动"), ("manual", "人工")],
        string="补链模式",
        default="auto",
    )
    link_fail_reason = fields.Text(string="补链失败原因")
    retry_count = fields.Integer(string="重试次数", default=0)
    linked_at = fields.Datetime(string="补链时间")
    linked_by = fields.Many2one("res.users", string="补链人")

    def action_retry_image_package_line(self):
        self.ensure_one()
        if self.task_id.object_type != ImagePackageImportService.OBJECT_TYPE:
            raise ValidationError("当前导入行不属于图片包任务。")
        return ImagePackageImportService.retry_failed_lines(self.env, self.task_id)

    def action_open_linked_evidence(self):
        self.ensure_one()
        if not self.linked_evidence_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": "正式证据",
            "res_model": "logistics.trace.evidence",
            "view_mode": "form",
            "res_id": self.linked_evidence_id.id,
        }


class LogisticsTraceImagePackageImportWizard(models.TransientModel):
    _name = "logistics.trace.image.package.import.wizard"
    _description = "图片包导入向导"

    package_file = fields.Binary(string="ZIP 文件", required=True)
    package_file_name = fields.Char(string="文件名", required=True)
    note = fields.Text(
        string="导入说明",
        default=(
            "支持 ZIP 图片包。首轮按文件名命中："
            "waybill_no__scene.jpg、waybill_no__store_no__scene.jpg、"
            "waybill_no__customer_line_no__scene.jpg。"
        ),
    )

    def action_import_image_package(self):
        self.ensure_one()
        if not self.package_file:
            raise ValidationError("请先选择图片包 ZIP 文件。")
        try:
            raw_bytes = base64.b64decode(self.package_file)
        except Exception as exc:
            raise ValidationError(f"图片包内容不是有效的 Base64 数据：{exc}") from exc
        task = ImagePackageImportService.import_zip(
            self.env,
            raw_bytes=raw_bytes,
            file_name=self.package_file_name,
            operator=self.env.user,
        )
        return {
            "type": "ir.actions.act_window",
            "name": "图片包导入任务",
            "res_model": "logistics.import.task",
            "view_mode": "form",
            "res_id": task.id,
        }
