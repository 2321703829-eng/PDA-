import hashlib
import io
import json
import zipfile
import csv
from datetime import timedelta
from pathlib import Path

from odoo import fields

from odoo.addons.logistics_trace_evidence.services.image_storage_service import LogisticsEvidenceImageStorage

from .dispatch_main_export_service import DispatchMainExportService, ExportServiceError


class EvidenceImageExportService(DispatchMainExportService):
    OBJECT_TYPE = "evidence_image_bundle"
    ENTRY_TYPE = "from_waybill"
    ENTRY_TYPE_EVIDENCE = "from_evidence"
    EXPORT_MODE = "zip_package"
    PACKAGE_STRUCTURE = "evidence_image_bundle_v1"
    SOURCE_MODEL = "logistics.dispatch.waybill"
    SOURCE_MODEL_EVIDENCE = "logistics.trace.evidence"
    SOURCE_MODEL_SUMMARY = "logistics.trace.evidence.summary"
    SOURCE_PAGE_DEFAULT = "waybill_list"
    TARGET_OBJECT_TYPE = "waybill"
    TARGET_OBJECT_TYPE_EVIDENCE = "evidence"
    ENTRY_TYPE_SUMMARY = "from_summary"
    DOWNLOAD_CONTENT_TYPE = "application/zip"

    @classmethod
    def create_export_task(
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
        records, target_object_type, target_res_model = cls._get_records_for_scope(
            env,
            selected_ids=normalized_ids,
            source_model=source_model,
        )

        scope_vals = {
            "object_type": object_type,
            "entry_type": entry_type,
            "source_model": source_model,
            "source_page": (source_page or cls.SOURCE_PAGE_DEFAULT).strip() or cls.SOURCE_PAGE_DEFAULT,
            "selected_ids_json": normalized_ids,
            "selected_count": len(normalized_ids),
            "scope_snapshot_json": scope_snapshot or cls._build_scope_snapshot(records, source_model=source_model),
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
                "summary_message": f"Evidence image export task created, waiting to run. Total {len(normalized_ids)} records.",
            }
        )
        line_vals_list = []
        for index, record in enumerate(records, start=1):
            line_vals_list.append(
                {
                    "task_id": task.id,
                    "line_no": index,
                    "target_object_type": target_object_type,
                    "target_res_model": target_res_model,
                    "target_res_id": record.id,
                    "business_key": cls._build_business_key(record, source_model=source_model),
                    "display_name": cls._build_display_name(record, source_model=source_model),
                    "status": "pending",
                }
            )
        if line_vals_list:
            env["logistics.export.task.line"].sudo().create(line_vals_list)
        return cls._build_created_task_payload(task.sudo())

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
        return cls.create_export_task(
            env,
            selected_ids=selected_ids,
            source_page=source_page,
            scope_snapshot=scope_snapshot,
            request_payload=request_payload,
            object_type=object_type,
            entry_type=entry_type,
            export_mode=export_mode,
            package_structure=package_structure,
            source_model=source_model,
        )

    @classmethod
    def run_export_task(cls, env, *, task_no="", task=None):
        task = cls._get_image_export_task(env, task_no=task_no, task=task)
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
                "summary_message": f"Evidence image export task {task.task_no} is running.",
                "failure_error_code": False,
                "failure_reason": False,
                "package_metrics_json": {},
            }
        )
        try:
            package_entries = []
            manifest_items = []
            error_vals_list = []
            success_count = 0
            fail_count = 0
            skipped_count = 0
            waybill_count = 0
            evidence_count = 0
            image_count = 0
            matched_evidence_count = 0
            matched_image_count = 0
            skipped_image_count = 0
            failed_image_count = 0

            for task_line in task.sudo().task_line_ids.sorted(key=lambda rec: (rec.line_no, rec.id)):
                try:
                    package = cls._collect_task_line_package(env, task, task_line)
                    task_line.sudo().write(
                        {
                            "status": "success",
                            "message": cls._build_task_line_message(package),
                            "line_metrics_json": package["line_metrics_json"],
                            "exported_waybill_count": package["waybill_count"],
                            "exported_customer_line_count": 0,
                            "exported_order_line_count": 0,
                            "exported_goods_line_count": 0,
                        }
                    )
                    package_entries.extend(package["zip_entries"])
                    manifest_items.extend(package["manifest_items"])
                    success_count += 1
                    waybill_count += package["waybill_count"]
                    evidence_count += package["evidence_count"]
                    image_count += package["image_count"]
                    matched_evidence_count += package.get("matched_evidence_count", package["evidence_count"])
                    matched_image_count += package.get("matched_image_count", package["image_count"])
                    skipped_image_count += package.get("skipped_image_count", 0)
                    failed_image_count += package.get("failed_image_count", 0)
                except ExportServiceError as error:
                    is_skipped = error.error_code == "EXPORT_TARGET_NO_DOWNSTREAM_DATA"
                    task_line.sudo().write(
                        {
                            "status": "skipped" if is_skipped else "failed",
                            "message": str(error),
                            "line_metrics_json": {},
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
                            field_name="waybill_id",
                            raw_value=task_line.business_key,
                        )
                    )
                except Exception as error:
                    message = f"Unexpected evidence image export error: {error}"
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
                            error_code="EXPORT_ARCHIVE_BUILD_FAILED",
                            error_message=message,
                            error_stage="workbook_build",
                            field_name="waybill_id",
                            raw_value=task_line.business_key,
                        )
                    )

            task_level_error_code = False
            task_level_error_message = False
            output_file_vals = {}
            if package_entries:
                try:
                    archive_bytes = cls._build_zip_bytes(task, package_entries, manifest_items)
                    output_file_vals = cls._store_output_file(task, archive_bytes)
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

            image_gap_count = skipped_image_count + failed_image_count
            final_status = cls._compute_task_status(
                success_count=success_count,
                fail_count=fail_count,
                skipped_count=skipped_count,
                task_level_error_code=task_level_error_code,
            )
            if final_status == "success" and image_gap_count:
                final_status = "partial_failed"
            task.sudo().write(
                {
                    "status": final_status,
                    "success_count": success_count,
                    "fail_count": fail_count,
                    "skipped_count": skipped_count,
                    "exported_waybill_count": waybill_count,
                    "exported_customer_line_count": 0,
                    "exported_order_line_count": 0,
                    "exported_goods_line_count": 0,
                    "package_metrics_json": {
                        "waybill_count": waybill_count,
                        "matched_evidence_count": matched_evidence_count,
                        "evidence_count": evidence_count,
                        "matched_image_count": matched_image_count,
                        "image_count": image_count,
                        "skipped_image_count": skipped_image_count,
                        "failed_image_count": failed_image_count,
                    },
                    "finished_at": fields.Datetime.now(),
                    "summary_message": cls._build_summary_message(
                        success_count=success_count,
                        fail_count=fail_count,
                        skipped_count=skipped_count,
                        task_level_error_message=task_level_error_message,
                        skipped_image_count=skipped_image_count,
                        failed_image_count=failed_image_count,
                    ),
                    "failure_error_code": task_level_error_code or False,
                    "failure_reason": task_level_error_message or False,
                    **output_file_vals,
                }
            )
            return cls._build_task_result_payload(task.sudo())
        except Exception as error:
            error_code = error.error_code if isinstance(error, ExportServiceError) else "EXPORT_TASK_RUN_ABORTED"
            error_message = str(error)
            cls._mark_task_failed_if_running(task, error_code=error_code, error_message=error_message)
            if isinstance(error, ExportServiceError):
                raise
            raise ExportServiceError(error_code, error_message) from error

    @classmethod
    def run_waybill_export_task(cls, env, *, task_no="", task=None):
        return cls.run_export_task(env, task_no=task_no, task=task)

    @classmethod
    def _collect_task_line_package(cls, env, task, task_line):
        source_model = task.source_scope_id.source_model or cls.SOURCE_MODEL
        if source_model == cls.SOURCE_MODEL_EVIDENCE:
            return cls._collect_evidence_image_package(env, task_line)
        if source_model == cls.SOURCE_MODEL_SUMMARY:
            return cls._collect_evidence_summary_image_package(env, task_line)
        return cls._collect_waybill_image_package(env, task_line)

    @classmethod
    def _collect_waybill_image_package(cls, env, task_line):
        waybill = env[cls.SOURCE_MODEL].browse(task_line.target_res_id).exists()
        if not waybill:
            raise ExportServiceError("EXPORT_WAYBILL_NOT_FOUND", f"Waybill for line {task_line.line_no} was not found.")

        evidences = waybill.evidence_ids.sorted(key=lambda rec: (rec.uploaded_at or fields.Datetime.now(), rec.sequence, rec.id))
        if not evidences:
            raise ExportServiceError(
                "EXPORT_TARGET_NO_DOWNSTREAM_DATA",
                f"Waybill {waybill.name or waybill.id} has no evidence images to export.",
            )

        storage = LogisticsEvidenceImageStorage(env)
        zip_entries = []
        manifest_items = []
        matched_image_count = 0
        exported_image_count = 0
        skipped_image_count = 0
        failed_image_count = 0
        matched_evidence_count = 0
        exported_evidence_count = 0
        waybill_folder = cls._sanitize_name(waybill.name or f"waybill_{waybill.id}")

        for evidence in evidences:
            evidence_entries = cls._build_evidence_image_entries(evidence)
            if not evidence_entries:
                continue
            matched_evidence_count += 1
            evidence_folder = cls._sanitize_name(f"evidence_{evidence.id}")
            exported_for_evidence = 0
            for image_index, image_entry in enumerate(evidence_entries, start=1):
                matched_image_count += 1
                try:
                    file_payload = cls._read_evidence_image_entry(storage, image_entry)
                except Exception as error:
                    if cls._is_missing_image_error(error):
                        skipped_image_count += 1
                        continue
                    failed_image_count += 1
                    continue
                exported_image_count += 1
                exported_for_evidence += 1
                safe_file_name = cls._sanitize_name(file_payload["file_name"] or f"image_{image_index}")
                extension = Path(safe_file_name).suffix or Path(image_entry.get("file_name") or "").suffix or ".bin"
                if not Path(safe_file_name).suffix:
                    safe_file_name = f"{safe_file_name}{extension}"
                archive_name = f"{waybill_folder}/{evidence_folder}/{image_index:03d}_{safe_file_name}"
                zip_entries.append({"archive_name": archive_name, "content": file_payload["content"]})
                manifest_items.append(
                    {
                        "waybill_id": waybill.id,
                        "waybill_no": waybill.name or "",
                        "batch_id": waybill.batch_id.id if waybill.batch_id else False,
                        "batch_no": waybill.batch_id.name if waybill.batch_id else "",
                        "trace_event_id": evidence.trace_event_id.id,
                        "trace_event_name": evidence.trace_event_id.display_name or "",
                        "evidence_id": evidence.id,
                        "evidence_name": evidence.name or "",
                        "evidence_uploaded_at": fields.Datetime.to_string(evidence.uploaded_at) if evidence.uploaded_at else False,
                        "evidence_remark": evidence.remark or "",
                        "image_id": image_entry.get("image_id") or False,
                        "image_access_key": image_entry.get("image_access_key") or "",
                        "image_file_name": file_payload["file_name"],
                        "archive_name": archive_name,
                        "storage_provider": image_entry.get("storage_provider") or "",
                    }
                )
            if exported_for_evidence:
                exported_evidence_count += 1

        if not zip_entries:
            if failed_image_count:
                raise ExportServiceError(
                    "EXPORT_IMAGE_CONTENT_UNREADABLE",
                    f"Waybill {waybill.name or waybill.id} has image records, but none could be exported successfully.",
                )
            raise ExportServiceError(
                "EXPORT_TARGET_NO_DOWNSTREAM_DATA",
                f"Waybill {waybill.name or waybill.id} has no readable evidence images to export.",
            )

        return {
            "zip_entries": zip_entries,
            "manifest_items": manifest_items,
            "waybill_count": 1,
            "matched_evidence_count": matched_evidence_count,
            "evidence_count": exported_evidence_count,
            "matched_image_count": matched_image_count,
            "image_count": exported_image_count,
            "skipped_image_count": skipped_image_count,
            "failed_image_count": failed_image_count,
            "line_metrics_json": {
                "waybill_count": 1,
                "matched_evidence_count": matched_evidence_count,
                "evidence_count": exported_evidence_count,
                "matched_image_count": matched_image_count,
                "image_count": exported_image_count,
                "skipped_image_count": skipped_image_count,
                "failed_image_count": failed_image_count,
            },
        }

    @classmethod
    def _collect_evidence_image_package(cls, env, task_line):
        evidence = env[cls.SOURCE_MODEL_EVIDENCE].browse(task_line.target_res_id).exists()
        if not evidence:
            raise ExportServiceError("EXPORT_EVIDENCE_NOT_FOUND", f"Evidence for line {task_line.line_no} was not found.")

        evidence_entries = cls._build_evidence_image_entries(evidence)
        if not evidence_entries:
            raise ExportServiceError(
                "EXPORT_TARGET_NO_DOWNSTREAM_DATA",
                f"Evidence {evidence.name or evidence.id} has no exportable images.",
            )

        storage = LogisticsEvidenceImageStorage(env)
        zip_entries = []
        manifest_items = []
        matched_image_count = 0
        exported_image_count = 0
        skipped_image_count = 0
        failed_image_count = 0
        waybill = evidence.waybill_id
        waybill_folder = cls._sanitize_name(waybill.name if waybill else "waybill_unbound")
        evidence_folder = cls._sanitize_name(f"evidence_{evidence.id}")

        for image_index, image_entry in enumerate(evidence_entries, start=1):
            matched_image_count += 1
            try:
                file_payload = cls._read_evidence_image_entry(storage, image_entry)
            except Exception as error:
                if cls._is_missing_image_error(error):
                    skipped_image_count += 1
                    continue
                failed_image_count += 1
                continue
            exported_image_count += 1
            safe_file_name = cls._sanitize_name(file_payload["file_name"] or f"image_{image_index}")
            extension = Path(safe_file_name).suffix or Path(image_entry.get("file_name") or "").suffix or ".bin"
            if not Path(safe_file_name).suffix:
                safe_file_name = f"{safe_file_name}{extension}"
            archive_name = f"{waybill_folder}/{evidence_folder}/{image_index:03d}_{safe_file_name}"
            zip_entries.append({"archive_name": archive_name, "content": file_payload["content"]})
            manifest_items.append(
                {
                    "waybill_id": waybill.id if waybill else False,
                    "waybill_no": waybill.name if waybill else "",
                    "batch_id": waybill.batch_id.id if waybill and waybill.batch_id else False,
                    "batch_no": waybill.batch_id.name if waybill and waybill.batch_id else "",
                    "trace_event_id": evidence.trace_event_id.id,
                    "trace_event_name": evidence.trace_event_id.display_name or "",
                    "evidence_id": evidence.id,
                    "evidence_name": evidence.name or "",
                    "evidence_uploaded_at": fields.Datetime.to_string(evidence.uploaded_at) if evidence.uploaded_at else False,
                    "evidence_remark": evidence.remark or "",
                    "image_id": image_entry.get("image_id") or False,
                    "image_access_key": image_entry.get("image_access_key") or "",
                    "image_file_name": file_payload["file_name"],
                    "archive_name": archive_name,
                    "storage_provider": image_entry.get("storage_provider") or "",
                }
            )

        if not zip_entries:
            if failed_image_count:
                raise ExportServiceError(
                    "EXPORT_IMAGE_CONTENT_UNREADABLE",
                    f"Evidence {evidence.name or evidence.id} has image records, but none could be exported successfully.",
                )
            raise ExportServiceError(
                "EXPORT_TARGET_NO_DOWNSTREAM_DATA",
                f"Evidence {evidence.name or evidence.id} has no readable evidence images to export.",
            )

        return {
            "zip_entries": zip_entries,
            "manifest_items": manifest_items,
            "waybill_count": 1 if waybill else 0,
            "matched_evidence_count": 1,
            "evidence_count": 1,
            "matched_image_count": matched_image_count,
            "image_count": exported_image_count,
            "skipped_image_count": skipped_image_count,
            "failed_image_count": failed_image_count,
            "line_metrics_json": {
                "waybill_count": 1 if waybill else 0,
                "matched_evidence_count": 1,
                "evidence_count": 1,
                "matched_image_count": matched_image_count,
                "image_count": exported_image_count,
                "skipped_image_count": skipped_image_count,
                "failed_image_count": failed_image_count,
            },
        }

    @classmethod
    def _collect_evidence_summary_image_package(cls, env, task_line):
        summary = env[cls.SOURCE_MODEL_SUMMARY].browse(task_line.target_res_id).exists()
        if not summary:
            raise ExportServiceError(
                "EXPORT_EVIDENCE_SUMMARY_NOT_FOUND",
                f"Evidence summary for line {task_line.line_no} was not found.",
            )

        waybill = summary.waybill_id
        if not waybill:
            raise ExportServiceError(
                "EXPORT_WAYBILL_NOT_FOUND",
                f"Evidence summary {summary.id} is not linked to a readable waybill.",
            )

        evidences = waybill.evidence_ids.filtered(lambda rec: (rec.upload_role or "unknown") == (summary.upload_role or "unknown"))
        evidences = evidences.sorted(key=lambda rec: (rec.uploaded_at or fields.Datetime.now(), rec.sequence, rec.id))
        if not evidences:
            raise ExportServiceError(
                "EXPORT_TARGET_NO_DOWNSTREAM_DATA",
                f"Waybill {waybill.name or waybill.id} has no evidence images under upload_role {summary.upload_role or 'unknown'}.",
            )

        storage = LogisticsEvidenceImageStorage(env)
        zip_entries = []
        manifest_items = []
        matched_image_count = 0
        exported_image_count = 0
        skipped_image_count = 0
        failed_image_count = 0
        matched_evidence_count = 0
        exported_evidence_count = 0
        waybill_folder = cls._sanitize_name(waybill.name or f"waybill_{waybill.id}")
        role_folder = cls._sanitize_name(summary.upload_role or "unknown")

        for evidence in evidences:
            evidence_entries = cls._build_evidence_image_entries(evidence)
            if not evidence_entries:
                continue
            matched_evidence_count += 1
            evidence_folder = cls._sanitize_name(f"evidence_{evidence.id}")
            exported_for_evidence = 0
            for image_index, image_entry in enumerate(evidence_entries, start=1):
                matched_image_count += 1
                try:
                    file_payload = cls._read_evidence_image_entry(storage, image_entry)
                except Exception as error:
                    if cls._is_missing_image_error(error):
                        skipped_image_count += 1
                        continue
                    failed_image_count += 1
                    continue
                exported_image_count += 1
                exported_for_evidence += 1
                safe_file_name = cls._sanitize_name(file_payload["file_name"] or f"image_{image_index}")
                extension = Path(safe_file_name).suffix or Path(image_entry.get("file_name") or "").suffix or ".bin"
                if not Path(safe_file_name).suffix:
                    safe_file_name = f"{safe_file_name}{extension}"
                archive_name = f"{waybill_folder}/{role_folder}/{evidence_folder}/{image_index:03d}_{safe_file_name}"
                zip_entries.append({"archive_name": archive_name, "content": file_payload["content"]})
                manifest_items.append(
                    {
                        "waybill_id": waybill.id,
                        "waybill_no": waybill.name or "",
                        "batch_id": waybill.batch_id.id if waybill.batch_id else False,
                        "batch_no": waybill.batch_id.name if waybill.batch_id else "",
                        "upload_role": summary.upload_role or "unknown",
                        "trace_event_id": evidence.trace_event_id.id,
                        "trace_event_name": evidence.trace_event_id.display_name or "",
                        "evidence_id": evidence.id,
                        "evidence_name": evidence.name or "",
                        "evidence_uploaded_at": fields.Datetime.to_string(evidence.uploaded_at) if evidence.uploaded_at else False,
                        "evidence_remark": evidence.remark or "",
                        "image_id": image_entry.get("image_id") or False,
                        "image_access_key": image_entry.get("image_access_key") or "",
                        "image_file_name": file_payload["file_name"],
                        "archive_name": archive_name,
                        "storage_provider": image_entry.get("storage_provider") or "",
                    }
                )
            if exported_for_evidence:
                exported_evidence_count += 1

        if not zip_entries:
            if failed_image_count:
                raise ExportServiceError(
                    "EXPORT_IMAGE_CONTENT_UNREADABLE",
                    f"Waybill {waybill.name or waybill.id} has image records under upload_role {summary.upload_role or 'unknown'}, but none could be exported successfully.",
                )
            raise ExportServiceError(
                "EXPORT_TARGET_NO_DOWNSTREAM_DATA",
                f"Waybill {waybill.name or waybill.id} has no readable evidence images under upload_role {summary.upload_role or 'unknown'}.",
            )

        return {
            "zip_entries": zip_entries,
            "manifest_items": manifest_items,
            "waybill_count": 1,
            "matched_evidence_count": matched_evidence_count,
            "evidence_count": exported_evidence_count,
            "matched_image_count": matched_image_count,
            "image_count": exported_image_count,
            "skipped_image_count": skipped_image_count,
            "failed_image_count": failed_image_count,
            "line_metrics_json": {
                "waybill_count": 1,
                "matched_evidence_count": matched_evidence_count,
                "evidence_count": exported_evidence_count,
                "matched_image_count": matched_image_count,
                "image_count": exported_image_count,
                "skipped_image_count": skipped_image_count,
                "failed_image_count": failed_image_count,
            },
        }

    @classmethod
    def _build_evidence_image_entries(cls, evidence):
        image_entries = []
        image_records = evidence.image_ids.sorted(key=lambda rec: (rec.sequence, rec.id))
        for image_record in image_records:
            image_entries.append(
                {
                    "image_id": image_record.id,
                    "image_access_key": image_record.image_access_key,
                    "file_name": image_record.source_filename or image_record.stored_file_name or image_record.image_access_key,
                    "storage_provider": image_record.storage_provider,
                    "image_record": image_record,
                }
            )
        if image_entries:
            return image_entries
        if evidence.image_access_key or evidence.preview_url or evidence.full_url:
            return [
                {
                    "image_id": False,
                    "image_access_key": evidence.image_access_key or "",
                    "file_name": evidence.name or f"evidence_{evidence.id}",
                    "storage_provider": "legacy_url",
                    "legacy_preview_url": evidence.preview_url or "",
                    "legacy_full_url": evidence.full_url or "",
                }
            ]
        return []

    @classmethod
    def _read_evidence_image_entry(cls, storage, image_entry):
        image_record = image_entry.get("image_record")
        if image_record:
            return storage.read_image(image_record)
        return storage.read_legacy_image(
            image_entry.get("file_name"),
            image_entry.get("legacy_full_url"),
            image_entry.get("legacy_preview_url"),
        )

    @classmethod
    def _is_missing_image_error(cls, error):
        message = str(error or "")
        missing_markers = (
            "Legacy image file does not exist on local storage.",
            "Image file does not exist on server storage.",
            "Image storage path is missing.",
        )
        return any(marker in message for marker in missing_markers)

    @classmethod
    def _build_zip_bytes(cls, task, zip_entries, manifest_items):
        try:
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
                for entry in zip_entries:
                    archive.writestr(entry["archive_name"], entry["content"])
                archive.writestr("index.csv", cls._build_index_csv_bytes(manifest_items))
                archive.writestr(
                    "manifest.json",
                    json.dumps(
                        {
                            "task_no": task.task_no,
                            "object_type": cls.OBJECT_TYPE,
                            "entry_type": task.entry_type or cls.ENTRY_TYPE,
                            "generated_at": fields.Datetime.to_string(fields.Datetime.now()),
                            "items": manifest_items,
                        },
                        ensure_ascii=False,
                        indent=2,
                    ).encode("utf-8"),
                )
            return buffer.getvalue()
        except Exception as error:
            raise ExportServiceError("EXPORT_ARCHIVE_BUILD_FAILED", f"Failed to build image archive: {error}") from error

    @classmethod
    def _build_index_csv_bytes(cls, manifest_items):
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            [
                "batch_no",
                "waybill_no",
                "trace_event_id",
                "trace_event_name",
                "evidence_id",
                "evidence_name",
                "image_id",
                "image_access_key",
                "image_file_name",
                "storage_provider",
                "evidence_uploaded_at",
                "archive_name",
            ]
        )
        for item in manifest_items:
            writer.writerow(
                [
                    item.get("batch_no") or "",
                    item.get("waybill_no") or "",
                    item.get("trace_event_id") or "",
                    item.get("trace_event_name") or "",
                    item.get("evidence_id") or "",
                    item.get("evidence_name") or "",
                    item.get("image_id") or "",
                    item.get("image_access_key") or "",
                    item.get("image_file_name") or "",
                    item.get("storage_provider") or "",
                    item.get("evidence_uploaded_at") or "",
                    item.get("archive_name") or "",
                ]
            )
        return buffer.getvalue().encode("utf-8-sig")

    @classmethod
    def _store_output_file(cls, task, archive_bytes):
        task.ensure_one()
        timestamp = fields.Datetime.now()
        file_name = f"TSL-EXPORT-EVIDENCE-IMAGE-{timestamp.strftime('%Y%m%d-%H%M%S')}.zip"
        return cls._store_output_file_bytes(task, archive_bytes, file_name=file_name)

    @classmethod
    def _store_output_file_bytes(cls, task, file_bytes, *, file_name):
        task.ensure_one()
        timestamp = fields.Datetime.now()
        export_root = cls._get_export_root_dir()
        folder = export_root / timestamp.strftime("%Y") / timestamp.strftime("%m") / timestamp.strftime("%d") / task.task_no
        file_path = folder / file_name
        try:
            folder.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(file_bytes or b"")
        except OSError as error:
            raise ExportServiceError("EXPORT_FILE_WRITE_FAILED", f"Failed to store export file: {error}") from error
        download_ready_at = fields.Datetime.now()
        expires_at = download_ready_at + timedelta(days=cls.DOWNLOAD_EXPIRE_DAYS)
        relative_path = file_path.relative_to(export_root).as_posix()
        return {
            "download_ready_at": download_ready_at,
            "expires_at": expires_at,
            "output_file_name": file_name,
            "output_file_ext": "zip",
            "output_storage_path": relative_path,
            "output_file_sha256": hashlib.sha256(file_bytes or b"").hexdigest(),
            "output_file_size": len(file_bytes or b""),
        }

    @classmethod
    def _validate_create_contract(cls, *, object_type, entry_type, export_mode, package_structure, source_model):
        if object_type != cls.OBJECT_TYPE:
            raise ExportServiceError("EXPORT_TASK_OBJECT_TYPE_INVALID", f"Unsupported object_type: {object_type}")
        if entry_type not in (cls.ENTRY_TYPE, cls.ENTRY_TYPE_EVIDENCE, cls.ENTRY_TYPE_SUMMARY):
            raise ExportServiceError("EXPORT_TASK_ENTRY_TYPE_INVALID", f"Unsupported entry_type: {entry_type}")
        if export_mode != cls.EXPORT_MODE:
            raise ExportServiceError("EXPORT_MODE_INVALID", f"Unsupported export_mode: {export_mode}")
        if package_structure != cls.PACKAGE_STRUCTURE:
            raise ExportServiceError("EXPORT_PACKAGE_STRUCTURE_INVALID", f"Unsupported package_structure: {package_structure}")
        valid_pairs = {
            (cls.ENTRY_TYPE, cls.SOURCE_MODEL),
            (cls.ENTRY_TYPE_EVIDENCE, cls.SOURCE_MODEL_EVIDENCE),
            (cls.ENTRY_TYPE_SUMMARY, cls.SOURCE_MODEL_SUMMARY),
        }
        if (entry_type, source_model) not in valid_pairs:
            raise ExportServiceError("EXPORT_SCOPE_SNAPSHOT_INVALID", f"Unsupported source_model: {source_model}")

    @classmethod
    def _get_records_for_scope(cls, env, *, selected_ids, source_model):
        if source_model == cls.SOURCE_MODEL_EVIDENCE:
            return cls._get_evidences_for_scope(env, selected_ids), cls.TARGET_OBJECT_TYPE_EVIDENCE, cls.SOURCE_MODEL_EVIDENCE
        if source_model == cls.SOURCE_MODEL_SUMMARY:
            return cls._get_summaries_for_scope(env, selected_ids), cls.TARGET_OBJECT_TYPE, cls.SOURCE_MODEL_SUMMARY
        return cls._get_waybills_for_scope(env, selected_ids), cls.TARGET_OBJECT_TYPE, cls.SOURCE_MODEL

    @classmethod
    def _get_evidences_for_scope(cls, env, selected_ids):
        model = env[cls.SOURCE_MODEL_EVIDENCE]
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
            raise ExportServiceError("EXPORT_EVIDENCE_NOT_FOUND", f"Evidence ids not found or not readable: {missing_ids}")
        return model.browse([record.id for record in ordered_records])

    @classmethod
    def _get_summaries_for_scope(cls, env, selected_ids):
        model = env[cls.SOURCE_MODEL_SUMMARY]
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
            raise ExportServiceError("EXPORT_EVIDENCE_SUMMARY_NOT_FOUND", f"Evidence summary ids not found or not readable: {missing_ids}")
        return model.browse([record.id for record in ordered_records])

    @classmethod
    def _build_scope_snapshot(cls, records, *, source_model):
        if source_model == cls.SOURCE_MODEL_EVIDENCE:
            items = []
            for evidence in records:
                items.append(
                    {
                        "id": evidence.id,
                        "evidence_name": evidence.name or "",
                        "trace_event_id": evidence.trace_event_id.id,
                        "waybill_no": evidence.waybill_id.name or "",
                    }
                )
            return {
                "object_type": cls.OBJECT_TYPE,
                "entry_type": cls.ENTRY_TYPE_EVIDENCE,
                "selected_count": len(items),
                "items": items,
            }
        if source_model == cls.SOURCE_MODEL_SUMMARY:
            items = []
            for summary in records:
                items.append(
                    {
                        "id": summary.id,
                        "waybill_id": summary.waybill_id.id if summary.waybill_id else False,
                        "waybill_no": summary.waybill_no or "",
                        "upload_role": summary.upload_role or "unknown",
                        "evidence_count": summary.evidence_count or 0,
                    }
                )
            return {
                "object_type": cls.OBJECT_TYPE,
                "entry_type": cls.ENTRY_TYPE_SUMMARY,
                "selected_count": len(items),
                "items": items,
            }
        return super()._build_scope_snapshot(records)

    @classmethod
    def _build_business_key(cls, record, *, source_model):
        if source_model == cls.SOURCE_MODEL_EVIDENCE:
            return record.name or f"evidence_{record.id}"
        if source_model == cls.SOURCE_MODEL_SUMMARY:
            return f"{record.waybill_no or record.waybill_id.id or record.id}:{record.upload_role or 'unknown'}"
        return record.name or str(record.id)

    @classmethod
    def _build_display_name(cls, record, *, source_model):
        if source_model == cls.SOURCE_MODEL_EVIDENCE:
            return f"Evidence {record.name or record.id}"
        if source_model == cls.SOURCE_MODEL_SUMMARY:
            return f"Waybill {record.waybill_no or record.waybill_id.id or record.id} / {record.upload_role or 'unknown'}"
        return f"Waybill {record.name or record.id}"

    @classmethod
    def _get_image_export_task(cls, env, *, task_no="", task=None):
        task = super()._get_task(env, task_no=task_no, task=task)
        if task.object_type != cls.OBJECT_TYPE:
            raise ExportServiceError(
                "EXPORT_TASK_OBJECT_TYPE_INVALID",
                f"Task {task.task_no} does not belong to object_type {cls.OBJECT_TYPE}.",
            )
        return task

    @classmethod
    def _build_summary_message(
        cls,
        *,
        success_count,
        fail_count,
        skipped_count,
        task_level_error_message,
        skipped_image_count=0,
        failed_image_count=0,
    ):
        if task_level_error_message:
            return task_level_error_message
        message = (
            f"Evidence image export finished. Success lines {success_count}, "
            f"failed lines {fail_count}, skipped lines {skipped_count}."
        )
        if skipped_image_count or failed_image_count:
            message += (
                f" Images not exported: data-missing {skipped_image_count}, "
                f"system-failed {failed_image_count}."
            )
        return message

    @classmethod
    def _build_task_line_message(cls, package):
        matched_images = package.get("matched_image_count", package["image_count"])
        skipped_images = package.get("skipped_image_count", 0)
        failed_images = package.get("failed_image_count", 0)
        message = (
            f"Matched Waybill {package['waybill_count']} / "
            f"Exported Evidence {package['evidence_count']} / "
            f"Exported Images {package['image_count']}"
        )
        if matched_images != package["image_count"] or skipped_images or failed_images:
            message += (
                f" (matched {matched_images}, "
                f"data-missing {skipped_images}, system-failed {failed_images})"
            )
        return f"{message}."

    @classmethod
    def _build_task_result_payload(cls, task):
        task.ensure_one()
        download_ready = bool(task.output_storage_path) and task.status in ("success", "partial_failed")
        error_ready = bool(task.error_line_ids)
        metrics = task.package_metrics_json or {}
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
                "waybill_count": int(metrics.get("waybill_count", 0) or 0),
                "matched_evidence_count": int(metrics.get("matched_evidence_count", 0) or 0),
                "evidence_count": int(metrics.get("evidence_count", 0) or 0),
                "matched_image_count": int(metrics.get("matched_image_count", 0) or 0),
                "image_count": int(metrics.get("image_count", 0) or 0),
                "skipped_image_count": int(metrics.get("skipped_image_count", 0) or 0),
                "failed_image_count": int(metrics.get("failed_image_count", 0) or 0),
            },
            "summary_message": task.summary_message or cls._build_summary_message(
                success_count=task.success_count,
                fail_count=task.fail_count,
                skipped_count=task.skipped_count,
                task_level_error_message=task.failure_reason,
                skipped_image_count=int(metrics.get("skipped_image_count", 0) or 0),
                failed_image_count=int(metrics.get("failed_image_count", 0) or 0),
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
        waybill_count = int(line_metrics.get("waybill_count", 0) or 0)
        evidence_count = int(line_metrics.get("evidence_count", 0) or 0)
        image_count = int(line_metrics.get("image_count", 0) or 0)
        matched_image_count = int(line_metrics.get("matched_image_count", 0) or 0)
        skipped_image_count = int(line_metrics.get("skipped_image_count", 0) or 0)
        failed_image_count = int(line_metrics.get("failed_image_count", 0) or 0)
        export_count_summary = f"Waybill {waybill_count} / Evidence {evidence_count} / Images {image_count}"
        if matched_image_count != image_count or skipped_image_count or failed_image_count:
            export_count_summary += (
                f" (matched {matched_image_count}, "
                f"data-missing {skipped_image_count}, system-failed {failed_image_count})"
            )
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
            "export_count_summary": export_count_summary,
            "line_metrics": {
                "waybill_count": waybill_count,
                "evidence_count": evidence_count,
                "image_count": image_count,
                "matched_image_count": matched_image_count,
                "skipped_image_count": skipped_image_count,
                "failed_image_count": failed_image_count,
            },
            "exported_waybill_count": task_line.exported_waybill_count,
            "exported_customer_line_count": task_line.exported_customer_line_count,
            "exported_order_line_count": task_line.exported_order_line_count,
            "exported_goods_line_count": task_line.exported_goods_line_count,
        }

    @classmethod
    def _error_stage_for_code(cls, error_code):
        if error_code in ("EXPORT_WAYBILL_NOT_FOUND", "EXPORT_EVIDENCE_NOT_FOUND"):
            return "target_resolve"
        if error_code in ("EXPORT_TARGET_NO_DOWNSTREAM_DATA",):
            return "data_collect"
        if error_code == "EXPORT_ARCHIVE_BUILD_FAILED":
            return "workbook_build"
        if error_code in ("EXPORT_FILE_WRITE_FAILED", "EXPORT_FILE_READ_FAILED", "EXPORT_OUTPUT_FILE_MISSING"):
            return "file_store"
        return "scope_validate"

    @classmethod
    def _sanitize_name(cls, value):
        raw = (value or "").strip()
        if not raw:
            return "unnamed"
        safe_chars = []
        for char in raw:
            if char.isalnum() or char in ("-", "_", "."):
                safe_chars.append(char)
            else:
                safe_chars.append("_")
        sanitized = "".join(safe_chars).strip("._")
        return sanitized or "unnamed"
