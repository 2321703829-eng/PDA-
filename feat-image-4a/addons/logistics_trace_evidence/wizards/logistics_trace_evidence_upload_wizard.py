import base64
import mimetypes

from odoo import fields, models
from odoo.exceptions import UserError


class LogisticsTraceEvidenceUploadWizard(models.TransientModel):
    _name = "logistics.trace.evidence.upload.wizard"
    _description = "Upload Evidence Image Wizard"

    evidence_id = fields.Many2one(
        "logistics.trace.evidence",
        required=True,
        ondelete="cascade",
    )
    file_data = fields.Binary(required=True, attachment=False)
    file_name = fields.Char(required=True)

    def action_upload(self):
        self.ensure_one()
        if not self.file_data:
            raise UserError("Please choose a file to upload.")

        content = base64.b64decode(self.file_data)
        content_type = mimetypes.guess_type(self.file_name or "")[0] or "application/octet-stream"
        self.evidence_id.upload_image_binary(
            file_name=self.file_name,
            content=content,
            content_type=content_type,
        )
        return {"type": "ir.actions.act_window_close"}
