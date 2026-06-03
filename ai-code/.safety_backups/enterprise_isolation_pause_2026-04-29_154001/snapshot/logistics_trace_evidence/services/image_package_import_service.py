import hashlib
import io
import mimetypes
import tempfile
import zipfile
import csv
from pathlib import Path, PurePosixPath

from odoo import fields
from odoo.exceptions import AccessError, ValidationError


class ImagePackageImportService:
    OBJECT_TYPE = "image_package"
    OBJECT_TYPE_LABEL = "图片包导入"
    IMPORT_ROOT_DIR = Path(tempfile.gettempdir()) / "odoo_logistics_imports" / "image_package"
    SUPPORTED_IMAGE_SUFFIXES = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".bmp",
        ".gif",
    }
    MATCH_STATUS_SELECTION = [
        ("pending", "待命中"),
        ("matched", "已命中"),
        ("ambiguous", "命中歧义"),
        ("unmatched", "未命中"),
    ]
    MATCH_METHOD_SELECTION = [
        ("waybill_customer_line", "运单号 + 配送节点编号"),
        ("waybill_store", "运单号 + 门店编码"),
        ("waybill_only", "仅运单号"),
        ("manual", "人工确认"),
    ]
    LINK_STATUS_SELECTION = [
        ("pending", "待补链"),
        ("linked", "已补链"),
        ("failed", "补链失败"),
        ("manual_review", "待人工复核"),
    ]
    SCENE_CODES = {
        "arrive_loading_point",
        "start_loading",
        "finish_loading",
        "departed",
        "arrive_store",
        "deliver_finish",
        "signoff",
        "exception_report",
    }
    STATUS_LABELS = {
        "pending": "待执行",
        "running": "执行中",
        "success": "成功",
        "partial_failed": "部分失败",
        "failed": "失败",
        "cancelled": "已取消",
    }

    @classmethod
    def import_zip(cls, env, *, raw_bytes, file_name, operator):
        cls._ensure_upload_permission(env)
        if not raw_bytes:
            raise ValidationError("图片包内容为空，无法执行导入。")
        if not (file_name or "").lower().endswith(".zip"):
            raise ValidationError("图片包导入当前只支持 ZIP 文件。")

        source_file = cls._create_source_file(env, raw_bytes=raw_bytes, file_name=file_name, operator=operator)
        task = cls._create_task(env, source_file=source_file, operator=operator)
        entries = cls._collect_zip_entries(raw_bytes)
        if not entries:
            task.sudo().write(
                {
                    "status": "failed",
                    "started_at": fields.Datetime.now(),
                    "finished_at": fields.Datetime.now(),
                    "summary_message": "图片包内未找到可导入的图片文件。",
                }
            )
            return task

        task.sudo().write(
            {
                "status": "running",
                "started_at": fields.Datetime.now(),
                "total_count": len(entries),
                "summary_message": "图片包导入执行中。",
            }
        )
        line_model = env["logistics.import.task.line"].sudo()
        for index, entry in enumerate(entries, start=1):
            line = line_model.create(
                {
                    "task_id": task.id,
                    "line_no": index,
                    "source_row_no": index,
                    "object_type": cls.OBJECT_TYPE,
                    "status": "pending",
                    "business_key": entry["file_name"],
                    "target_model": "logistics.trace.evidence",
                    "message": "待处理",
                    "package_entry_name": entry["entry_name"],
                    "source_filename": entry["file_name"],
                    "capture_time": entry["capture_time"],
                    "mime_type": entry["mime_type"],
                }
            )
            cls._process_task_line(env, task=task, task_line=line, entry=entry, operator=operator, retry=False)
        cls._refresh_task_summary(task)
        return task

    @classmethod
    def retry_failed_lines(cls, env, task):
        cls._ensure_retry_permission(env)
        task.ensure_one()
        if task.object_type != cls.OBJECT_TYPE:
            raise ValidationError("当前任务不是图片包任务，不能执行补链重试。")
        raw_bytes = cls._load_source_file_bytes(task.source_file_id)
        entry_map = {entry["entry_name"]: entry for entry in cls._collect_zip_entries(raw_bytes)}
        task.sudo().write(
            {
                "status": "running",
                "started_at": task.started_at or fields.Datetime.now(),
                "summary_message": "图片包补链重试执行中。",
            }
        )
        failed_lines = task.task_line_ids.filtered(
            lambda rec: rec.object_type == cls.OBJECT_TYPE and rec.status == "failed"
        ).sorted(key=lambda rec: (rec.line_no, rec.id))
        for line in failed_lines:
            entry = entry_map.get((line.package_entry_name or "").strip())
            if not entry:
                cls._mark_line_failed(
                    env,
                    task=task,
                    task_line=line,
                    error_code="IMAGE_PACKAGE_ENTRY_NOT_FOUND",
                    error_message="在源 ZIP 中未找到对应图片文件，无法执行重试。",
                    field_name="package_entry_name",
                    raw_value=line.package_entry_name or "",
                    link_status="failed",
                )
                continue
            cls._process_task_line(env, task=task, task_line=line, entry=entry, operator=env.user, retry=True)
        cls._refresh_task_summary(task)
        return task

    @classmethod
    def get_import_task_result(cls, env, *, task_no="", import_batch_no=""):
        task = cls._get_task_by_task_no(env, task_no or import_batch_no)
        if not task:
            raise ValidationError("未找到对应的图片包导入任务。")
        return cls._build_task_result_payload(task)

    @classmethod
    def get_import_task_lines(cls, env, *, task_no, page=1, page_size=20, status=""):
        task = cls._get_task_by_task_no(env, task_no)
        if not task:
            raise ValidationError("未找到对应的图片包导入任务。")
        page = max(int(page or 1), 1)
        page_size = min(max(int(page_size or 20), 1), 200)
        line_status = (status or "").strip()
        line_model = env["logistics.import.task.line"]
        valid_statuses = {value for value, _label in line_model._fields["status"].selection}
        domain = [("task_id", "=", task.id), ("object_type", "=", cls.OBJECT_TYPE)]
        if line_status:
            if line_status not in valid_statuses:
                raise ValidationError("当前状态筛选值不合法。")
            domain.append(("status", "=", line_status))
        total = line_model.search_count(domain)
        total_pages = max((total + page_size - 1) // page_size, 1)
        page = min(page, total_pages)
        records = line_model.search(domain, order="line_no asc", offset=(page - 1) * page_size, limit=page_size)
        showing_from = (page - 1) * page_size + 1 if total else 0
        showing_to = min(page * page_size, total)
        return {
            "task_no": task.task_no,
            "object_type": task.object_type,
            "object_type_label": cls.OBJECT_TYPE_LABEL,
            "task_status": task.status,
            "task_status_label": cls._status_label(task.status),
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_prev": page > 1,
            "has_next": page < total_pages,
            "showing_from": showing_from,
            "showing_to": showing_to,
            "status_filter": line_status or False,
            "status_filter_label": cls._selection_label(line_model, "status", line_status) if line_status else False,
            "items": [
                {
                    "line_no": record.line_no,
                    "source_row_no": record.source_row_no,
                    "object_type": record.object_type,
                    "status": record.status,
                    "status_label": cls._selection_label(record, "status", record.status),
                    "business_key": record.business_key or False,
                    "target_model": record.target_model or False,
                    "target_res_id": record.target_res_id or False,
                    "message": record.message or False,
                }
                for record in records
            ],
        }

    @classmethod
    def get_import_task_errors(cls, env, *, task_no, page=1, page_size=50):
        task = cls._get_task_by_task_no(env, task_no)
        if not task:
            raise ValidationError("未找到对应的图片包导入任务。")
        page = max(int(page or 1), 1)
        page_size = min(max(int(page_size or 50), 1), 200)
        error_model = env["logistics.import.error.line"]
        domain = [("task_id", "=", task.id)]
        total = error_model.search_count(domain)
        total_pages = max((total + page_size - 1) // page_size, 1)
        page = min(page, total_pages)
        records = error_model.search(domain, order="source_row_no asc, id asc", offset=(page - 1) * page_size, limit=page_size)
        showing_from = (page - 1) * page_size + 1 if total else 0
        showing_to = min(page * page_size, total)
        return {
            "task_no": task.task_no,
            "object_type": task.object_type,
            "object_type_label": cls.OBJECT_TYPE_LABEL,
            "task_status": task.status,
            "task_status_label": cls._status_label(task.status),
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_prev": page > 1,
            "has_next": page < total_pages,
            "showing_from": showing_from,
            "showing_to": showing_to,
            "items": [
                {
                    "line_no": record.task_line_id.line_no if record.task_line_id else False,
                    "business_key": record.task_line_id.business_key if record.task_line_id else False,
                    "source_row_no": record.source_row_no,
                    "field_name": record.field_name,
                    "raw_value": record.raw_value or False,
                    "mapped_value": record.mapped_value or False,
                    "error_code": record.error_code,
                    "error_message": record.error_message,
                }
                for record in records
            ],
        }

    @classmethod
    def build_import_task_error_report(cls, env, *, task_no="", import_batch_no="", precheck_token=""):
        del precheck_token
        task = cls._get_task_by_task_no(env, task_no or import_batch_no)
        if not task:
            raise ValidationError("未找到对应的图片包导入任务。")
        errors = env["logistics.import.error.line"].search([("task_id", "=", task.id)], order="source_row_no asc, id asc")
        if not errors:
            raise ValidationError("当前任务没有可导出的错误报告。")
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["任务行号", "源行号", "字段", "原始值", "映射值", "错误编码", "错误说明"])
        for error in errors:
            writer.writerow(
                [
                    error.task_line_id.line_no if error.task_line_id else "",
                    error.source_row_no or "",
                    error.field_name or "",
                    error.raw_value or "",
                    error.mapped_value or "",
                    error.error_code or "",
                    error.error_message or "",
                ]
            )
        return {
            "file_name": f"{task.task_no}-image-package-error-report.csv",
            "file_bytes": buffer.getvalue().encode("utf-8-sig"),
            "content_type": "text/csv; charset=utf-8",
        }

    @classmethod
    def _process_task_line(cls, env, *, task, task_line, entry, operator, retry=False):
        image_bytes = entry["content"]
        file_name = entry["file_name"]
        parsed = cls._parse_file_name(file_name)
        if not parsed["waybill_no"]:
            cls._mark_line_failed(
                env,
                task=task,
                task_line=task_line,
                error_code="IMAGE_PACKAGE_NAME_INVALID",
                error_message="文件名未包含可识别的运单号，无法命中。",
                field_name="file_name",
                raw_value=file_name,
                link_status="manual_review",
            )
            return

        line_vals = {
            "waybill_no": parsed["waybill_no"],
            "customer_line_no": parsed["customer_line_no"],
            "store_no": parsed["store_no"],
            "scene_code": parsed["scene_code"],
            "match_status": "pending",
            "match_method": False,
            "link_status": "pending",
            "link_fail_reason": False,
            "retry_count": task_line.retry_count + 1 if retry else task_line.retry_count,
            "link_mode": "manual" if retry else "auto",
        }

        waybill, customer_line, match_status, match_method, match_reason = cls._match_waybill_context(
            env,
            parsed,
        )
        line_vals.update(
            {
                "matched_waybill_id": waybill.id if waybill else False,
                "matched_customer_line_id": customer_line.id if customer_line else False,
                "match_status": match_status,
                "match_method": match_method or False,
                "match_remark": match_reason or False,
            }
        )
        task_line.sudo().write(line_vals)

        if match_status != "matched" or not waybill:
            cls._mark_line_failed(
                env,
                task=task,
                task_line=task_line,
                error_code="IMAGE_PACKAGE_MATCH_FAILED",
                error_message=match_reason or "未命中运单，无法进入正式补链。",
                field_name="waybill_no",
                raw_value=parsed["waybill_no"],
                mapped_value=waybill.name if waybill else "",
                link_status="manual_review",
                preserve_match=True,
            )
            return

        trace_event, trace_reason = cls._resolve_trace_event(waybill, parsed["scene_code"])
        if not trace_event:
            cls._mark_line_failed(
                env,
                task=task,
                task_line=task_line,
                error_code="IMAGE_PACKAGE_TRACE_EVENT_MISSING",
                error_message=trace_reason or "未找到可挂接的留痕事件，需人工复核。",
                field_name="scene_code",
                raw_value=parsed["scene_code"] or "",
                mapped_value=waybill.name or "",
                link_status="manual_review",
                preserve_match=True,
            )
            return

        try:
            evidence = cls._create_linked_evidence(
                env,
                trace_event=trace_event,
                matched_waybill=waybill,
                matched_customer_line=customer_line,
                file_name=file_name,
                image_bytes=image_bytes,
                mime_type=entry["mime_type"],
                uploaded_at=entry["capture_time"],
                operator=operator,
                scene_code=parsed["scene_code"],
            )
        except Exception as exc:
            cls._mark_line_failed(
                env,
                task=task,
                task_line=task_line,
                error_code="IMAGE_PACKAGE_LINK_FAILED",
                error_message=f"正式补链失败：{exc}",
                field_name="trace_event_id",
                raw_value=str(trace_event.id),
                mapped_value=trace_event.display_name or "",
                link_status="failed",
                preserve_match=True,
            )
            return

        task_line.sudo().write(
            {
                "status": "success",
                "message": "图片已命中并补链成功。",
                "target_res_id": evidence.id,
                "selected_trace_event_id": trace_event.id,
                "linked_evidence_id": evidence.id,
                "image_access_key": evidence.image_access_key or False,
                "link_status": "linked",
                "link_fail_reason": False,
                "linked_at": fields.Datetime.now(),
                "linked_by": operator.id,
            }
        )

    @classmethod
    def _create_linked_evidence(
        cls,
        env,
        *,
        trace_event,
        matched_waybill,
        matched_customer_line,
        file_name,
        image_bytes,
        mime_type,
        uploaded_at,
        operator,
        scene_code="",
    ):
        evidence = env["logistics.trace.evidence"].sudo().create(
            {
                "trace_event_id": trace_event.id,
                "matched_waybill_id": matched_waybill.id,
                "matched_customer_line_id": matched_customer_line.id if matched_customer_line else False,
                "match_status": "matched",
                "link_status": "linked",
                "linked_at": fields.Datetime.now(),
                "linked_by": operator.id,
                "uploaded_at": uploaded_at or fields.Datetime.now(),
                "uploader_id": operator.id,
                "remark": f"图片包导入：{scene_code or '未标记场景'} / {file_name}",
            }
        )
        evidence.upload_image_binary(
            file_name=file_name,
            content=image_bytes,
            content_type=mime_type or "application/octet-stream",
        )
        return evidence

    @classmethod
    def _build_task_result_payload(cls, task):
        task.ensure_one()
        source_file = task.source_file_id
        return {
            "task_no": task.task_no,
            "import_batch_no": task.task_no,
            "object_type": task.object_type,
            "object_type_label": cls.OBJECT_TYPE_LABEL,
            "template_code": "IMAGE_PACKAGE_ZIP_V1",
            "template_version": "v1",
            "status": task.status,
            "status_label": cls._status_label(task.status),
            "total_count": task.total_count,
            "success_count": task.success_count,
            "fail_count": task.fail_count,
            "failed_row_count": task.fail_count,
            "failed_record_count": task.fail_count,
            "matched_count": task.matched_count,
            "unmatched_count": task.unmatched_count,
            "ambiguous_count": task.ambiguous_count,
            "linked_count": task.linked_count,
            "link_failed_count": task.link_failed_count,
            "manual_review_count": task.manual_review_count,
            "started_at": fields.Datetime.to_string(task.started_at) if task.started_at else False,
            "finished_at": fields.Datetime.to_string(task.finished_at) if task.finished_at else False,
            "operator": {
                "id": task.operator_id.id if task.operator_id else False,
                "name": task.operator_id.name if task.operator_id else "",
            },
            "source_file": {
                "id": source_file.id if source_file else False,
                "file_name": source_file.file_name if source_file else "",
            },
            "summary_message": task.summary_message or "",
            "failure_reason": task.summary_message if task.status in ("failed", "partial_failed") else "",
            "error_report_url": (
                f"/api/admin/logistics/imports/tasks/{task.task_no}/error-report"
                if task.error_line_ids
                else False
            ),
            "error_report": {
                "download_ready": bool(task.error_line_ids),
                "download_url": (
                    f"/api/admin/logistics/imports/tasks/{task.task_no}/error-report"
                    if task.error_line_ids
                    else False
                ),
            },
        }

    @classmethod
    def _match_waybill_context(cls, env, parsed):
        waybill_no = (parsed.get("waybill_no") or "").strip()
        if not waybill_no:
            return False, False, "unmatched", False, "未提供运单号。"

        waybills = env["logistics.dispatch.waybill"].search([("name", "=", waybill_no)], limit=2)
        if not waybills:
            return False, False, "unmatched", False, f"未找到运单 {waybill_no}。"
        if len(waybills) > 1:
            return False, False, "ambiguous", False, f"运单号 {waybill_no} 匹配到多张运单。"

        waybill = waybills[:1]
        customer_line_key = (parsed.get("customer_line_no") or "").strip()
        store_no = (parsed.get("store_no") or "").strip()
        customer_lines = waybill.customer_line_ids
        if customer_line_key:
            direct_lines = customer_lines.filtered(lambda rec: (rec.customer_line_no or "").strip() == customer_line_key)
            if len(direct_lines) == 1:
                return waybill, direct_lines[:1], "matched", "waybill_customer_line", "按运单号 + 配送节点编号命中。"
            if len(direct_lines) > 1:
                return waybill, False, "ambiguous", "waybill_customer_line", "配送节点编号命中到多个候选。"

            store_lines = customer_lines.filtered(
                lambda rec: customer_line_key
                in {
                    (rec.store_no or "").strip(),
                    (rec.partner_no or "").strip(),
                    (rec.customer_no or "").strip(),
                }
            )
            if len(store_lines) == 1:
                return waybill, store_lines[:1], "matched", "waybill_store", "按运单号 + 门店编码命中。"
            if len(store_lines) > 1:
                return waybill, False, "ambiguous", "waybill_store", "门店编码命中到多个候选。"
            return waybill, False, "matched", "waybill_only", "仅命中运单；未识别到唯一配送节点。"

        if store_no:
            store_lines = customer_lines.filtered(
                lambda rec: store_no
                in {
                    (rec.store_no or "").strip(),
                    (rec.partner_no or "").strip(),
                    (rec.customer_no or "").strip(),
                }
            )
            if len(store_lines) == 1:
                return waybill, store_lines[:1], "matched", "waybill_store", "按运单号 + 门店编码命中。"
            if len(store_lines) > 1:
                return waybill, False, "ambiguous", "waybill_store", "门店编码命中到多个候选。"

        if len(customer_lines) == 1:
            return waybill, customer_lines[:1], "matched", "waybill_only", "仅命中运单，自动带出唯一配送节点。"
        return waybill, False, "matched", "waybill_only", "仅命中运单。"

    @classmethod
    def _resolve_trace_event(cls, waybill, scene_code):
        events = waybill.trace_event_ids.filtered(lambda rec: rec.state == "submitted").sorted(
            key=lambda rec: rec.trace_time or rec.create_date or fields.Datetime.now(),
            reverse=True,
        )
        if not events:
            return False, "当前运单下还没有可挂接的已提交留痕事件。"

        scene_code = (scene_code or "").strip()
        if scene_code:
            same_scene_events = events.filtered(lambda rec: rec.event_type == scene_code)
            if same_scene_events:
                return same_scene_events[:1], "按场景精确命中留痕事件。"

        if len(events) == 1:
            return events[:1], "当前运单仅有一条留痕，自动补链到该事件。"
        return False, "当前运单存在多条留痕，且图片文件名未命中唯一场景，需人工复核。"

    @classmethod
    def _parse_file_name(cls, file_name):
        stem = Path(file_name or "").stem
        parts = [part.strip() for part in stem.split("__") if part and part.strip()]
        waybill_no = parts[0] if parts else ""
        customer_line_no = ""
        store_no = ""
        scene_code = ""
        if len(parts) >= 2 and parts[1] in cls.SCENE_CODES:
            scene_code = parts[1]
        elif len(parts) >= 3 and parts[2] in cls.SCENE_CODES:
            scene_code = parts[2]
            customer_line_no = parts[1]
            store_no = parts[1]
        elif len(parts) >= 2:
            customer_line_no = parts[1]
            store_no = parts[1]
            scene_code = parts[2] if len(parts) >= 3 else ""
        return {
            "waybill_no": waybill_no,
            "customer_line_no": customer_line_no,
            "store_no": store_no,
            "scene_code": scene_code,
        }

    @classmethod
    def _collect_zip_entries(cls, raw_bytes):
        entries = []
        with zipfile.ZipFile(io.BytesIO(raw_bytes), mode="r") as archive:
            for info in archive.infolist():
                if info.is_dir():
                    continue
                file_name = PurePosixPath(info.filename).name
                if not file_name or file_name.startswith("."):
                    continue
                suffix = Path(file_name).suffix.lower()
                if suffix not in cls.SUPPORTED_IMAGE_SUFFIXES:
                    continue
                entries.append(
                    {
                        "entry_name": info.filename,
                        "file_name": file_name,
                        "content": archive.read(info.filename),
                        "capture_time": cls._zip_info_to_datetime(info),
                        "mime_type": mimetypes.guess_type(file_name)[0] or "application/octet-stream",
                    }
                )
        return entries

    @classmethod
    def _zip_info_to_datetime(cls, info):
        try:
            year, month, day, hour, minute, second = info.date_time
            return fields.Datetime.to_datetime(
                f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
            )
        except Exception:
            return fields.Datetime.now()

    @classmethod
    def _create_source_file(cls, env, *, raw_bytes, file_name, operator):
        storage_dir = cls._get_import_storage_dir()
        source_file_no = env["ir.sequence"].next_by_code("logistics.import.source.file") or "ISF-NEW"
        suffix = Path(file_name or "").suffix or ".zip"
        storage_key = f"{source_file_no}{suffix}"
        storage_path = storage_dir / storage_key
        storage_path.write_bytes(raw_bytes or b"")
        return env["logistics.import.source.file"].sudo().create(
            {
                "source_file_no": source_file_no,
                "file_name": file_name,
                "file_ext": suffix.lstrip("."),
                "file_sha256": hashlib.sha256(raw_bytes or b"").hexdigest(),
                "storage_path": storage_key,
                "uploader_id": operator.id,
                "uploaded_at": fields.Datetime.now(),
            }
        )

    @classmethod
    def _create_task(cls, env, *, source_file, operator):
        return env["logistics.import.task"].sudo().create(
            {
                "object_type": cls.OBJECT_TYPE,
                "source_file_id": source_file.id,
                "status": "pending",
                "operator_id": operator.id,
                "summary_message": "待执行图片包导入。",
            }
        )

    @classmethod
    def _refresh_task_summary(cls, task):
        task.ensure_one()
        lines = task.task_line_ids.filtered(lambda rec: rec.object_type == cls.OBJECT_TYPE)
        success_count = len(lines.filtered(lambda rec: rec.status == "success"))
        fail_count = len(lines.filtered(lambda rec: rec.status == "failed"))
        final_status = "success"
        if fail_count and success_count:
            final_status = "partial_failed"
        elif fail_count and not success_count:
            final_status = "failed"
        elif not lines:
            final_status = "failed"
        task.sudo().write(
            {
                "status": final_status,
                "success_count": success_count,
                "fail_count": fail_count,
                "finished_at": fields.Datetime.now(),
                "summary_message": cls._build_task_summary(task),
            }
        )

    @classmethod
    def _get_task_by_task_no(cls, env, task_no):
        task_ref = (task_no or "").strip()
        if not task_ref:
            return False
        return env["logistics.import.task"].search(
            [("task_no", "=", task_ref), ("object_type", "=", cls.OBJECT_TYPE)],
            limit=1,
        )

    @classmethod
    def _status_label(cls, status):
        return cls.STATUS_LABELS.get(status, status or "")

    @classmethod
    def _selection_label(cls, record_or_model, field_name, value):
        if not value:
            return ""
        field = record_or_model._fields[field_name]
        mapping = dict(field.selection)
        return mapping.get(value, value)

    @classmethod
    def _build_task_summary(cls, task):
        return (
            f"图片包导入完成：总数 {task.total_count}，"
            f"成功 {task.success_count}，失败 {task.fail_count}，"
            f"已命中 {task.matched_count}，待人工复核 {task.manual_review_count}，已补链 {task.linked_count}。"
        )

    @classmethod
    def _mark_line_failed(
        cls,
        env,
        *,
        task,
        task_line,
        error_code,
        error_message,
        field_name,
        raw_value,
        mapped_value="",
        link_status="failed",
        preserve_match=False,
    ):
        values = {
            "status": "failed",
            "message": error_message,
            "link_status": link_status,
            "link_fail_reason": error_message,
            "linked_evidence_id": False,
            "selected_trace_event_id": False,
        }
        if not preserve_match:
            values.update(
                {
                    "match_status": "unmatched",
                    "matched_waybill_id": False,
                    "matched_customer_line_id": False,
                    "match_method": False,
                }
            )
        task_line.sudo().write(values)
        env["logistics.import.error.line"].sudo().create(
            {
                "task_id": task.id,
                "task_line_id": task_line.id,
                "source_row_no": task_line.source_row_no,
                "field_name": field_name,
                "raw_value": raw_value or "",
                "mapped_value": mapped_value or "",
                "error_code": error_code,
                "error_message": error_message,
            }
        )

    @classmethod
    def _load_source_file_bytes(cls, source_file):
        source_file.ensure_one()
        storage_path = (source_file.storage_path or "").strip()
        if not storage_path:
            raise ValidationError("当前任务未找到图片包源文件路径。")
        file_path = cls._get_import_storage_dir() / storage_path
        if not file_path.exists():
            raise ValidationError("图片包源文件不存在，请重新上传。")
        return file_path.read_bytes()

    @classmethod
    def _get_import_storage_dir(cls):
        cls.IMPORT_ROOT_DIR.mkdir(parents=True, exist_ok=True)
        return cls.IMPORT_ROOT_DIR

    @classmethod
    def _ensure_upload_permission(cls, env):
        user = env.user
        if env.su or user.has_group("base.group_system"):
            return True
        if user.has_group("logistics_trace_core.group_logistics_image_field_operator"):
            return True
        if user.has_group("logistics_dispatch.group_logistics_import_manager"):
            return True
        if user.has_group("logistics_dispatch.group_logistics_dispatch_manager"):
            return True
        raise AccessError("当前账号无权导入图片包。")

    @classmethod
    def _ensure_retry_permission(cls, env):
        user = env.user
        if env.su or user.has_group("base.group_system"):
            return True
        if user.has_group("logistics_trace_evidence.group_logistics_image_auditor"):
            return True
        if user.has_group("logistics_dispatch.group_logistics_import_manager"):
            return True
        if user.has_group("logistics_dispatch.group_logistics_dispatch_manager"):
            return True
        raise AccessError("当前账号无权执行图片补链重试。")
