from odoo import fields, models

from ..services.dispatch_main_export_service import DispatchMainExportService


class LogisticsDispatchWaybill(models.Model):
    _inherit = "logistics.dispatch.waybill"

    trace_timeline_panel = fields.Char(
        string="留痕时间线面板",
        compute="_compute_ui_panels",
        readonly=True,
    )
    evidence_viewer_panel = fields.Char(
        string="证据查看面板",
        compute="_compute_ui_panels",
        readonly=True,
    )

    def _compute_ui_panels(self):
        for record in self:
            record.trace_timeline_panel = ""
            record.evidence_viewer_panel = ""

    def action_open_export_result(self):
        self.ensure_one()
        created = DispatchMainExportService.create_waybill_export_task(
            self.env,
            selected_ids=self.ids,
            source_page="waybill_form",
            scope_snapshot={
                "selected_waybill_ids": self.ids,
                "selected_waybill_no_list": self.mapped("name"),
            },
            request_payload={
                "object_type": DispatchMainExportService.OBJECT_TYPE,
                "entry_type": DispatchMainExportService.ENTRY_TYPE,
                "export_mode": DispatchMainExportService.EXPORT_MODE,
                "selected_ids": self.ids,
                "from_page": "waybill_form",
            },
        )
        result = DispatchMainExportService.run_waybill_export_task(self.env, task_no=created["task_no"])
        return {
            "type": "ir.actions.client",
            "name": "导出结果",
            "tag": "logistics_web.export_result",
            "params": {
                "task_no": result["task_no"],
                "source_model": self._name,
            },
        }
