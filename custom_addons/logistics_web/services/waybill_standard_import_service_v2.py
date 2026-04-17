import csv
import hashlib
import io
from datetime import datetime

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font

from odoo import fields
from odoo.exceptions import ValidationError


class WaybillStandardImportService:
    TEMPLATE_CODE = "TSL-IMPORT-WAYBILL-V2"
    TEMPLATE_VERSION = "v2"
    TEMPLATE_FILE_NAME = "TSL-IMPORT-WAYBILL-V2.xlsx"
    TEMPLATE_VARIANTS = {
        "en_US": {
            "label": "标准模板（英文列头）",
            "file_name": "TSL-IMPORT-WAYBILL-V2.xlsx",
            "field_locale": "en_US",
        },
        "zh_CN": {
            "label": "标准模板（中文列头）",
            "file_name": "TSL-IMPORT-WAYBILL-V2.zh_CN.xlsx",
            "field_locale": "zh_CN",
        },
    }
    DEFAULT_TEMPLATE_LOCALE = "zh_CN"
    FIELD_LABELS = {
        "waybill_no": "运单号",
        "batch_no": "批次号",
        "wave_no": "波次号",
        "delivery_date": "配送日期",
        "warehouse_code": "仓库编码",
        "vehicle_no": "车辆号",
        "driver_name": "司机姓名",
        "driver_phone": "司机电话",
        "remark": "运单备注",
        "customer_no": "客户编号",
        "customer_name": "客户名称",
        "store_no": "门店编号",
        "store_name": "门店名称",
        "delivery_remark": "客户配送备注",
        "signoff_requirement": "签收要求",
        "customer_ref": "客户外部参考号",
        "goods_code": "货物编码",
        "goods_name": "货物名称",
        "spec": "规格",
        "qty": "数量",
        "package_count": "件数",
        "uom_name": "单位",
        "weight": "重量",
        "volume": "体积",
        "temperature_zone": "温层",
        "package_type": "包装类型",
        "template_file": "模板文件",
    }
    SHEETS = [
        {
            "key": "waybill_rows",
            "sheet_name": "运单",
            "fields": [
                "waybill_no",
                "batch_no",
                "wave_no",
                "delivery_date",
                "warehouse_code",
                "vehicle_no",
                "driver_name",
                "driver_phone",
                "remark",
            ],
            "required_fields": {"waybill_no"},
        },
        {
            "key": "customer_rows",
            "sheet_name": "客户明细",
            "fields": [
                "waybill_no",
                "customer_no",
                "customer_name",
                "store_no",
                "store_name",
                "delivery_remark",
                "signoff_requirement",
                "customer_ref",
            ],
            "required_fields": {"waybill_no", "customer_no"},
        },
        {
            "key": "goods_rows",
            "sheet_name": "货物明细",
            "fields": [
                "waybill_no",
                "customer_no",
                "store_no",
                "goods_code",
                "goods_name",
                "spec",
                "qty",
                "package_count",
                "uom_name",
                "weight",
                "volume",
                "temperature_zone",
                "package_type",
                "remark",
            ],
            "required_fields": {"waybill_no", "customer_no", "goods_name", "qty"},
        },
    ]
    STATUS_LABELS = {
        "prechecked": "已预校验",
        "importing": "导入中",
        "finished": "已完成",
        "failed": "已失败",
        "expired": "已失效",
    }
    ALLOWED_TEMPERATURE_ZONES = {"ambient", "chilled", "frozen", "other"}
    ERROR_REPORT_HEADERS = [
        ("sheet_name", "Sheet"),
        ("row_no", "行号"),
        ("field_code", "字段编码"),
        ("field_label", "字段名称"),
        ("error_code", "错误编码"),
        ("error_message", "错误说明"),
    ]
    FIELD_ALIASES = {
        "waybill_no": ["waybill_no", "waybill no", "运单号"],
        "batch_no": ["batch_no", "batch no", "批次号"],
        "wave_no": ["wave_no", "wave no", "波次号"],
        "delivery_date": ["delivery_date", "delivery date", "配送日期"],
        "warehouse_code": ["warehouse_code", "warehouse code", "仓库编码"],
        "vehicle_no": ["vehicle_no", "vehicle no", "车辆号"],
        "driver_name": ["driver_name", "driver name", "司机姓名"],
        "driver_phone": ["driver_phone", "driver phone", "司机电话"],
        "remark": ["remark", "运单备注", "备注", "货物备注"],
        "customer_no": ["customer_no", "customer no", "客户编号", "客户号"],
        "customer_name": ["customer_name", "customer name", "客户名称"],
        "store_no": ["store_no", "store no", "门店编号", "门店号"],
        "store_name": ["store_name", "store name", "门店名称"],
        "delivery_remark": ["delivery_remark", "delivery remark", "客户配送备注", "配送备注"],
        "signoff_requirement": ["signoff_requirement", "signoff requirement", "签收要求"],
        "customer_ref": ["customer_ref", "customer ref", "客户外部参考号"],
        "goods_code": ["goods_code", "goods code", "货物编码"],
        "goods_name": ["goods_name", "goods name", "货物名称"],
        "spec": ["spec", "specification", "规格"],
        "qty": ["qty", "quantity", "数量"],
        "package_count": ["package_count", "package count", "件数"],
        "uom_name": ["uom_name", "uom name", "单位"],
        "weight": ["weight", "重量"],
        "volume": ["volume", "体积"],
        "temperature_zone": ["temperature_zone", "temperature zone", "温层"],
        "package_type": ["package_type", "package type", "包装类型"],
    }

    @classmethod
    def build_template_payload(cls):
        default_locale = cls.DEFAULT_TEMPLATE_LOCALE
        return {
            "template_code": cls.TEMPLATE_CODE,
            "template_version": cls.TEMPLATE_VERSION,
            "default_template_locale": default_locale,
            "file_name": cls.TEMPLATE_VARIANTS[default_locale]["file_name"],
            "download_url": cls._build_template_download_url(template_locale=default_locale),
            "available_templates": [
                {
                    "template_locale": template_locale,
                    "template_label": template_meta["label"],
                    "file_name": template_meta["file_name"],
                    "download_url": cls._build_template_download_url(template_locale=template_locale),
                }
                for template_locale, template_meta in cls.TEMPLATE_VARIANTS.items()
            ],
            "sheets": [
                {
                    "sheet_name": sheet_meta["sheet_name"],
                    "fields": [
                        {"field_code": field_code, "field_label": cls.FIELD_LABELS[field_code]}
                        for field_code in sheet_meta["fields"]
                    ],
                }
                for sheet_meta in cls.SHEETS
            ],
        }

    @classmethod
    def load_template_bytes(cls, *, template_locale=""):
        template_variant = cls.get_template_variant(template_locale)
        workbook = Workbook()
        default_sheet = workbook.active
        workbook.remove(default_sheet)
        field_locale = template_variant["field_locale"]
        samples = cls._build_template_samples()
        for sheet_meta in cls.SHEETS:
            worksheet = workbook.create_sheet(sheet_meta["sheet_name"])
            headers = [cls._get_field_header(field_code, field_locale) for field_code in sheet_meta["fields"]]
            worksheet.append(headers)
            for cell in worksheet[1]:
                cell.font = Font(bold=True)
            for sample_row in samples[sheet_meta["key"]]:
                worksheet.append([sample_row.get(field_code, "") for field_code in sheet_meta["fields"]])
        buffer = io.BytesIO()
        workbook.save(buffer)
        return buffer.getvalue()

    @classmethod
    def get_template_variant(cls, template_locale=""):
        normalized_locale = cls.normalize_template_locale(template_locale)
        variant = cls.TEMPLATE_VARIANTS.get(normalized_locale)
        if not variant:
            supported_locales = " / ".join(cls.TEMPLATE_VARIANTS.keys())
            raise ValidationError(f"模板语言非法，请使用 {supported_locales} 之一。")
        return {"template_locale": normalized_locale, **variant}

    @classmethod
    def normalize_template_locale(cls, template_locale=""):
        return (template_locale or cls.DEFAULT_TEMPLATE_LOCALE).strip() or cls.DEFAULT_TEMPLATE_LOCALE

    @classmethod
    def precheck(cls, env, raw_bytes, *, filename="", template_code="", template_version=""):
        template_errors = cls._validate_template_identity(template_code, template_version)
        parsed_data, parse_errors = cls._parse_workbook(raw_bytes)
        errors = template_errors + parse_errors
        if not parse_errors:
            errors.extend(cls._validate_rows(env, parsed_data))

        result = cls._build_precheck_result(parsed_data, errors)
        batch = env["logistics.import.batch"].sudo().create(
            env["logistics.import.batch"].build_precheck_vals(
                template_code=cls.TEMPLATE_CODE,
                template_version=cls.TEMPLATE_VERSION,
                file_name=filename or cls.TEMPLATE_FILE_NAME,
                file_checksum=hashlib.sha256(raw_bytes or b"").hexdigest(),
                total_row_count=result["total_row_count"],
                passed_row_count=result["passed_row_count"],
                failed_row_count=result["failed_row_count"],
                can_confirm_import=result["can_confirm_import"],
                source_rows=parsed_data,
                errors=result["errors"],
            )
        )
        error_report_url = cls._build_error_report_url(batch) if result["errors"] else False
        batch.sudo().write({"error_report_url": error_report_url})
        result["import_batch_no"] = batch.name
        result["precheck_token"] = batch.precheck_token
        result["error_report_url"] = error_report_url
        return result

    @classmethod
    def confirm_import(cls, env, *, precheck_token, import_batch_no=""):
        batch = cls._get_batch_by_precheck_token(env, precheck_token)
        batch.mark_expired_if_needed()
        if batch.state == "finished":
            return cls._build_result_payload(batch)
        if batch.state == "expired":
            raise ValidationError("预校验令牌已失效，请重新执行预校验。")
        if batch.state == "failed":
            raise ValidationError(batch.failure_reason or "这批数据导入失败，请重新执行预校验。")
        if batch.state != "prechecked":
            raise ValidationError("当前批次状态不允许正式导入。")
        if not batch.can_confirm_import:
            raise ValidationError("预校验未通过，不能执行正式导入。")

        if import_batch_no and import_batch_no != batch.name:
            existing_batch = env["logistics.import.batch"].sudo().search([("name", "=", import_batch_no)], limit=1)
            if existing_batch:
                raise ValidationError("导入批次号已存在，请更换后重试。")
            batch.sudo().write({"name": import_batch_no})

        source_data = batch.get_source_rows()
        stats = {
            "created_waybill_count": 0,
            "created_customer_line_count": 0,
            "created_goods_line_count": 0,
            "updated_record_count": 0,
            "skipped_record_count": 0,
            "failed_record_count": 0,
        }
        batch.sudo().write({"state": "importing", "confirmed_at": fields.Datetime.now(), "failure_reason": False})
        try:
            cls._apply_import(env, source_data, stats)
        except Exception as exc:
            batch.sudo().write(
                {
                    "state": "failed",
                    "finished_at": fields.Datetime.now(),
                    "failed_record_count": cls._count_total_rows(source_data),
                    "failure_reason": str(exc),
                }
            )
            raise ValidationError(f"正式导入失败：{exc}") from exc

        batch.sudo().write({"state": "finished", "finished_at": fields.Datetime.now(), **stats})
        return cls._build_result_payload(batch)

    @classmethod
    def get_import_result(cls, env, *, import_batch_no):
        if not import_batch_no:
            raise ValidationError("请提供导入批次号。")
        batch = env["logistics.import.batch"].sudo().search([("name", "=", import_batch_no)], limit=1)
        if not batch:
            raise ValidationError("未找到对应的导入批次。")
        batch.mark_expired_if_needed()
        return cls._build_result_payload(batch)

    @classmethod
    def build_error_report(cls, env, *, import_batch_no="", precheck_token=""):
        batch = cls._get_batch_for_error_report(env, import_batch_no=import_batch_no, precheck_token=precheck_token)
        errors = batch.get_errors()
        if not errors:
            raise ValidationError("当前批次没有可导出的预校验错误报告。")

        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow([header_label for _, header_label in cls.ERROR_REPORT_HEADERS])
        for error in errors:
            writer.writerow([error.get(field_code, "") for field_code, _label in cls.ERROR_REPORT_HEADERS])

        return {
            "file_name": f"{batch.name}-error-report.csv",
            "file_bytes": buffer.getvalue().encode("utf-8-sig"),
            "content_type": "text/csv; charset=utf-8",
        }

    @classmethod
    def _build_template_samples(cls):
        return {
            "waybill_rows": [
                {
                    "waybill_no": "WB260416-0001",
                    "batch_no": "BT260416-0001",
                    "wave_no": "WV260416-01",
                    "delivery_date": "2026-04-16",
                    "warehouse_code": "",
                    "vehicle_no": "",
                    "driver_name": "",
                    "driver_phone": "",
                    "remark": "上午配送",
                }
            ],
            "customer_rows": [
                {
                    "waybill_no": "WB260416-0001",
                    "customer_no": "CUST-001",
                    "customer_name": "华东客户A",
                    "store_no": "STORE-001",
                    "store_name": "浦东门店",
                    "delivery_remark": "后门卸货",
                    "signoff_requirement": "门店负责人签收",
                    "customer_ref": "ERP-CUST-001",
                },
                {
                    "waybill_no": "WB260416-0001",
                    "customer_no": "CUST-002",
                    "customer_name": "华北客户B",
                    "store_no": "STORE-002",
                    "store_name": "朝阳门店",
                    "delivery_remark": "上午优先",
                    "signoff_requirement": "",
                    "customer_ref": "",
                },
            ],
            "goods_rows": [
                {
                    "waybill_no": "WB260416-0001",
                    "customer_no": "CUST-001",
                    "store_no": "STORE-001",
                    "goods_code": "SKU-001",
                    "goods_name": "鲜牛奶",
                    "spec": "250ml*24",
                    "qty": "120",
                    "package_count": "10",
                    "uom_name": "箱",
                    "weight": "360",
                    "volume": "1.2",
                    "temperature_zone": "chilled",
                    "package_type": "carton",
                    "remark": "优先卸货",
                },
                {
                    "waybill_no": "WB260416-0001",
                    "customer_no": "CUST-002",
                    "store_no": "STORE-002",
                    "goods_code": "SKU-003",
                    "goods_name": "速冻水饺",
                    "spec": "1kg*8",
                    "qty": "32",
                    "package_count": "4",
                    "uom_name": "箱",
                    "weight": "128",
                    "volume": "0.9",
                    "temperature_zone": "frozen",
                    "package_type": "foam_box",
                    "remark": "保持冷冻",
                },
            ],
        }

    @classmethod
    def _get_field_header(cls, field_code, field_locale):
        if field_locale == "en_US":
            return field_code
        return cls.FIELD_LABELS[field_code]

    @classmethod
    def _validate_template_identity(cls, template_code, template_version):
        errors = []
        normalized_code = (template_code or cls.TEMPLATE_CODE).strip()
        normalized_version = (template_version or cls.TEMPLATE_VERSION).strip().lower()
        if normalized_code != cls.TEMPLATE_CODE:
            errors.append(
                cls._make_error(
                    sheet_name="模板文件",
                    row_no=0,
                    field_code="template_file",
                    error_code="TEMPLATE_CODE_INVALID",
                    error_message=f"请使用标准模板 {cls.TEMPLATE_CODE}。",
                )
            )
        if normalized_version != cls.TEMPLATE_VERSION:
            errors.append(
                cls._make_error(
                    sheet_name="模板文件",
                    row_no=0,
                    field_code="template_file",
                    error_code="TEMPLATE_VERSION_INVALID",
                    error_message=f"请使用模板版本 {cls.TEMPLATE_VERSION}。",
                )
            )
        return errors

    @classmethod
    def _parse_workbook(cls, raw_bytes):
        if not raw_bytes:
            return cls._empty_source_data(), [
                cls._make_error(
                    sheet_name="模板文件",
                    row_no=0,
                    field_code="template_file",
                    error_code="PRECHECK_PARSE_FAILED",
                    error_message="未检测到上传文件，请先选择标准导入模板文件。",
                )
            ]

        try:
            workbook = load_workbook(io.BytesIO(raw_bytes), data_only=True)
        except Exception:
            return cls._empty_source_data(), [
                cls._make_error(
                    sheet_name="模板文件",
                    row_no=0,
                    field_code="template_file",
                    error_code="TEMPLATE_FILE_TYPE_INVALID",
                    error_message="模板解析失败，请上传 .xlsx 标准模板。",
                )
            ]

        source_data = cls._empty_source_data()
        errors = []
        for sheet_meta in cls.SHEETS:
            sheet_name = sheet_meta["sheet_name"]
            if sheet_name not in workbook.sheetnames:
                errors.append(
                    cls._make_error(
                        sheet_name="模板文件",
                        row_no=0,
                        field_code="template_file",
                        error_code="TEMPLATE_SHEET_MISSING",
                        error_message=f"模板缺少工作表：{sheet_name}。",
                    )
                )
                continue

            worksheet = workbook[sheet_name]
            rows = list(worksheet.iter_rows(values_only=True))
            if not rows:
                errors.append(
                    cls._make_error(
                        sheet_name=sheet_name,
                        row_no=0,
                        field_code="template_file",
                        error_code="TEMPLATE_HEADER_MISMATCH",
                        error_message=f"{sheet_name} 工作表没有表头。",
                    )
                )
                continue

            header_values = [cls._cell_text(value) for value in rows[0]]
            header_map, header_errors = cls._build_header_map(sheet_meta, header_values)
            if header_errors:
                errors.extend(header_errors)
                continue

            parsed_rows = []
            for row_index, row_values in enumerate(rows[1:], start=2):
                normalized_row = {field_code: "" for field_code in sheet_meta["fields"]}
                has_value = False
                for col_index, header_value in enumerate(header_values):
                    if not header_value:
                        continue
                    field_code = header_map.get(col_index)
                    if not field_code:
                        continue
                    cell_value = cls._cell_text(row_values[col_index] if col_index < len(row_values) else "")
                    normalized_row[field_code] = cell_value
                    if cell_value:
                        has_value = True
                if not has_value:
                    continue
                normalized_row["_sheet_name"] = sheet_name
                normalized_row["_source_row_no"] = row_index
                parsed_rows.append(normalized_row)

            if not parsed_rows:
                errors.append(
                    cls._make_error(
                        sheet_name=sheet_name,
                        row_no=0,
                        field_code="template_file",
                        error_code="TEMPLATE_SHEET_EMPTY",
                        error_message=f"{sheet_name} 工作表没有可导入数据。",
                    )
                )
                continue
            source_data[sheet_meta["key"]] = parsed_rows

        return source_data, errors

    @classmethod
    def _build_header_map(cls, sheet_meta, header_values):
        normalized_headers = {
            cls._normalize_header(header_value): index
            for index, header_value in enumerate(header_values)
            if header_value
        }
        header_map = {}
        missing_fields = []
        for field_code in sheet_meta["fields"]:
            matched_index = None
            for alias in cls.FIELD_ALIASES[field_code]:
                alias_index = normalized_headers.get(cls._normalize_header(alias))
                if alias_index is not None:
                    matched_index = alias_index
                    break
            if matched_index is None:
                missing_fields.append(cls.FIELD_LABELS[field_code])
                continue
            header_map[matched_index] = field_code

        if missing_fields:
            return {}, [
                cls._make_error(
                    sheet_name=sheet_meta["sheet_name"],
                    row_no=0,
                    field_code="template_file",
                    error_code="TEMPLATE_HEADER_MISMATCH",
                    error_message=f"{sheet_meta['sheet_name']} 列头不匹配，缺少这些字段：{' / '.join(missing_fields)}。",
                )
            ]
        return header_map, []

    @classmethod
    def _validate_rows(cls, env, source_data):
        errors = []
        waybill_rows = source_data["waybill_rows"]
        customer_rows = source_data["customer_rows"]
        goods_rows = source_data["goods_rows"]

        customers_by_code = cls._search_partner_map(
            env,
            model_domain=[("is_logistics_customer", "=", True)],
            field_name="logistics_customer_code",
            values={row["customer_no"] for row in customer_rows + goods_rows if row.get("customer_no")},
        )
        stores_by_code = cls._search_partner_map(
            env,
            model_domain=[("is_logistics_store", "=", True)],
            field_name="logistics_store_code",
            values={row["store_no"] for row in customer_rows + goods_rows if row.get("store_no")},
        )
        batches_by_no = cls._search_record_map(
            env,
            model_name="logistics.dispatch.batch",
            field_name="name",
            values={row["batch_no"] for row in waybill_rows if row.get("batch_no")},
        )
        waves_by_no = cls._search_record_map(
            env,
            model_name="logistics.dispatch.wave",
            field_name="name",
            values={row["wave_no"] for row in waybill_rows if row.get("wave_no")},
        )
        existing_waybills = cls._search_record_map(
            env,
            model_name="logistics.dispatch.waybill",
            field_name="name",
            values={row["waybill_no"] for row in waybill_rows if row.get("waybill_no")},
        )
        warehouses_by_code = cls._search_record_map(
            env,
            model_name="stock.warehouse",
            field_name="code",
            values={row["warehouse_code"] for row in waybill_rows if row.get("warehouse_code")},
        )

        waybill_rows_by_no = {}
        for row in waybill_rows:
            errors.extend(cls._validate_required_fields(row, {"waybill_no"}))
            errors.extend(cls._validate_waybill_row(row, batches_by_no, waves_by_no, existing_waybills, warehouses_by_code))
            waybill_no = row.get("waybill_no")
            if waybill_no in waybill_rows_by_no:
                errors.append(
                    cls._make_error(
                        sheet_name=row["_sheet_name"],
                        row_no=row["_source_row_no"],
                        field_code="waybill_no",
                        error_code="WAYBILL_DUPLICATED_IN_SHEET",
                        error_message="同一个运单号在“运单”工作表中只能出现一次。",
                    )
                )
            else:
                waybill_rows_by_no[waybill_no] = row

        customer_rows_by_key = {}
        for row in customer_rows:
            errors.extend(cls._validate_required_fields(row, {"waybill_no", "customer_no"}))
            errors.extend(cls._validate_customer_row(row, customers_by_code, stores_by_code))
            if row.get("waybill_no") and row["waybill_no"] not in waybill_rows_by_no:
                errors.append(
                    cls._make_error(
                        sheet_name=row["_sheet_name"],
                        row_no=row["_source_row_no"],
                        field_code="waybill_no",
                        error_code="WAYBILL_NOT_FOUND_IN_WAYBILL_SHEET",
                        error_message="客户明细引用的运单号未在“运单”工作表中找到。",
                    )
                )
            customer_key = cls._customer_key(row)
            if customer_key in customer_rows_by_key:
                errors.append(
                    cls._make_error(
                        sheet_name=row["_sheet_name"],
                        row_no=row["_source_row_no"],
                        field_code="customer_no",
                        error_code="CUSTOMER_LINE_DUPLICATED_IN_SHEET",
                        error_message="同一运单号 + 客户编号 + 门店编号在“客户明细”工作表中只能出现一次。",
                    )
                )
            else:
                customer_rows_by_key[customer_key] = row

        goods_keys = set()
        for row in goods_rows:
            errors.extend(cls._validate_required_fields(row, {"waybill_no", "customer_no", "goods_name", "qty"}))
            errors.extend(cls._validate_goods_row(row))
            if row.get("customer_no") and row["customer_no"] not in customers_by_code:
                errors.append(
                    cls._make_error(
                        sheet_name=row["_sheet_name"],
                        row_no=row["_source_row_no"],
                        field_code="customer_no",
                        error_code="CUSTOMER_NO_NOT_FOUND",
                        error_message="客户编号不存在，请先维护客户主数据。",
                    )
                )
            if row.get("store_no") and row["store_no"] not in stores_by_code:
                errors.append(
                    cls._make_error(
                        sheet_name=row["_sheet_name"],
                        row_no=row["_source_row_no"],
                        field_code="store_no",
                        error_code="STORE_NO_NOT_FOUND",
                        error_message="门店编号不存在，请先维护门店主数据。",
                    )
                )
            if row.get("waybill_no") and row["waybill_no"] not in waybill_rows_by_no:
                errors.append(
                    cls._make_error(
                        sheet_name=row["_sheet_name"],
                        row_no=row["_source_row_no"],
                        field_code="waybill_no",
                        error_code="WAYBILL_NOT_FOUND_IN_WAYBILL_SHEET",
                        error_message="货物明细引用的运单号未在“运单”工作表中找到。",
                    )
                )
            if cls._customer_key(row) not in customer_rows_by_key:
                errors.append(
                    cls._make_error(
                        sheet_name=row["_sheet_name"],
                        row_no=row["_source_row_no"],
                        field_code="customer_no",
                        error_code="CUSTOMER_LINE_NOT_FOUND_IN_CUSTOMER_SHEET",
                        error_message="货物明细引用的客户层记录未在“客户明细”工作表中找到。",
                    )
                )
            goods_key = cls._goods_key(row)
            if goods_key in goods_keys:
                errors.append(
                    cls._make_error(
                        sheet_name=row["_sheet_name"],
                        row_no=row["_source_row_no"],
                        field_code="goods_name",
                        error_code="GOODS_LINE_DUPLICATED_IN_SHEET",
                        error_message="检测到重复货物明细，请在“货物明细”工作表中去重。",
                    )
                )
            else:
                goods_keys.add(goods_key)

        return errors

    @classmethod
    def _validate_required_fields(cls, row, required_fields):
        errors = []
        for field_code in required_fields:
            if row.get(field_code):
                continue
            errors.append(
                cls._make_error(
                    sheet_name=row["_sheet_name"],
                    row_no=row["_source_row_no"],
                    field_code=field_code,
                    error_code="FIELD_REQUIRED",
                    error_message=f"{cls.FIELD_LABELS[field_code]}不能为空。",
                )
            )
        return errors

    @classmethod
    def _validate_waybill_row(cls, row, batches_by_no, waves_by_no, existing_waybills, warehouses_by_code):
        errors = []
        if row.get("delivery_date"):
            try:
                datetime.strptime(row["delivery_date"], "%Y-%m-%d")
            except ValueError:
                errors.append(
                    cls._make_error(
                        sheet_name=row["_sheet_name"],
                        row_no=row["_source_row_no"],
                        field_code="delivery_date",
                        error_code="FIELD_FORMAT_INVALID",
                        error_message="配送日期格式必须为 YYYY-MM-DD。",
                    )
                )
        if row.get("waybill_no") and row["waybill_no"] in existing_waybills:
            errors.append(
                cls._make_error(
                    sheet_name=row["_sheet_name"],
                    row_no=row["_source_row_no"],
                    field_code="waybill_no",
                    error_code="WAYBILL_NO_ALREADY_EXISTS",
                    error_message="运单号已存在，请更换运单号后重新导入。",
                )
            )
        if row.get("wave_no") and not row.get("batch_no"):
            errors.append(
                cls._make_error(
                    sheet_name=row["_sheet_name"],
                    row_no=row["_source_row_no"],
                    field_code="batch_no",
                    error_code="FIELD_REQUIRED",
                    error_message="填写波次号时必须同时填写批次号。",
                )
            )
        if row.get("batch_no") and row["batch_no"] not in batches_by_no:
            errors.append(
                cls._make_error(
                    sheet_name=row["_sheet_name"],
                    row_no=row["_source_row_no"],
                    field_code="batch_no",
                    error_code="BATCH_NO_NOT_FOUND",
                    error_message="批次号不存在，请先维护批次数据。",
                )
            )
        if row.get("wave_no") and row["wave_no"] not in waves_by_no:
            errors.append(
                cls._make_error(
                    sheet_name=row["_sheet_name"],
                    row_no=row["_source_row_no"],
                    field_code="wave_no",
                    error_code="WAVE_NO_NOT_FOUND",
                    error_message="波次号不存在，请先维护波次数据。",
                )
            )
        batch_record = batches_by_no.get(row.get("batch_no"))
        if batch_record and row.get("wave_no") and batch_record.wave_id and batch_record.wave_id.name != row["wave_no"]:
            errors.append(
                cls._make_error(
                    sheet_name=row["_sheet_name"],
                    row_no=row["_source_row_no"],
                    field_code="wave_no",
                    error_code="WAYBILL_GROUP_CONFLICT",
                    error_message="批次号与波次号不一致，请检查该运单所属批次和波次。",
                )
            )
        if row.get("warehouse_code") and row["warehouse_code"] not in warehouses_by_code:
            errors.append(
                cls._make_error(
                    sheet_name=row["_sheet_name"],
                    row_no=row["_source_row_no"],
                    field_code="warehouse_code",
                    error_code="WAREHOUSE_CODE_NOT_FOUND",
                    error_message="仓库编码不存在，请先维护仓库主数据。",
                )
            )
        return errors

    @classmethod
    def _validate_customer_row(cls, row, customers_by_code, stores_by_code):
        errors = []
        customer_record = customers_by_code.get(row.get("customer_no"))
        if row.get("customer_no") and not customer_record:
            errors.append(
                cls._make_error(
                    sheet_name=row["_sheet_name"],
                    row_no=row["_source_row_no"],
                    field_code="customer_no",
                    error_code="CUSTOMER_NO_NOT_FOUND",
                    error_message="客户编号不存在，请先维护客户主数据。",
                )
            )
        if row.get("store_no") and row["store_no"] not in stores_by_code:
            errors.append(
                cls._make_error(
                    sheet_name=row["_sheet_name"],
                    row_no=row["_source_row_no"],
                    field_code="store_no",
                    error_code="STORE_NO_NOT_FOUND",
                    error_message="门店编号不存在，请先维护门店主数据。",
                )
            )
        store_record = stores_by_code.get(row.get("store_no"))
        if customer_record and row.get("customer_name") and customer_record.name != row["customer_name"]:
            errors.append(
                cls._make_error(
                    sheet_name=row["_sheet_name"],
                    row_no=row["_source_row_no"],
                    field_code="customer_name",
                    error_code="FIELD_VALUE_INVALID",
                    error_message="客户编号与客户名称不一致，请检查客户主数据或模板内容。",
                )
            )
        if store_record and row.get("store_name") and store_record.name != row["store_name"]:
            errors.append(
                cls._make_error(
                    sheet_name=row["_sheet_name"],
                    row_no=row["_source_row_no"],
                    field_code="store_name",
                    error_code="FIELD_VALUE_INVALID",
                    error_message="门店编号与门店名称不一致，请检查门店主数据或模板内容。",
                )
            )
        if customer_record and store_record and store_record.parent_id and store_record.parent_id.id != customer_record.id:
            errors.append(
                cls._make_error(
                    sheet_name=row["_sheet_name"],
                    row_no=row["_source_row_no"],
                    field_code="store_no",
                    error_code="CUSTOMER_STORE_MISMATCH",
                    error_message="门店与客户归属不一致，请检查客户编号和门店编号。",
                )
            )
        return errors

    @classmethod
    def _validate_goods_row(cls, row):
        errors = []
        errors.extend(cls._validate_positive_number(row, "qty", allow_zero=False))
        errors.extend(cls._validate_positive_number(row, "weight", allow_zero=True))
        errors.extend(cls._validate_positive_number(row, "volume", allow_zero=True))
        errors.extend(cls._validate_integer(row, "package_count", allow_zero=True))
        if row.get("temperature_zone") and row["temperature_zone"] not in cls.ALLOWED_TEMPERATURE_ZONES:
            errors.append(
                cls._make_error(
                    sheet_name=row["_sheet_name"],
                    row_no=row["_source_row_no"],
                    field_code="temperature_zone",
                    error_code="FIELD_ENUM_INVALID",
                    error_message="温层必须是 ambient / chilled / frozen / other 之一。",
                )
            )
        return errors

    @classmethod
    def _validate_positive_number(cls, row, field_code, *, allow_zero):
        value = row.get(field_code, "")
        if value == "":
            return []
        try:
            numeric_value = float(value)
        except ValueError:
            return [
                cls._make_error(
                    sheet_name=row["_sheet_name"],
                    row_no=row["_source_row_no"],
                    field_code=field_code,
                    error_code="FIELD_FORMAT_INVALID",
                    error_message=f"{cls.FIELD_LABELS[field_code]}必须是数字。",
                )
            ]
        if allow_zero and numeric_value < 0:
            return [
                cls._make_error(
                    sheet_name=row["_sheet_name"],
                    row_no=row["_source_row_no"],
                    field_code=field_code,
                    error_code="FIELD_VALUE_INVALID",
                    error_message=f"{cls.FIELD_LABELS[field_code]}不能小于 0。",
                )
            ]
        if not allow_zero and numeric_value <= 0:
            return [
                cls._make_error(
                    sheet_name=row["_sheet_name"],
                    row_no=row["_source_row_no"],
                    field_code=field_code,
                    error_code="FIELD_VALUE_INVALID",
                    error_message=f"{cls.FIELD_LABELS[field_code]}必须大于 0。",
                )
            ]
        return []

    @classmethod
    def _validate_integer(cls, row, field_code, *, allow_zero):
        value = row.get(field_code, "")
        if value == "":
            return []
        try:
            numeric_value = int(float(value))
        except ValueError:
            return [
                cls._make_error(
                    sheet_name=row["_sheet_name"],
                    row_no=row["_source_row_no"],
                    field_code=field_code,
                    error_code="FIELD_FORMAT_INVALID",
                    error_message=f"{cls.FIELD_LABELS[field_code]}必须是整数。",
                )
            ]
        if allow_zero and numeric_value < 0:
            return [
                cls._make_error(
                    sheet_name=row["_sheet_name"],
                    row_no=row["_source_row_no"],
                    field_code=field_code,
                    error_code="FIELD_VALUE_INVALID",
                    error_message=f"{cls.FIELD_LABELS[field_code]}不能小于 0。",
                )
            ]
        return []

    @classmethod
    def _search_partner_map(cls, env, *, model_domain, field_name, values):
        if not values:
            return {}
        records = env["res.partner"].sudo().search(model_domain + [(field_name, "in", list(values))])
        return {getattr(record, field_name): record for record in records if getattr(record, field_name)}

    @classmethod
    def _search_record_map(cls, env, *, model_name, field_name, values):
        if not values:
            return {}
        records = env[model_name].sudo().search([(field_name, "in", list(values))])
        return {getattr(record, field_name): record for record in records if getattr(record, field_name)}

    @classmethod
    def _make_error(cls, *, sheet_name, row_no, field_code, error_code, error_message):
        return {
            "sheet_name": sheet_name,
            "row_no": row_no,
            "field_code": field_code,
            "field_label": cls.FIELD_LABELS.get(field_code, field_code),
            "error_code": error_code,
            "error_message": error_message,
        }

    @classmethod
    def _build_precheck_result(cls, source_data, errors):
        failed_row_keys = {
            (error.get("sheet_name"), error.get("row_no"))
            for error in errors
            if error.get("row_no")
        }
        total_row_count = cls._count_total_rows(source_data)
        failed_row_count = len(failed_row_keys)
        if errors and failed_row_count == 0:
            failed_row_count = 1
        return {
            "template_code": cls.TEMPLATE_CODE,
            "template_version": cls.TEMPLATE_VERSION,
            "import_batch_no": False,
            "precheck_token": False,
            "error_report_url": False,
            "total_row_count": total_row_count,
            "passed_row_count": max(total_row_count - failed_row_count, 0),
            "failed_row_count": failed_row_count,
            "can_confirm_import": total_row_count > 0 and not errors,
            "errors": sorted(
                errors,
                key=lambda item: (
                    item.get("sheet_name", ""),
                    item.get("row_no", 0),
                    item.get("field_code", ""),
                    item.get("error_code", ""),
                ),
            ),
        }

    @classmethod
    def _count_total_rows(cls, source_data):
        return sum(len(source_data.get(sheet_meta["key"], [])) for sheet_meta in cls.SHEETS)

    @classmethod
    def _get_batch_by_precheck_token(cls, env, precheck_token):
        if not precheck_token:
            raise ValidationError("请提供预校验令牌。")
        batch = env["logistics.import.batch"].sudo().search([("precheck_token", "=", precheck_token)], limit=1)
        if not batch:
            raise ValidationError("未找到对应的预校验批次。")
        return batch

    @classmethod
    def _get_batch_for_error_report(cls, env, *, import_batch_no="", precheck_token=""):
        batch_model = env["logistics.import.batch"].sudo()
        if import_batch_no:
            batch = batch_model.search([("name", "=", import_batch_no)], limit=1)
            if batch:
                return batch
        if precheck_token:
            batch = batch_model.search([("precheck_token", "=", precheck_token)], limit=1)
            if batch:
                return batch
        raise ValidationError("未找到可导出错误报告的导入批次。")

    @classmethod
    def _apply_import(cls, env, source_data, stats):
        waybill_model = env["logistics.dispatch.waybill"].sudo()
        customer_line_model = env["logistics.dispatch.waybill.customer.line"].sudo()
        goods_line_model = env["logistics.dispatch.waybill.customer.goods.line"].sudo()

        waybill_rows = source_data["waybill_rows"]
        customer_rows = source_data["customer_rows"]
        goods_rows = source_data["goods_rows"]
        warehouse_map = cls._search_record_map(
            env,
            model_name="stock.warehouse",
            field_name="code",
            values={row["warehouse_code"] for row in waybill_rows if row.get("warehouse_code")},
        )

        existing_waybills = waybill_model.search([("name", "in", [row["waybill_no"] for row in waybill_rows])])
        existing_waybill_map = {record.name: record for record in existing_waybills}
        waybill_record_map = {}
        for row in waybill_rows:
            waybill_no = row["waybill_no"]
            if waybill_no in existing_waybill_map:
                stats["skipped_record_count"] += 1
                waybill_record_map[waybill_no] = existing_waybill_map[waybill_no]
                continue
            vals = {
                "waybill_no": waybill_no,
                "delivery_date": row.get("delivery_date") or False,
                "remark": row.get("remark") or False,
            }
            if row.get("batch_no"):
                vals["batch_no"] = row["batch_no"]
            if row.get("warehouse_code") and row["warehouse_code"] in warehouse_map:
                vals["warehouse_id"] = warehouse_map[row["warehouse_code"]].id
            waybill = waybill_model.create(vals)
            waybill_record_map[waybill_no] = waybill
            stats["created_waybill_count"] += 1

        customer_line_record_map = {}
        for row in customer_rows:
            waybill = waybill_record_map.get(row["waybill_no"])
            if not waybill or waybill.name in existing_waybill_map:
                stats["skipped_record_count"] += 1
                continue
            customer_line = customer_line_model.create(
                {
                    "waybill_id": waybill.id,
                    "customer_no": row["customer_no"],
                    "customer_name": row.get("customer_name") or False,
                    "store_no": row.get("store_no") or False,
                    "store_name": row.get("store_name") or False,
                    "delivery_note": row.get("delivery_remark") or False,
                    "signoff_requirement": row.get("signoff_requirement") or False,
                    "customer_ref": row.get("customer_ref") or False,
                }
            )
            customer_line_record_map[cls._customer_key(row)] = customer_line
            stats["created_customer_line_count"] += 1

        for row in goods_rows:
            customer_line = customer_line_record_map.get(cls._customer_key(row))
            if not customer_line:
                stats["skipped_record_count"] += 1
                continue
            goods_line_model.create(
                {
                    "customer_line_id": customer_line.id,
                    "goods_code": row.get("goods_code") or False,
                    "goods_name": row["goods_name"],
                    "specification": row.get("spec") or False,
                    "quantity": cls._safe_float(row.get("qty"), default=0.0),
                    "package_count": cls._safe_int(row.get("package_count"), default=0),
                    "uom_name": row.get("uom_name") or False,
                    "weight": cls._safe_float(row.get("weight"), default=0.0),
                    "volume": cls._safe_float(row.get("volume"), default=0.0),
                    "temperature_zone": row.get("temperature_zone") or "ambient",
                    "package_type": row.get("package_type") or False,
                    "remark": row.get("remark") or False,
                }
            )
            stats["created_goods_line_count"] += 1

    @classmethod
    def _build_result_payload(cls, batch):
        batch.ensure_one()
        return {
            "import_batch_no": batch.name,
            "status": batch.state,
            "status_label": cls.STATUS_LABELS.get(batch.state, batch.state),
            "created_waybill_count": batch.created_waybill_count,
            "created_customer_line_count": batch.created_customer_line_count,
            "created_goods_line_count": batch.created_goods_line_count,
            "updated_record_count": batch.updated_record_count,
            "skipped_record_count": batch.skipped_record_count,
            "failed_record_count": batch.failed_record_count,
            "error_report_url": batch.error_report_url,
            "failure_reason": batch.failure_reason,
        }

    @classmethod
    def _build_error_report_url(cls, batch):
        batch.ensure_one()
        return f"/api/admin/logistics/imports/waybill-standard/error-report?import_batch_no={batch.name}"

    @classmethod
    def _build_template_download_url(cls, *, template_locale):
        return (
            "/api/admin/logistics/imports/waybill-standard/template/download"
            f"?template_code={cls.TEMPLATE_CODE}"
            f"&template_version={cls.TEMPLATE_VERSION}"
            f"&template_locale={template_locale}"
        )

    @classmethod
    def _empty_source_data(cls):
        return {sheet_meta["key"]: [] for sheet_meta in cls.SHEETS}

    @classmethod
    def _cell_text(cls, value):
        if value is None:
            return ""
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")
        return str(value).strip()

    @classmethod
    def _normalize_header(cls, header_name):
        return (header_name or "").strip().lower().replace("-", "_")

    @classmethod
    def _customer_key(cls, row):
        return (
            (row.get("waybill_no") or "").strip(),
            (row.get("customer_no") or "").strip(),
            (row.get("store_no") or "").strip(),
        )

    @classmethod
    def _goods_key(cls, row):
        return (
            (row.get("waybill_no") or "").strip(),
            (row.get("customer_no") or "").strip(),
            (row.get("store_no") or "").strip(),
            (row.get("goods_code") or "").strip(),
            (row.get("goods_name") or "").strip(),
            (row.get("spec") or "").strip(),
        )

    @classmethod
    def _safe_int(cls, value, *, default=0):
        if value in (None, ""):
            return default
        return int(float(value))

    @classmethod
    def _safe_float(cls, value, *, default=0.0):
        if value in (None, ""):
            return default
        return float(value)
