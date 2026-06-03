import base64
import json
import uuid

from odoo import _, http
from odoo.http import Response, content_disposition, request

from ..services.import_service import WaybillStandardImportService


class LogisticsWebImportController(http.Controller):
    @http.route(
        "/api/admin/logistics/imports/waybill-standard/template",
        type="http",
        auth="user",
        methods=["GET"],
    )
    def download_waybill_standard_template_meta(self, **kwargs):
        return self._json_response(
            {
                "code": 0,
                "message": _("成功"),
                "data": WaybillStandardImportService.build_template_payload(),
                "request_id": self._build_request_id("req_import_template"),
            }
        )

    @http.route(
        "/api/admin/logistics/imports/waybill-standard/template/download",
        type="http",
        auth="user",
        methods=["GET"],
    )
    def download_waybill_standard_template_file(self, template_code=None, template_version=None, **kwargs):
        if template_code and template_code != WaybillStandardImportService.TEMPLATE_CODE:
            return self._json_response(
                {
                    "code": 1,
                    "message": _("模板编码不正确"),
                    "data": {
                        "errors": [
                            {
                                "error_code": "TEMPLATE_CODE_INVALID",
                                "error_message": _("请使用标准模板 %(code)s。")
                                % {"code": WaybillStandardImportService.TEMPLATE_CODE},
                            }
                        ]
                    },
                    "request_id": self._build_request_id("req_import_template"),
                },
                status=400,
            )
        if template_version and template_version.lower() != WaybillStandardImportService.TEMPLATE_VERSION:
            return self._json_response(
                {
                    "code": 1,
                    "message": _("模板版本不正确"),
                    "data": {
                        "errors": [
                            {
                                "error_code": "TEMPLATE_VERSION_INVALID",
                                "error_message": _("请使用模板版本 %(version)s。")
                                % {"version": WaybillStandardImportService.TEMPLATE_VERSION},
                            }
                        ]
                    },
                    "request_id": self._build_request_id("req_import_template"),
                },
                status=400,
            )

        file_bytes = WaybillStandardImportService.load_template_bytes()
        headers = [
            ("Content-Type", "text/csv; charset=utf-8"),
            ("Content-Disposition", content_disposition(WaybillStandardImportService.TEMPLATE_FILE_NAME)),
        ]
        return request.make_response(file_bytes, headers=headers)

    @http.route(
        "/api/admin/logistics/imports/waybill-standard/precheck",
        type="http",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def precheck_waybill_standard_import(self, **kwargs):
        upload_file = request.httprequest.files.get("file")
        filename = upload_file.filename if upload_file else request.params.get("file_name", "")
        raw_bytes = upload_file.read() if upload_file else self._decode_base64_file(request.params.get("file_base64"))
        if raw_bytes is None:
            return self._json_response(
                {
                    "code": 1,
                    "message": _("预校验失败"),
                    "data": {
                        "template_code": WaybillStandardImportService.TEMPLATE_CODE,
                        "template_version": WaybillStandardImportService.TEMPLATE_VERSION,
                        "precheck_token": False,
                        "total_row_count": 0,
                        "passed_row_count": 0,
                        "failed_row_count": 0,
                        "can_confirm_import": False,
                        "errors": [
                            {
                                "row_no": 0,
                                "field_code": "template_file",
                                "field_label": _("模板文件"),
                                "error_code": "PRECHECK_PARSE_FAILED",
                                "error_message": _("文件内容不是有效的 Base64 编码。"),
                            }
                        ],
                    },
                    "request_id": self._build_request_id("req_import_precheck"),
                },
                status=400,
            )

        data = WaybillStandardImportService.precheck(
            request.env,
            raw_bytes,
            filename=filename,
            template_code=request.params.get("template_code"),
            template_version=request.params.get("template_version"),
        )
        return self._json_response(
            {
                "code": 0,
                "message": _("预校验完成") if data["errors"] else _("预校验通过"),
                "data": data,
                "request_id": self._build_request_id("req_import_precheck"),
            }
        )

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
