import csv
import hashlib
import io
import json
from datetime import timedelta
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font

from odoo import fields
from odoo.exceptions import AccessError, ValidationError

from .waybill_standard_import_service_v2 import WaybillStandardImportService


class ExportServiceError(ValidationError):
    def __init__(self, error_code, message):
        self.error_code = error_code
        super().__init__(message)


class DispatchMainExportService:
    OBJECT_TYPE = "dispatch_main"
    ENTRY_TYPE = "from_waybill"
    EXPORT_MODE = "standard_xlsx"
    PACKAGE_STRUCTURE = "dispatch_main_four_sheet"
    SOURCE_MODEL = "logistics.dispatch.waybill"
    SOURCE_PAGE_DEFAULT = "waybill_list"
    TARGET_OBJECT_TYPE = "waybill"
    DOWNLOAD_EXPIRE_DAYS = 7
    DOWNLOAD_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    EXPORT_ROOT_DIR = Path(__file__).resolve().parents[3] / ".odoo_data" / "export_tasks"
    SHEETS = WaybillStandardImportService.SHEETS
    FIELD_LABELS = WaybillStandardImportService.FIELD_LABELS

    @classmethod
    def create_waybill_export_task(
        cls,
        env,
        *,
        selected_ids,
        source_page="",
        scope_snapshot=None,
        request_payload=None,
        object_type=OBJECT_TYPE,
        entry_type=ENTRY_TYPE,
        export_mode=EXPORT_MODE,
        package_structure=PACKAGE_STRUCTURE,
        source_model=SOURCE_MODEL,
    ):
        cls._check_export_model_access(env, mode="create")
        cls._validate_create_contract(
            object_type=object_type,
            entry_type=entry_type,
            export_mode=export_mode,
            package_structure=package_structure,
            source_model=source_model,
        )
        normalized_ids = cls._normalize_selected_ids(selected_ids)
        waybills = cls._get_waybills_for_scope(env, normalized_ids)

        scope_vals = {
            "object_type": object_type,
            "entry_type": entry_type,
            "source_model": source_model,
            "source_page": (source_page or cls.SOURCE_PAGE_DEFAULT).strip() or cls.SOURCE_PAGE_DEFAULT,
            "selected_ids_json": normalized_ids,
            "selected_count": len(normalized_ids),
            "scope_snapshot_json": scope_snapshot or cls._build_scope_snapshot(waybills),
            "request_payload_json": request_payload
            or {
                "object_type": object_type,
                "entry_type": entry_type,
                "export_mode": export_mode,
                "package_structure": package_structure,
                "selected_ids": normalized_ids,
            },
            "operator_id": env.user.id,
        }
        scope = env["logistics.export.source.scope"].sudo().create(scope_vals)
        task = env["logistics.export.task"].sudo().create(
            {
                "object_type": object_type,
                "entry_type": entry_type,
                "export_mode": export_mode,
                "package_structure": package_structure,
                "source_scope_id": scope.id,
                "status": "pending",
                "total_count": len(normalized_ids),
                "operator_id": env.user.id,
                "summary_message": f"Export task created, waiting to run. Total {len(normalized_ids)} waybills.",
            }
        )
        line_vals_list = []
        for index, waybill in enumerate(waybills, start=1):
            line_vals_list.append(
                {
                    "task_id": task.id,
                    "line_no": index,
                    "target_object_type": cls.TARGET_OBJECT_TYPE,
                    "target_res_model": cls.SOURCE_MODEL,
                    "target_res_id": waybill.id,
                    "business_key": waybill.name or str(waybill.id),
                    "display_name": f"Waybill {waybill.name or waybill.id}",
                    "status": "pending",
                }
            )
        if line_vals_list:
            env["logistics.export.task.line"].sudo().create(line_vals_list)
        return cls._build_created_task_payload(task.sudo())

    @classmethod
    def run_waybill_export_task(cls, env, *, task_no="", task=None):
        task = cls._get_task(env, task_no=task_no, task=task)
        cls._ensure_task_access(env, task)
        cls._mark_task_expired_if_needed(task)
        if task.status in ("success", "partial_failed", "failed", "cancelled", "expired"):
            return cls._build_task_result_payload(task.sudo())
        if task.status != "pending":
            raise ExportServiceError("EXPORT_TASK_STATUS_INVALID", f"Task {task.task_no} cannot run in status {task.status}.")

        task.sudo().write(
            {
                "status": "running",
                "started_at": fields.Datetime.now(),
                "summary_message": f"Export task {task.task_no} is running.",
                "failure_error_code": False,
                "failure_reason": False,
            }
        )
        try:
            waybill_rows = []
            customer_rows = []
            order_rows = []
            goods_rows = []
            error_vals_list = []
            success_count = 0
            fail_count = 0
            skipped_count = 0
            exported_waybill_count = 0
            exported_customer_line_count = 0
            exported_order_line_count = 0
            exported_goods_line_count = 0

            for task_line in task.sudo().task_line_ids.sorted(key=lambda rec: (rec.line_no, rec.id)):
                try:
                    package = cls._collect_waybill_package(env, task_line)
                    task_line.sudo().write(
                        {
                            "status": "success",
                            "message": cls._build_task_line_message(package),
                            "exported_waybill_count": package["exported_waybill_count"],
                            "exported_customer_line_count": package["exported_customer_line_count"],
                            "exported_order_line_count": package["exported_order_line_count"],
                            "exported_goods_line_count": package["exported_goods_line_count"],
                        }
                    )
                    waybill_rows.extend(package["waybill_rows"])
                    customer_rows.extend(package["customer_rows"])
                    order_rows.extend(package["order_rows"])
                    goods_rows.extend(package["goods_rows"])
                    success_count += 1
                    exported_waybill_count += package["exported_waybill_count"]
                    exported_customer_line_count += package["exported_customer_line_count"]
                    exported_order_line_count += package["exported_order_line_count"]
                    exported_goods_line_count += package["exported_goods_line_count"]
                except ExportServiceError as error:
                    is_skipped = error.error_code == "EXPORT_TARGET_NO_DOWNSTREAM_DATA"
                    task_line.sudo().write(
                        {
                            "status": "skipped" if is_skipped else "failed",
                            "message": str(error),
                            "exported_waybill_count": 0,
                            "exported_customer_line_count": 0,
                            "exported_order_line_count": 0,
                            "exported_goods_line_count": 0,
                        }
                    )
                    if is_skipped:
                        skipped_count += 1
                    else:
                        fail_count += 1
                    error_vals_list.append(
                        cls._build_error_line_vals(
                            task=task,
                            task_line=task_line,
                            error_code=error.error_code,
                            error_message=str(error),
                            error_stage=cls._error_stage_for_code(error.error_code),
                            field_name="selected_ids",
                            raw_value=task_line.business_key,
                        )
                    )
                except Exception as error:
                    message = f"Unexpected export error: {error}"
                    task_line.sudo().write(
                        {
                            "status": "failed",
                            "message": message,
                            "exported_waybill_count": 0,
                            "exported_customer_line_count": 0,
                            "exported_order_line_count": 0,
                            "exported_goods_line_count": 0,
                        }
                    )
                    fail_count += 1
                    error_vals_list.append(
                        cls._build_error_line_vals(
                            task=task,
                            task_line=task_line,
                            error_code="EXPORT_WORKBOOK_BUILD_FAILED",
                            error_message=message,
                            error_stage="workbook_build",
                            field_name="selected_ids",
                            raw_value=task_line.business_key,
                        )
                    )

            task_level_error_code = False
            task_level_error_message = False
            output_file_vals = {}
            if success_count:
                try:
                    workbook_bytes = cls._build_workbook_bytes(
                        {
                            "waybill_rows": waybill_rows,
                            "customer_line_rows": customer_rows,
                            "order_line_rows": order_rows,
                            "goods_line_rows": goods_rows,
                        }
                    )
                    output_file_vals = cls._store_output_file(task, workbook_bytes)
                except ExportServiceError as error:
                    task_level_error_code = error.error_code
                    task_level_error_message = str(error)
                    error_vals_list.append(
                        cls._build_error_line_vals(
                            task=task,
                            task_line=False,
                            error_code=error.error_code,
                            error_message=str(error),
                            error_stage=cls._error_stage_for_code(error.error_code),
                            field_name="output_file",
                            raw_value=task.task_no,
                        )
                    )

            if error_vals_list:
                env["logistics.export.error.line"].sudo().create(error_vals_list)

            final_status = cls._compute_task_status(
                success_count=success_count,
                fail_count=fail_count,
                skipped_count=skipped_count,
                task_level_error_code=task_level_error_code,
            )
            now = fields.Datetime.now()
            task_write_vals = {
                "status": final_status,
                "success_count": success_count,
                "fail_count": fail_count,
                "skipped_count": skipped_count,
                "exported_waybill_count": exported_waybill_count,
                "exported_customer_line_count": exported_customer_line_count,
                "exported_order_line_count": exported_order_line_count,
                "exported_goods_line_count": exported_goods_line_count,
                "finished_at": now,
                "summary_message": cls._build_summary_message(
                    success_count=success_count,
                    fail_count=fail_count,
                    skipped_count=skipped_count,
                    task_level_error_message=task_level_error_message,
                ),
                "failure_error_code": task_level_error_code or False,
                "failure_reason": task_level_error_message or False,
            }
            task_write_vals.update(output_file_vals)
            task.sudo().write(task_write_vals)
            return cls._build_task_result_payload(task.sudo())
        except Exception as error:
            error_code = error.error_code if isinstance(error, ExportServiceError) else "EXPORT_TASK_RUN_ABORTED"
            error_message = str(error)
            cls._mark_task_failed_if_running(task, error_code=error_code, error_message=error_message)
            if isinstance(error, ExportServiceError):
                raise
            raise ExportServiceError(error_code, error_message) from error

    @classmethod
    def get_export_task_result(cls, env, *, task_no):
        task = cls._get_task(env, task_no=task_no)
        cls._ensure_task_access(env, task)
        cls._mark_task_expired_if_needed(task)
        return cls._build_task_result_payload(task.sudo())

    @classmethod
    def get_export_task_lines(cls, env, *, task_no, page=1, page_size=20, status=""):
        task = cls._get_task(env, task_no=task_no)
        cls._ensure_task_access(env, task)
        page, page_size = cls._normalize_pagination(page=page, page_size=page_size, default_size=20, max_size=200)
        task_lines = task.sudo().task_line_ids.sorted(key=lambda rec: (rec.line_no, rec.id))
        status_filter = (status or "").strip()
        if status_filter:
            task_lines = task_lines.filtered(lambda rec: rec.status == status_filter)
        total = len(task_lines)
        total_pages = max((total + page_size - 1) // page_size, 1)
        page = min(page, total_pages)
        offset = (page - 1) * page_size
        items = task_lines[offset : offset + page_size]
        showing_from = offset + 1 if total else 0
        showing_to = offset + len(items) if total else 0
        return {
            "task_no": task.task_no,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "showing_from": showing_from,
            "showing_to": showing_to,
            "status_filter": status_filter or "all",
            "status_filter_label": cls._status_filter_label(status_filter),
            "items": [cls._build_task_line_payload(task_line) for task_line in items],
        }

    @classmethod
    def get_export_task_errors(cls, env, *, task_no, page=1, page_size=20):
        task = cls._get_task(env, task_no=task_no)
        cls._ensure_task_access(env, task)
        page, page_size = cls._normalize_pagination(page=page, page_size=page_size, default_size=20, max_size=200)
        errors = task.sudo().error_line_ids.sorted(key=lambda rec: ((rec.task_line_id.line_no or 0), rec.id))
        total = len(errors)
        total_pages = max((total + page_size - 1) // page_size, 1)
        page = min(page, total_pages)
        offset = (page - 1) * page_size
        items = errors[offset : offset + page_size]
        showing_from = offset + 1 if total else 0
        showing_to = offset + len(items) if total else 0
        return {
            "task_no": task.task_no,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "showing_from": showing_from,
            "showing_to": showing_to,
            "items": [cls._build_error_payload(error) for error in items],
        }

    @classmethod
    def build_export_task_error_report(cls, env, *, task_no):
        task = cls._get_task(env, task_no=task_no)
        cls._ensure_task_access(env, task)
        errors = task.sudo().error_line_ids.sorted(key=lambda rec: ((rec.task_line_id.line_no or 0), rec.id))
        if not errors:
            raise ExportServiceError("EXPORT_OUTPUT_FILE_NOT_READY", f"Task {task.task_no} has no error report.")
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            [
                "task_no",
                "line_no",
                "business_key",
                "error_stage",
                "field_name",
                "raw_value",
                "mapped_value",
                "error_code",
                "error_message",
            ]
        )
        for error in errors:
            writer.writerow(
                [
                    task.task_no,
                    error.task_line_id.line_no if error.task_line_id else "",
                    error.task_line_id.business_key if error.task_line_id else "",
                    error.error_stage,
                    error.field_name,
                    error.raw_value or "",
                    error.mapped_value or "",
                    error.error_code,
                    error.error_message,
                ]
            )
        return {
            "file_name": f"{task.task_no}-error-report.csv",
            "file_bytes": buffer.getvalue().encode("utf-8-sig"),
            "content_type": "text/csv; charset=utf-8",
        }

    @classmethod
    def get_export_download_file(cls, env, *, task_no):
        task = cls._get_task(env, task_no=task_no)
        cls._ensure_task_access(env, task)
        cls._mark_task_expired_if_needed(task)
        if task.status == "expired":
            raise ExportServiceError("EXPORT_TASK_EXPIRED", f"Task {task.task_no} has expired.")
        if task.status not in ("success", "partial_failed"):
            raise ExportServiceError("EXPORT_TASK_NOT_FINISHED", f"Task {task.task_no} is not ready to download.")
        storage_path = (task.output_storage_path or "").strip()
        if not storage_path:
            raise ExportServiceError("EXPORT_OUTPUT_FILE_NOT_READY", f"Task {task.task_no} has no output file.")
        file_path = cls._resolve_output_storage_path(storage_path)
        if not file_path.exists():
            raise ExportServiceError("EXPORT_OUTPUT_FILE_MISSING", f"Output file for task {task.task_no} is missing.")
        try:
            file_bytes = file_path.read_bytes()
        except OSError as error:
            raise ExportServiceError("EXPORT_FILE_READ_FAILED", f"Failed to read export file: {error}") from error
        return {
            "file_name": task.output_file_name or f"{task.task_no}.xlsx",
            "file_bytes": file_bytes,
            "content_type": cls.DOWNLOAD_CONTENT_TYPE,
        }

    @classmethod
    def _check_export_model_access(cls, env, *, mode):
        cls._ensure_export_operator_access(env)
        try:
            env["logistics.export.source.scope"].check_access(mode)
            env["logistics.export.task"].check_access(mode)
        except AccessError as error:
            raise ExportServiceError(
                "EXPORT_PERMISSION_DENIED",
                "You do not have permission to create or manage logistics export tasks.",
            ) from error

    @classmethod
    def _ensure_export_operator_access(cls, env):
        if env.user.has_group("logistics_dispatch.group_logistics_export_user"):
            return
        raise ExportServiceError(
            "EXPORT_PERMISSION_DENIED",
            "You do not have permission to start this logistics export.",
        )

    @classmethod
    def _validate_create_contract(cls, *, object_type, entry_type, export_mode, package_structure, source_model):
        if object_type != cls.OBJECT_TYPE:
            raise ExportServiceError("EXPORT_TASK_OBJECT_TYPE_INVALID", f"Unsupported object_type: {object_type}")
        if entry_type != cls.ENTRY_TYPE:
            raise ExportServiceError("EXPORT_TASK_ENTRY_TYPE_INVALID", f"Unsupported entry_type: {entry_type}")
        if export_mode != cls.EXPORT_MODE:
            raise ExportServiceError("EXPORT_MODE_INVALID", f"Unsupported export_mode: {export_mode}")
        if package_structure != cls.PACKAGE_STRUCTURE:
            raise ExportServiceError("EXPORT_MODE_INVALID", f"Unsupported package_structure: {package_structure}")
        if source_model != cls.SOURCE_MODEL:
            raise ExportServiceError("EXPORT_SCOPE_SNAPSHOT_INVALID", f"Unsupported source_model: {source_model}")

    @classmethod
    def _normalize_selected_ids(cls, selected_ids):
        normalized_ids = []
        for value in selected_ids or []:
            if value in (None, "", False):
                continue
            try:
                normalized_value = int(value)
            except (TypeError, ValueError) as error:
                raise ExportServiceError("EXPORT_SCOPE_SNAPSHOT_INVALID", f"Invalid selected id: {value}") from error
            if normalized_value > 0 and normalized_value not in normalized_ids:
                normalized_ids.append(normalized_value)
        if not normalized_ids:
            raise ExportServiceError("EXPORT_SCOPE_EMPTY", "selected_ids cannot be empty.")
        return normalized_ids

    @classmethod
    def _get_waybills_for_scope(cls, env, selected_ids):
        model = env[cls.SOURCE_MODEL]
        model.check_access("read")
        records = model.browse(selected_ids)
        records.check_access("read")
        existing = {record.id: record for record in records.exists()}
        ordered_records = []
        missing_ids = []
        for record_id in selected_ids:
            record = existing.get(record_id)
            if record:
                ordered_records.append(record)
            else:
                missing_ids.append(record_id)
        if missing_ids:
            raise ExportServiceError("EXPORT_WAYBILL_NOT_FOUND", f"Waybill ids not found or not readable: {missing_ids}")
        return model.browse([record.id for record in ordered_records])

    @classmethod
    def _build_scope_snapshot(cls, waybills):
        items = []
        for waybill in waybills:
            items.append(
                {
                    "id": waybill.id,
                    "waybill_no": waybill.name,
                    "batch_no": waybill.batch_id.name or "",
                    "wave_no": waybill.wave_id.name or "",
                }
            )
        return {
            "object_type": cls.OBJECT_TYPE,
            "entry_type": cls.ENTRY_TYPE,
            "selected_count": len(items),
            "items": items,
        }

    @classmethod
    def _get_task(cls, env, *, task_no="", task=None):
        if task:
            return task.sudo()
        task_ref = (task_no or "").strip()
        if not task_ref:
            raise ExportServiceError("EXPORT_TASK_NOT_FOUND", "task_no is required.")
        task = env["logistics.export.task"].sudo().search([("task_no", "=", task_ref)], limit=1)
        if not task:
            raise ExportServiceError("EXPORT_TASK_NOT_FOUND", f"Task {task_ref} was not found.")
        return task

    @classmethod
    def _ensure_task_access(cls, env, task):
        if env.user.has_group("logistics_dispatch.group_logistics_export_manager"):
            return
        if task.operator_id.id != env.user.id:
            raise ExportServiceError("EXPORT_DOWNLOAD_PERMISSION_DENIED", f"You cannot access task {task.task_no}.")

    @classmethod
    def _mark_task_expired_if_needed(cls, task):
        if task.status not in ("success", "partial_failed"):
            return
        if not task.expires_at:
            return
        if task.expires_at < fields.Datetime.now():
            task.sudo().write(
                {
                    "status": "expired",
                    "summary_message": f"Export task {task.task_no} expired.",
                }
            )

    @classmethod
    def _mark_task_failed_if_running(cls, task, *, error_code, error_message):
        if not task or not task.exists():
            return
        if task.status != "running":
            return
        try:
            task.sudo().write(
                {
                    "status": "failed",
                    "finished_at": fields.Datetime.now(),
                    "summary_message": error_message,
                    "failure_error_code": error_code or False,
                    "failure_reason": error_message or False,
                }
            )
        except Exception:
            return

    @classmethod
    def _collect_waybill_package(cls, env, task_line):
        waybill = env[cls.SOURCE_MODEL].browse(task_line.target_res_id).exists()
        if not waybill:
            raise ExportServiceError("EXPORT_WAYBILL_NOT_FOUND", f"Waybill for line {task_line.line_no} was not found.")
        cls._validate_waybill_header(waybill)

        customer_lines = waybill.customer_line_ids.sorted(key=lambda rec: (rec.stop_seq_in_waybill or 0, rec.id))
        order_lines = waybill.order_line_ids.sorted(key=lambda rec: (rec.customer_line_id.stop_seq_in_waybill or 0, rec.id))
        goods_lines = waybill.goods_line_ids.sorted(key=lambda rec: (rec.customer_line_id.stop_seq_in_waybill or 0, rec.id))

        if not customer_lines and not order_lines and not goods_lines:
            raise ExportServiceError(
                "EXPORT_TARGET_NO_DOWNSTREAM_DATA",
                f"Waybill {waybill.name} has no customer, order, or goods data to export.",
            )
        order_line_no_map = {}
        for index, order_line in enumerate(order_lines, start=1):
            if not order_line.customer_line_id or order_line.customer_line_id.waybill_id.id != waybill.id:
                raise ExportServiceError(
                    "EXPORT_ORDER_LINE_RELATION_BROKEN",
                    f"Order line {order_line.id} under waybill {waybill.name} is missing customer relation.",
                )
            order_line_no_map[order_line.id] = f"{waybill.name}-OL-{index:03d}"

        for goods_line in goods_lines:
            if not goods_line.order_line_id or goods_line.order_line_id.waybill_id.id != waybill.id:
                raise ExportServiceError(
                    "EXPORT_GOODS_LINE_RELATION_BROKEN",
                    f"Goods line {goods_line.id} under waybill {waybill.name} is missing order relation.",
                )

        waybill_row = cls._build_waybill_row(waybill)
        customer_rows = [cls._build_customer_row(waybill, customer_line) for customer_line in customer_lines]
        order_rows = [cls._build_order_row(waybill, order_line, order_line_no_map) for order_line in order_lines]
        goods_rows = [cls._build_goods_row(goods_line, order_line_no_map) for goods_line in goods_lines]
        return {
            "waybill_rows": [waybill_row],
            "customer_rows": customer_rows,
            "order_rows": order_rows,
            "goods_rows": goods_rows,
            "exported_waybill_count": 1,
            "exported_customer_line_count": len(customer_rows),
            "exported_order_line_count": len(order_rows),
            "exported_goods_line_count": len(goods_rows),
        }

    @classmethod
    def _validate_waybill_header(cls, waybill):
        warehouse_code = cls._warehouse_code(waybill)
        required_values = {
            "warehouse_code": warehouse_code,
            "delivery_date": waybill.delivery_date,
            "wave_no": waybill.wave_id.name,
            "batch_no": waybill.batch_id.name,
            "waybill_no": waybill.name,
        }
        missing_fields = [field_name for field_name, value in required_values.items() if not value]
        if missing_fields:
            raise ExportServiceError(
                "EXPORT_WAYBILL_DATA_INCOMPLETE",
                f"Waybill {waybill.name or waybill.id} is missing required fields: {', '.join(missing_fields)}.",
            )

    @classmethod
    def _build_waybill_row(cls, waybill):
        return cls._normalize_row(
            cls.SHEETS[0],
            {
                "warehouse_code": cls._warehouse_code(waybill),
                "delivery_date": cls._format_value(waybill.delivery_date),
                "wave_no": waybill.wave_id.name or "",
                "batch_no": waybill.batch_id.name or "",
                "waybill_no": waybill.name or "",
                "organization_name": waybill.organization_name_snapshot or "",
                "route_name": waybill.route_name_snapshot or "",
                "driver_name": cls._driver_name(waybill),
                "driver_phone": cls._driver_phone(waybill),
                "delivery_remark": waybill.delivery_remark_snapshot or waybill.remark or "",
            },
        )

    @classmethod
    def _build_customer_row(cls, waybill, customer_line):
        region = cls._extract_region_snapshot(customer_line.address_region_json_snapshot)
        access_flags = cls._extract_access_flags(customer_line.delivery_access_flags_snapshot)
        return cls._normalize_row(
            cls.SHEETS[1],
            {
                "waybill_no": waybill.name or "",
                "customer_line_no": customer_line.customer_line_no or f"{waybill.name}-CL-{customer_line.id}",
                "external_customer_code": customer_line.external_customer_code_snapshot
                or customer_line.partner_no
                or customer_line.customer_no
                or "",
                "customer_name": customer_line.customer_name_snapshot or customer_line.partner_name or "",
                "contact_name": customer_line.contact_name_snapshot or "",
                "contact_phone": customer_line.contact_phone_snapshot or "",
                "organization_name": waybill.organization_name_snapshot or "",
                "department_name": "",
                "salesperson_name": "",
                "channel_name": "",
                "customer_level": "",
                "allow_cash_on_delivery": "",
                "customer_status": "",
                "internal_counterparty_flag": "",
                "invoice_type": "",
                "registered_phone": "",
                "registered_address": "",
                "customer_seq_no": "",
                "address_full": customer_line.address_full_snapshot or "",
                "province_name": region.get("province_name", ""),
                "city_name": region.get("city_name", ""),
                "district_name": region.get("district_name", ""),
                "longitude": cls._format_value(customer_line.longitude_snapshot),
                "latitude": cls._format_value(customer_line.latitude_snapshot),
                "route_preference": waybill.route_name_snapshot or "",
                "warehouse_preference": cls._warehouse_code(waybill),
                "stop_seq_in_waybill": cls._format_value(customer_line.stop_seq_in_waybill),
                "receive_start_time": "",
                "receive_end_time": "",
                "receive_time_slots_text": "",
                "no_receive_time_slots_text": "",
                "illegal_parking_flag": "",
                "free_parking_minutes": "",
                "parking_fee_per_hour": "",
                "parking_location_text": "",
                "parking_mode_text": "",
                "unload_entrance_text": "",
                "unload_location_text": "",
                "access_alley": access_flags["access_alley"],
                "access_handcart": access_flags["access_handcart"],
                "access_pallet_exchange": access_flags["access_pallet_exchange"],
                "access_cooler_box_exchange": access_flags["access_cooler_box_exchange"],
                "upstairs_floor_count": cls._format_value(customer_line.upstairs_floor_count_snapshot),
                "basement_height_limit_text": customer_line.basement_height_limit_text_snapshot or "",
                "delivery_week_mon": "",
                "delivery_week_tue": "",
                "delivery_week_wed": "",
                "delivery_week_thu": "",
                "delivery_week_fri": "",
                "delivery_week_sat": "",
                "delivery_week_sun": "",
            },
        )

    @classmethod
    def _build_order_row(cls, waybill, order_line, order_line_no_map):
        return cls._normalize_row(
            cls.SHEETS[2],
            {
                "order_line_no": order_line_no_map[order_line.id],
                "waybill_no": waybill.name or "",
                "customer_line_no": order_line.customer_line_id.customer_line_no or "",
                "source_doc_no": order_line.source_doc_no or order_line.order_no or "",
                "sales_order_no": order_line.sales_order_no or order_line.order_no or "",
                "source_ref_no": order_line.source_ref_no or "",
                "third_party_doc_no": order_line.third_party_doc_no or "",
                "doc_type": order_line.doc_type or "",
                "business_type": order_line.business_type or "",
                "doc_source": order_line.doc_source or "",
                "doc_date": cls._format_value(order_line.doc_date),
                "audited_at": cls._format_value(order_line.audited_at),
                "department_name": order_line.department_name_snapshot or "",
                "channel_name": order_line.channel_name_snapshot or "",
                "salesperson_name": order_line.salesperson_name_snapshot or "",
                "payment_status": order_line.payment_status or "",
                "settlement_status": order_line.settlement_status or "",
                "doc_status": order_line.doc_status or "",
                "logistics_status": order_line.logistics_status or "",
                "maker_name": order_line.maker_name or "",
                "auditor_name": order_line.auditor_name or "",
                "made_at": cls._format_value(order_line.made_at),
                "order_remark": order_line.order_remark or "",
                "custom_field_1": order_line.custom_field_1 or "",
            },
        )

    @classmethod
    def _build_goods_row(cls, goods_line, order_line_no_map):
        return cls._normalize_row(
            cls.SHEETS[3],
            {
                "order_line_no": order_line_no_map[goods_line.order_line_id.id],
                "external_product_code": goods_line.external_product_code_snapshot or goods_line.goods_code or "",
                "product_name": goods_line.product_name_snapshot or goods_line.goods_name or "",
                "spec": goods_line.spec_snapshot or goods_line.specification or "",
                "barcode": goods_line.barcode_snapshot or "",
                "brand_name": goods_line.brand_name_snapshot or "",
                "category_name": goods_line.category_name_snapshot or "",
                "base_unit_name": goods_line.base_unit_name or "",
                "doc_unit_name": goods_line.doc_unit_name or goods_line.uom_name or "",
                "small_unit_name": goods_line.small_unit_name or "",
                "base_qty": cls._format_value(goods_line.base_qty),
                "doc_qty": cls._format_value(goods_line.doc_qty or goods_line.quantity),
                "small_qty": cls._format_value(goods_line.small_qty),
                "box_qty": cls._format_value(goods_line.box_qty or goods_line.package_count),
                "gift_qty": cls._format_value(goods_line.gift_qty),
                "exchange_qty": cls._format_value(goods_line.exchange_qty),
                "unit_price": cls._format_value(goods_line.unit_price),
                "small_unit_price": cls._format_value(goods_line.small_unit_price),
                "amount": cls._format_value(goods_line.amount),
                "settled_amount": cls._format_value(goods_line.settled_amount),
                "unsettled_amount": cls._format_value(goods_line.unsettled_amount),
                "tax_amount": cls._format_value(goods_line.tax_amount),
                "amount_ex_tax": cls._format_value(goods_line.amount_ex_tax),
                "cost_amount": cls._format_value(goods_line.cost_amount),
                "gross_profit": cls._format_value(goods_line.gross_profit),
                "gross_profit_rate": cls._format_value(goods_line.gross_profit_rate),
                "above_standard_price_flag": cls._bool_flag(goods_line.above_standard_price_flag),
                "below_standard_price_flag": cls._bool_flag(goods_line.below_standard_price_flag),
                "unit_weight": cls._format_value(goods_line.unit_weight),
                "unit_volume": cls._format_value(goods_line.unit_volume),
                "total_weight": cls._format_value(goods_line.total_weight or goods_line.weight),
                "total_volume": cls._format_value(goods_line.total_volume or goods_line.volume),
                "line_remark": goods_line.line_remark or goods_line.remark or "",
            },
        )

    @classmethod
    def _normalize_row(cls, sheet_meta, row_values):
        row = {}
        for field_name in sheet_meta["fields"]:
            row[field_name] = row_values.get(field_name, "")
        return row

    @classmethod
    def _build_workbook_bytes(cls, rows_by_sheet_key):
        try:
            workbook = Workbook()
            header_font = Font(bold=True)
            active_sheet = workbook.active
            for index, sheet_meta in enumerate(cls.SHEETS):
                sheet = active_sheet if index == 0 else workbook.create_sheet(title=sheet_meta["sheet_name"])
                sheet.title = sheet_meta["sheet_name"]
                headers = [cls.FIELD_LABELS.get(field_name, field_name) for field_name in sheet_meta["fields"]]
                sheet.append(headers)
                for cell in sheet[1]:
                    cell.font = header_font
                for row in rows_by_sheet_key.get(sheet_meta["key"], []):
                    sheet.append([row.get(field_name, "") for field_name in sheet_meta["fields"]])
            buffer = io.BytesIO()
            workbook.save(buffer)
            return buffer.getvalue()
        except Exception as error:
            raise ExportServiceError("EXPORT_WORKBOOK_BUILD_FAILED", f"Failed to build workbook: {error}") from error

    @classmethod
    def _store_output_file(cls, task, workbook_bytes):
        task.ensure_one()
        timestamp = fields.Datetime.now()
        file_name = f"TSL-EXPORT-FROM-WAYBILL-{timestamp.strftime('%Y%m%d-%H%M%S')}.xlsx"
        return cls._store_output_file_bytes(task, workbook_bytes, file_name=file_name)

    @classmethod
    def _store_output_file_bytes(cls, task, workbook_bytes, *, file_name):
        task.ensure_one()
        timestamp = fields.Datetime.now()
        folder = cls.EXPORT_ROOT_DIR / timestamp.strftime("%Y") / timestamp.strftime("%m") / timestamp.strftime("%d") / task.task_no
        file_path = folder / file_name
        try:
            folder.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(workbook_bytes or b"")
        except OSError as error:
            raise ExportServiceError("EXPORT_FILE_WRITE_FAILED", f"Failed to store export file: {error}") from error
        download_ready_at = fields.Datetime.now()
        expires_at = download_ready_at + timedelta(days=cls.DOWNLOAD_EXPIRE_DAYS)
        relative_path = file_path.relative_to(cls.EXPORT_ROOT_DIR).as_posix()
        return {
            "download_ready_at": download_ready_at,
            "expires_at": expires_at,
            "output_file_name": file_name,
            "output_file_ext": "xlsx",
            "output_storage_path": relative_path,
            "output_file_sha256": hashlib.sha256(workbook_bytes or b"").hexdigest(),
            "output_file_size": len(workbook_bytes or b""),
        }

    @classmethod
    def _resolve_output_storage_path(cls, storage_path):
        raw_path = (storage_path or "").strip()
        if not raw_path:
            raise ExportServiceError("EXPORT_OUTPUT_FILE_NOT_READY", "output_storage_path is empty.")
        export_root = cls.EXPORT_ROOT_DIR.resolve()
        candidate = Path(raw_path)
        if not candidate.is_absolute():
            candidate = export_root / candidate
        try:
            resolved_path = candidate.resolve(strict=False)
        except OSError as error:
            raise ExportServiceError("EXPORT_OUTPUT_FILE_INVALID", f"Invalid output storage path: {error}") from error
        try:
            resolved_path.relative_to(export_root)
        except ValueError as error:
            raise ExportServiceError(
                "EXPORT_OUTPUT_FILE_INVALID",
                f"Output file path is outside export root: {raw_path}",
            ) from error
        return resolved_path

    @classmethod
    def _compute_task_status(cls, *, success_count, fail_count, skipped_count, task_level_error_code):
        if task_level_error_code:
            return "failed"
        if success_count and not fail_count and not skipped_count:
            return "success"
        if success_count and (fail_count or skipped_count):
            return "partial_failed"
        return "failed"

    @classmethod
    def _build_summary_message(cls, *, success_count, fail_count, skipped_count, task_level_error_message):
        if task_level_error_message:
            return task_level_error_message
        return (
            f"Export finished. Success {success_count}, "
            f"failed {fail_count}, skipped {skipped_count}."
        )

    @classmethod
    def _build_task_line_message(cls, package):
        return (
            f"Exported Waybill {package['exported_waybill_count']} / "
            f"CustomerLine {package['exported_customer_line_count']} / "
            f"OrderLine {package['exported_order_line_count']} / "
            f"GoodsLine {package['exported_goods_line_count']}."
        )

    @classmethod
    def _build_created_task_payload(cls, task):
        task.ensure_one()
        return {
            "task_no": task.task_no,
            "object_type": task.object_type,
            "entry_type": task.entry_type,
            "export_mode": task.export_mode,
            "package_structure": task.package_structure,
            "status": task.status,
            "total_count": task.total_count,
            "success_count": task.success_count,
            "fail_count": task.fail_count,
            "skipped_count": task.skipped_count,
            "summary_message": task.summary_message or "Export task created.",
            "download_file": {
                "ready": False,
                "name": False,
                "download_url": False,
            },
        }

    @classmethod
    def _build_task_result_payload(cls, task):
        task.ensure_one()
        download_ready = bool(task.output_storage_path) and task.status in ("success", "partial_failed")
        error_ready = bool(task.error_line_ids)
        return {
            "task_no": task.task_no,
            "object_type": task.object_type,
            "object_type_label": cls._selection_label(task, "object_type", task.object_type),
            "entry_type": task.entry_type,
            "entry_type_label": cls._selection_label(task, "entry_type", task.entry_type),
            "export_mode": task.export_mode,
            "package_structure": task.package_structure,
            "status": task.status,
            "status_label": cls._selection_label(task, "status", task.status),
            "total_count": task.total_count,
            "success_count": task.success_count,
            "fail_count": task.fail_count,
            "skipped_count": task.skipped_count,
            "business_summary": {
                "exported_waybill_count": task.exported_waybill_count,
                "exported_customer_line_count": task.exported_customer_line_count,
                "exported_order_line_count": task.exported_order_line_count,
                "exported_goods_line_count": task.exported_goods_line_count,
            },
            "summary_message": task.summary_message or cls._build_summary_message(
                success_count=task.success_count,
                fail_count=task.fail_count,
                skipped_count=task.skipped_count,
                task_level_error_message=task.failure_reason,
            ),
            "failure_error_code": task.failure_error_code or False,
            "failure_reason": task.failure_reason or False,
            "operator": cls._build_operator_payload(task.operator_id),
            "source_scope": cls._build_source_scope_payload(task.source_scope_id),
            "started_at": cls._datetime_string(task.started_at),
            "finished_at": cls._datetime_string(task.finished_at),
            "download_file": {
                "ready": download_ready,
                "name": task.output_file_name or False,
                "size": task.output_file_size or 0,
                "download_url": cls._build_download_url(task) if download_ready else False,
            },
            "error_report": {
                "download_ready": error_ready,
                "download_url": cls._build_error_report_url(task) if error_ready else False,
            },
        }

    @classmethod
    def _build_task_line_payload(cls, task_line):
        task_line.ensure_one()
        return {
            "line_no": task_line.line_no,
            "business_key": task_line.business_key,
            "display_name": task_line.display_name or task_line.business_key,
            "target_object_type": task_line.target_object_type,
            "target_object_type_label": cls._selection_label(task_line, "target_object_type", task_line.target_object_type),
            "target_model": task_line.target_res_model or False,
            "target_res_id": task_line.target_res_id or False,
            "status": task_line.status,
            "status_label": cls._selection_label(task_line, "status", task_line.status),
            "message": task_line.message or False,
            "export_count_summary": (
                f"Waybill {task_line.exported_waybill_count} / "
                f"CustomerLine {task_line.exported_customer_line_count} / "
                f"OrderLine {task_line.exported_order_line_count} / "
                f"GoodsLine {task_line.exported_goods_line_count}"
            ),
            "exported_waybill_count": task_line.exported_waybill_count,
            "exported_customer_line_count": task_line.exported_customer_line_count,
            "exported_order_line_count": task_line.exported_order_line_count,
            "exported_goods_line_count": task_line.exported_goods_line_count,
        }

    @classmethod
    def _build_error_payload(cls, error):
        error.ensure_one()
        task_line = error.task_line_id
        return {
            "line_no": task_line.line_no if task_line else False,
            "business_key": task_line.business_key if task_line else False,
            "error_stage": error.error_stage,
            "error_stage_label": cls._selection_label(error, "error_stage", error.error_stage),
            "field_name": error.field_name,
            "raw_value": error.raw_value or "",
            "mapped_value": error.mapped_value or "",
            "error_code": error.error_code,
            "error_message": error.error_message,
        }

    @classmethod
    def _build_source_scope_payload(cls, source_scope):
        if not source_scope:
            return False
        return {
            "scope_no": source_scope.scope_no,
            "source_model": source_scope.source_model,
            "source_page": source_scope.source_page or False,
            "selected_count": source_scope.selected_count,
        }

    @classmethod
    def _build_operator_payload(cls, operator):
        if not operator:
            return False
        return {
            "id": operator.id,
            "name": operator.name,
        }

    @classmethod
    def _build_download_url(cls, task):
        return f"/api/admin/logistics/exports/tasks/{task.task_no}/download"

    @classmethod
    def _build_error_report_url(cls, task):
        return f"/api/admin/logistics/exports/tasks/{task.task_no}/error-report"

    @classmethod
    def _selection_label(cls, record, field_name, value):
        selection_map = dict(record._fields[field_name].selection or [])
        return selection_map.get(value, value)

    @classmethod
    def _build_error_line_vals(
        cls,
        *,
        task,
        task_line,
        error_code,
        error_message,
        error_stage,
        field_name,
        raw_value,
        mapped_value=False,
    ):
        return {
            "task_id": task.id,
            "task_line_id": task_line.id if task_line else False,
            "error_stage": error_stage,
            "field_name": field_name,
            "raw_value": raw_value or False,
            "mapped_value": mapped_value or False,
            "error_code": error_code,
            "error_message": error_message,
        }

    @classmethod
    def _error_stage_for_code(cls, error_code):
        if error_code in ("EXPORT_WAYBILL_NOT_FOUND",):
            return "target_resolve"
        if error_code in (
            "EXPORT_TARGET_NO_DOWNSTREAM_DATA",
            "EXPORT_WAYBILL_DATA_INCOMPLETE",
            "EXPORT_ORDER_LINE_RELATION_BROKEN",
            "EXPORT_GOODS_LINE_RELATION_BROKEN",
        ):
            return "data_collect"
        if error_code == "EXPORT_WORKBOOK_BUILD_FAILED":
            return "workbook_build"
        if error_code in ("EXPORT_FILE_WRITE_FAILED", "EXPORT_FILE_READ_FAILED", "EXPORT_OUTPUT_FILE_MISSING"):
            return "file_store"
        return "scope_validate"

    @classmethod
    def _normalize_pagination(cls, *, page, page_size, default_size, max_size):
        try:
            normalized_page = max(int(page or 1), 1)
        except (TypeError, ValueError):
            normalized_page = 1
        try:
            normalized_size = int(page_size or default_size)
        except (TypeError, ValueError):
            normalized_size = default_size
        normalized_size = max(1, min(normalized_size, max_size))
        return normalized_page, normalized_size

    @classmethod
    def _status_filter_label(cls, status):
        if not status:
            return "All"
        return {
            "pending": "Pending",
            "success": "Success",
            "failed": "Failed",
            "skipped": "Skipped",
        }.get(status, status)

    @classmethod
    def _warehouse_code(cls, waybill):
        warehouse = waybill.warehouse_id
        return getattr(warehouse, "code", False) or waybill.warehouse_name_snapshot or ""

    @classmethod
    def _driver_name(cls, waybill):
        batch = getattr(waybill, "batch_id", False)
        if batch and batch.driver_name_snapshot:
            return batch.driver_name_snapshot
        employee = getattr(waybill.sudo(), "driver_employee_id", False)
        return getattr(employee, "name", False) or ""

    @classmethod
    def _driver_phone(cls, waybill):
        batch = getattr(waybill, "batch_id", False)
        if batch and batch.driver_phone_snapshot:
            return batch.driver_phone_snapshot
        employee = getattr(waybill.sudo(), "driver_employee_id", False)
        return cls._employee_phone(employee)

    @classmethod
    def _employee_phone(cls, employee):
        return (
            getattr(employee, "mobile_phone", False)
            or getattr(employee, "work_phone", False)
            or getattr(employee, "phone", False)
            or ""
        )

    @classmethod
    def _extract_region_snapshot(cls, region_snapshot):
        if not region_snapshot:
            return {}
        if isinstance(region_snapshot, str):
            try:
                region_snapshot = json.loads(region_snapshot)
            except ValueError:
                return {}
        if isinstance(region_snapshot, dict):
            return {
                "province_name": region_snapshot.get("province_name")
                or region_snapshot.get("province")
                or "",
                "city_name": region_snapshot.get("city_name") or region_snapshot.get("city") or "",
                "district_name": region_snapshot.get("district_name")
                or region_snapshot.get("district")
                or "",
            }
        return {}

    @classmethod
    def _extract_access_flags(cls, access_flags_snapshot):
        raw_text = (access_flags_snapshot or "").strip().lower()
        return {
            "access_alley": cls._bool_flag("alley" in raw_text or "access_alley" in raw_text),
            "access_handcart": cls._bool_flag("handcart" in raw_text or "access_handcart" in raw_text),
            "access_pallet_exchange": cls._bool_flag("pallet_exchange" in raw_text or "access_pallet_exchange" in raw_text),
            "access_cooler_box_exchange": cls._bool_flag(
                "cooler_box_exchange" in raw_text or "access_cooler_box_exchange" in raw_text
            ),
        }

    @classmethod
    def _bool_flag(cls, value):
        return "Y" if value else "N"

    @classmethod
    def _format_value(cls, value):
        if value in (None, False):
            return ""
        if hasattr(value, "strftime"):
            if getattr(value, "hour", None) is None:
                return value.strftime("%Y-%m-%d")
            if value.hour == 0 and value.minute == 0 and value.second == 0:
                return value.strftime("%Y-%m-%d")
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return value

    @classmethod
    def _datetime_string(cls, value):
        if not value:
            return False
        return fields.Datetime.to_string(value)
