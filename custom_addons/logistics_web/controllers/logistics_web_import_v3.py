import base64
import json
import uuid

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import Response, content_disposition, request

from ..services.waybill_standard_import_service_v2 import WaybillStandardImportService


class LogisticsWebImportController(http.Controller):
    @http.route("/api/admin/logistics/imports/waybill-standard/template", type="http", auth="user", methods=["GET"])
    def download_waybill_standard_template_meta(self, **kwargs):
        payload = self._merged_payload()
        try:
            template_locale = WaybillStandardImportService.normalize_template_locale(payload.get("template_locale"))
            data = WaybillStandardImportService.build_template_payload()
            data["default_template_locale"] = template_locale
            data["file_name"] = WaybillStandardImportService.get_template_variant(template_locale)["file_name"]
            data["download_url"] = (
                "/api/admin/logistics/imports/waybill-standard/template/download"
                f"?template_code={WaybillStandardImportService.TEMPLATE_CODE}"
                f"&template_version={WaybillStandardImportService.TEMPLATE_VERSION}"
                f"&template_locale={template_locale}"
            )
        except ValidationError as exc:
            return self._json_response(
                {
                    "code": 1,
                    "message": "模板语言不正确",
                    "data": {"errors": [{"error_code": "TEMPLATE_LOCALE_INVALID", "error_message": str(exc)}]},
                    "request_id": self._build_request_id("req_import_template"),
                },
                status=400,
            )
        return self._json_response(
            {
                "code": 0,
                "message": "成功",
                "data": data,
                "request_id": self._build_request_id("req_import_template"),
            }
        )

    @http.route(
        "/api/admin/logistics/imports/waybill-standard/template/download",
        type="http",
        auth="user",
        methods=["GET"],
    )
    def download_waybill_standard_template_file(self, template_code=None, template_version=None, template_locale=None, **kwargs):
        if template_code and template_code != WaybillStandardImportService.TEMPLATE_CODE:
            return self._json_response(
                {
                    "code": 1,
                    "message": "模板编码不正确",
                    "data": {"errors": [{"error_code": "TEMPLATE_CODE_INVALID", "error_message": f"请使用标准模板 {WaybillStandardImportService.TEMPLATE_CODE}。"}]},
                    "request_id": self._build_request_id("req_import_template"),
                },
                status=400,
            )
        if template_version and template_version.lower() != WaybillStandardImportService.TEMPLATE_VERSION:
            return self._json_response(
                {
                    "code": 1,
                    "message": "模板版本不正确",
                    "data": {"errors": [{"error_code": "TEMPLATE_VERSION_INVALID", "error_message": f"请使用模板版本 {WaybillStandardImportService.TEMPLATE_VERSION}。"}]},
                    "request_id": self._build_request_id("req_import_template"),
                },
                status=400,
            )
        try:
            template_variant = WaybillStandardImportService.get_template_variant(template_locale)
        except ValidationError as exc:
            return self._json_response(
                {
                    "code": 1,
                    "message": "模板语言不正确",
                    "data": {"errors": [{"error_code": "TEMPLATE_LOCALE_INVALID", "error_message": str(exc)}]},
                    "request_id": self._build_request_id("req_import_template"),
                },
                status=400,
            )

        file_bytes = WaybillStandardImportService.load_template_bytes(template_locale=template_variant["template_locale"])
        headers = [
            ("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            ("Content-Disposition", content_disposition(template_variant["file_name"])),
        ]
        return request.make_response(file_bytes, headers=headers)

    @http.route("/api/admin/logistics/imports/waybill-standard/precheck", type="http", auth="user", methods=["POST"], csrf=False)
    def precheck_waybill_standard_import(self, **kwargs):
        payload = self._merged_payload()
        upload_file = request.httprequest.files.get("file")
        filename = upload_file.filename if upload_file else payload.get("file_name", "")
        raw_bytes = upload_file.read() if upload_file else self._decode_base64_file(payload.get("file_base64"))
        if raw_bytes is None:
            return self._json_response(
                {
                    "code": 1,
                    "message": "预校验失败",
                    "data": {
                        "template_code": WaybillStandardImportService.TEMPLATE_CODE,
                        "template_version": WaybillStandardImportService.TEMPLATE_VERSION,
                        "import_batch_no": False,
                        "precheck_token": False,
                        "error_report_url": False,
                        "total_row_count": 0,
                        "passed_row_count": 0,
                        "failed_row_count": 0,
                        "can_confirm_import": False,
                        "errors": [{"sheet_name": "模板文件", "row_no": 0, "field_code": "template_file", "field_label": "模板文件", "error_code": "PRECHECK_PARSE_FAILED", "error_message": "文件内容不是有效的 Base64 编码。"}],
                    },
                    "request_id": self._build_request_id("req_import_precheck"),
                },
                status=400,
            )

        data = WaybillStandardImportService.precheck(
            request.env,
            raw_bytes,
            filename=filename,
            template_code=payload.get("template_code"),
            template_version=payload.get("template_version"),
        )
        return self._json_response(
            {
                "code": 0,
                "message": "预校验完成" if data["errors"] else "预校验通过",
                "data": data,
                "request_id": self._build_request_id("req_import_precheck"),
            }
        )

    @http.route("/api/admin/logistics/imports/waybill-standard/confirm", type="http", auth="user", methods=["POST"], csrf=False)
    def confirm_waybill_standard_import(self, **kwargs):
        payload = self._merged_payload()
        try:
            data = WaybillStandardImportService.confirm_import(
                request.env,
                precheck_token=payload.get("precheck_token"),
                import_batch_no=payload.get("import_batch_no", ""),
            )
        except ValidationError as exc:
            return self._json_response(
                {
                    "code": 1,
                    "message": "正式导入失败",
                    "data": {"errors": [{"error_code": "IMPORT_CONFIRM_FAILED", "error_message": str(exc)}]},
                    "request_id": self._build_request_id("req_import_confirm"),
                },
                status=400,
            )

        return self._json_response(
            {
                "code": 0,
                "message": "正式导入完成",
                "data": data,
                "request_id": self._build_request_id("req_import_confirm"),
            }
        )

    @http.route("/api/admin/logistics/imports/waybill-standard/result", type="http", auth="user", methods=["GET"])
    def get_waybill_import_result(self, **kwargs):
        payload = self._merged_payload()
        try:
            data = WaybillStandardImportService.get_import_result(
                request.env,
                import_batch_no=payload.get("import_batch_no"),
            )
        except ValidationError as exc:
            return self._json_response(
                {
                    "code": 1,
                    "message": "查询导入结果失败",
                    "data": {"errors": [{"error_code": "IMPORT_RESULT_NOT_FOUND", "error_message": str(exc)}]},
                    "request_id": self._build_request_id("req_import_result"),
                },
                status=400,
            )

        return self._json_response(
            {
                "code": 0,
                "message": "成功",
                "data": data,
                "request_id": self._build_request_id("req_import_result"),
            }
        )

    @http.route("/api/admin/logistics/imports/waybill-standard/error-report", type="http", auth="user", methods=["GET"])
    def download_waybill_import_error_report(self, **kwargs):
        payload = self._merged_payload()
        try:
            report = WaybillStandardImportService.build_error_report(
                request.env,
                import_batch_no=payload.get("import_batch_no", ""),
                precheck_token=payload.get("precheck_token", ""),
            )
        except ValidationError as exc:
            return self._json_response(
                {
                    "code": 1,
                    "message": "下载错误报告失败",
                    "data": {"errors": [{"error_code": "ERROR_REPORT_NOT_FOUND", "error_message": str(exc)}]},
                    "request_id": self._build_request_id("req_import_error_report"),
                },
                status=400,
            )

        headers = [
            ("Content-Type", report["content_type"]),
            ("Content-Disposition", content_disposition(report["file_name"])),
        ]
        return request.make_response(report["file_bytes"], headers=headers)

    def _merged_payload(self):
        payload = dict(request.params)
        if request.httprequest.mimetype == "application/json":
            json_payload = request.httprequest.get_json(silent=True) or {}
            if isinstance(json_payload, dict):
                payload.update({key: value for key, value in json_payload.items() if value is not None})
        return payload

    def _decode_base64_file(self, payload):
        if not payload:
            return b""
        try:
            return base64.b64decode(payload)
        except Exception:
            return None

    def _json_response(self, payload, *, status=200):
        return Response(
            json.dumps(payload, ensure_ascii=False),
            status=status,
            headers=[("Content-Type", "application/json; charset=utf-8")],
        )

    def _build_request_id(self, prefix):
        return f"{prefix}_{uuid.uuid4().hex[:12]}"
