import csv
import hashlib
import io
from collections import defaultdict
from datetime import datetime

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tools import file_path


class WaybillStandardImportService:
    TEMPLATE_CODE = "TSL-IMPORT-WAYBILL-V1"
    TEMPLATE_VERSION = "v1"
    TEMPLATE_FILE_NAME = "TSL-IMPORT-WAYBILL-V1.csv"
    TEMPLATE_VARIANTS = {
        "en_US": {
            "label": "标准模板（英文列头）",
            "file_name": "TSL-IMPORT-WAYBILL-V1.csv",
        },
        "zh_CN": {
            "label": "标准模板（中文列头）",
            "file_name": "TSL-IMPORT-WAYBILL-V1.zh_CN.csv",
        },
    }
    DEFAULT_TEMPLATE_LOCALE = "en_US"
    EXPECTED_FIELDS = [
        "row_no",
        "import_batch_mark",
        "waybill_no",
        "batch_no",
        "wave_no",
        "delivery_date",
        "customer_no",
        "customer_name",
        "store_no",
        "store_name",
        "delivery_remark",
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
    ]
    REQUIRED_FIELDS = {"waybill_no", "customer_no", "goods_name", "qty"}
    HEADER_ALIASES = {
        "row_no": ["row_no", "row no", "行序号"],
        "import_batch_mark": ["import_batch_mark", "import batch mark", "导入批次标识"],
        "waybill_no": ["waybill_no", "waybill no", "运单号"],
        "batch_no": ["batch_no", "batch no", "批次号"],
        "wave_no": ["wave_no", "wave no", "波次号"],
        "delivery_date": ["delivery_date", "delivery date", "配送日期"],
        "customer_no": ["customer_no", "customer no", "客户编号", "客户号"],
        "customer_name": ["customer_name", "customer name", "客户名称"],
        "store_no": ["store_no", "store no", "门店编号", "门店号"],
        "store_name": ["store_name", "store name", "门店名称"],
        "delivery_remark": ["delivery_remark", "delivery remark", "客户配送备注", "配送备注"],
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
        "remark": ["remark", "备注", "货物备注"],
    }
    FIELD_LABELS = {
        "row_no": "行序号",
        "import_batch_mark": "导入批次标识",
        "waybill_no": "运单号",
        "batch_no": "批次号",
        "wave_no": "波次号",
        "delivery_date": "配送日期",
        "customer_no": "客户编号",
        "customer_name": "客户名称",
        "store_no": "门店编号",
        "store_name": "门店名称",
        "delivery_remark": "客户配送备注",
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
        "remark": "备注",
        "template_file": "模板文件",
    }
    STATUS_LABELS = {
        "prechecked": "已预校验",
        "importing": "导入中",
        "finished": "已完成",
        "failed": "已失败",
        "expired": "已失效",
    }
    ALLOWED_TEMPERATURE_ZONES = {"ambient", "chilled", "frozen", "other"}
    ERROR_REPORT_HEADERS = [
        ("row_no", "行号"),
        ("field_code", "字段编码"),
        ("field_label", "字段名称"),
        ("error_code", "错误编码"),
        ("error_message", "错误说明"),
    ]

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
            "expected_fields": [
                {"field_code": field_code, "field_label": cls.FIELD_LABELS[field_code]}
                for field_code in cls.EXPECTED_FIELDS
            ],
        }

    @classmethod
    def load_template_bytes(cls, *, template_locale=""):
        template_meta = cls.get_template_variant(template_locale)
        template_path = file_path(
            "/".join(
                (
                    "logistics_dispatch",
                    "static",
                    "src",
                    "import_templates",
                    template_meta["file_name"],
                )
            )
        )
        with open(template_path, "rb") as file_pointer:
            return file_pointer.read()

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
        parsed_rows, parse_errors = cls._parse_rows(raw_bytes)
        errors = template_errors + parse_errors
        if not parse_errors:
            errors.extend(cls._validate_rows(env, parsed_rows))

        result = cls._build_precheck_result(parsed_rows, errors)
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
                source_rows=parsed_rows,
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

        rows = batch.get_source_rows()
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
            cls._apply_import(env, rows, stats)
        except Exception as exc:
            batch.sudo().write(
                {
                    "state": "failed",
                    "finished_at": fields.Datetime.now(),
                    "failed_record_count": len(rows),
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
            writer.writerow([error.get(field_code, "") for field_code, _header_label in cls.ERROR_REPORT_HEADERS])

        return {
            "file_name": f"{batch.name}-error-report.csv",
            "file_bytes": buffer.getvalue().encode("utf-8-sig"),
            "content_type": "text/csv; charset=utf-8",
        }

    @classmethod
    def _validate_template_identity(cls, template_code, template_version):
        errors = []
        normalized_code = (template_code or cls.TEMPLATE_CODE).strip()
        normalized_version = (template_version or cls.TEMPLATE_VERSION).strip().lower()
        if normalized_code != cls.TEMPLATE_CODE:
            errors.append(
                cls._make_error(
                    row_no=0,
                    field_code="template_file",
                    error_code="TEMPLATE_CODE_INVALID",
                    error_message=f"请使用标准模板 {cls.TEMPLATE_CODE}。",
                )
            )
        if normalized_version != cls.TEMPLATE_VERSION:
            errors.append(
                cls._make_error(
                    row_no=0,
                    field_code="template_file",
                    error_code="TEMPLATE_VERSION_INVALID",
                    error_message=f"请使用模板版本 {cls.TEMPLATE_VERSION}。",
                )
            )
        return errors

    @classmethod
    def _parse_rows(cls, raw_bytes):
        if not raw_bytes:
            return [], [
                cls._make_error(
                    row_no=0,
                    field_code="template_file",
                    error_code="PRECHECK_PARSE_FAILED",
                    error_message="未检测到上传文件，请先选择标准导入模板文件。",
                )
            ]

        text, encoding_error = cls._decode_bytes(raw_bytes)
        if encoding_error:
            return [], [encoding_error]

        reader = csv.DictReader(io.StringIO(text))
        headers = reader.fieldnames or []
        header_map, header_errors = cls._build_header_map(headers)
        if header_errors:
            return [], header_errors

        rows = []
        for source_row_no, raw_row in enumerate(reader, start=2):
            normalized_row = {field_code: "" for field_code in cls.EXPECTED_FIELDS}
            for original_header, value in raw_row.items():
                field_code = header_map.get(original_header)
                if field_code:
                    normalized_row[field_code] = (value or "").strip()
            normalized_row["_source_row_no"] = source_row_no
            rows.append(normalized_row)

        if not rows:
            return [], [
                cls._make_error(
                    row_no=0,
                    field_code="template_file",
                    error_code="PRECHECK_PARSE_FAILED",
                    error_message="模板中没有可校验的数据行，请至少保留一条明细。",
                )
            ]
        return rows, []

    @classmethod
    def _decode_bytes(cls, raw_bytes):
        for encoding in ("utf-8-sig", "utf-8", "gb18030"):
            try:
                return raw_bytes.decode(encoding), None
            except UnicodeDecodeError:
                continue
        return None, cls._make_error(
            row_no=0,
            field_code="template_file",
            error_code="PRECHECK_PARSE_FAILED",
            error_message="文件解析失败，请使用 UTF-8 或 GBK/GB18030 编码的 CSV 模板。",
        )

    @classmethod
    def _build_header_map(cls, headers):
        normalized_headers = {cls._normalize_header(header): header for header in headers if header}
        header_map = {}
        missing_fields = []
        for field_code in cls.EXPECTED_FIELDS:
            matched_header = None
            for alias in cls.HEADER_ALIASES[field_code]:
                original_header = normalized_headers.get(cls._normalize_header(alias))
                if original_header:
                    matched_header = original_header
                    break
            if matched_header:
                header_map[matched_header] = field_code
            else:
                missing_fields.append(cls.FIELD_LABELS[field_code])

        if missing_fields:
            return {}, [
                cls._make_error(
                    row_no=0,
                    field_code="template_file",
                    error_code="TEMPLATE_AND_FILE_MISMATCH",
                    error_message=f"模板列头不匹配，缺少这些字段：{' / '.join(missing_fields)}。",
                )
            ]
        return header_map, []

    @classmethod
    def _normalize_header(cls, header_name):
        return (header_name or "").strip().lower().replace("-", "_")

    @classmethod
    def _validate_rows(cls, env, rows):
        errors_by_row = defaultdict(list)
        customers_by_code = cls._search_partner_map(
            env,
            model_domain=[("is_logistics_customer", "=", True)],
            field_name="logistics_customer_code",
            values={row["customer_no"] for row in rows if row["customer_no"]},
        )
        stores_by_code = cls._search_partner_map(
            env,
            model_domain=[("is_logistics_store", "=", True)],
            field_name="logistics_store_code",
            values={row["store_no"] for row in rows if row["store_no"]},
        )
        batches_by_no = cls._search_record_map(
            env,
            model_name="logistics.dispatch.batch",
            field_name="name",
            values={row["batch_no"] for row in rows if row["batch_no"]},
        )
        waves_by_no = cls._search_record_map(
            env,
            model_name="logistics.dispatch.wave",
            field_name="name",
            values={row["wave_no"] for row in rows if row["wave_no"]},
        )
        existing_waybills = cls._search_record_map(
            env,
            model_name="logistics.dispatch.waybill",
            field_name="name",
            values={row["waybill_no"] for row in rows if row["waybill_no"]},
        )
        waybill_groups = {}
        customer_groups = {}

        for row in rows:
            row_no = row["_source_row_no"]
            cls._validate_required_fields(row, errors_by_row[row_no])
            cls._validate_format_fields(row, errors_by_row[row_no])
            cls._validate_master_data(
                row,
                errors_by_row[row_no],
                customers_by_code,
                stores_by_code,
                batches_by_no,
                waves_by_no,
                existing_waybills,
            )
            cls._validate_group_consistency(row, errors_by_row[row_no], waybill_groups, customer_groups)
            cls._validate_customer_store_relation(row, errors_by_row[row_no], customers_by_code, stores_by_code)

        return [error for row_errors in errors_by_row.values() for error in row_errors]

    @classmethod
    def _validate_required_fields(cls, row, row_errors):
        for field_code in cls.REQUIRED_FIELDS:
            if row[field_code]:
                continue
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code=field_code,
                    error_code="FIELD_REQUIRED",
                    error_message=f"{cls.FIELD_LABELS[field_code]}不能为空。",
                )
            )
        if row["wave_no"] and not row["batch_no"]:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code="batch_no",
                    error_code="FIELD_REQUIRED",
                    error_message="当前实现中填写波次号时必须同时填写批次号。",
                )
            )

    @classmethod
    def _validate_format_fields(cls, row, row_errors):
        if row["delivery_date"]:
            try:
                datetime.strptime(row["delivery_date"], "%Y-%m-%d")
            except ValueError:
                row_errors.append(
                    cls._make_error(
                        row_no=row["_source_row_no"],
                        field_code="delivery_date",
                        error_code="FIELD_FORMAT_INVALID",
                        error_message="配送日期格式必须为 YYYY-MM-DD。",
                    )
                )

        cls._validate_positive_number(row, row_errors, "qty", allow_zero=False)
        cls._validate_positive_number(row, row_errors, "weight", allow_zero=True)
        cls._validate_positive_number(row, row_errors, "volume", allow_zero=True)
        cls._validate_integer(row, row_errors, "package_count", allow_zero=True)
        if row["temperature_zone"] and row["temperature_zone"] not in cls.ALLOWED_TEMPERATURE_ZONES:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code="temperature_zone",
                    error_code="FIELD_ENUM_INVALID",
                    error_message="温层必须是 ambient / chilled / frozen / other 之一。",
                )
            )

    @classmethod
    def _validate_positive_number(cls, row, row_errors, field_code, *, allow_zero):
        value = row[field_code]
        if value == "":
            return
        try:
            numeric_value = float(value)
        except ValueError:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code=field_code,
                    error_code="FIELD_FORMAT_INVALID",
                    error_message=f"{cls.FIELD_LABELS[field_code]}必须是数字。",
                )
            )
            return
        if allow_zero and numeric_value < 0:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code=field_code,
                    error_code="FIELD_VALUE_INVALID",
                    error_message=f"{cls.FIELD_LABELS[field_code]}不能小于 0。",
                )
            )
        if not allow_zero and numeric_value <= 0:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code=field_code,
                    error_code="FIELD_VALUE_INVALID",
                    error_message=f"{cls.FIELD_LABELS[field_code]}必须大于 0。",
                )
            )

    @classmethod
    def _validate_integer(cls, row, row_errors, field_code, *, allow_zero):
        value = row[field_code]
        if value == "":
            return
        try:
            numeric_value = int(float(value))
        except ValueError:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code=field_code,
                    error_code="FIELD_FORMAT_INVALID",
                    error_message=f"{cls.FIELD_LABELS[field_code]}必须是整数。",
                )
            )
            return
        if allow_zero and numeric_value < 0:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code=field_code,
                    error_code="FIELD_VALUE_INVALID",
                    error_message=f"{cls.FIELD_LABELS[field_code]}不能小于 0。",
                )
            )

    @classmethod
    def _validate_master_data(
        cls,
        row,
        row_errors,
        customers_by_code,
        stores_by_code,
        batches_by_no,
        waves_by_no,
        existing_waybills,
    ):
        if row["waybill_no"] and row["waybill_no"] in existing_waybills:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code="waybill_no",
                    error_code="WAYBILL_NO_ALREADY_EXISTS",
                    error_message="运单号已存在，请更换运单号后重新导入。",
                )
            )
        if row["customer_no"] and row["customer_no"] not in customers_by_code:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code="customer_no",
                    error_code="CUSTOMER_NO_NOT_FOUND",
                    error_message="客户编号不存在，请先维护客户主数据。",
                )
            )
        if row["store_no"] and row["store_no"] not in stores_by_code:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code="store_no",
                    error_code="STORE_NO_NOT_FOUND",
                    error_message="门店编号不存在，请先维护门店主数据。",
                )
            )
        if row["batch_no"] and row["batch_no"] not in batches_by_no:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code="batch_no",
                    error_code="BATCH_NO_NOT_FOUND",
                    error_message="批次号不存在，请先维护批次数据。",
                )
            )
        if row["wave_no"] and row["wave_no"] not in waves_by_no:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code="wave_no",
                    error_code="WAVE_NO_NOT_FOUND",
                    error_message="波次号不存在，请先维护波次数据。",
                )
            )

        batch_record = batches_by_no.get(row["batch_no"])
        if batch_record and row["wave_no"] and batch_record.wave_id and batch_record.wave_id.name != row["wave_no"]:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code="wave_no",
                    error_code="WAYBILL_GROUP_CONFLICT",
                    error_message="批次号与波次号不一致，请检查这条运单所属的批次/波次。",
                )
            )

        customer_record = customers_by_code.get(row["customer_no"])
        if customer_record and row["customer_name"] and customer_record.name != row["customer_name"]:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code="customer_name",
                    error_code="FIELD_VALUE_INVALID",
                    error_message="客户编号与客户名称不一致，请检查客户主数据或模板内容。",
                )
            )

        store_record = stores_by_code.get(row["store_no"])
        if store_record and row["store_name"] and store_record.name != row["store_name"]:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code="store_name",
                    error_code="FIELD_VALUE_INVALID",
                    error_message="门店编号与门店名称不一致，请检查门店主数据或模板内容。",
                )
            )

    @classmethod
    def _validate_group_consistency(cls, row, row_errors, waybill_groups, customer_groups):
        waybill_key = row["waybill_no"]
        if waybill_key:
            current_signature = {field_code: row[field_code] for field_code in ("batch_no", "wave_no", "delivery_date")}
            first_signature = waybill_groups.setdefault(waybill_key, current_signature)
            if first_signature != current_signature:
                row_errors.append(
                    cls._make_error(
                        row_no=row["_source_row_no"],
                        field_code="waybill_no",
                        error_code="WAYBILL_GROUP_CONFLICT",
                        error_message="同一运单号下的批次号、波次号、配送日期必须保持一致。",
                    )
                )

        customer_key = (row["waybill_no"], row["customer_no"])
        if all(customer_key):
            current_signature = {
                field_code: row[field_code]
                for field_code in ("customer_name", "store_no", "store_name", "delivery_remark")
            }
            first_signature = customer_groups.setdefault(customer_key, current_signature)
            if first_signature != current_signature:
                row_errors.append(
                    cls._make_error(
                        row_no=row["_source_row_no"],
                        field_code="customer_no",
                        error_code="CUSTOMER_GROUP_CONFLICT",
                        error_message="同一运单号和客户编号下的客户层字段必须保持一致。",
                    )
                )

    @classmethod
    def _validate_customer_store_relation(cls, row, row_errors, customers_by_code, stores_by_code):
        customer_record = customers_by_code.get(row["customer_no"])
        store_record = stores_by_code.get(row["store_no"])
        if not customer_record or not store_record or not store_record.parent_id:
            return
        if store_record.parent_id.id != customer_record.id:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code="store_no",
                    error_code="CUSTOMER_STORE_MISMATCH",
                    error_message="门店与客户归属不一致，请检查客户编号和门店编号。",
                )
            )

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
    def _make_error(cls, *, row_no, field_code, error_code, error_message):
        return {
            "row_no": row_no,
            "field_code": field_code,
            "field_label": cls.FIELD_LABELS.get(field_code, field_code),
            "error_code": error_code,
            "error_message": error_message,
        }

    @classmethod
    def _build_precheck_result(cls, rows, errors):
        failed_row_numbers = {error["row_no"] for error in errors if error["row_no"]}
        total_row_count = len(rows)
        failed_row_count = len(failed_row_numbers)
        return {
            "template_code": cls.TEMPLATE_CODE,
            "template_version": cls.TEMPLATE_VERSION,
            "import_batch_no": False,
            "precheck_token": False,
            "error_report_url": False,
            "total_row_count": total_row_count,
            "passed_row_count": max(total_row_count - failed_row_count, 0),
            "failed_row_count": failed_row_count,
            "can_confirm_import": total_row_count > 0 and failed_row_count == 0,
            "errors": sorted(errors, key=lambda item: (item["row_no"], item["field_code"], item["error_code"])),
        }

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
    def _apply_import(cls, env, rows, stats):
        waybill_model = env["logistics.dispatch.waybill"].sudo()
        customer_line_model = env["logistics.dispatch.waybill.customer.line"].sudo()
        goods_line_model = env["logistics.dispatch.waybill.customer.goods.line"].sudo()

        rows_by_waybill = defaultdict(list)
        for row in rows:
            rows_by_waybill[row["waybill_no"]].append(row)

        existing_waybills = waybill_model.search([("name", "in", list(rows_by_waybill.keys()))])
        existing_waybill_map = {record.name: record for record in existing_waybills}

        for waybill_no, waybill_rows in rows_by_waybill.items():
            if waybill_no in existing_waybill_map:
                stats["skipped_record_count"] += len(waybill_rows)
                continue

            first_row = waybill_rows[0]
            waybill_vals = {
                "waybill_no": waybill_no,
                "delivery_date": first_row["delivery_date"] or False,
                "remark": first_row["remark"] or False,
            }
            if first_row["batch_no"]:
                waybill_vals["batch_no"] = first_row["batch_no"]

            waybill = waybill_model.create(waybill_vals)
            stats["created_waybill_count"] += 1

            customer_groups = defaultdict(list)
            for row in waybill_rows:
                customer_groups[(row["customer_no"], row["store_no"])].append(row)

            for customer_rows in customer_groups.values():
                first_customer_row = customer_rows[0]
                customer_line_vals = {
                    "waybill_id": waybill.id,
                    "sequence": cls._safe_int(first_customer_row["row_no"], default=10),
                    "customer_no": first_customer_row["customer_no"],
                    "customer_name": first_customer_row["customer_name"] or False,
                    "store_no": first_customer_row["store_no"] or False,
                    "store_name": first_customer_row["store_name"] or False,
                    "delivery_note": first_customer_row["delivery_remark"] or False,
                }
                customer_line = customer_line_model.create(customer_line_vals)
                stats["created_customer_line_count"] += 1

                for row in customer_rows:
                    goods_line_model.create(
                        {
                            "customer_line_id": customer_line.id,
                            "sequence": cls._safe_int(row["row_no"], default=row["_source_row_no"]),
                            "goods_code": row["goods_code"] or False,
                            "goods_name": row["goods_name"],
                            "specification": row["spec"] or False,
                            "quantity": cls._safe_float(row["qty"], default=0.0),
                            "package_count": cls._safe_int(row["package_count"], default=0),
                            "uom_name": row["uom_name"] or False,
                            "weight": cls._safe_float(row["weight"], default=0.0),
                            "volume": cls._safe_float(row["volume"], default=0.0),
                            "temperature_zone": row["temperature_zone"] or "ambient",
                            "package_type": row["package_type"] or False,
                            "remark": row["remark"] or False,
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
        return (
            "/api/admin/logistics/imports/waybill-standard/error-report"
            f"?import_batch_no={batch.name}"
        )

    @classmethod
    def _build_template_download_url(cls, *, template_locale):
        return (
            "/api/admin/logistics/imports/waybill-standard/template/download"
            f"?template_code={cls.TEMPLATE_CODE}"
            f"&template_version={cls.TEMPLATE_VERSION}"
            f"&template_locale={template_locale}"
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
