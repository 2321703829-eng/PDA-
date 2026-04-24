from collections import Counter
from datetime import datetime, time

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.addons.logistics_base.models.selection_options import DRIVER_DISPATCH_STATUS_SELECTION, SHIFT_TYPE_SELECTION


DRIVER_MANAGEMENT_VIEW_GROUP = "logistics_web.group_logistics_driver_management_viewer"
DRIVER_MANAGEMENT_ACCESS_ERROR = "当前账号暂无查看司机管理的权限。"
BATCH_ACTIVE_STATES = ("draft", "ready", "loading", "in_transit")


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    logistics_has_own_vehicle = fields.Boolean(
        string="是否有自有车",
        default=False,
    )


class LogisticsDispatchWaybill(models.Model):
    _inherit = "logistics.dispatch.waybill"

    @api.model
    def getDriverList(self, params=None):
        self._ensure_driver_management_access()
        params = params or {}
        page = max(int(params.get("page") or 1), 1)
        page_size = min(max(int(params.get("page_size") or 20), 1), 100)
        sort_by = params.get("sort_by") or "latest_execution_at"
        sort_order = "asc" if (params.get("sort_order") or "").lower() == "asc" else "desc"
        keyword = (params.get("keyword") or "").strip()
        status = (params.get("status") or "").strip()
        vehicle_id = int(params.get("vehicle_id") or 0)
        warehouse_id = int(params.get("warehouse_id") or 0)

        snapshots = []
        for driver in self._search_driver_employees():
            snapshot = self._build_driver_snapshot(driver)
            if self._match_driver_snapshot(
                snapshot,
                keyword=keyword,
                status=status,
                vehicle_id=vehicle_id,
                warehouse_id=warehouse_id,
            ):
                snapshots.append(snapshot)

        snapshots = self._sort_driver_snapshots(snapshots, sort_by=sort_by, sort_order=sort_order)
        total = len(snapshots)
        start = (page - 1) * page_size
        end = start + page_size
        return {
            "items": snapshots[start:end],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @api.model
    def getDriverFilterOptions(self):
        self._ensure_driver_management_access()
        snapshots = [self._build_driver_snapshot(driver) for driver in self._search_driver_employees()]
        vehicle_ids = [item["current_vehicle_id"] for item in snapshots if item.get("current_vehicle_id")]
        warehouse_ids = [item["current_warehouse_id"] for item in snapshots if item.get("current_warehouse_id")]
        vehicles = self.env["fleet.vehicle"].sudo().browse(list(set(vehicle_ids)))
        warehouses = self.env["stock.warehouse"].sudo().browse(list(set(warehouse_ids)))
        return {
            "status_options": [
                {"value": value, "label": label}
                for value, label in DRIVER_DISPATCH_STATUS_SELECTION
            ],
            "vehicle_options": [
                {"value": str(vehicle.id), "label": self._get_vehicle_label(vehicle)}
                for vehicle in vehicles.sorted(lambda item: (item.license_plate or item.name or "", item.id))
            ],
            "warehouse_options": [
                {"value": str(warehouse.id), "label": warehouse.name or ""}
                for warehouse in warehouses.sorted(lambda item: (item.name or "", item.id))
            ],
        }

    @api.model
    def get_driver_profile_overview_payload(self, driver_id):
        driver = self._get_driver_employee(driver_id)
        profile = self._get_driver_profile(driver)
        all_waybills = self._get_driver_waybills(driver.id)
        recent_waybills = self._get_driver_waybills(driver.id, date_from=self._days_ago(30))
        current_batch = self._get_current_batch_for_driver(driver.id)
        latest_batch = self._get_latest_batch(driver.id)
        current_vehicle = current_batch.vehicle_id if current_batch else False
        current_warehouse = current_batch.warehouse_id if current_batch else False
        current_status = self._get_driver_runtime_status(driver, current_batch)
        shift_type = self._get_shift_type_from_batch(current_batch)
        recent_vehicle = current_vehicle or (latest_batch.vehicle_id if latest_batch else False)

        top_regions = []
        top_stores = []
        if recent_waybills:
            region_counter = Counter(self._get_store_region(waybill.store_id) for waybill in recent_waybills if waybill.store_id)
            store_counter = Counter(waybill.store_id.name for waybill in recent_waybills if waybill.store_id)
            top_regions = [item for item, _count in region_counter.most_common(3) if item]
            top_stores = [item for item, _count in store_counter.most_common(3) if item]

        batch_count = len(set(all_waybills.mapped("batch_id").ids))
        recent_batch_count = len(set(recent_waybills.mapped("batch_id").ids))
        recent_store_count = len(set(recent_waybills.mapped("store_id").ids))
        recent_region_count = len(
            {
                region
                for region in (self._get_store_region(waybill.store_id) for waybill in recent_waybills if waybill.store_id)
                if region
            }
        )

        return {
            "driver_id": driver.id,
            "driver_name": profile.driver_name or driver.name,
            "mobile": self._mask_mobile(profile.driver_phone or self._get_employee_mobile(driver)),
            "status": current_status,
            "status_label": self._get_dispatch_status_label(current_status),
            "dispatch_enabled": bool(getattr(driver, "active", True)),
            "allow_night_shift": bool(profile.allow_night_shift) if profile else False,
            "shift_type": shift_type,
            "shift_type_label": self._get_shift_type_label(shift_type),
            "internal_driver_code": profile.internal_driver_code if profile else "",
            "driver_license_level": profile.driver_license_level if profile else "",
            "current_residence_region": profile.current_residence_region if profile else "",
            "remark": getattr(driver, "notes", False) or getattr(driver, "note", False) or "",
            "latest_execution_at": self._get_driver_latest_execution_at(driver.id),
            "current_vehicle": self._serialize_vehicle(current_vehicle),
            "current_warehouse": self._serialize_warehouse(current_warehouse),
            "current_batch": self._serialize_batch(current_batch),
            "recent_vehicle": self._serialize_vehicle(recent_vehicle),
            "execution_summary": {
                "batch_count": batch_count,
                "waybill_count": len(all_waybills),
                "recent_30d_waybill_count": len(recent_waybills),
                "recent_30d_batch_count": recent_batch_count,
                "recent_store_count": recent_store_count,
                "recent_region_count": recent_region_count,
                "top_regions": top_regions,
                "top_stores": top_stores,
            },
        }

    @api.model
    def get_driver_kpi_cards_payload(self, driver_id):
        self._get_driver_employee(driver_id)
        current_month_start = self._month_start(fields.Date.context_today(self))
        month_waybills = self._get_driver_waybills(driver_id, date_from=current_month_start)
        valid_month_waybills = month_waybills.filtered(lambda item: item.state != "cancelled")
        valid_all_waybills = self._get_driver_waybills(driver_id).filtered(lambda item: item.state != "cancelled")

        return {
            "month_waybill_count": len(valid_month_waybills),
            "month_avg_exception_rate": self._compute_average_month_exception_rate(driver_id),
            "current_month_signed_rate": self._safe_ratio(
                len(valid_month_waybills.filtered(lambda item: item.state in ("signed", "done"))),
                len(valid_month_waybills),
            ),
            "current_month_timeout_rate": self._safe_ratio(
                len(valid_month_waybills.filtered(self._is_timeout_waybill)),
                len(valid_month_waybills),
            ),
            "missing_evidence_rate": self._safe_ratio(
                len(valid_all_waybills.filtered(self._is_missing_evidence_waybill)),
                len(valid_all_waybills),
            ),
            "exception_count": self.env["logistics.trace.exception"].sudo().search_count(
                [("waybill_id.driver_employee_id", "=", driver_id)]
            ),
        }

    @api.model
    def get_driver_risk_summary_payload(self, driver_id):
        self._get_driver_employee(driver_id)
        waybills = self._get_driver_waybills(driver_id).filtered(lambda item: item.state != "cancelled")
        exceptions = self.env["logistics.trace.exception"].sudo().search(
            [("waybill_id.driver_employee_id", "=", driver_id)],
            order="report_time desc, id desc",
        )
        top_exception_types = Counter(exceptions.mapped("exception_type"))
        exception_type_labels = dict(self.env["logistics.trace.exception"]._fields["exception_type"].selection)

        return {
            "exception_waybill_count": len(waybills.filtered(lambda item: item.exception_status in ("open", "processing", "closed"))),
            "severe_exception_count": len(exceptions.filtered(lambda item: item.severity_level in ("high", "critical"))),
            "timeout_waybill_count": len(waybills.filtered(self._is_timeout_waybill)),
            "missing_evidence_waybill_count": len(waybills.filtered(self._is_missing_evidence_waybill)),
            "top_exception_types": [
                {
                    "key": key,
                    "label": exception_type_labels.get(key, key),
                    "value": value,
                }
                for key, value in top_exception_types.most_common(5)
            ],
        }

    @api.model
    def get_driver_trend_metrics_payload(self, driver_id, metric_codes=None, date_from=None, date_to=None):
        self._get_driver_employee(driver_id)
        metric_codes = metric_codes or ["month_waybill_count", "exception_rate", "signed_rate", "timeout_rate"]
        date_to_value = fields.Date.to_date(date_to) if date_to else fields.Date.context_today(self)
        date_from_value = fields.Date.to_date(date_from) if date_from else (self._month_start(date_to_value) - relativedelta(months=5))
        buckets = self._build_month_buckets(date_from_value, date_to_value)

        series = []
        for metric_code in metric_codes:
            points = []
            for bucket in buckets:
                bucket_start, bucket_end = self._bucket_range(bucket)
                waybills = self._get_driver_waybills(driver_id, date_from=bucket_start, date_to=bucket_end).filtered(
                    lambda item: item.state != "cancelled"
                )
                valid_count = len(waybills)
                if metric_code == "month_waybill_count":
                    value = valid_count
                elif metric_code == "exception_rate":
                    value = self._safe_ratio(
                        len(waybills.filtered(lambda item: item.exception_status in ("open", "processing", "closed"))),
                        valid_count,
                    )
                elif metric_code == "signed_rate":
                    value = self._safe_ratio(
                        len(waybills.filtered(lambda item: item.state in ("signed", "done"))),
                        valid_count,
                    )
                elif metric_code == "timeout_rate":
                    value = self._safe_ratio(
                        len(waybills.filtered(self._is_timeout_waybill)),
                        valid_count,
                    )
                else:
                    value = 0
                points.append({"bucket": bucket, "value": round(value, 4) if isinstance(value, float) else value})
            series.append(
                {
                    "metric_code": metric_code,
                    "metric_label": self._get_metric_label(metric_code),
                    "points": points,
                }
            )

        return {"driver_id": driver_id, "series": series}

    @api.model
    def get_driver_recent_waybills_payload(self, driver_id):
        self._get_driver_employee(driver_id)
        waybills = self._get_driver_waybills(driver_id, limit=8)
        return {
            "items": [
                {
                    "waybill_id": waybill.id,
                    "waybill_no": waybill.name,
                    "store_name": waybill.store_id.name or "",
                    "store_region": self._get_store_region(waybill.store_id),
                    "status": waybill.state,
                    "status_label": self._get_selection_label(waybill, "state"),
                    "delivery_date": self._to_date_string(waybill.delivery_date),
                    "is_timeout": self._is_timeout_waybill(waybill),
                    "is_missing_evidence": self._is_missing_evidence_waybill(waybill),
                }
                for waybill in waybills
            ]
        }

    @api.model
    def get_driver_recent_exceptions_payload(self, driver_id, limit=8):
        self._get_driver_employee(driver_id)
        exceptions = self.env["logistics.trace.exception"].sudo().search(
            [("waybill_id.driver_employee_id", "=", driver_id)],
            order="report_time desc, id desc",
            limit=limit,
        )
        return {
            "items": [
                {
                    "exception_id": exception.id,
                    "exception_no": exception.name,
                    "waybill_id": exception.waybill_id.id,
                    "waybill_no": exception.waybill_id.name or "",
                    "exception_type": exception.exception_type,
                    "exception_type_label": self._get_selection_label(exception, "exception_type"),
                    "status": exception.state,
                    "status_label": self._get_selection_label(exception, "state"),
                    "report_time": self._to_datetime_string(exception.report_time),
                }
                for exception in exceptions
            ]
        }

    @api.model
    def get_driver_waybill_drilldown_payload(self, driver_id, metric_code, bucket=None, page=1, page_size=20):
        self._get_driver_employee(driver_id)
        candidates = self._get_driver_waybills(driver_id)
        candidates = self._filter_waybills_by_metric(candidates, metric_code=metric_code, bucket=bucket)
        page = max(int(page or 1), 1)
        page_size = min(max(int(page_size or 20), 1), 100)
        start = (page - 1) * page_size
        end = start + page_size
        items = candidates.sorted(key=lambda item: (item.latest_trace_time or datetime.min, item.id), reverse=True)
        return {
            "record_ids": items.ids,
            "items": [
                {
                    "waybill_id": waybill.id,
                    "waybill_no": waybill.name,
                    "store_name": waybill.store_id.name or "",
                    "status": waybill.state,
                    "status_label": self._get_selection_label(waybill, "state"),
                    "delivery_date": self._to_date_string(waybill.delivery_date),
                }
                for waybill in items[start:end]
            ],
            "total": len(items),
            "page": page,
            "page_size": page_size,
        }

    @api.model
    def get_driver_exception_drilldown_payload(
        self,
        driver_id,
        metric_code,
        bucket=None,
        page=1,
        page_size=20,
        exception_type=None,
        severity_levels=None,
    ):
        self._get_driver_employee(driver_id)
        page = max(int(page or 1), 1)
        page_size = min(max(int(page_size or 20), 1), 100)
        exceptions = self.env["logistics.trace.exception"].sudo().search(
            [("waybill_id.driver_employee_id", "=", driver_id)],
            order="report_time desc, id desc",
        )
        exceptions = self._filter_exceptions_by_metric(
            exceptions,
            metric_code=metric_code,
            bucket=bucket,
            exception_type=exception_type,
            severity_levels=severity_levels,
        )
        start = (page - 1) * page_size
        end = start + page_size
        return {
            "record_ids": exceptions.ids,
            "items": [
                {
                    "exception_id": exception.id,
                    "exception_no": exception.name,
                    "waybill_id": exception.waybill_id.id,
                    "waybill_no": exception.waybill_id.name or "",
                    "exception_type": exception.exception_type,
                    "exception_type_label": self._get_selection_label(exception, "exception_type"),
                    "status": exception.state,
                    "status_label": self._get_selection_label(exception, "state"),
                    "report_time": self._to_datetime_string(exception.report_time),
                }
                for exception in exceptions[start:end]
            ],
            "total": len(exceptions),
            "page": page,
            "page_size": page_size,
        }

    @api.model
    def _search_driver_employees(self):
        return self.env["hr.employee"].sudo().search([("logistics_role", "=", "driver")])

    @api.model
    def _build_driver_snapshot(self, driver):
        profile = self._get_driver_profile(driver)
        current_batch = self._get_current_batch_for_driver(driver.id)
        latest_batch = self._get_latest_batch(driver.id)
        current_vehicle = current_batch.vehicle_id if current_batch else False
        current_warehouse = current_batch.warehouse_id if current_batch else False
        current_status = self._get_driver_runtime_status(driver, current_batch)
        shift_type = self._get_shift_type_from_batch(current_batch)
        return {
            "driver_id": driver.id,
            "driver_name": profile.driver_name or driver.name,
            "internal_driver_code": profile.internal_driver_code if profile else "",
            "mobile": self._mask_mobile(profile.driver_phone or self._get_employee_mobile(driver)),
            "status": current_status,
            "status_label": self._get_dispatch_status_label(current_status),
            "dispatch_enabled": bool(getattr(driver, "active", True)),
            "allow_night_shift": bool(profile.allow_night_shift) if profile else False,
            "shift_type": shift_type,
            "shift_type_label": self._get_shift_type_label(shift_type),
            "current_vehicle_id": current_vehicle.id if current_vehicle else False,
            "current_vehicle_label": self._get_vehicle_label(current_vehicle) if current_vehicle else "",
            "current_warehouse_id": current_warehouse.id if current_warehouse else False,
            "current_warehouse_label": current_warehouse.name if current_warehouse else "",
            "current_batch_id": current_batch.id if current_batch else False,
            "current_batch_no": current_batch.name if current_batch else "",
            "recent_vehicle_label": self._get_vehicle_label(latest_batch.vehicle_id) if latest_batch and latest_batch.vehicle_id else "",
            "latest_execution_at": self._get_driver_latest_execution_at(driver.id),
            "waybill_count": len(self._get_driver_waybills(driver.id)),
            "month_avg_exception_rate": self._compute_average_month_exception_rate(driver.id),
        }

    @api.model
    def _match_driver_snapshot(self, snapshot, keyword=None, status=None, vehicle_id=0, warehouse_id=0):
        if status and snapshot.get("status") != status:
            return False
        if vehicle_id and snapshot.get("current_vehicle_id") != vehicle_id:
            return False
        if warehouse_id and snapshot.get("current_warehouse_id") != warehouse_id:
            return False
        if keyword:
            haystack = " ".join(
                str(value or "")
                for value in (
                    snapshot.get("driver_name"),
                    snapshot.get("internal_driver_code"),
                    snapshot.get("mobile"),
                    snapshot.get("current_vehicle_label"),
                    snapshot.get("current_warehouse_label"),
                    snapshot.get("current_batch_no"),
                )
            ).lower()
            if keyword.lower() not in haystack:
                return False
        return True

    @api.model
    def _sort_driver_snapshots(self, items, sort_by="latest_execution_at", sort_order="desc"):
        reverse = sort_order != "asc"
        default_datetime = "0000-00-00 00:00:00" if reverse else "9999-12-31 23:59:59"
        if sort_by == "month_avg_exception_rate":
            key_func = lambda item: (item.get("month_avg_exception_rate") or 0, item.get("driver_id") or 0)
        elif sort_by == "waybill_count":
            key_func = lambda item: (item.get("waybill_count") or 0, item.get("driver_id") or 0)
        else:
            key_func = lambda item: (item.get("latest_execution_at") or default_datetime, item.get("driver_id") or 0)
        return sorted(items, key=key_func, reverse=reverse)

    @api.model
    def _get_driver_employee(self, driver_id):
        self._ensure_driver_management_access()
        driver = self.env["hr.employee"].sudo().browse(driver_id)
        if not driver.exists() or driver.logistics_role != "driver":
            raise ValidationError("当前司机不存在或已不可用。")
        return driver

    @api.model
    def _ensure_driver_management_access(self):
        user = self.env.user
        if user.has_group("base.group_system") or user.has_group(DRIVER_MANAGEMENT_VIEW_GROUP):
            return True
        raise AccessError(DRIVER_MANAGEMENT_ACCESS_ERROR)

    @api.model
    def _get_driver_waybills(self, driver_id, date_from=None, date_to=None, limit=None):
        domain = [("driver_employee_id", "=", driver_id)]
        if date_from:
            domain.append(("delivery_date", ">=", date_from))
        if date_to:
            domain.append(("delivery_date", "<=", date_to))
        return self.sudo().search(domain, order="latest_trace_time desc, delivery_date desc, id desc", limit=limit)

    @api.model
    def _get_latest_batch(self, driver_id):
        return self.env["logistics.dispatch.batch"].sudo().search(
            [("driver_employee_id", "=", driver_id), ("vehicle_id", "!=", False)],
            order="actual_depart_time desc, planned_depart_time desc, id desc",
            limit=1,
        )

    @api.model
    def _get_current_batch_for_driver(self, driver_id):
        return self.env["logistics.dispatch.batch"].sudo().search(
            [("driver_employee_id", "=", driver_id), ("state", "in", BATCH_ACTIVE_STATES)],
            order="actual_depart_time desc, planned_depart_time desc, id desc",
            limit=1,
        )

    @api.model
    def _get_driver_latest_execution_at(self, driver_id):
        latest_waybill = self._get_driver_waybills(driver_id, limit=1)
        if not latest_waybill:
            return False
        waybill = latest_waybill[0]
        if waybill.latest_trace_time:
            return self._to_datetime_string(waybill.latest_trace_time)
        if waybill.delivery_date:
            return f"{self._to_date_string(waybill.delivery_date)} 00:00:00"
        return False

    @api.model
    def _get_driver_profile(self, driver):
        return self.env["logistics.driver.profile"].sudo().search([("employee_id", "=", driver.id)], limit=1)

    @api.model
    def _get_driver_runtime_status(self, driver, current_batch):
        if not getattr(driver, "active", True):
            return "disabled"
        if current_batch:
            return "assigned"
        return "idle"

    @api.model
    def _get_shift_type_from_batch(self, batch):
        if not batch:
            return ""
        depart_at = batch.actual_depart_time or batch.planned_depart_time
        if not depart_at:
            return ""
        hour = depart_at.hour
        if hour >= 18 or hour < 6:
            return "night"
        return "day"

    @api.model
    def _compute_average_month_exception_rate(self, driver_id):
        buckets = self._build_month_buckets(self._month_start(fields.Date.context_today(self) - relativedelta(months=5)), fields.Date.context_today(self))
        rates = []
        for bucket in buckets:
            bucket_start, bucket_end = self._bucket_range(bucket)
            waybills = self._get_driver_waybills(driver_id, date_from=bucket_start, date_to=bucket_end).filtered(
                lambda item: item.state != "cancelled"
            )
            if not waybills:
                continue
            rates.append(
                self._safe_ratio(
                    len(waybills.filtered(lambda item: item.exception_status in ("open", "processing", "closed"))),
                    len(waybills),
                )
            )
        if not rates:
            return 0
        return round(sum(rates) / len(rates), 4)

    @api.model
    def _build_month_buckets(self, date_from, date_to):
        start = self._month_start(fields.Date.to_date(date_from))
        end = self._month_start(fields.Date.to_date(date_to))
        buckets = []
        cursor = start
        while cursor <= end:
            buckets.append(cursor.strftime("%Y-%m"))
            cursor += relativedelta(months=1)
        return buckets

    @api.model
    def _bucket_range(self, bucket):
        bucket_date = fields.Date.to_date(f"{bucket}-01")
        month_start = self._month_start(bucket_date)
        month_end = month_start + relativedelta(months=1, days=-1)
        return month_start, month_end

    @api.model
    def _filter_waybills_by_metric(self, waybills, metric_code, bucket=None):
        if bucket:
            bucket_start, bucket_end = self._bucket_range(bucket)
            waybills = waybills.filtered(lambda item: item.delivery_date and bucket_start <= item.delivery_date <= bucket_end)
        if metric_code in ("month_waybill_count",):
            return waybills.filtered(lambda item: item.state != "cancelled")
        if metric_code in ("signed_rate", "current_month_signed_rate"):
            return waybills.filtered(lambda item: item.state in ("signed", "done"))
        if metric_code in ("timeout_rate", "current_month_timeout_rate"):
            return waybills.filtered(self._is_timeout_waybill)
        if metric_code in ("missing_evidence_rate",):
            return waybills.filtered(self._is_missing_evidence_waybill)
        if metric_code in ("exception_rate", "month_avg_exception_rate"):
            return waybills.filtered(lambda item: item.exception_status in ("open", "processing", "closed"))
        return waybills

    @api.model
    def _filter_exceptions_by_metric(self, exceptions, metric_code, bucket=None, exception_type=None, severity_levels=None):
        if bucket:
            bucket_start, bucket_end = self._bucket_range(bucket)
            start_dt = datetime.combine(bucket_start, time.min)
            end_dt = datetime.combine(bucket_end, time.max)
            exceptions = exceptions.filtered(lambda item: item.report_time and start_dt <= item.report_time <= end_dt)
        if exception_type:
            exceptions = exceptions.filtered(lambda item: item.exception_type == exception_type)
        if severity_levels:
            allowed_levels = set(severity_levels)
            exceptions = exceptions.filtered(lambda item: item.severity_level in allowed_levels)
        if metric_code in ("month_avg_exception_rate", "exception_rate", "exception_count"):
            return exceptions
        return exceptions

    @api.model
    def _get_employee_mobile(self, employee):
        return (
            getattr(employee, "mobile_phone", False)
            or getattr(employee, "work_phone", False)
            or getattr(employee, "private_phone", False)
            or ""
        )

    @api.model
    def _mask_mobile(self, mobile):
        digits = (mobile or "").strip()
        if len(digits) < 7:
            return digits
        return f"{digits[:3]}****{digits[-4:]}"

    @api.model
    def _get_employee_status_label(self, employee):
        return dict(employee._fields["logistics_work_status"].selection).get(
            employee.logistics_work_status,
            employee.logistics_work_status or "",
        )

    @api.model
    def _get_dispatch_status_label(self, status):
        return dict(DRIVER_DISPATCH_STATUS_SELECTION).get(status, status or "")

    @api.model
    def _get_shift_type_label(self, shift_type):
        return dict(SHIFT_TYPE_SELECTION).get(shift_type, shift_type or "")

    @api.model
    def _get_vehicle_label(self, vehicle):
        if not vehicle:
            return ""
        parts = [vehicle.license_plate or vehicle.name or ""]
        if vehicle.model_id and vehicle.model_id.name:
            parts.append(vehicle.model_id.name)
        return " / ".join([item for item in parts if item])

    @api.model
    def _serialize_vehicle(self, vehicle):
        if not vehicle:
            return {"vehicle_id": False, "vehicle_label": ""}
        return {
            "vehicle_id": vehicle.id,
            "vehicle_label": self._get_vehicle_label(vehicle),
        }

    @api.model
    def _serialize_warehouse(self, warehouse):
        if not warehouse:
            return {"warehouse_id": False, "warehouse_label": ""}
        return {
            "warehouse_id": warehouse.id,
            "warehouse_label": warehouse.name or "",
        }

    @api.model
    def _serialize_batch(self, batch):
        if not batch:
            return {"batch_id": False, "batch_no": ""}
        return {
            "batch_id": batch.id,
            "batch_no": batch.name or "",
        }

    @api.model
    def _get_store_region(self, store):
        if not store:
            return ""
        return store.state_id.name or store.city or store.parent_id.name or ""

    @api.model
    def _is_timeout_waybill(self, waybill):
        today = fields.Date.context_today(self)
        return bool(
            waybill.delivery_date
            and waybill.delivery_date < today
            and waybill.state not in ("signed", "done", "cancelled")
        )

    @api.model
    def _is_missing_evidence_waybill(self, waybill):
        return waybill.evidence_status in ("missing", "partial")

    @api.model
    def _safe_ratio(self, numerator, denominator):
        if not denominator:
            return 0
        return round(numerator / denominator, 4)

    @api.model
    def _month_start(self, value):
        value = fields.Date.to_date(value)
        return value.replace(day=1)

    @api.model
    def _days_ago(self, days):
        return fields.Date.context_today(self) - relativedelta(days=days)

    @api.model
    def _get_selection_label(self, record, field_name):
        selection = record._fields[field_name].selection
        return dict(selection).get(record[field_name], record[field_name] or "")

    @api.model
    def _get_metric_label(self, metric_code):
        mapping = {
            "month_waybill_count": "月度运单量",
            "exception_rate": "异常率",
            "signed_rate": "签收率",
            "timeout_rate": "超时率",
        }
        return mapping.get(metric_code, metric_code)

    @api.model
    def _to_date_string(self, value):
        if not value:
            return False
        return fields.Date.to_string(value)

    @api.model
    def _to_datetime_string(self, value):
        if not value:
            return False
        return fields.Datetime.to_string(value)
