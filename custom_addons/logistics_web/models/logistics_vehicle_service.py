from collections import Counter

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.addons.logistics_base.models.selection_options import VEHICLE_DISPATCH_STATUS_SELECTION


VEHICLE_MANAGEMENT_VIEW_GROUP = "logistics_web.group_logistics_vehicle_management_viewer"
VEHICLE_MANAGEMENT_ACCESS_ERROR = "当前账号暂无查看车辆管理的权限。"
BATCH_ACTIVE_STATES = ("draft", "ready", "loading", "in_transit")


class LogisticsDispatchWaybill(models.Model):
    _inherit = "logistics.dispatch.waybill"

    @api.model
    def getVehicleList(self, params=None):
        self._ensure_vehicle_management_access()
        params = params or {}
        page = max(int(params.get("page") or 1), 1)
        page_size = min(max(int(params.get("page_size") or 20), 1), 100)
        sort_by = params.get("sort_by") or "latest_execution_at"
        sort_order = "asc" if (params.get("sort_order") or "").lower() == "asc" else "desc"
        keyword = (params.get("keyword") or "").strip()
        status = (params.get("status") or "").strip()
        warehouse_id = int(params.get("warehouse_id") or 0)
        driver_id = int(params.get("driver_id") or 0)

        snapshots = []
        for vehicle in self._search_vehicles():
            snapshot = self._build_vehicle_snapshot(vehicle)
            if self._match_vehicle_snapshot(
                snapshot,
                keyword=keyword,
                status=status,
                warehouse_id=warehouse_id,
                driver_id=driver_id,
            ):
                snapshots.append(snapshot)

        snapshots = self._sort_vehicle_snapshots(snapshots, sort_by=sort_by, sort_order=sort_order)
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
    def getVehicleFilterOptions(self):
        self._ensure_vehicle_management_access()
        snapshots = [self._build_vehicle_snapshot(vehicle) for vehicle in self._search_vehicles()]
        warehouse_ids = [item["current_warehouse_id"] for item in snapshots if item.get("current_warehouse_id")]
        driver_ids = [item["current_driver_id"] for item in snapshots if item.get("current_driver_id")]
        warehouses = self.env["stock.warehouse"].sudo().browse(list(set(warehouse_ids)))
        drivers = self.env["hr.employee"].sudo().browse(list(set(driver_ids)))
        return {
            "status_options": [{"value": value, "label": label} for value, label in VEHICLE_DISPATCH_STATUS_SELECTION],
            "warehouse_options": [
                {"value": str(warehouse.id), "label": warehouse.name or ""}
                for warehouse in warehouses.sorted(lambda item: (item.name or "", item.id))
            ],
            "driver_options": [
                {"value": str(driver.id), "label": driver.name or ""}
                for driver in drivers.sorted(lambda item: (item.name or "", item.id))
            ],
        }

    @api.model
    def get_vehicle_profile_overview_payload(self, vehicle_id):
        vehicle = self._get_vehicle_record(vehicle_id)
        profile = self._get_vehicle_profile(vehicle)
        all_waybills = self._get_vehicle_waybills(vehicle.id)
        recent_waybills = self._get_vehicle_waybills(vehicle.id, date_from=self._days_ago(30))
        current_batch = self._get_current_batch_for_vehicle(vehicle.id)
        latest_batch = self._get_latest_vehicle_batch(vehicle.id)
        current_warehouse = current_batch.warehouse_id if current_batch else False
        current_driver = current_batch.driver_employee_id if current_batch else False
        current_status = self._get_vehicle_runtime_status(vehicle, current_batch)
        recent_driver = current_driver or (latest_batch.driver_employee_id if latest_batch else False)

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
            "vehicle_id": vehicle.id,
            "vehicle_label": self._get_vehicle_label(vehicle),
            "internal_vehicle_code": profile.internal_vehicle_code if profile else "",
            "status": current_status,
            "status_label": self._get_vehicle_dispatch_status_label(current_status),
            "dispatch_enabled": bool(getattr(vehicle, "active", True)),
            "current_warehouse": self._serialize_warehouse(current_warehouse),
            "current_driver": self._serialize_driver(current_driver),
            "current_batch": self._serialize_batch(current_batch),
            "recent_driver": self._serialize_driver(recent_driver),
            "latest_execution_at": self._get_vehicle_latest_execution_at(vehicle.id),
            "operation_type": profile.operation_type if profile else "",
            "standby_site_name": profile.standby_site_name if profile else "",
            "vehicle_spec": profile.vehicle_spec if profile else "",
            "purchase_mode": profile.purchase_mode if profile else "",
            "energy_type": vehicle.energy_type or "",
            "approved_load_ton": profile.approved_load_ton if profile else 0,
            "approved_volume_m3": profile.approved_volume_m3 if profile else 0,
            "license_plate": vehicle.license_plate or vehicle.name or "",
            "organization_name": vehicle.organization_name or "",
            "remark": (profile.vehicle_remark if profile else "") or "",
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
    def get_vehicle_kpi_cards_payload(self, vehicle_id):
        self._get_vehicle_record(vehicle_id)
        current_month_start = self._month_start(fields.Date.context_today(self))
        month_waybills = self._get_vehicle_waybills(vehicle_id, date_from=current_month_start)
        valid_month_waybills = month_waybills.filtered(lambda item: item.state != "cancelled")
        valid_all_waybills = self._get_vehicle_waybills(vehicle_id).filtered(lambda item: item.state != "cancelled")

        return {
            "month_waybill_count": len(valid_month_waybills),
            "month_avg_exception_rate": self._compute_average_month_vehicle_exception_rate(vehicle_id),
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
                [("waybill_id.vehicle_id", "=", vehicle_id)]
            ),
        }

    @api.model
    def get_vehicle_risk_summary_payload(self, vehicle_id):
        self._get_vehicle_record(vehicle_id)
        waybills = self._get_vehicle_waybills(vehicle_id).filtered(lambda item: item.state != "cancelled")
        exceptions = self.env["logistics.trace.exception"].sudo().search(
            [("waybill_id.vehicle_id", "=", vehicle_id)],
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
    def get_vehicle_trend_metrics_payload(self, vehicle_id, metric_codes=None, date_from=None, date_to=None):
        self._get_vehicle_record(vehicle_id)
        metric_codes = metric_codes or ["month_waybill_count", "exception_rate", "signed_rate", "timeout_rate"]
        date_to_value = fields.Date.to_date(date_to) if date_to else fields.Date.context_today(self)
        date_from_value = fields.Date.to_date(date_from) if date_from else (self._month_start(date_to_value) - relativedelta(months=5))
        buckets = self._build_month_buckets(date_from_value, date_to_value)

        series = []
        for metric_code in metric_codes:
            points = []
            for bucket in buckets:
                bucket_start, bucket_end = self._bucket_range(bucket)
                waybills = self._get_vehicle_waybills(vehicle_id, date_from=bucket_start, date_to=bucket_end).filtered(
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

        return {"vehicle_id": vehicle_id, "series": series}

    @api.model
    def get_vehicle_recent_waybills_payload(self, vehicle_id):
        self._get_vehicle_record(vehicle_id)
        waybills = self._get_vehicle_waybills(vehicle_id, limit=8)
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
    def get_vehicle_recent_exceptions_payload(self, vehicle_id, limit=8):
        self._get_vehicle_record(vehicle_id)
        exceptions = self.env["logistics.trace.exception"].sudo().search(
            [("waybill_id.vehicle_id", "=", vehicle_id)],
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
    def _search_vehicles(self):
        return self.env["fleet.vehicle"].sudo().search([])

    @api.model
    def _build_vehicle_snapshot(self, vehicle):
        profile = self._get_vehicle_profile(vehicle)
        current_batch = self._get_current_batch_for_vehicle(vehicle.id)
        current_driver = current_batch.driver_employee_id if current_batch else False
        current_warehouse = current_batch.warehouse_id if current_batch else False
        current_status = self._get_vehicle_runtime_status(vehicle, current_batch)
        return {
            "vehicle_id": vehicle.id,
            "vehicle_label": self._get_vehicle_label(vehicle),
            "internal_vehicle_code": profile.internal_vehicle_code if profile else "",
            "status": current_status,
            "status_label": self._get_vehicle_dispatch_status_label(current_status),
            "dispatch_enabled": bool(getattr(vehicle, "active", True)),
            "current_driver_id": current_driver.id if current_driver else False,
            "current_driver_label": current_driver.name if current_driver else "",
            "current_warehouse_id": current_warehouse.id if current_warehouse else False,
            "current_warehouse_label": current_warehouse.name if current_warehouse else "",
            "current_batch_id": current_batch.id if current_batch else False,
            "current_batch_no": current_batch.name if current_batch else "",
            "standby_site_name": profile.standby_site_name if profile else "",
            "approved_load_ton": profile.approved_load_ton if profile else 0,
            "approved_volume_m3": profile.approved_volume_m3 if profile else 0,
            "latest_execution_at": self._get_vehicle_latest_execution_at(vehicle.id),
            "waybill_count": len(self._get_vehicle_waybills(vehicle.id)),
            "month_avg_exception_rate": self._compute_average_month_vehicle_exception_rate(vehicle.id),
        }

    @api.model
    def _match_vehicle_snapshot(self, snapshot, keyword=None, status=None, warehouse_id=0, driver_id=0):
        if status and snapshot.get("status") != status:
            return False
        if warehouse_id and snapshot.get("current_warehouse_id") != warehouse_id:
            return False
        if driver_id and snapshot.get("current_driver_id") != driver_id:
            return False
        if keyword:
            haystack = " ".join(
                str(value or "")
                for value in (
                    snapshot.get("vehicle_label"),
                    snapshot.get("internal_vehicle_code"),
                    snapshot.get("current_driver_label"),
                    snapshot.get("current_warehouse_label"),
                    snapshot.get("current_batch_no"),
                    snapshot.get("standby_site_name"),
                )
            ).lower()
            if keyword.lower() not in haystack:
                return False
        return True

    @api.model
    def _sort_vehicle_snapshots(self, items, sort_by="latest_execution_at", sort_order="desc"):
        reverse = sort_order != "asc"
        default_datetime = "0000-00-00 00:00:00" if reverse else "9999-12-31 23:59:59"
        if sort_by == "month_avg_exception_rate":
            key_func = lambda item: (item.get("month_avg_exception_rate") or 0, item.get("vehicle_id") or 0)
        elif sort_by == "waybill_count":
            key_func = lambda item: (item.get("waybill_count") or 0, item.get("vehicle_id") or 0)
        else:
            key_func = lambda item: (item.get("latest_execution_at") or default_datetime, item.get("vehicle_id") or 0)
        return sorted(items, key=key_func, reverse=reverse)

    @api.model
    def _get_vehicle_record(self, vehicle_id):
        self._ensure_vehicle_management_access()
        vehicle = self.env["fleet.vehicle"].sudo().browse(vehicle_id)
        if not vehicle.exists():
            raise ValidationError("当前车辆不存在或已不可用。")
        return vehicle

    @api.model
    def _ensure_vehicle_management_access(self):
        user = self.env.user
        if user.has_group("base.group_system") or user.has_group(VEHICLE_MANAGEMENT_VIEW_GROUP):
            return True
        raise AccessError(VEHICLE_MANAGEMENT_ACCESS_ERROR)

    @api.model
    def _get_vehicle_profile(self, vehicle):
        return self.env["logistics.vehicle.profile"].sudo().search([("vehicle_id", "=", vehicle.id)], limit=1)

    @api.model
    def _get_current_batch_for_vehicle(self, vehicle_id):
        return self.env["logistics.dispatch.batch"].sudo().search(
            [("vehicle_id", "=", vehicle_id), ("state", "in", BATCH_ACTIVE_STATES)],
            order="actual_depart_time desc, planned_depart_time desc, id desc",
            limit=1,
        )

    @api.model
    def _get_vehicle_runtime_status(self, vehicle, current_batch):
        if not getattr(vehicle, "active", True):
            return "disabled"
        if current_batch:
            return "assigned"
        return "idle"

    @api.model
    def _get_vehicle_waybills(self, vehicle_id, date_from=None, date_to=None, limit=None):
        domain = [("vehicle_id", "=", vehicle_id)]
        if date_from:
            domain.append(("delivery_date", ">=", date_from))
        if date_to:
            domain.append(("delivery_date", "<=", date_to))
        return self.sudo().search(domain, order="latest_trace_time desc, delivery_date desc, id desc", limit=limit)

    @api.model
    def _get_latest_vehicle_batch(self, vehicle_id):
        return self.env["logistics.dispatch.batch"].sudo().search(
            [("vehicle_id", "=", vehicle_id), ("driver_employee_id", "!=", False)],
            order="actual_depart_time desc, planned_depart_time desc, id desc",
            limit=1,
        )

    @api.model
    def _get_vehicle_latest_execution_at(self, vehicle_id):
        latest_waybill = self._get_vehicle_waybills(vehicle_id, limit=1)
        if not latest_waybill:
            return False
        waybill = latest_waybill[0]
        if waybill.latest_trace_time:
            return self._to_datetime_string(waybill.latest_trace_time)
        if waybill.delivery_date:
            return f"{self._to_date_string(waybill.delivery_date)} 00:00:00"
        return False

    @api.model
    def _compute_average_month_vehicle_exception_rate(self, vehicle_id):
        buckets = self._build_month_buckets(
            self._month_start(fields.Date.context_today(self) - relativedelta(months=5)),
            fields.Date.context_today(self),
        )
        rates = []
        for bucket in buckets:
            bucket_start, bucket_end = self._bucket_range(bucket)
            waybills = self._get_vehicle_waybills(vehicle_id, date_from=bucket_start, date_to=bucket_end).filtered(
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
    def _serialize_driver(self, driver):
        if not driver:
            return {"driver_id": False, "driver_label": ""}
        return {
            "driver_id": driver.id,
            "driver_label": driver.name or "",
        }

    @api.model
    def _get_vehicle_dispatch_status_label(self, status):
        return dict(VEHICLE_DISPATCH_STATUS_SELECTION).get(status, status or "")
