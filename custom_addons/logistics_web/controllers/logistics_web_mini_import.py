import base64

from odoo import http
from odoo.exceptions import AccessError, ValidationError
from odoo.http import request

from .logistics_web_import_v3 import LogisticsWebImportController
from .logistics_web_mini_trace import LogisticsMiniApiAuthMixin
from ..services.mini_program_raw_sheet_import_service import MiniProgramRawSheetImportService


class LogisticsWebMiniImportController(LogisticsWebImportController, LogisticsMiniApiAuthMixin):
    @http.route("/api/mini/logistics/imports/mini-program-raw-sheet/template", type="http", auth="public", methods=["GET"])
    def mini_get_mini_program_raw_sheet_template(self, **kwargs):
        payload = self._merged_payload()
        try:
            self._ensure_mini_token(payload)
            data = MiniProgramRawSheetImportService.build_template_payload()
        except PermissionError as exc:
            return self._error_response(
                message="Template query failed",
                error_code="IMPORT_PERMISSION_DENIED",
                error_message=str(exc),
                request_id_prefix="req_mini_import_template",
                status=401,
            )
        except Exception as exc:
            return self._error_response(
                message="Template query failed",
                error_code="IMPORT_INTERNAL_ERROR",
                error_message=str(exc),
                request_id_prefix="req_mini_import_template",
            )
        return self._success_response(data=data, request_id_prefix="req_mini_import_template")

    @http.route(
        "/api/mini/logistics/imports/mini-program-raw-sheet/precheck",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def mini_precheck_mini_program_raw_sheet(self, **kwargs):
        payload = self._merged_payload()
        upload_file = request.httprequest.files.get("file")
        filename = upload_file.filename if upload_file else payload.get("file_name", "")
        raw_bytes = upload_file.read() if upload_file else self._decode_base64_file(payload.get("file_base64"))
        if raw_bytes is None:
            return self._error_response(
                message="Precheck failed",
                error_code="PRECHECK_PARSE_FAILED",
                error_message="file_base64 is not valid Base64.",
                request_id_prefix="req_mini_import_precheck",
            )
        try:
            self._ensure_mini_token(payload)
            data = MiniProgramRawSheetImportService.precheck(
                request.env,
                raw_bytes,
                filename=filename,
                template_code=payload.get("template_code"),
                template_version=payload.get("template_version"),
            )
        except PermissionError as exc:
            return self._error_response(
                message="Precheck failed",
                error_code="IMPORT_PERMISSION_DENIED",
                error_message=str(exc),
                request_id_prefix="req_mini_import_precheck",
                status=401,
            )
        except ValidationError as exc:
            return self._error_response(
                message="Precheck failed",
                error_code="IMPORT_PRECHECK_INVALID",
                error_message=str(exc),
                request_id_prefix="req_mini_import_precheck",
            )
        except AccessError as exc:
            return self._error_response(
                message="Precheck failed",
                error_code="IMPORT_PERMISSION_DENIED",
                error_message=str(exc),
                request_id_prefix="req_mini_import_precheck",
            )
        except Exception as exc:
            return self._error_response(
                message="Precheck failed",
                error_code="IMPORT_INTERNAL_ERROR",
                error_message=str(exc),
                request_id_prefix="req_mini_import_precheck",
            )
        return self._success_response(data=data, request_id_prefix="req_mini_import_precheck", message="Precheck finished")

    @http.route(
        "/api/mini/logistics/imports/mini-program-raw-sheet/confirm",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def mini_confirm_mini_program_raw_sheet(self, **kwargs):
        payload = self._merged_payload()
        try:
            self._ensure_mini_token(payload)
            data = MiniProgramRawSheetImportService.confirm_import(
                request.env,
                precheck_token=payload.get("precheck_token"),
                import_batch_no=payload.get("import_batch_no", ""),
                task_no=payload.get("task_no", ""),
            )
        except PermissionError as exc:
            return self._error_response(
                message="Confirm failed",
                error_code="IMPORT_PERMISSION_DENIED",
                error_message=str(exc),
                request_id_prefix="req_mini_import_confirm",
                status=401,
            )
        except AccessError as exc:
            return self._error_response(
                message="Confirm failed",
                error_code="IMPORT_PERMISSION_DENIED",
                error_message=str(exc),
                request_id_prefix="req_mini_import_confirm",
            )
        except ValidationError as exc:
            return self._error_response(
                message="Confirm failed",
                error_code=self._resolve_import_confirm_error_code(str(exc)),
                error_message=str(exc),
                request_id_prefix="req_mini_import_confirm",
            )
        except Exception as exc:
            return self._error_response(
                message="Confirm failed",
                error_code="IMPORT_INTERNAL_ERROR",
                error_message=str(exc),
                request_id_prefix="req_mini_import_confirm",
            )
        return self._success_response(data=data, request_id_prefix="req_mini_import_confirm", message="Confirm finished")

    @http.route("/api/mini/logistics/imports/tasks/<string:task_no>", type="http", auth="public", methods=["GET"])
    def mini_get_import_task_summary(self, task_no=None, **kwargs):
        payload = self._merged_payload()
        try:
            self._ensure_mini_token(payload)
            data = MiniProgramRawSheetImportService.get_import_task_result(
                request.env,
                task_no=task_no or payload.get("task_no", ""),
                import_batch_no=payload.get("import_batch_no", ""),
            )
        except PermissionError as exc:
            return self._error_response(
                message="Query failed",
                error_code="IMPORT_PERMISSION_DENIED",
                error_message=str(exc),
                request_id_prefix="req_mini_import_task",
                status=401,
            )
        except Exception as exc:
            return self._error_response(
                message="Query failed",
                error_code="IMPORT_INTERNAL_ERROR",
                error_message=str(exc),
                request_id_prefix="req_mini_import_task",
            )
        return self._success_response(data=data, request_id_prefix="req_mini_import_task")

    @http.route("/api/mini/logistics/imports/tasks/<string:task_no>/lines", type="http", auth="public", methods=["GET"])
    def mini_get_import_task_lines(self, task_no=None, **kwargs):
        payload = self._merged_payload()
        try:
            self._ensure_mini_token(payload)
            data = MiniProgramRawSheetImportService.get_import_task_lines(
                request.env,
                task_no=task_no or payload.get("task_no", ""),
                page=payload.get("page", 1),
                page_size=payload.get("page_size", 20),
                match_status=payload.get("match_status", ""),
                keyword=payload.get("keyword", ""),
            )
        except PermissionError as exc:
            return self._error_response(
                message="Query failed",
                error_code="IMPORT_PERMISSION_DENIED",
                error_message=str(exc),
                request_id_prefix="req_mini_import_lines",
                status=401,
            )
        except Exception as exc:
            return self._error_response(
                message="Query failed",
                error_code="IMPORT_INTERNAL_ERROR",
                error_message=str(exc),
                request_id_prefix="req_mini_import_lines",
            )
        return self._success_response(data=data, request_id_prefix="req_mini_import_lines")

    @http.route("/api/mini/logistics/imports/tasks/<string:task_no>/errors", type="http", auth="public", methods=["GET"])
    def mini_get_import_task_errors(self, task_no=None, **kwargs):
        payload = self._merged_payload()
        try:
            self._ensure_mini_token(payload)
            data = MiniProgramRawSheetImportService.get_import_task_errors(
                request.env,
                task_no=task_no or payload.get("task_no", ""),
                page=payload.get("page", 1),
                page_size=payload.get("page_size", 50),
                error_code=payload.get("error_code", ""),
            )
        except PermissionError as exc:
            return self._error_response(
                message="Query failed",
                error_code="IMPORT_PERMISSION_DENIED",
                error_message=str(exc),
                request_id_prefix="req_mini_import_errors",
                status=401,
            )
        except Exception as exc:
            return self._error_response(
                message="Query failed",
                error_code="IMPORT_INTERNAL_ERROR",
                error_message=str(exc),
                request_id_prefix="req_mini_import_errors",
            )
        return self._success_response(data=data, request_id_prefix="req_mini_import_errors")

    @http.route(
        "/api/mini/logistics/imports/tasks/<string:task_no>/error-report",
        type="http",
        auth="public",
        methods=["GET"],
    )
    def mini_download_import_task_error_report(self, task_no=None, **kwargs):
        payload = self._merged_payload()
        try:
            self._ensure_mini_token(payload)
            report = MiniProgramRawSheetImportService.build_import_task_error_report(
                request.env,
                task_no=task_no or payload.get("task_no", ""),
                import_batch_no=payload.get("import_batch_no", ""),
                precheck_token=payload.get("precheck_token", ""),
            )
        except PermissionError as exc:
            return self._error_response(
                message="Download failed",
                error_code="IMPORT_PERMISSION_DENIED",
                error_message=str(exc),
                request_id_prefix="req_mini_import_report",
                status=401,
            )
        except Exception as exc:
            return self._error_response(
                message="Download failed",
                error_code="IMPORT_INTERNAL_ERROR",
                error_message=str(exc),
                request_id_prefix="req_mini_import_report",
            )
        headers = [
            ("Content-Type", report["content_type"]),
            ("Content-Disposition", f'attachment; filename="{report["file_name"]}"'),
        ]
        return request.make_response(report["file_bytes"], headers=headers)

    def _decode_base64_file(self, payload):
        if not payload:
            return b""
        try:
            return base64.b64decode(payload)
        except Exception:
            return None
