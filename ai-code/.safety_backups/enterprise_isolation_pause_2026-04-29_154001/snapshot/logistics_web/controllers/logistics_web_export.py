import json
import uuid

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import Response, content_disposition, request

from ..services.customer_profile_export_service import CustomerProfileExportService
from ..services.dispatch_main_export_service import DispatchMainExportService, ExportServiceError
from ..services.driver_route_excel_export_service import DriverRouteExcelExportService
from ..services.evidence_image_export_service import EvidenceImageExportService
from ..services.product_profile_export_service import ProductProfileExportService


class LogisticsWebExportController(http.Controller):
    EXPORT_SERVICE_MAP = {
        DispatchMainExportService.OBJECT_TYPE: DispatchMainExportService,
        CustomerProfileExportService.OBJECT_TYPE: CustomerProfileExportService,
        ProductProfileExportService.OBJECT_TYPE: ProductProfileExportService,
        EvidenceImageExportService.OBJECT_TYPE: EvidenceImageExportService,
    }
    TOP_LEVEL_HTTP_STATUS = {
        4001: 400,
        4003: 403,
        4004: 404,
        4090: 409,
        5000: 500,
    }

    @http.route(
        "/api/admin/logistics/exports/driver-route-excel/direct-download",
        type="http",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def download_driver_route_excel(self, **kwargs):
        payload = self._merged_payload()
        try:
            export_file = DriverRouteExcelExportService.export_by_delivery_date(
                request.env,
                delivery_date=payload.get("delivery_date") or "",
                file_locale=payload.get("file_locale") or "zh_CN",
            )
        except ValidationError as exc:
            return self._error_response(
                message="司机侧Excel导出失败",
                error_code=self._resolve_error_code(exc, "DRIVER_ROUTE_EXPORT_FAILED"),
                error_message=str(exc),
                request_id_prefix="req_driver_route_excel_export",
            )
        headers = [
            ("Content-Type", export_file["content_type"]),
            ("Content-Disposition", content_disposition(export_file["file_name"])),
        ]
        return request.make_response(export_file["file_bytes"], headers=headers)

    @http.route("/api/admin/logistics/exports/waybill", type="http", auth="user", methods=["POST"], csrf=False)
    def export_waybill(self, **kwargs):
        payload = self._merged_payload()
        selected_ids = self._load_list_payload(payload.get("selected_ids"))
        scope_snapshot = self._load_json_value(payload.get("scope_snapshot"))
        try:
            created = DispatchMainExportService.create_waybill_export_task(
                request.env,
                selected_ids=selected_ids,
                source_page=payload.get("from_page") or payload.get("source_page") or "",
                scope_snapshot=scope_snapshot,
                request_payload=payload,
                object_type=payload.get("object_type") or DispatchMainExportService.OBJECT_TYPE,
                entry_type=payload.get("entry_type") or DispatchMainExportService.ENTRY_TYPE,
                export_mode=payload.get("export_mode") or DispatchMainExportService.EXPORT_MODE,
                package_structure=payload.get("package_structure") or DispatchMainExportService.PACKAGE_STRUCTURE,
            )
            data = DispatchMainExportService.run_waybill_export_task(request.env, task_no=created["task_no"])
        except ValidationError as exc:
            return self._error_response(
                message="导出失败",
                error_code=self._resolve_error_code(exc, "EXPORT_TASK_CREATE_FAILED"),
                error_message=str(exc),
                request_id_prefix="req_export_waybill",
            )
        return self._json_response(
            {
                "code": 0,
                "message": self._build_export_success_message(data),
                "data": data,
                "request_id": self._build_request_id("req_export_waybill"),
            }
        )

    @http.route("/api/admin/logistics/exports/evidence-images", type="http", auth="user", methods=["POST"], csrf=False)
    def export_evidence_images(self, **kwargs):
        payload = self._merged_payload()
        selected_ids = self._load_list_payload(payload.get("selected_ids"))
        scope_snapshot = self._load_json_value(payload.get("scope_snapshot"))
        try:
            created = EvidenceImageExportService.create_waybill_export_task(
                request.env,
                selected_ids=selected_ids,
                source_page=payload.get("from_page") or payload.get("source_page") or "",
                scope_snapshot=scope_snapshot,
                request_payload=payload,
                object_type=payload.get("object_type") or EvidenceImageExportService.OBJECT_TYPE,
                entry_type=payload.get("entry_type") or EvidenceImageExportService.ENTRY_TYPE,
                export_mode=payload.get("export_mode") or EvidenceImageExportService.EXPORT_MODE,
                package_structure=payload.get("package_structure") or EvidenceImageExportService.PACKAGE_STRUCTURE,
            )
            data = EvidenceImageExportService.run_waybill_export_task(request.env, task_no=created["task_no"])
        except ValidationError as exc:
            return self._error_response(
                message="Evidence image export failed",
                error_code=self._resolve_error_code(exc, "EXPORT_TASK_CREATE_FAILED"),
                error_message=str(exc),
                request_id_prefix="req_export_evidence_images",
            )
        return self._json_response(
            {
                "code": 0,
                "message": self._build_export_success_message(data),
                "data": data,
                "request_id": self._build_request_id("req_export_evidence_images"),
            }
        )

    @http.route("/api/admin/logistics/exports/customer-profile", type="http", auth="user", methods=["POST"], csrf=False)
    def export_customer_profile(self, **kwargs):
        payload = self._merged_payload()
        selected_ids = self._load_list_payload(payload.get("selected_ids"))
        scope_snapshot = self._load_json_value(payload.get("scope_snapshot"))
        try:
            created = CustomerProfileExportService.create_customer_profile_export_task(
                request.env,
                selected_ids=selected_ids,
                source_page=payload.get("from_page") or payload.get("source_page") or "",
                scope_snapshot=scope_snapshot,
                request_payload=payload,
                object_type=payload.get("object_type") or CustomerProfileExportService.OBJECT_TYPE,
                entry_type=payload.get("entry_type") or CustomerProfileExportService.ENTRY_TYPE,
                export_mode=payload.get("export_mode") or CustomerProfileExportService.EXPORT_MODE,
                package_structure=payload.get("package_structure") or CustomerProfileExportService.PACKAGE_STRUCTURE,
            )
            data = CustomerProfileExportService.run_customer_profile_export_task(request.env, task_no=created["task_no"])
        except ValidationError as exc:
            return self._error_response(
                message="客户画像导出失败",
                error_code=self._resolve_error_code(exc, "EXPORT_TASK_CREATE_FAILED"),
                error_message=str(exc),
                request_id_prefix="req_export_customer_profile",
            )
        return self._json_response(
            {
                "code": 0,
                "message": self._build_export_success_message(data),
                "data": data,
                "request_id": self._build_request_id("req_export_customer_profile"),
            }
        )

    @http.route("/api/admin/logistics/exports/product-profile", type="http", auth="user", methods=["POST"], csrf=False)
    def export_product_profile(self, **kwargs):
        payload = self._merged_payload()
        selected_ids = self._load_list_payload(payload.get("selected_ids"))
        scope_snapshot = self._load_json_value(payload.get("scope_snapshot"))
        try:
            created = ProductProfileExportService.create_product_profile_export_task(
                request.env,
                selected_ids=selected_ids,
                source_page=payload.get("from_page") or payload.get("source_page") or "",
                scope_snapshot=scope_snapshot,
                request_payload=payload,
                object_type=payload.get("object_type") or ProductProfileExportService.OBJECT_TYPE,
                entry_type=payload.get("entry_type") or ProductProfileExportService.ENTRY_TYPE,
                export_mode=payload.get("export_mode") or ProductProfileExportService.EXPORT_MODE,
                package_structure=payload.get("package_structure") or ProductProfileExportService.PACKAGE_STRUCTURE,
            )
            data = ProductProfileExportService.run_product_profile_export_task(request.env, task_no=created["task_no"])
        except ValidationError as exc:
            return self._error_response(
                message="货物画像导出失败",
                error_code=self._resolve_error_code(exc, "EXPORT_TASK_CREATE_FAILED"),
                error_message=str(exc),
                request_id_prefix="req_export_product_profile",
            )
        return self._json_response(
            {
                "code": 0,
                "message": self._build_export_success_message(data),
                "data": data,
                "request_id": self._build_request_id("req_export_product_profile"),
            }
        )

    @http.route("/api/admin/logistics/exports/tasks/<string:task_no>", type="http", auth="user", methods=["GET"])
    def get_export_task_result(self, task_no=None, **kwargs):
        payload = self._merged_payload()
        try:
            export_service = self._resolve_task_service(task_no or payload.get("task_no") or "")
            data = export_service.get_export_task_result(
                request.env,
                task_no=task_no or payload.get("task_no") or "",
            )
        except ValidationError as exc:
            return self._error_response(
                message="查询导出结果失败",
                error_code=self._resolve_error_code(exc, "EXPORT_TASK_NOT_FOUND"),
                error_message=str(exc),
                request_id_prefix="req_export_task_result",
            )
        return self._json_response(
            {
                "code": 0,
                "message": "成功",
                "data": data,
                "request_id": self._build_request_id("req_export_task_result"),
            }
        )

    @http.route("/api/admin/logistics/exports/tasks/<string:task_no>/lines", type="http", auth="user", methods=["GET"])
    def get_export_task_lines(self, task_no=None, **kwargs):
        payload = self._merged_payload()
        try:
            export_service = self._resolve_task_service(task_no or payload.get("task_no") or "")
            data = export_service.get_export_task_lines(
                request.env,
                task_no=task_no or payload.get("task_no") or "",
                page=payload.get("page", 1),
                page_size=payload.get("page_size", 20),
                status=payload.get("status", ""),
            )
        except ValidationError as exc:
            return self._error_response(
                message="查询导出行结果失败",
                error_code=self._resolve_error_code(exc, "EXPORT_TASK_LINE_NOT_FOUND"),
                error_message=str(exc),
                request_id_prefix="req_export_task_lines",
            )
        return self._json_response(
            {
                "code": 0,
                "message": "成功",
                "data": data,
                "request_id": self._build_request_id("req_export_task_lines"),
            }
        )

    @http.route("/api/admin/logistics/exports/tasks/<string:task_no>/errors", type="http", auth="user", methods=["GET"])
    def get_export_task_errors(self, task_no=None, **kwargs):
        payload = self._merged_payload()
        try:
            export_service = self._resolve_task_service(task_no or payload.get("task_no") or "")
            data = export_service.get_export_task_errors(
                request.env,
                task_no=task_no or payload.get("task_no") or "",
                page=payload.get("page", 1),
                page_size=payload.get("page_size", 20),
            )
        except ValidationError as exc:
            return self._error_response(
                message="查询导出错误明细失败",
                error_code=self._resolve_error_code(exc, "EXPORT_TASK_ERROR_NOT_FOUND"),
                error_message=str(exc),
                request_id_prefix="req_export_task_errors",
            )
        return self._json_response(
            {
                "code": 0,
                "message": "成功",
                "data": data,
                "request_id": self._build_request_id("req_export_task_errors"),
            }
        )

    @http.route("/api/admin/logistics/exports/tasks/<string:task_no>/error-report", type="http", auth="user", methods=["GET"])
    def download_export_task_error_report(self, task_no=None, **kwargs):
        payload = self._merged_payload()
        try:
            export_service = self._resolve_task_service(task_no or payload.get("task_no") or "")
            report = export_service.build_export_task_error_report(
                request.env,
                task_no=task_no or payload.get("task_no") or "",
            )
        except ValidationError as exc:
            return self._error_response(
                message="下载导出错误报告失败",
                error_code=self._resolve_error_code(exc, "EXPORT_OUTPUT_FILE_NOT_READY"),
                error_message=str(exc),
                request_id_prefix="req_export_task_error_report",
            )
        headers = [
            ("Content-Type", report["content_type"]),
            ("Content-Disposition", content_disposition(report["file_name"])),
        ]
        return request.make_response(report["file_bytes"], headers=headers)

    @http.route("/api/admin/logistics/exports/tasks/<string:task_no>/download", type="http", auth="user", methods=["GET"])
    def download_export_task_file(self, task_no=None, **kwargs):
        payload = self._merged_payload()
        try:
            export_service = self._resolve_task_service(task_no or payload.get("task_no") or "")
            export_file = export_service.get_export_download_file(
                request.env,
                task_no=task_no or payload.get("task_no") or "",
            )
        except ValidationError as exc:
            return self._error_response(
                message="下载导出文件失败",
                error_code=self._resolve_error_code(exc, "EXPORT_OUTPUT_FILE_NOT_READY"),
                error_message=str(exc),
                request_id_prefix="req_export_task_download",
            )
        headers = [
            ("Content-Type", export_file["content_type"]),
            ("Content-Disposition", content_disposition(export_file["file_name"])),
        ]
        return request.make_response(export_file["file_bytes"], headers=headers)

    def _merged_payload(self):
        payload = dict(request.params)
        if request.httprequest.mimetype == "application/json":
            json_payload = request.httprequest.get_json(silent=True) or {}
            if isinstance(json_payload, dict):
                payload.update({key: value for key, value in json_payload.items() if value is not None})
        return payload

    def _load_json_value(self, value):
        if value in (None, "", False):
            return False
        if isinstance(value, (dict, list)):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except ValueError:
                return value
        return value

    def _load_list_payload(self, value):
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return []
            if stripped.startswith("["):
                parsed = self._load_json_value(stripped)
                return parsed if isinstance(parsed, list) else []
            return [item.strip() for item in stripped.split(",") if item.strip()]
        return []

    def _error_response(self, *, message, error_code, error_message, request_id_prefix, status=400):
        top_level_code = self._resolve_top_level_code(error_code)
        return self._json_response(
            {
                "code": top_level_code,
                "message": message,
                "data": {"errors": [{"error_code": error_code, "error_message": error_message}]},
                "request_id": self._build_request_id(request_id_prefix),
            },
            status=self.TOP_LEVEL_HTTP_STATUS.get(top_level_code, status),
        )

    def _resolve_error_code(self, exc, default_code):
        return getattr(exc, "error_code", default_code)

    def _resolve_top_level_code(self, error_code):
        code = (error_code or "").strip().upper()
        if not code:
            return 5000
        if code in {"EXPORT_PERMISSION_DENIED", "EXPORT_OUTPUT_FILE_INVALID"} or "PERMISSION" in code:
            return 4003
        if any(fragment in code for fragment in ("STATE", "STATUS", "EXPIRED", "NOT_READY", "NOT_FINISHED")):
            return 4090
        if any(fragment in code for fragment in ("NOT_FOUND", "MISSING")):
            return 4004
        if any(fragment in code for fragment in ("INVALID", "EMPTY")):
            return 4001
        return 5000

    def _build_export_success_message(self, data):
        status = (data or {}).get("status")
        if status == "success":
            return "导出完成"
        if status == "partial_failed":
            return "导出完成，部分失败"
        if status == "failed":
            return "导出失败"
        return "导出任务已创建"

    def _json_response(self, payload, *, status=200):
        return Response(
            json.dumps(payload, ensure_ascii=False),
            status=status,
            headers=[("Content-Type", "application/json; charset=utf-8")],
        )

    def _build_request_id(self, prefix):
        return f"{prefix}_{uuid.uuid4().hex[:12]}"

    def _resolve_task_service(self, task_no):
        task_ref = (task_no or "").strip()
        if not task_ref:
            raise ExportServiceError("EXPORT_TASK_NOT_FOUND", "task_no is required.")
        task = request.env["logistics.export.task"].sudo().search([("task_no", "=", task_ref)], limit=1)
        if not task:
            raise ExportServiceError("EXPORT_TASK_NOT_FOUND", f"Task {task_ref} was not found.")
        export_service = self.EXPORT_SERVICE_MAP.get(task.object_type)
        if not export_service:
            raise ExportServiceError(
                "EXPORT_TASK_OBJECT_TYPE_INVALID",
                f"Unsupported export task object_type: {task.object_type}",
            )
        return export_service
