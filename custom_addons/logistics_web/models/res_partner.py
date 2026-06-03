from odoo import models

from ..services.customer_profile_export_service import CustomerProfileExportService


class ResPartner(models.Model):
    _inherit = "res.partner"

    def action_open_customer_profile_export_result(self):
        self.ensure_one()
        created = CustomerProfileExportService.create_customer_profile_export_task(
            self.env,
            selected_ids=self.ids,
            source_page="customer_profile_form",
            scope_snapshot={
                "selected_partner_ids": self.ids,
                "selected_partner_names": self.mapped("name"),
            },
            request_payload={
                "object_type": CustomerProfileExportService.OBJECT_TYPE,
                "entry_type": CustomerProfileExportService.ENTRY_TYPE,
                "export_mode": CustomerProfileExportService.EXPORT_MODE,
                "selected_ids": self.ids,
                "from_page": "customer_profile_form",
            },
        )
        result = CustomerProfileExportService.run_customer_profile_export_task(self.env, task_no=created["task_no"])
        return {
            "type": "ir.actions.client",
            "name": "导出结果",
            "tag": "logistics_web.export_result",
            "params": {
                "task_no": result["task_no"],
                "source_model": self._name,
            },
        }
