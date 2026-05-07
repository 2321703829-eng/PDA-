from odoo import _, fields, models

from ..services.image_storage_service import LogisticsEvidenceImageStorage


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    logistics_trace_image_public_base_url = fields.Char(
        string="Image Public Base URL",
        config_parameter="logistics_trace_evidence.image_public_base_url",
    )
    logistics_trace_image_storage_root = fields.Char(
        string="Image Storage Root",
        config_parameter="logistics_trace_evidence.image_storage_root",
    )

    def action_test_logistics_trace_image_storage(self):
        self.ensure_one()
        storage = LogisticsEvidenceImageStorage(self.env)
        data = storage.ensure_storage_ready()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Image Storage Ready"),
                "message": _(
                    "The feat-image-4a storage path is ready. "
                    "Current root: %(root)s."
                )
                % {"root": data["storage_root"]},
                "type": "success",
                "sticky": False,
            },
        }
