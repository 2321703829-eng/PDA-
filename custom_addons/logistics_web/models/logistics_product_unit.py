from odoo import models
from odoo.exceptions import ValidationError

from ..services.product_profile_export_service import ProductProfileExportService


class LogisticsProductUnit(models.Model):
    _inherit = "logistics.product.unit"

    def action_open_product_profile_export_result(self):
        self.ensure_one()
        product_templates = self.mapped("product_tmpl_id").exists()
        if not product_templates:
            raise ValidationError("当前商品规格没有关联商品主档，暂时无法导出货物画像。")
        created = ProductProfileExportService.create_product_profile_export_task(
            self.env,
            selected_ids=product_templates.ids,
            source_page="product_unit_form",
            scope_snapshot={
                "selected_product_unit_ids": self.ids,
                "selected_product_unit_names": self.mapped("display_name"),
                "selected_product_template_ids": product_templates.ids,
                "selected_product_names": product_templates.mapped("display_name"),
            },
            request_payload={
                "object_type": ProductProfileExportService.OBJECT_TYPE,
                "entry_type": ProductProfileExportService.ENTRY_TYPE,
                "export_mode": ProductProfileExportService.EXPORT_MODE,
                "selected_ids": product_templates.ids,
                "from_page": "product_unit_form",
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
