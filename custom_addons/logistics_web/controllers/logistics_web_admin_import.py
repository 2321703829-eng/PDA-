import base64

from odoo import http
from odoo.exceptions import AccessError, ValidationError
from odoo.http import request

from .logistics_web_import_v3 import LogisticsWebImportController
from ..services.mini_program_raw_sheet_import_service import MiniProgramRawSheetImportService


class LogisticsWebAdminImportController(LogisticsWebImportController):
    @http.route("/api/admin/logistics/imports/mini-program-raw-sheet/template", type="http", auth="user", methods=["GET"])
    def admin_get_mini_program_raw_sheet_template(self, **kwargs):
        try:
            data = MiniProgramRawSheetImportService.build_template_payload()
        except Exception as exc:
            return self._error_response(
                message="Template query failed",
                error_code="IMPORT_INTERNAL_ERROR",
                error_message=str(exc),
                request_id_prefix="req_mini_raw_template",
            )
        return self._success_response(data=data, request_id_prefix="req_mini_raw_template")

    @http.route(
        "/api/admin/logistics/imports/mini-program-raw-sheet/precheck",
        type="http",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def admin_precheck_mini_program_raw_sheet(self, **kwargs):
        payload = self._merged_payload()
        upload_file = request.httprequest.files.get("file")
        filename = upload_file.filename if upload_file else payload.get("file_name", "")
        raw_bytes = upload_file.read() if upload_file else self._decode_base64_file(payload.get("file_base64"))
        if raw_bytes is None:
            return self._error_response(
                message="Precheck failed",
                error_code="PRECHECK_PARSE_FAILED",
                error_message="file_base64 is not valid Base64.",
                request_id_prefix="req_mini_raw_precheck",
            )
        try:
            data = MiniProgramRawSheetImportService.precheck(
                request.env,
                raw_bytes,
                filename=filename,
                template_code=payload.get("template_code"),
                template_version=payload.get("template_version"),
            )
        except ValidationError as exc:
            return self._error_response(
                message="Precheck failed",
                error_code="IMPORT_PRECHECK_INVALID",
                error_message=str(exc),
                request_id_prefix="req_mini_raw_precheck",
            )
        except AccessError as exc:
            return self._error_response(
                message="Precheck failed",
                error_code="IMPORT_PERMISSION_DENIED",
                error_message=str(exc),
                request_id_prefix="req_mini_raw_precheck",
            )
        except Exception as exc:
            return self._error_response(
                message="Precheck failed",
                error_code="IMPORT_INTERNAL_ERROR",
                error_message=str(exc),
                request_id_prefix="req_mini_raw_precheck",
            )
        return self._success_response(data=data, request_id_prefix="req_mini_raw_precheck", message="Precheck finished")

    @http.route(
        "/api/admin/logistics/imports/mini-program-raw-sheet/confirm",
        type="http",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def admin_confirm_mini_program_raw_sheet(self, **kwargs):
        payload = self._merged_payload()
        try:
            data = MiniProgramRawSheetImportService.confirm_import(
                request.env,
                precheck_token=payload.get("precheck_token"),
                import_batch_no=payload.get("import_batch_no", ""),
                task_no=payload.get("task_no", ""),
            )
        except AccessError as exc:
            return self._error_response(
                message="Confirm failed",
                error_code="IMPORT_PERMISSION_DENIED",
                error_message=str(exc),
                request_id_prefix="req_mini_raw_confirm",
            )
        except ValidationError as exc:
            return self._error_response(
                message="Confirm failed",
                error_code=self._resolve_import_confirm_error_code(str(exc)),
                error_message=str(exc),
                request_id_prefix="req_mini_raw_confirm",
            )
        except Exception as exc:
            return self._error_response(
                message="Confirm failed",
                error_code="IMPORT_INTERNAL_ERROR",
                error_message=str(exc),
                request_id_prefix="req_mini_raw_confirm",
            )
        return self._success_response(data=data, request_id_prefix="req_mini_raw_confirm", message="Confirm finished")

    def _decode_base64_file(self, payload):
        if not payload:
            return b""
        try:
            return base64.b64decode(payload)
        except Exception:
            return None
