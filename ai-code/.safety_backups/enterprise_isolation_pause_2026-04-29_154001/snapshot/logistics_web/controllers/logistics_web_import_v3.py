import base64
import json
import uuid

from odoo import http
from odoo.exceptions import AccessError, ValidationError
from odoo.http import Response, content_disposition, request

from odoo.addons.logistics_trace_evidence.services.image_package_import_service import ImagePackageImportService
from ..services.route_planning_import_service import RoutePlanningImportService
from ..services.waybill_standard_import_service_v2 import WaybillStandardImportService


class LogisticsWebImportController(http.Controller):
    IMPORT_SERVICE_BY_OBJECT_TYPE = {
        RoutePlanningImportService.OBJECT_TYPE: RoutePlanningImportService,
        ImagePackageImportService.OBJECT_TYPE: ImagePackageImportService,
    }
    TOP_LEVEL_HTTP_STATUS = {
        4001: 400,
        4003: 403,
        4004: 404,
        4090: 409,
        5000: 500,
    }

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
            return self._error_response(
                message="模板查询失败",
                error_code="TEMPLATE_LOCALE_INVALID",
                error_message=str(exc),
                request_id_prefix="req_import_template",
            )
        except Exception as exc:
            return self._error_response(
                message="模板查询失败",
                error_code="IMPORT_INTERNAL_ERROR",
                error_message=str(exc),
                request_id_prefix="req_import_template",
            )
        return self._success_response(data=data, request_id_prefix="req_import_template")

    @http.route(
        "/api/admin/logistics/imports/waybill-standard/template/download",
        type="http",
        auth="user",
        methods=["GET"],
    )
    def download_waybill_standard_template_file(self, template_code=None, template_version=None, template_locale=None, **kwargs):
        if template_code and template_code != WaybillStandardImportService.TEMPLATE_CODE:
            return self._error_response(
                message="模板下载失败",
                error_code="TEMPLATE_CODE_INVALID",
                error_message=f"请使用标准模板 {WaybillStandardImportService.TEMPLATE_CODE}。",
                request_id_prefix="req_import_template",
            )
        if template_version and template_version.lower() != WaybillStandardImportService.TEMPLATE_VERSION:
            return self._error_response(
                message="模板下载失败",
                error_code="TEMPLATE_VERSION_INVALID",
                error_message=f"请使用模板版本 {WaybillStandardImportService.TEMPLATE_VERSION}。",
                request_id_prefix="req_import_template",
            )
        try:
            template_variant = WaybillStandardImportService.get_template_variant(template_locale)
            file_bytes = WaybillStandardImportService.load_template_bytes(
                template_locale=template_variant["template_locale"]
            )
        except ValidationError as exc:
            return self._error_response(
                message="模板下载失败",
                error_code="TEMPLATE_LOCALE_INVALID",
                error_message=str(exc),
                request_id_prefix="req_import_template",
            )
        except Exception as exc:
            return self._error_response(
                message="模板下载失败",
                error_code="IMPORT_INTERNAL_ERROR",
                error_message=str(exc),
                request_id_prefix="req_import_template",
            )

        headers = [
            ("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            ("Content-Disposition", content_disposition(template_variant["file_name"])),
        ]
        return request.make_response(file_bytes, headers=headers)

    @http.route("/api/admin/logistics/imports/route-planning/template", type="http", auth="user", methods=["GET"])
    def download_route_planning_template_meta(self, **kwargs):
        payload = self._merged_payload()
        try:
            template_locale = RoutePlanningImportService.normalize_template_locale(payload.get("template_locale"))
            data = RoutePlanningImportService.build_template_payload()
            data["default_template_locale"] = template_locale
            data["file_name"] = RoutePlanningImportService.get_template_variant(template_locale)["file_name"]
            data["download_url"] = (
                "/api/admin/logistics/imports/route-planning/template/download"
                f"?template_code={RoutePlanningImportService.TEMPLATE_CODE}"
                f"&template_version={RoutePlanningImportService.TEMPLATE_VERSION}"
                f"&template_locale={template_locale}"
            )
        except ValidationError as exc:
            return self._error_response(
                message="模板查询失败",
                error_code="TEMPLATE_LOCALE_INVALID",
                error_message=str(exc),
                request_id_prefix="req_route_planning_template",
            )
        except Exception as exc:
            return self._error_response(
                message="模板查询失败",
                error_code="IMPORT_INTERNAL_ERROR",
                error_message=str(exc),
                request_id_prefix="req_route_planning_template",
            )
        return self._success_response(data=data, request_id_prefix="req_route_planning_template")

    @http.route(
        "/api/admin/logistics/imports/route-planning/template/download",
        type="http",
        auth="user",
        methods=["GET"],
    )
    def download_route_planning_template_file(self, template_code=None, template_version=None, template_locale=None, **kwargs):
        if template_code and template_code != RoutePlanningImportService.TEMPLATE_CODE:
            return self._error_response(
                message="模板下载失败",
                error_code="TEMPLATE_CODE_INVALID",
                error_message=f"请使用标准模板 {RoutePlanningImportService.TEMPLATE_CODE}。",
                request_id_prefix="req_route_planning_template",
            )
        if template_version and template_version.lower() != RoutePlanningImportService.TEMPLATE_VERSION:
            return self._error_response(
                message="模板下载失败",
                error_code="TEMPLATE_VERSION_INVALID",
                error_message=f"请使用模板版本 {RoutePlanningImportService.TEMPLATE_VERSION}。",
                request_id_prefix="req_route_planning_template",
            )
        try:
            template_variant = RoutePlanningImportService.get_template_variant(template_locale)
            file_bytes = RoutePlanningImportService.load_template_bytes(
                template_locale=template_variant["template_locale"]
            )
        except ValidationError as exc:
            return self._error_response(
                message="模板下载失败",
                error_code="TEMPLATE_LOCALE_INVALID",
                error_message=str(exc),
                request_id_prefix="req_route_planning_template",
            )
        except Exception as exc:
            return self._error_response(
                message="模板下载失败",
                error_code="IMPORT_INTERNAL_ERROR",
                error_message=str(exc),
                request_id_prefix="req_route_planning_template",
            )

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
            return self._error_response(
                message="预校验失败",
                error_code="PRECHECK_PARSE_FAILED",
                error_message="文件内容不是有效的 Base64 编码。",
                request_id_prefix="req_import_precheck",
            )
        try:
            data = WaybillStandardImportService.precheck(
                request.env,
                raw_bytes,
                filename=filename,
                template_code=payload.get("template_code"),
                template_version=payload.get("template_version"),
            )
        except ValidationError as exc:
            return self._error_response(
                message="预校验失败",
                error_code="IMPORT_PRECHECK_INVALID",
                error_message=str(exc),
                request_id_prefix="req_import_precheck",
            )
        except AccessError as exc:
            return self._error_response(
                message="预校验失败",
                error_code="IMPORT_PERMISSION_DENIED",
                error_message=str(exc),
                request_id_prefix="req_import_precheck",
            )
        except Exception as exc:
            return self._error_response(
                message="预校验失败",
                error_code="IMPORT_INTERNAL_ERROR",
                error_message=str(exc),
                request_id_prefix="req_import_precheck",
            )
        message = "预校验通过" if not data.get("errors") else "预校验完成"
        return self._success_response(data=data, request_id_prefix="req_import_precheck", message=message)

    @http.route("/api/admin/logistics/imports/image-package/upload", type="http", auth="user", methods=["POST"], csrf=False)
    def upload_image_package(self, **kwargs):
        payload = self._merged_payload()
        upload_file = request.httprequest.files.get("file")
        filename = upload_file.filename if upload_file else payload.get("file_name", "")
        raw_bytes = upload_file.read() if upload_file else self._decode_base64_file(payload.get("file_base64"))
        if raw_bytes is None:
            return self._error_response(
                message="图片包导入失败",
                error_code="IMAGE_PACKAGE_PARSE_FAILED",
                error_message="文件内容不是有效的 Base64 编码。",
                request_id_prefix="req_image_package_upload",
            )
        try:
            task = ImagePackageImportService.import_zip(
                request.env,
                raw_bytes=raw_bytes,
                file_name=filename,
                operator=request.env.user,
            )
            data = ImagePackageImportService.get_import_task_result(request.env, task_no=task.task_no)
            data["task_id"] = task.id
        except ValidationError as exc:
            return self._error_response(
                message="图片包导入失败",
                error_code="IMAGE_PACKAGE_UPLOAD_INVALID",
                error_message=str(exc),
                request_id_prefix="req_image_package_upload",
            )
        except AccessError as exc:
            return self._error_response(
                message="图片包导入失败",
                error_code="IMPORT_PERMISSION_DENIED",
                error_message=str(exc),
                request_id_prefix="req_image_package_upload",
            )
        except Exception as exc:
            return self._error_response(
                message="图片包导入失败",
                error_code="IMPORT_INTERNAL_ERROR",
                error_message=str(exc),
                request_id_prefix="req_image_package_upload",
            )
        return self._success_response(
            data=data,
            request_id_prefix="req_image_package_upload",
            message="图片包导入完成",
        )

    @http.route("/api/admin/logistics/imports/route-planning/precheck", type="http", auth="user", methods=["POST"], csrf=False)
    def precheck_route_planning_import(self, **kwargs):
        payload = self._merged_payload()
        upload_file = request.httprequest.files.get("file")
        filename = upload_file.filename if upload_file else payload.get("file_name", "")
        raw_bytes = upload_file.read() if upload_file else self._decode_base64_file(payload.get("file_base64"))
        if raw_bytes is None:
            return self._error_response(
                message="预校验失败",
                error_code="PRECHECK_PARSE_FAILED",
                error_message="文件内容不是有效的 Base64 编码。",
                request_id_prefix="req_route_planning_precheck",
            )
        try:
            data = RoutePlanningImportService.precheck(
                request.env,
                raw_bytes,
                filename=filename,
                template_code=payload.get("template_code"),
                template_version=payload.get("template_version"),
            )
        except ValidationError as exc:
            return self._error_response(
                message="预校验失败",
                error_code="IMPORT_PRECHECK_INVALID",
                error_message=str(exc),
                request_id_prefix="req_route_planning_precheck",
            )
        except AccessError as exc:
            return self._error_response(
                message="预校验失败",
                error_code="IMPORT_PERMISSION_DENIED",
                error_message=str(exc),
                request_id_prefix="req_route_planning_precheck",
            )
        except Exception as exc:
            return self._error_response(
                message="预校验失败",
                error_code="IMPORT_INTERNAL_ERROR",
                error_message=str(exc),
                request_id_prefix="req_route_planning_precheck",
            )

        message = "预校验通过"
        if data.get("errors"):
            message = "预校验完成"
        elif data.get("has_review_warning"):
            message = "预校验通过，但存在人工复查提醒"
        return self._success_response(data=data, request_id_prefix="req_route_planning_precheck", message=message)

    @http.route("/api/admin/logistics/imports/waybill-standard/confirm", type="http", auth="user", methods=["POST"], csrf=False)
    def confirm_waybill_standard_import(self, **kwargs):
        payload = self._merged_payload()
        try:
            data = WaybillStandardImportService.confirm_import(
                request.env,
                precheck_token=payload.get("precheck_token"),
                import_batch_no=payload.get("import_batch_no", ""),
                task_no=payload.get("task_no", ""),
            )
        except AccessError as exc:
            return self._error_response(
                message="正式导入失败",
                error_code="IMPORT_PERMISSION_DENIED",
                error_message=str(exc),
                request_id_prefix="req_import_confirm",
            )
        except ValidationError as exc:
            return self._error_response(
                message="正式导入失败",
                error_code=self._resolve_import_confirm_error_code(str(exc)),
                error_message=str(exc),
                request_id_prefix="req_import_confirm",
            )
        except Exception as exc:
            return self._error_response(
                message="正式导入失败",
                error_code="IMPORT_INTERNAL_ERROR",
                error_message=str(exc),
                request_id_prefix="req_import_confirm",
            )
        return self._success_response(data=data, request_id_prefix="req_import_confirm", message="正式导入完成")

    @http.route("/api/admin/logistics/imports/route-planning/confirm", type="http", auth="user", methods=["POST"], csrf=False)
    def confirm_route_planning_import(self, **kwargs):
        payload = self._merged_payload()
        try:
            data = RoutePlanningImportService.confirm_import(
                request.env,
                precheck_token=payload.get("precheck_token"),
                import_batch_no=payload.get("import_batch_no", ""),
                task_no=payload.get("task_no", ""),
            )
        except AccessError as exc:
            return self._error_response(
                message="正式导入失败",
                error_code="IMPORT_PERMISSION_DENIED",
                error_message=str(exc),
                request_id_prefix="req_route_planning_confirm",
            )
        except ValidationError as exc:
            return self._error_response(
                message="正式导入失败",
                error_code=self._resolve_import_confirm_error_code(str(exc)),
                error_message=str(exc),
                request_id_prefix="req_route_planning_confirm",
            )
        except Exception as exc:
            return self._error_response(
                message="正式导入失败",
                error_code="IMPORT_INTERNAL_ERROR",
                error_message=str(exc),
                request_id_prefix="req_route_planning_confirm",
            )
        return self._success_response(
            data=data,
            request_id_prefix="req_route_planning_confirm",
            message="正式导入完成",
        )

    @http.route("/api/admin/logistics/imports/tasks/<string:task_no>", type="http", auth="user", methods=["GET"])
    def get_import_task_result(self, task_no=None, **kwargs):
        payload = self._merged_payload()
        return self._get_import_task_result_response(
            task_no=task_no or payload.get("task_no"),
            import_batch_no=payload.get("import_batch_no"),
        )

    @http.route("/api/admin/logistics/imports/waybill-standard/result", type="http", auth="user", methods=["GET"])
    def get_waybill_import_result(self, **kwargs):
        payload = self._merged_payload()
        return self._get_import_task_result_response(
            task_no=payload.get("task_no"),
            import_batch_no=payload.get("import_batch_no"),
        )

    def _get_import_task_result_response(self, *, task_no=None, import_batch_no=None):
        try:
            task_ref = task_no or import_batch_no or ""
            service = self._get_import_service_by_task_ref(task_ref)
            data = service.get_import_task_result(
                request.env,
                task_no=task_no or "",
                import_batch_no=import_batch_no or "",
            )
        except AccessError as exc:
            return self._error_response(
                message="查询导入结果失败",
                error_code="IMPORT_PERMISSION_DENIED",
                error_message=str(exc),
                request_id_prefix="req_import_task_result",
            )
        except ValidationError as exc:
            return self._error_response(
                message="查询导入结果失败",
                error_code="IMPORT_RESULT_NOT_FOUND",
                error_message=str(exc),
                request_id_prefix="req_import_task_result",
            )
        except Exception as exc:
            return self._error_response(
                message="查询导入结果失败",
                error_code="IMPORT_INTERNAL_ERROR",
                error_message=str(exc),
                request_id_prefix="req_import_task_result",
            )
        return self._success_response(data=data, request_id_prefix="req_import_task_result")

    @http.route("/api/admin/logistics/imports/tasks/<string:task_no>/lines", type="http", auth="user", methods=["GET"])
    def get_import_task_lines(self, task_no=None, **kwargs):
        payload = self._merged_payload()
        try:
            service = self._get_import_service_by_task_ref(task_no or payload.get("task_no") or "")
            data = service.get_import_task_lines(
                request.env,
                task_no=task_no or payload.get("task_no"),
                page=payload.get("page", 1),
                page_size=payload.get("page_size", 20),
                status=payload.get("status", ""),
            )
        except AccessError as exc:
            return self._error_response(
                message="查询导入行结果失败",
                error_code="IMPORT_PERMISSION_DENIED",
                error_message=str(exc),
                request_id_prefix="req_import_task_lines",
            )
        except ValidationError as exc:
            return self._error_response(
                message="查询导入行结果失败",
                error_code="IMPORT_TASK_LINE_NOT_FOUND",
                error_message=str(exc),
                request_id_prefix="req_import_task_lines",
            )
        except Exception as exc:
            return self._error_response(
                message="查询导入行结果失败",
                error_code="IMPORT_INTERNAL_ERROR",
                error_message=str(exc),
                request_id_prefix="req_import_task_lines",
            )
        return self._success_response(data=data, request_id_prefix="req_import_task_lines")

    @http.route("/api/admin/logistics/imports/tasks/<string:task_no>/errors", type="http", auth="user", methods=["GET"])
    def get_import_task_errors(self, task_no=None, **kwargs):
        payload = self._merged_payload()
        try:
            service = self._get_import_service_by_task_ref(task_no or payload.get("task_no") or "")
            data = service.get_import_task_errors(
                request.env,
                task_no=task_no or payload.get("task_no"),
                page=payload.get("page", 1),
                page_size=payload.get("page_size", 50),
            )
        except AccessError as exc:
            return self._error_response(
                message="查询导入错误明细失败",
                error_code="IMPORT_PERMISSION_DENIED",
                error_message=str(exc),
                request_id_prefix="req_import_task_errors",
            )
        except ValidationError as exc:
            return self._error_response(
                message="查询导入错误明细失败",
                error_code="IMPORT_TASK_ERROR_NOT_FOUND",
                error_message=str(exc),
                request_id_prefix="req_import_task_errors",
            )
        except Exception as exc:
            return self._error_response(
                message="查询导入错误明细失败",
                error_code="IMPORT_INTERNAL_ERROR",
                error_message=str(exc),
                request_id_prefix="req_import_task_errors",
            )
        return self._success_response(data=data, request_id_prefix="req_import_task_errors")

    @http.route("/api/admin/logistics/imports/tasks/<string:task_no>/error-report", type="http", auth="user", methods=["GET"])
    def download_import_task_error_report(self, task_no=None, **kwargs):
        payload = self._merged_payload()
        return self._download_import_error_report_response(
            task_no=task_no or payload.get("task_no"),
            import_batch_no=payload.get("import_batch_no", ""),
            precheck_token=payload.get("precheck_token", ""),
        )

    @http.route("/api/admin/logistics/imports/waybill-standard/error-report", type="http", auth="user", methods=["GET"])
    def download_waybill_import_error_report(self, **kwargs):
        payload = self._merged_payload()
        return self._download_import_error_report_response(
            task_no=payload.get("task_no"),
            import_batch_no=payload.get("import_batch_no", ""),
            precheck_token=payload.get("precheck_token", ""),
        )

    def _download_import_error_report_response(self, *, task_no=None, import_batch_no="", precheck_token=""):
        try:
            task_ref = task_no or import_batch_no or ""
            service = self._get_import_service_by_task_ref(task_ref)
            report = service.build_import_task_error_report(
                request.env,
                task_no=task_no or "",
                import_batch_no=import_batch_no,
                precheck_token=precheck_token,
            )
        except AccessError as exc:
            return self._error_response(
                message="下载错误报告失败",
                error_code="IMPORT_PERMISSION_DENIED",
                error_message=str(exc),
                request_id_prefix="req_import_task_error_report",
            )
        except ValidationError as exc:
            return self._error_response(
                message="下载错误报告失败",
                error_code="ERROR_REPORT_NOT_FOUND",
                error_message=str(exc),
                request_id_prefix="req_import_task_error_report",
            )
        except Exception as exc:
            return self._error_response(
                message="下载错误报告失败",
                error_code="IMPORT_INTERNAL_ERROR",
                error_message=str(exc),
                request_id_prefix="req_import_task_error_report",
            )

        headers = [
            ("Content-Type", report["content_type"]),
            ("Content-Disposition", content_disposition(report["file_name"])),
        ]
        return request.make_response(report["file_bytes"], headers=headers)

    def _success_response(self, *, data, request_id_prefix, message="成功", status=200):
        return self._json_response(
            {
                "code": 0,
                "message": message,
                "data": data,
                "request_id": self._build_request_id(request_id_prefix),
            },
            status=status,
        )

    def _error_response(self, *, message, error_code, error_message, request_id_prefix, status=400):
        top_level_code = self._resolve_top_level_code(error_code, error_message)
        return self._json_response(
            {
                "code": top_level_code,
                "message": message,
                "data": {"errors": [{"error_code": error_code, "error_message": error_message}]},
                "request_id": self._build_request_id(request_id_prefix),
            },
            status=self.TOP_LEVEL_HTTP_STATUS.get(top_level_code, status),
        )

    def _resolve_top_level_code(self, error_code, error_message=""):
        code = (error_code or "").strip().upper()
        message = (error_message or "").strip()
        if code in {"IMPORT_PERMISSION_DENIED"} or "PERMISSION" in code or "FORBIDDEN" in code:
            return 4003
        if any(fragment in code for fragment in ("STATE", "STATUS", "EXPIRED", "NOT_READY", "NOT_FINISHED", "CONFLICT")):
            return 4090
        if any(fragment in code for fragment in ("NOT_FOUND", "REPORT_NOT_FOUND")):
            return 4004
        if any(fragment in code for fragment in ("INVALID", "EMPTY", "PARSE_FAILED", "TEMPLATE")):
            return 4001

        if any(fragment in message for fragment in ("无权", "禁止", "forbidden")):
            return 4003
        if any(fragment in message for fragment in ("失效", "不允许", "未通过", "正在执行", "已存在", "稍后刷新")):
            return 4090
        if any(fragment in message for fragment in ("未找到", "不存在")):
            return 4004
        if any(fragment in message for fragment in ("请提供", "非法", "无效", "模板", "Base64")):
            return 4001
        return 5000

    def _resolve_import_confirm_error_code(self, error_message):
        message = (error_message or "").strip()
        if any(fragment in message for fragment in ("失效", "不允许", "未通过", "正在执行", "已存在")):
            return "IMPORT_CONFIRM_STATUS_INVALID"
        if any(fragment in message for fragment in ("未找到", "不存在")):
            return "IMPORT_CONFIRM_NOT_FOUND"
        if any(fragment in message for fragment in ("请提供", "非法", "无效")):
            return "IMPORT_CONFIRM_INVALID"
        return "IMPORT_CONFIRM_FAILED"

    def _merged_payload(self):
        payload = dict(request.params)
        if request.httprequest.mimetype == "application/json":
            json_payload = request.httprequest.get_json(silent=True) or {}
            if isinstance(json_payload, dict):
                payload.update({key: value for key, value in json_payload.items() if value is not None})
        return payload

    def _get_import_service_by_task_ref(self, task_ref):
        task = WaybillStandardImportService._get_task_by_task_no(request.env, task_ref)
        if not task:
            return WaybillStandardImportService
        return self.IMPORT_SERVICE_BY_OBJECT_TYPE.get(task.object_type, WaybillStandardImportService)

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
