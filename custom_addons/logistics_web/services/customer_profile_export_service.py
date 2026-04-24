import hashlib
from datetime import timedelta
from pathlib import Path

from odoo import fields

from .dispatch_main_export_service import DispatchMainExportService, ExportServiceError


class CustomerProfileExportService(DispatchMainExportService):
    OBJECT_TYPE = "customer_profile"
    ENTRY_TYPE = "from_customer"
    EXPORT_MODE = "standard_xlsx"
    PACKAGE_STRUCTURE = "customer_profile_bundle_v1"
    SOURCE_MODEL = "res.partner"
    SOURCE_PAGE_DEFAULT = "customer_profile_list"
    TARGET_OBJECT_TYPE = "partner"
    EXPORT_ROOT_DIR = Path(__file__).resolve().parents[3] / ".odoo_data" / "export_tasks"
    SHEETS = [
        {
            "key": "customer_profile_rows",
            "sheet_name": "CustomerProfile",
            "fields": [
                "external_customer_code",
                "internal_customer_code",
                "logistics_customer_code",
                "customer_name",
                "contact_name",
                "contact_phone",
                "organization_name",
                "channel_name",
                "department_name",
                "salesperson_name",
                "customer_status",
                "logistics_customer_level",
                "allow_cash_on_delivery",
                "internal_counterparty_flag",
                "invoice_type",
                "default_signoff_requirement",
                "logistics_need_sign_receipt",
                "logistics_delivery_time_window",
                "address_full",
                "province_name",
                "city_name",
                "district_name",
                "partner_longitude",
                "partner_latitude",
                "route_preference",
                "warehouse_preference",
                "receive_start_time",
                "receive_end_time",
                "receive_time_slots_text",
                "no_receive_time_slots_text",
                "delivery_week_flags",
                "delivery_access_flags",
                "illegal_parking_flag",
                "free_parking_minutes",
                "parking_fee_per_hour",
                "parking_location_text",
                "parking_mode_text",
                "unload_entrance_text",
                "unload_location_text",
                "upstairs_floor_count",
                "basement_height_limit_text",
                "logistics_unload_requirement",
                "logistics_service_note",
            ],
        }
    ]
    FIELD_LABELS = {
        "external_customer_code": "外联客户编号",
        "internal_customer_code": "系统内部客户编号",
        "logistics_customer_code": "客户号",
        "customer_name": "统一客户名称",
        "contact_name": "默认联系人",
        "contact_phone": "默认联系电话",
        "organization_name": "组织归属",
        "channel_name": "渠道",
        "department_name": "部门",
        "salesperson_name": "业务员",
        "customer_status": "经营状态",
        "logistics_customer_level": "客户等级",
        "allow_cash_on_delivery": "允许货到付款",
        "internal_counterparty_flag": "内部往来单位",
        "invoice_type": "发票类型",
        "default_signoff_requirement": "默认签收要求",
        "logistics_need_sign_receipt": "需要签收回执",
        "logistics_delivery_time_window": "配送时间窗",
        "address_full": "默认地址",
        "province_name": "省",
        "city_name": "市",
        "district_name": "区/县",
        "partner_longitude": "经度",
        "partner_latitude": "纬度",
        "route_preference": "线路偏好",
        "warehouse_preference": "仓库偏好",
        "receive_start_time": "开始收货时间",
        "receive_end_time": "截止收货时间",
        "receive_time_slots_text": "收货时间段",
        "no_receive_time_slots_text": "不收货时间段",
        "delivery_week_flags": "周维度配送周期",
        "delivery_access_flags": "配送可达性编码串",
        "illegal_parking_flag": "违停",
        "free_parking_minutes": "免费停车时长",
        "parking_fee_per_hour": "停车费/小时",
        "parking_location_text": "停车位置",
        "parking_mode_text": "停车方式",
        "unload_entrance_text": "卸货入口",
        "unload_location_text": "卸货位置",
        "upstairs_floor_count": "上楼层数",
        "basement_height_limit_text": "地库限高",
        "logistics_unload_requirement": "卸货要求",
        "logistics_service_note": "服务备注",
    }

    @classmethod
    def create_customer_profile_export_task(
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
        partners = cls._get_partners_for_scope(env, normalized_ids)

        scope_vals = {
            "object_type": object_type,
            "entry_type": entry_type,
            "source_model": source_model,
            "source_page": (source_page or cls.SOURCE_PAGE_DEFAULT).strip() or cls.SOURCE_PAGE_DEFAULT,
            "selected_ids_json": normalized_ids,
            "selected_count": len(normalized_ids),
            "scope_snapshot_json": scope_snapshot or cls._build_scope_snapshot(partners),
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
                "summary_message": f"Export task created, waiting to run. Total {len(normalized_ids)} customer profiles.",
            }
        )
        line_vals_list = []
        for index, partner in enumerate(partners, start=1):
            line_vals_list.append(
                {
                    "task_id": task.id,
                    "line_no": index,
                    "target_object_type": cls.TARGET_OBJECT_TYPE,
                    "target_res_model": cls.SOURCE_MODEL,
                    "target_res_id": partner.id,
                    "business_key": cls._partner_business_key(partner),
                    "display_name": f"Customer {partner.name or partner.id}",
                    "status": "pending",
                }
            )
        if line_vals_list:
            env["logistics.export.task.line"].sudo().create(line_vals_list)
        return cls._build_created_task_payload(task.sudo())

    @classmethod
    def run_customer_profile_export_task(cls, env, *, task_no="", task=None):
        task = cls._get_customer_profile_task(env, task_no=task_no, task=task)
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
                "package_metrics_json": {},
            }
        )

        customer_profile_rows = []
        error_vals_list = []
        success_count = 0
        fail_count = 0
        skipped_count = 0
        customer_count = 0

        for task_line in task.sudo().task_line_ids.sorted(key=lambda rec: (rec.line_no, rec.id)):
            try:
                package = cls._collect_customer_profile_package(env, task_line)
                task_line.sudo().write(
                    {
                        "status": "success",
                        "message": cls._build_task_line_message(package),
                        "line_metrics_json": package["line_metrics_json"],
                        "exported_waybill_count": 0,
                        "exported_customer_line_count": 0,
                        "exported_order_line_count": 0,
                        "exported_goods_line_count": 0,
                    }
                )
                customer_profile_rows.extend(package["customer_profile_rows"])
                success_count += 1
                customer_count += package["customer_count"]
            except ExportServiceError as error:
                task_line.sudo().write(
                    {
                        "status": "failed",
                        "message": str(error),
                        "line_metrics_json": {},
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
                        error_code=error.error_code,
                        error_message=str(error),
                        error_stage=cls._error_stage_for_code(error.error_code),
                        field_name="partner_id",
                        raw_value=task_line.business_key,
                    )
                )
            except Exception as error:
                message = f"Unexpected export error: {error}"
                task_line.sudo().write(
                    {
                        "status": "failed",
                        "message": message,
                        "line_metrics_json": {},
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
                        field_name="partner_id",
                        raw_value=task_line.business_key,
                    )
                )

        task_level_error_code = False
        task_level_error_message = False
        output_file_vals = {}
        if success_count:
            try:
                workbook_bytes = cls._build_workbook_bytes({"customer_profile_rows": customer_profile_rows})
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
            "package_metrics_json": {
                "customer_count": customer_count,
            },
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

    @classmethod
    def get_export_task_result(cls, env, *, task_no):
        task = cls._get_customer_profile_task(env, task_no=task_no)
        cls._ensure_task_access(env, task)
        cls._mark_task_expired_if_needed(task)
        return cls._build_task_result_payload(task.sudo())

    @classmethod
    def get_export_task_lines(cls, env, *, task_no, page=1, page_size=20, status=""):
        task = cls._get_customer_profile_task(env, task_no=task_no)
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
        task = cls._get_customer_profile_task(env, task_no=task_no)
        cls._ensure_task_access(env, task)
        return super().get_export_task_errors(env, task_no=task.task_no, page=page, page_size=page_size)

    @classmethod
    def build_export_task_error_report(cls, env, *, task_no):
        task = cls._get_customer_profile_task(env, task_no=task_no)
        cls._ensure_task_access(env, task)
        return super().build_export_task_error_report(env, task_no=task.task_no)

    @classmethod
    def get_export_download_file(cls, env, *, task_no):
        task = cls._get_customer_profile_task(env, task_no=task_no)
        cls._ensure_task_access(env, task)
        return super().get_export_download_file(env, task_no=task.task_no)

    @classmethod
    def _validate_create_contract(cls, *, object_type, entry_type, export_mode, package_structure, source_model):
        if object_type != cls.OBJECT_TYPE:
            raise ExportServiceError("EXPORT_TASK_OBJECT_TYPE_INVALID", f"Unsupported object_type: {object_type}")
        if entry_type != cls.ENTRY_TYPE:
            raise ExportServiceError("EXPORT_TASK_ENTRY_TYPE_INVALID", f"Unsupported entry_type: {entry_type}")
        if export_mode != cls.EXPORT_MODE:
            raise ExportServiceError("EXPORT_MODE_INVALID", f"Unsupported export_mode: {export_mode}")
        if package_structure != cls.PACKAGE_STRUCTURE:
            raise ExportServiceError("EXPORT_PACKAGE_STRUCTURE_INVALID", f"Unsupported package_structure: {package_structure}")
        if source_model != cls.SOURCE_MODEL:
            raise ExportServiceError("EXPORT_SCOPE_SNAPSHOT_INVALID", f"Unsupported source_model: {source_model}")

    @classmethod
    def _get_partners_for_scope(cls, env, selected_ids):
        model = env[cls.SOURCE_MODEL]
        model.check_access_rights("read")
        records = model.browse(selected_ids)
        records.check_access_rule("read")
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
            raise ExportServiceError("EXPORT_CUSTOMER_PROFILE_NOT_FOUND", f"Customer ids not found or not readable: {missing_ids}")
        return model.browse([record.id for record in ordered_records])

    @classmethod
    def _build_scope_snapshot(cls, partners):
        items = []
        for partner in partners:
            items.append(
                {
                    "id": partner.id,
                    "external_customer_code": partner.external_customer_code or "",
                    "logistics_customer_code": partner.logistics_customer_code or "",
                    "customer_name": partner.name or "",
                    "is_logistics_partner": bool(partner.is_logistics_partner),
                }
            )
        return {
            "object_type": cls.OBJECT_TYPE,
            "entry_type": cls.ENTRY_TYPE,
            "selected_count": len(items),
            "items": items,
        }

    @classmethod
    def _get_customer_profile_task(cls, env, *, task_no="", task=None):
        task = super()._get_task(env, task_no=task_no, task=task)
        if task.object_type != cls.OBJECT_TYPE:
            raise ExportServiceError(
                "EXPORT_TASK_OBJECT_TYPE_INVALID",
                f"Task {task.task_no} does not belong to object_type {cls.OBJECT_TYPE}.",
            )
        return task

    @classmethod
    def _collect_customer_profile_package(cls, env, task_line):
        partner = env[cls.SOURCE_MODEL].browse(task_line.target_res_id).exists()
        if not partner:
            raise ExportServiceError(
                "EXPORT_CUSTOMER_PROFILE_NOT_FOUND",
                f"Customer profile for line {task_line.line_no} was not found.",
            )
        if not partner.is_logistics_partner:
            raise ExportServiceError(
                "EXPORT_CUSTOMER_PROFILE_NOT_LOGISTICS_PARTNER",
                f"Partner {partner.display_name} is not a logistics customer profile.",
            )
        row = cls._build_customer_profile_row(partner)
        return {
            "customer_profile_rows": [row],
            "customer_count": 1,
            "line_metrics_json": {
                "customer_count": 1,
            },
        }

    @classmethod
    def _build_customer_profile_row(cls, partner):
        region = cls._extract_region_snapshot(partner.address_region_json)
        return cls._normalize_row(
            cls.SHEETS[0],
            {
                "external_customer_code": partner.external_customer_code or "",
                "internal_customer_code": partner.internal_customer_code or "",
                "logistics_customer_code": partner.logistics_customer_code or "",
                "customer_name": partner.customer_name or partner.name or "",
                "contact_name": partner.contact_name or "",
                "contact_phone": partner.contact_phone or "",
                "organization_name": partner.organization_name or "",
                "channel_name": partner.channel_name or "",
                "department_name": partner.department_name or "",
                "salesperson_name": partner.salesperson_name or "",
                "customer_status": partner.customer_status or "",
                "logistics_customer_level": partner.logistics_customer_level or "",
                "allow_cash_on_delivery": cls._bool_flag(partner.allow_cash_on_delivery),
                "internal_counterparty_flag": cls._bool_flag(partner.internal_counterparty_flag),
                "invoice_type": partner.invoice_type or "",
                "default_signoff_requirement": partner.default_signoff_requirement or "",
                "logistics_need_sign_receipt": cls._bool_flag(partner.logistics_need_sign_receipt),
                "logistics_delivery_time_window": partner.logistics_delivery_time_window or "",
                "address_full": partner.address_full or "",
                "province_name": region.get("province_name", ""),
                "city_name": region.get("city_name", ""),
                "district_name": region.get("district_name", ""),
                "partner_longitude": cls._format_value(partner.partner_longitude),
                "partner_latitude": cls._format_value(partner.partner_latitude),
                "route_preference": partner.route_preference or "",
                "warehouse_preference": partner.warehouse_preference or "",
                "receive_start_time": partner.receive_start_time or "",
                "receive_end_time": partner.receive_end_time or "",
                "receive_time_slots_text": partner.receive_time_slots_text or "",
                "no_receive_time_slots_text": partner.no_receive_time_slots_text or "",
                "delivery_week_flags": partner.delivery_week_flags or "",
                "delivery_access_flags": partner.delivery_access_flags or "",
                "illegal_parking_flag": cls._bool_flag(partner.illegal_parking_flag),
                "free_parking_minutes": cls._format_value(partner.free_parking_minutes),
                "parking_fee_per_hour": cls._format_value(partner.parking_fee_per_hour),
                "parking_location_text": partner.parking_location_text or "",
                "parking_mode_text": partner.parking_mode_text or "",
                "unload_entrance_text": partner.unload_entrance_text or "",
                "unload_location_text": partner.unload_location_text or "",
                "upstairs_floor_count": cls._format_value(partner.upstairs_floor_count),
                "basement_height_limit_text": partner.basement_height_limit_text or "",
                "logistics_unload_requirement": partner.logistics_unload_requirement or "",
                "logistics_service_note": partner.logistics_service_note or "",
            },
        )

    @classmethod
    def _store_output_file(cls, task, workbook_bytes):
        task.ensure_one()
        timestamp = fields.Datetime.now()
        folder = cls.EXPORT_ROOT_DIR / timestamp.strftime("%Y") / timestamp.strftime("%m") / timestamp.strftime("%d") / task.task_no
        file_name = f"TSL-EXPORT-CUSTOMER-PROFILE-{timestamp.strftime('%Y%m%d-%H%M%S')}.xlsx"
        file_path = folder / file_name
        try:
            folder.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(workbook_bytes or b"")
        except OSError as error:
            raise ExportServiceError("EXPORT_FILE_WRITE_FAILED", f"Failed to store export file: {error}") from error
        download_ready_at = fields.Datetime.now()
        expires_at = download_ready_at + timedelta(days=cls.DOWNLOAD_EXPIRE_DAYS)
        return {
            "download_ready_at": download_ready_at,
            "expires_at": expires_at,
            "output_file_name": file_name,
            "output_file_ext": "xlsx",
            "output_storage_path": str(file_path),
            "output_file_sha256": hashlib.sha256(workbook_bytes or b"").hexdigest(),
            "output_file_size": len(workbook_bytes or b""),
        }

    @classmethod
    def _build_summary_message(cls, *, success_count, fail_count, skipped_count, task_level_error_message):
        if task_level_error_message:
            return task_level_error_message
        return (
            f"Customer profile export finished. Success {success_count}, "
            f"failed {fail_count}, skipped {skipped_count}."
        )

    @classmethod
    def _build_task_line_message(cls, package):
        return f"Exported CustomerProfile {package['customer_count']}."

    @classmethod
    def _build_task_result_payload(cls, task):
        task.ensure_one()
        download_ready = bool(task.output_storage_path) and task.status in ("success", "partial_failed")
        error_ready = bool(task.error_line_ids)
        business_metrics = task.package_metrics_json or {}
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
            "business_metrics": {
                "customer_count": int(business_metrics.get("customer_count", 0) or 0),
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
        line_metrics = task_line.line_metrics_json or {}
        customer_count = int(line_metrics.get("customer_count", 0) or 0)
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
            "export_count_summary": f"CustomerProfile {customer_count}",
            "line_metrics": {
                "customer_count": customer_count,
            },
            "exported_waybill_count": task_line.exported_waybill_count,
            "exported_customer_line_count": task_line.exported_customer_line_count,
            "exported_order_line_count": task_line.exported_order_line_count,
            "exported_goods_line_count": task_line.exported_goods_line_count,
        }

    @classmethod
    def _error_stage_for_code(cls, error_code):
        if error_code in ("EXPORT_CUSTOMER_PROFILE_NOT_FOUND",):
            return "target_resolve"
        if error_code in ("EXPORT_CUSTOMER_PROFILE_NOT_LOGISTICS_PARTNER", "EXPORT_CUSTOMER_PROFILE_DATA_INCOMPLETE"):
            return "data_collect"
        if error_code == "EXPORT_WORKBOOK_BUILD_FAILED":
            return "workbook_build"
        if error_code in ("EXPORT_FILE_WRITE_FAILED", "EXPORT_FILE_READ_FAILED", "EXPORT_OUTPUT_FILE_MISSING"):
            return "file_store"
        return "scope_validate"

    @classmethod
    def _partner_business_key(cls, partner):
        return (
            partner.external_customer_code
            or partner.logistics_customer_code
            or partner.internal_customer_code
            or partner.name
            or str(partner.id)
        )
