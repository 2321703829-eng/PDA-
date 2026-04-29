from odoo import fields

from .dispatch_main_export_service import DispatchMainExportService, ExportServiceError


class ProductProfileExportService(DispatchMainExportService):
    OBJECT_TYPE = "product_profile"
    ENTRY_TYPE = "from_product"
    EXPORT_MODE = "standard_xlsx"
    PACKAGE_STRUCTURE = "product_profile_bundle_v1"
    SOURCE_MODEL = "product.template"
    SOURCE_PAGE_DEFAULT = "product_profile_list"
    TARGET_OBJECT_TYPE = "product"
    PRODUCT_UNIT_MODEL = "logistics.product.unit"
    SHEETS = [
        {
            "key": "product_profile_rows",
            "sheet_name": "ProductProfile",
            "fields": [
                "external_product_code",
                "internal_product_code",
                "product_name",
                "brand_name",
                "category_name",
                "product_tag",
                "default_barcode",
                "base_unit_name",
                "default_weight",
                "default_volume",
                "delivery_requirement_text",
            ],
        },
        {
            "key": "product_unit_rows",
            "sheet_name": "ProductUnit",
            "fields": [
                "product_key",
                "sku_code",
                "spec_desc",
                "full_category_name",
                "unit_name",
                "sale_unit_name",
                "convert_to_base",
                "barcode",
                "standard_price",
                "purchase_price",
                "retail_price",
                "sale_tax_rate",
                "length_cm",
                "width_cm",
                "height_cm",
                "weight",
                "volume",
                "large_unit_qty",
                "min_order_qty",
                "can_press_stock",
                "brand_owner_name",
                "default_vendor_name",
                "buyer_name",
                "unit_remark",
            ],
        },
    ]
    FIELD_LABELS = {
        "external_product_code": "外部商品编码",
        "internal_product_code": "内部商品编码",
        "product_name": "商品名称",
        "brand_name": "品牌",
        "category_name": "分类",
        "product_tag": "商品标签",
        "default_barcode": "默认条码",
        "base_unit_name": "基础单位",
        "default_weight": "默认重量",
        "default_volume": "默认体积",
        "delivery_requirement_text": "配送要求",
        "product_key": "商品业务键",
        "sku_code": "SKU 编号",
        "spec_desc": "规格描述",
        "full_category_name": "全级分类",
        "unit_name": "单位名",
        "sale_unit_name": "销售单位",
        "convert_to_base": "换算系数",
        "barcode": "条码",
        "standard_price": "标准价",
        "purchase_price": "采购价",
        "retail_price": "零售价",
        "sale_tax_rate": "税率",
        "length_cm": "长(cm)",
        "width_cm": "宽(cm)",
        "height_cm": "高(cm)",
        "weight": "重量",
        "volume": "体积",
        "large_unit_qty": "大单位数量",
        "min_order_qty": "起订量",
        "can_press_stock": "可压货",
        "brand_owner_name": "品牌方",
        "default_vendor_name": "默认供应商",
        "buyer_name": "采购员",
        "unit_remark": "备注",
    }

    @classmethod
    def create_product_profile_export_task(
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
        products = cls._get_products_for_scope(env, normalized_ids)

        scope_vals = {
            "object_type": object_type,
            "entry_type": entry_type,
            "source_model": source_model,
            "source_page": (source_page or cls.SOURCE_PAGE_DEFAULT).strip() or cls.SOURCE_PAGE_DEFAULT,
            "selected_ids_json": normalized_ids,
            "selected_count": len(normalized_ids),
            "scope_snapshot_json": scope_snapshot or cls._build_scope_snapshot(products),
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
                "summary_message": f"Export task created, waiting to run. Total {len(normalized_ids)} product profiles.",
            }
        )
        line_vals_list = []
        for index, product in enumerate(products, start=1):
            line_vals_list.append(
                {
                    "task_id": task.id,
                    "line_no": index,
                    "target_object_type": cls.TARGET_OBJECT_TYPE,
                    "target_res_model": cls.SOURCE_MODEL,
                    "target_res_id": product.id,
                    "business_key": cls._product_business_key(product),
                    "display_name": f"Product {product.display_name or product.id}",
                    "status": "pending",
                }
            )
        if line_vals_list:
            env["logistics.export.task.line"].sudo().create(line_vals_list)
        return cls._build_created_task_payload(task.sudo())

    @classmethod
    def run_product_profile_export_task(cls, env, *, task_no="", task=None):
        task = cls._get_product_profile_task(env, task_no=task_no, task=task)
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
        try:
            product_profile_rows = []
            product_unit_rows = []
            error_vals_list = []
            success_count = 0
            fail_count = 0
            skipped_count = 0
            product_count = 0
            product_unit_count = 0

            for task_line in task.sudo().task_line_ids.sorted(key=lambda rec: (rec.line_no, rec.id)):
                try:
                    package = cls._collect_product_profile_package(env, task_line)
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
                    product_profile_rows.extend(package["product_profile_rows"])
                    product_unit_rows.extend(package["product_unit_rows"])
                    success_count += 1
                    product_count += package["product_count"]
                    product_unit_count += package["product_unit_count"]
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
                            field_name="product_tmpl_id",
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
                            field_name="product_tmpl_id",
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
                            "product_profile_rows": product_profile_rows,
                            "product_unit_rows": product_unit_rows,
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
                "package_metrics_json": {
                    "product_count": product_count,
                    "product_unit_count": product_unit_count,
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
        except Exception as error:
            error_code = error.error_code if isinstance(error, ExportServiceError) else "EXPORT_TASK_RUN_ABORTED"
            error_message = str(error)
            cls._mark_task_failed_if_running(task, error_code=error_code, error_message=error_message)
            if isinstance(error, ExportServiceError):
                raise
            raise ExportServiceError(error_code, error_message) from error

    @classmethod
    def get_export_task_result(cls, env, *, task_no):
        task = cls._get_product_profile_task(env, task_no=task_no)
        cls._ensure_task_access(env, task)
        cls._mark_task_expired_if_needed(task)
        return cls._build_task_result_payload(task.sudo())

    @classmethod
    def get_export_task_lines(cls, env, *, task_no, page=1, page_size=20, status=""):
        task = cls._get_product_profile_task(env, task_no=task_no)
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
        task = cls._get_product_profile_task(env, task_no=task_no)
        cls._ensure_task_access(env, task)
        return super().get_export_task_errors(env, task_no=task.task_no, page=page, page_size=page_size)

    @classmethod
    def build_export_task_error_report(cls, env, *, task_no):
        task = cls._get_product_profile_task(env, task_no=task_no)
        cls._ensure_task_access(env, task)
        return super().build_export_task_error_report(env, task_no=task.task_no)

    @classmethod
    def get_export_download_file(cls, env, *, task_no):
        task = cls._get_product_profile_task(env, task_no=task_no)
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
    def _get_products_for_scope(cls, env, selected_ids):
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
            raise ExportServiceError("EXPORT_PRODUCT_PROFILE_NOT_FOUND", f"Product ids not found or not readable: {missing_ids}")
        return model.browse([record.id for record in ordered_records])

    @classmethod
    def _build_scope_snapshot(cls, products):
        items = []
        for product in products:
            items.append(
                {
                    "id": product.id,
                    "external_product_code": product.external_product_code or "",
                    "internal_product_code": product.internal_product_code or "",
                    "product_name": product.product_name or product.name or "",
                }
            )
        return {
            "object_type": cls.OBJECT_TYPE,
            "entry_type": cls.ENTRY_TYPE,
            "selected_count": len(items),
            "items": items,
        }

    @classmethod
    def _get_product_profile_task(cls, env, *, task_no="", task=None):
        task = super()._get_task(env, task_no=task_no, task=task)
        if task.object_type != cls.OBJECT_TYPE:
            raise ExportServiceError(
                "EXPORT_TASK_OBJECT_TYPE_INVALID",
                f"Task {task.task_no} does not belong to object_type {cls.OBJECT_TYPE}.",
            )
        return task

    @classmethod
    def _collect_product_profile_package(cls, env, task_line):
        product = env[cls.SOURCE_MODEL].browse(task_line.target_res_id).exists()
        if not product:
            raise ExportServiceError(
                "EXPORT_PRODUCT_PROFILE_NOT_FOUND",
                f"Product profile for line {task_line.line_no} was not found.",
            )
        cls._validate_product_header(product)
        product_units = cls._get_product_units_for_product(env, product)
        product_key = cls._product_business_key(product)
        product_row = cls._build_product_profile_row(product)
        product_unit_rows = [cls._build_product_unit_row(product_key, unit) for unit in product_units]
        return {
            "product_profile_rows": [product_row],
            "product_unit_rows": product_unit_rows,
            "product_count": 1,
            "product_unit_count": len(product_unit_rows),
            "line_metrics_json": {
                "product_count": 1,
                "product_unit_count": len(product_unit_rows),
            },
        }

    @classmethod
    def _validate_product_header(cls, product):
        required_values = {
            "product_name": product.product_name or product.name,
        }
        missing_fields = [field_name for field_name, value in required_values.items() if not value]
        if missing_fields:
            raise ExportServiceError(
                "EXPORT_PRODUCT_PROFILE_DATA_INCOMPLETE",
                f"Product {product.display_name or product.id} is missing required fields: {', '.join(missing_fields)}.",
            )

    @classmethod
    def _get_product_units_for_product(cls, env, product):
        unit_model = env[cls.PRODUCT_UNIT_MODEL]
        unit_model.check_access_rights("read")
        units = unit_model.search([("product_tmpl_id", "=", product.id)], order="id asc")
        units.check_access_rule("read")
        broken_units = units.filtered(lambda rec: rec.product_tmpl_id.id != product.id)
        if broken_units:
            raise ExportServiceError(
                "EXPORT_PRODUCT_UNIT_RELATION_BROKEN",
                f"Product {product.display_name or product.id} has broken unit relations.",
            )
        return units

    @classmethod
    def _build_product_profile_row(cls, product):
        return cls._normalize_row(
            cls.SHEETS[0],
            {
                "external_product_code": product.external_product_code or "",
                "internal_product_code": product.internal_product_code or "",
                "product_name": product.product_name or product.name or "",
                "brand_name": product.brand_name or "",
                "category_name": product.category_name or "",
                "product_tag": product.product_tag or "",
                "default_barcode": product.default_barcode or "",
                "base_unit_name": product.base_unit_name or "",
                "default_weight": cls._format_value(product.default_weight),
                "default_volume": cls._format_value(product.default_volume),
                "delivery_requirement_text": product.delivery_requirement_text or "",
            },
        )

    @classmethod
    def _build_product_unit_row(cls, product_key, unit):
        return cls._normalize_row(
            cls.SHEETS[1],
            {
                "product_key": product_key,
                "sku_code": unit.sku_code or "",
                "spec_desc": unit.spec_desc or "",
                "full_category_name": unit.full_category_name or "",
                "unit_name": unit.unit_name or "",
                "sale_unit_name": unit.sale_unit_name or "",
                "convert_to_base": cls._format_value(unit.convert_to_base),
                "barcode": unit.barcode or "",
                "standard_price": cls._format_value(unit.standard_price),
                "purchase_price": cls._format_value(unit.purchase_price),
                "retail_price": cls._format_value(unit.retail_price),
                "sale_tax_rate": cls._format_value(unit.sale_tax_rate),
                "length_cm": cls._format_value(unit.length_cm),
                "width_cm": cls._format_value(unit.width_cm),
                "height_cm": cls._format_value(unit.height_cm),
                "weight": cls._format_value(unit.weight),
                "volume": cls._format_value(unit.volume),
                "large_unit_qty": cls._format_value(unit.large_unit_qty),
                "min_order_qty": cls._format_value(unit.min_order_qty),
                "can_press_stock": cls._bool_flag(unit.can_press_stock),
                "brand_owner_name": unit.brand_owner_name or "",
                "default_vendor_name": unit.default_vendor_name or "",
                "buyer_name": unit.buyer_name or "",
                "unit_remark": unit.unit_remark or "",
            },
        )

    @classmethod
    def _store_output_file(cls, task, workbook_bytes):
        task.ensure_one()
        timestamp = fields.Datetime.now()
        file_name = f"TSL-EXPORT-PRODUCT-PROFILE-{timestamp.strftime('%Y%m%d-%H%M%S')}.xlsx"
        return cls._store_output_file_bytes(task, workbook_bytes, file_name=file_name)

    @classmethod
    def _build_summary_message(cls, *, success_count, fail_count, skipped_count, task_level_error_message):
        if task_level_error_message:
            return task_level_error_message
        return (
            f"Product profile export finished. Success {success_count}, "
            f"failed {fail_count}, skipped {skipped_count}."
        )

    @classmethod
    def _build_task_line_message(cls, package):
        return (
            f"Exported ProductProfile {package['product_count']} / "
            f"ProductUnit {package['product_unit_count']}."
        )

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
                "product_count": int(business_metrics.get("product_count", 0) or 0),
                "product_unit_count": int(business_metrics.get("product_unit_count", 0) or 0),
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
        product_count = int(line_metrics.get("product_count", 0) or 0)
        product_unit_count = int(line_metrics.get("product_unit_count", 0) or 0)
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
            "export_count_summary": f"ProductProfile {product_count} / ProductUnit {product_unit_count}",
            "line_metrics": {
                "product_count": product_count,
                "product_unit_count": product_unit_count,
            },
            "exported_waybill_count": task_line.exported_waybill_count,
            "exported_customer_line_count": task_line.exported_customer_line_count,
            "exported_order_line_count": task_line.exported_order_line_count,
            "exported_goods_line_count": task_line.exported_goods_line_count,
        }

    @classmethod
    def _error_stage_for_code(cls, error_code):
        if error_code in ("EXPORT_PRODUCT_PROFILE_NOT_FOUND",):
            return "target_resolve"
        if error_code in ("EXPORT_PRODUCT_PROFILE_DATA_INCOMPLETE", "EXPORT_PRODUCT_UNIT_RELATION_BROKEN"):
            return "data_collect"
        if error_code == "EXPORT_WORKBOOK_BUILD_FAILED":
            return "workbook_build"
        if error_code in ("EXPORT_FILE_WRITE_FAILED", "EXPORT_FILE_READ_FAILED", "EXPORT_OUTPUT_FILE_MISSING"):
            return "file_store"
        return "scope_validate"

    @classmethod
    def _product_business_key(cls, product):
        return (
            product.external_product_code
            or product.internal_product_code
            or product.product_name
            or product.name
            or str(product.id)
        )
