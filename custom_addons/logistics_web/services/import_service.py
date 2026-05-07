import csv
import io
import uuid
from collections import defaultdict
from datetime import datetime

from odoo import _
from odoo.tools import file_path


class WaybillStandardImportService:
    TEMPLATE_CODE = "TSL-IMPORT-WAYBILL-V1"
    TEMPLATE_VERSION = "v1"
    TEMPLATE_FILE_NAME = "TSL-IMPORT-WAYBILL-V1.csv"
    TEMPLATE_RELATIVE_PATH = (
        "logistics_dispatch",
        "static",
        "src",
        "import_templates",
        TEMPLATE_FILE_NAME,
    )
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
    ALLOWED_TEMPERATURE_ZONES = {"ambient", "chilled", "frozen", "other"}

    @classmethod
    def build_template_payload(cls):
        return {
            "template_code": cls.TEMPLATE_CODE,
            "template_version": cls.TEMPLATE_VERSION,
            "file_name": cls.TEMPLATE_FILE_NAME,
            "download_url": (
                f"/api/admin/logistics/imports/waybill-standard/template/download"
                f"?template_code={cls.TEMPLATE_CODE}&template_version={cls.TEMPLATE_VERSION}"
            ),
            "expected_fields": [
                {"field_code": field_code, "field_label": cls.FIELD_LABELS[field_code]}
                for field_code in cls.EXPECTED_FIELDS
            ],
        }

    @classmethod
    def load_template_bytes(cls):
        template_path = file_path("/".join(cls.TEMPLATE_RELATIVE_PATH))
        with open(template_path, "rb") as file_pointer:
            return file_pointer.read()

    @classmethod
    def precheck(cls, env, raw_bytes, *, filename="", template_code="", template_version=""):
        template_errors = cls._validate_template_identity(template_code, template_version)
        parsed_rows, parse_errors = cls._parse_rows(raw_bytes, filename=filename)
        errors = template_errors + parse_errors
        if parse_errors:
            return cls._build_precheck_result(parsed_rows, errors)

        errors.extend(cls._validate_rows(env, parsed_rows))
        return cls._build_precheck_result(parsed_rows, errors)

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
                    error_message=_("请使用标准模板 %(code)s。") % {"code": cls.TEMPLATE_CODE},
                )
            )
        if normalized_version != cls.TEMPLATE_VERSION:
            errors.append(
                cls._make_error(
                    row_no=0,
                    field_code="template_file",
                    error_code="TEMPLATE_VERSION_INVALID",
                    error_message=_("请使用模板版本 %(version)s。") % {"version": cls.TEMPLATE_VERSION},
                )
            )
        return errors

    @classmethod
    def _parse_rows(cls, raw_bytes, *, filename=""):
        if not raw_bytes:
            return [], [
                cls._make_error(
                    row_no=0,
                    field_code="template_file",
                    error_code="PRECHECK_PARSE_FAILED",
                    error_message=_("未检测到上传文件，请先选择标准导入模板文件。"),
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
                if not field_code:
                    continue
                normalized_row[field_code] = (value or "").strip()
            normalized_row["_source_row_no"] = source_row_no
            normalized_row["_file_name"] = filename or ""
            rows.append(normalized_row)

        if not rows:
            return [], [
                cls._make_error(
                    row_no=0,
                    field_code="template_file",
                    error_code="PRECHECK_PARSE_FAILED",
                    error_message=_("模板中没有可校验的数据行，请至少保留一条明细。"),
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
            error_message=_("文件解析失败，请使用 UTF-8 或 GBK/GB18030 编码的 CSV 模板。"),
        )

    @classmethod
    def _build_header_map(cls, headers):
        header_map = {}
        normalized_headers = {cls._normalize_header(header): header for header in headers if header}
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
                    error_message=_("模板列头不匹配，缺少这些字段：%(fields)s。")
                    % {"fields": " / ".join(missing_fields)},
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
            )
            cls._validate_group_consistency(row, errors_by_row[row_no], waybill_groups, customer_groups)
            cls._validate_customer_store_relation(
                row,
                errors_by_row[row_no],
                customers_by_code,
                stores_by_code,
            )

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
                    error_message=_("%(field_label)s不能为空。")
                    % {"field_label": cls.FIELD_LABELS[field_code]},
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
                        error_message=_("配送日期格式必须为 YYYY-MM-DD。"),
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
                    error_message=_("温层必须是 ambient / chilled / frozen / other 之一。"),
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
                    error_message=_("%(field_label)s必须是数字。")
                    % {"field_label": cls.FIELD_LABELS[field_code]},
                )
            )
            return
        if allow_zero and numeric_value < 0:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code=field_code,
                    error_code="FIELD_VALUE_INVALID",
                    error_message=_("%(field_label)s不能小于 0。")
                    % {"field_label": cls.FIELD_LABELS[field_code]},
                )
            )
        if not allow_zero and numeric_value <= 0:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code=field_code,
                    error_code="FIELD_VALUE_INVALID",
                    error_message=_("%(field_label)s必须大于 0。")
                    % {"field_label": cls.FIELD_LABELS[field_code]},
                )
            )

    @classmethod
    def _validate_integer(cls, row, row_errors, field_code, *, allow_zero):
        value = row[field_code]
        if value == "":
            return
        try:
            numeric_value = int(value)
        except ValueError:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code=field_code,
                    error_code="FIELD_FORMAT_INVALID",
                    error_message=_("%(field_label)s必须是整数。")
                    % {"field_label": cls.FIELD_LABELS[field_code]},
                )
            )
            return
        if allow_zero and numeric_value < 0:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code=field_code,
                    error_code="FIELD_VALUE_INVALID",
                    error_message=_("%(field_label)s不能小于 0。")
                    % {"field_label": cls.FIELD_LABELS[field_code]},
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
    ):
        if row["customer_no"] and row["customer_no"] not in customers_by_code:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code="customer_no",
                    error_code="CUSTOMER_NO_NOT_FOUND",
                    error_message=_("客户编号不存在，请先维护客户主数据。"),
                )
            )
        if row["store_no"] and row["store_no"] not in stores_by_code:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code="store_no",
                    error_code="STORE_NO_NOT_FOUND",
                    error_message=_("门店编号不存在，请先维护门店主数据。"),
                )
            )
        if row["batch_no"] and row["batch_no"] not in batches_by_no:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code="batch_no",
                    error_code="BATCH_NO_NOT_FOUND",
                    error_message=_("批次号不存在，请先维护批次数据。"),
                )
            )
        if row["wave_no"] and row["wave_no"] not in waves_by_no:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code="wave_no",
                    error_code="WAVE_NO_NOT_FOUND",
                    error_message=_("波次号不存在，请先维护波次数据。"),
                )
            )
        batch_record = batches_by_no.get(row["batch_no"])
        if batch_record and row["wave_no"] and batch_record.wave_id and batch_record.wave_id.name != row["wave_no"]:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code="wave_no",
                    error_code="WAYBILL_GROUP_CONFLICT",
                    error_message=_("批次号与波次号不一致，请检查这条运单所属的批次/波次。"),
                )
            )
        customer_record = customers_by_code.get(row["customer_no"])
        if customer_record and row["customer_name"] and customer_record.name != row["customer_name"]:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code="customer_name",
                    error_code="FIELD_VALUE_INVALID",
                    error_message=_("客户编号与客户名称不一致，请检查客户主数据或模板内容。"),
                )
            )
        store_record = stores_by_code.get(row["store_no"])
        if store_record and row["store_name"] and store_record.name != row["store_name"]:
            row_errors.append(
                cls._make_error(
                    row_no=row["_source_row_no"],
                    field_code="store_name",
                    error_code="FIELD_VALUE_INVALID",
                    error_message=_("门店编号与门店名称不一致，请检查门店主数据或模板内容。"),
                )
            )

    @classmethod
    def _validate_group_consistency(cls, row, row_errors, waybill_groups, customer_groups):
        waybill_key = row["waybill_no"]
        if waybill_key:
            comparable_fields = ["batch_no", "wave_no", "delivery_date"]
            current_signature = {field_code: row[field_code] for field_code in comparable_fields}
            first_signature = waybill_groups.setdefault(waybill_key, current_signature)
            if first_signature != current_signature:
                row_errors.append(
                    cls._make_error(
                        row_no=row["_source_row_no"],
                        field_code="waybill_no",
                        error_code="WAYBILL_GROUP_CONFLICT",
                        error_message=_("同一运单号下的批次号、波次号、配送日期必须保持一致。"),
                    )
                )

        customer_key = (row["waybill_no"], row["customer_no"])
        if all(customer_key):
            comparable_fields = ["customer_name", "store_no", "store_name", "delivery_remark"]
            current_signature = {field_code: row[field_code] for field_code in comparable_fields}
            first_signature = customer_groups.setdefault(customer_key, current_signature)
            if first_signature != current_signature:
                row_errors.append(
                    cls._make_error(
                        row_no=row["_source_row_no"],
                        field_code="customer_no",
                        error_code="CUSTOMER_GROUP_CONFLICT",
                        error_message=_("同一运单号和客户编号下的客户层字段必须保持一致。"),
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
                    error_message=_("门店与客户归属不一致，请检查客户编号和门店编号。"),
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
        passed_row_count = total_row_count - failed_row_count
        return {
            "template_code": cls.TEMPLATE_CODE,
            "template_version": cls.TEMPLATE_VERSION,
            "precheck_token": f"pre_{uuid.uuid4().hex[:12]}",
            "total_row_count": total_row_count,
            "passed_row_count": max(passed_row_count, 0),
            "failed_row_count": failed_row_count,
            "can_confirm_import": total_row_count > 0 and failed_row_count == 0,
            "errors": sorted(errors, key=lambda item: (item["row_no"], item["field_code"], item["error_code"])),
        }
