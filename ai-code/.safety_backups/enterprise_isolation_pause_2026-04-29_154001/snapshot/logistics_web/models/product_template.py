from odoo import models

from ..services.product_profile_export_service import ProductProfileExportService


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_open_product_profile_export_result(self):
        self.ensure_one()
        created = ProductProfileExportService.create_product_profile_export_task(
            self.env,
            selected_ids=self.ids,
            source_page="product_profile_form",
            scope_snapshot={
                "selected_product_template_ids": self.ids,
                "selected_product_names": self.mapped("display_name"),
            },
            request_payload={
                "object_type": ProductProfileExportService.OBJECT_TYPE,
                "entry_type": ProductProfileExportService.ENTRY_TYPE,
                "export_mode": ProductProfileExportService.EXPORT_MODE,
                "selected_ids": self.ids,
                "from_page": "product_profile_form",
            },
        )
        result = ProductProfileExportService.run_product_profile_export_task(self.env, task_no=created["task_no"])
        return {
            "type": "ir.actions.client",
            "name": "导出结果",
            "tag": "logistics_web.export_result",
            "params": {
                "task_no": result["task_no"],
                "source_model": self._name,
            },
        }
