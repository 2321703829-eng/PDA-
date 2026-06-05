import json
import uuid
from datetime import datetime, time

from odoo import fields, http
from odoo.exceptions import AccessError, ValidationError
from odoo.http import Response, request
from odoo.osv import expression


class LogisticsWebERPDocumentsController(http.Controller):
    DOCUMENT_SOURCES = (
        {
            "key": "purchase_order",
            "label": "采购订单",
            "category": "采购业务",
            "model": "purchase.order",
            "date_fields": ("date_order", "create_date"),
            "name_fields": ("name",),
            "partner_fields": ("partner_id",),
            "amount_fields": ("amount_total",),
            "state_fields": ("state",),
            "warehouse_fields": ("warehouse_id",),
            "keyword_fields": ("name", "partner_id", "origin", "batch_ref", "logistics_note"),
        },
        {
            "key": "purchase_return",
            "label": "采购退货单",
            "category": "采购业务",
            "model": "purchase.order",
            "requires_fields": ("order_type",),
            "date_fields": ("date_order", "create_date"),
            "name_fields": ("name",),
            "partner_fields": ("partner_id",),
            "amount_fields": ("amount_total",),
            "state_fields": ("state",),
            "warehouse_fields": ("warehouse_id",),
            "keyword_fields": ("name", "partner_id", "origin", "return_reason", "batch_ref"),
        },
        {
            "key": "purchase_receipt",
            "label": "采购入库单",
            "category": "仓库作业",
            "model": "stock.picking",
            "date_fields": ("scheduled_date", "date_done", "create_date"),
            "name_fields": ("name", "origin"),
            "partner_fields": ("partner_id",),
            "amount_fields": ("amount_total",),
            "state_fields": ("state",),
            "warehouse_fields": ("warehouse_id", "picking_type_id"),
            "keyword_fields": ("name", "origin", "partner_id", "source_shipment_no", "wms_task_ref"),
        },
        {
            "key": "purchase_return_out",
            "label": "采购退货出库单",
            "category": "仓库作业",
            "model": "stock.picking",
            "requires_fields": ("erp_source_type",),
            "date_fields": ("scheduled_date", "date_done", "create_date"),
            "name_fields": ("name", "origin"),
            "partner_fields": ("partner_id",),
            "amount_fields": ("amount_total",),
            "state_fields": ("state",),
            "warehouse_fields": ("warehouse_id", "picking_type_id"),
            "keyword_fields": ("name", "origin", "partner_id", "source_shipment_no", "wms_task_ref"),
        },
        {
            "key": "sale_order",
            "label": "销售订单",
            "category": "销售业务",
            "model": "sale.order",
            "date_fields": ("date_order", "create_date"),
            "name_fields": ("name",),
            "partner_fields": ("partner_id",),
            "amount_fields": ("amount_total",),
            "state_fields": ("state",),
            "warehouse_fields": ("warehouse_id",),
            "keyword_fields": ("name", "partner_id", "client_order_ref", "origin", "batch_ref", "delivery_note"),
        },
        {
            "key": "sale_outbound",
            "label": "销售出库单",
            "category": "仓库作业",
            "model": "stock.picking",
            "date_fields": ("scheduled_date", "date_done", "create_date"),
            "name_fields": ("name", "origin"),
            "partner_fields": ("partner_id",),
            "amount_fields": ("amount_total",),
            "state_fields": ("state",),
            "warehouse_fields": ("warehouse_id", "picking_type_id"),
            "keyword_fields": ("name", "origin", "partner_id", "source_shipment_no", "wms_task_ref"),
        },
        {
            "key": "sale_return",
            "label": "销售退货单",
            "category": "销售业务",
            "model": "erp.sale.return",
            "date_fields": ("return_date", "create_date"),
            "name_fields": ("name",),
            "partner_fields": ("partner_id",),
            "amount_fields": ("amount_total",),
            "state_fields": ("state",),
            "warehouse_fields": ("warehouse_id",),
            "keyword_fields": ("name", "partner_id", "sale_order_id", "return_reason", "source_shipment_no", "route_name"),
        },
        {
            "key": "sale_return_receipt",
            "label": "销售退货入库单",
            "category": "仓库作业",
            "model": "stock.picking",
            "date_fields": ("scheduled_date", "date_done", "create_date"),
            "name_fields": ("name", "origin"),
            "partner_fields": ("partner_id",),
            "amount_fields": ("amount_total",),
            "state_fields": ("state",),
            "warehouse_fields": ("warehouse_id", "picking_type_id"),
            "keyword_fields": ("name", "origin", "partner_id", "source_shipment_no", "wms_task_ref"),
        },
        {
            "key": "replenishment",
            "label": "智能补货",
            "category": "库存计划",
            "model": "stock.warehouse.orderpoint",
            "date_fields": ("write_date", "create_date"),
            "name_fields": ("display_name",),
            "partner_fields": ("product_id",),
            "amount_fields": ("suggested_purchase_qty", "product_min_qty"),
            "state_fields": ("replenishment_strategy",),
            "warehouse_fields": ("warehouse_id", "location_id"),
            "keyword_fields": ("name", "display_name", "product_id", "warehouse_id", "location_id"),
        },
        {
            "key": "stock_move",
            "label": "库存移动",
            "category": "仓库作业",
            "model": "stock.move",
            "date_fields": ("date", "write_date", "create_date"),
            "name_fields": ("reference", "name"),
            "partner_fields": ("product_id",),
            "amount_fields": ("sale_price_subtotal", "purchase_price_subtotal", "product_uom_qty"),
            "state_fields": ("state",),
            "warehouse_fields": ("warehouse_id", "picking_type_id", "location_dest_id"),
            "keyword_fields": ("reference", "name", "origin", "product_id", "picking_id"),
        },
    )

    @http.route("/api/admin/logistics/erp-documents/search", type="http", auth="user", methods=["GET"])
    def search_erp_documents(self, **kwargs):
        payload = self._merged_payload()
        return self._handle_payload(
            "req_erp_documents_search",
            lambda: self._get_documents_payload(payload),
        )

    def _get_documents_payload(self, payload):
        self._check_access()
        filters = self._normalize_filters(payload)
        sources = self._available_sources()
        if not sources:
            return self._empty_payload(filters)

        source_counts = self._build_source_counts(sources, filters)
        selected_sources = [
            source for source in sources
            if filters["document_type"] == "all" or source["key"] == filters["document_type"]
        ]
        if filters["document_type"] != "all" and not selected_sources:
            raise ValidationError("当前单据类型不可用，请刷新页面后重试。")

        total = 0
        records = []
        page = filters["page"]
        page_size = filters["page_size"]
        requested_limit = page * page_size if filters["document_type"] == "all" else page_size
        requested_offset = 0 if filters["document_type"] == "all" else (page - 1) * page_size

        for source in selected_sources:
            model = request.env[source["model"]].sudo()
            domain = self._build_domain(model, source, filters)
            count = model.search_count(domain)
            total += count
            found = model.search(
                domain,
                order=self._order_for_source(model, source),
                offset=requested_offset,
                limit=requested_limit,
            )
            records.extend(self._serialize_records(found, source))

        records.sort(key=self._sort_record_key, reverse=True)
        if filters["document_type"] == "all":
            start = (page - 1) * page_size
            records = records[start:start + page_size]

        total_pages = max(1, (total + page_size - 1) // page_size)
        return {
            "filters": filters,
            "types": self._build_type_options(source_counts, filters),
            "summary": self._build_summary(total, records, source_counts, filters),
            "records": records,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
                "has_previous": page > 1,
                "has_next": page < total_pages,
            },
        }

    def _check_access(self):
        user = request.env.user
        if user.has_group("base.group_system") or user.has_group("logistics_web.group_logistics_analysis_viewer"):
            return
        raise AccessError("当前账号没有查看 ERP 单据查询中心的权限。")

    def _available_sources(self):
        available = []
        registry_models = request.env.registry.models
        for source in self.DOCUMENT_SOURCES:
            model_name = source["model"]
            if model_name not in registry_models:
                continue
            model = request.env[model_name]
            required_fields = source.get("requires_fields") or ()
            if any(field_name not in model._fields for field_name in required_fields):
                continue
            available.append(source)
        return available

    def _normalize_filters(self, payload):
        date_from = (payload.get("date_from") or "").strip()
        date_to = (payload.get("date_to") or "").strip()
        if date_from and date_to and date_from > date_to:
            raise ValidationError("开始日期不能晚于结束日期。")
        return {
            "document_type": (payload.get("document_type") or "all").strip() or "all",
            "keyword": (payload.get("keyword") or "").strip(),
            "date_from": date_from,
            "date_to": date_to,
            "page": self._normalize_int(payload.get("page"), 1, minimum=1, maximum=500),
            "page_size": self._normalize_int(payload.get("page_size"), 20, minimum=10, maximum=100),
        }

    def _normalize_int(self, value, default, *, minimum, maximum):
        try:
            normalized = int(value)
        except (TypeError, ValueError):
            normalized = default
        return max(minimum, min(maximum, normalized))

    def _build_source_counts(self, sources, filters):
        counts = []
        for source in sources:
            model = request.env[source["model"]].sudo()
            domain = self._build_domain(model, source, {**filters, "document_type": "all"})
            counts.append({
                "key": source["key"],
                "label": source["label"],
                "category": source["category"],
                "count": model.search_count(domain),
            })
        return counts

    def _build_type_options(self, source_counts, filters):
        total = sum(item["count"] for item in source_counts)
        options = [{
            "key": "all",
            "label": "全部单据",
            "category": "全部",
            "count": total,
            "active": filters["document_type"] == "all",
        }]
        options.extend({
            **item,
            "active": filters["document_type"] == item["key"],
        } for item in source_counts)
        return options

    def _build_summary(self, total, records, source_counts, filters):
        active_type_count = len([item for item in source_counts if item["count"]])
        latest_record = records[0] if records else None
        return {
            "total": total,
            "current_page_count": len(records),
            "active_type_count": active_type_count,
            "latest_updated_at": latest_record.get("updated_at_display") if latest_record else "",
            "date_range": self._date_range_label(filters),
        }

    def _date_range_label(self, filters):
        if filters["date_from"] and filters["date_to"]:
            return f"{filters['date_from']} 至 {filters['date_to']}"
        if filters["date_from"]:
            return f"{filters['date_from']} 起"
        if filters["date_to"]:
            return f"截至 {filters['date_to']}"
        return "全部时间"

    def _build_domain(self, model, source, filters):
        domains = [self._source_base_domain(model, source)]
        date_domain = self._date_domain(model, source, filters)
        if date_domain:
            domains.append(date_domain)
        keyword_domain = self._keyword_domain(model, source, filters.get("keyword"))
        if keyword_domain:
            domains.append(keyword_domain)
        return expression.AND([domain for domain in domains if domain])

    def _source_base_domain(self, model, source):
        key = source["key"]
        if source["model"] == "purchase.order" and "order_type" in model._fields:
            if key == "purchase_return":
                return [("order_type", "=", "return")]
            if key == "purchase_order":
                return expression.OR([[("order_type", "=", False)], [("order_type", "=", "standard")]])

        if source["model"] == "stock.picking":
            domains = []
            if "picking_type_code" in model._fields:
                if key in ("purchase_receipt", "sale_return_receipt"):
                    domains.append([("picking_type_code", "=", "incoming")])
                if key in ("sale_outbound", "purchase_return_out"):
                    domains.append([("picking_type_code", "=", "outgoing")])

            if key == "purchase_return_out":
                domains.append([("erp_source_type", "=", "purchase_return")])
            elif key == "sale_return_receipt":
                sale_return_domains = []
                if "sale_return_id" in model._fields:
                    sale_return_domains.append([("sale_return_id", "!=", False)])
                if "erp_source_type" in model._fields:
                    sale_return_domains.append([("erp_source_type", "=", "sale_return")])
                domains.append(expression.OR(sale_return_domains) if sale_return_domains else [("id", "=", 0)])
            elif key == "purchase_receipt" and "erp_source_type" in model._fields:
                domains.append([("erp_source_type", "not in", ["sale_return", "purchase_return", "internal"])])
            elif key == "sale_outbound" and "erp_source_type" in model._fields:
                domains.append(expression.OR([[("erp_source_type", "=", False)], [("erp_source_type", "=", "sale")]]))
            return expression.AND([domain for domain in domains if domain])
        return []

    def _date_domain(self, model, source, filters):
        field_name = self._first_existing_field(model, source.get("date_fields") or ("write_date", "create_date"))
        if not field_name:
            return []
        date_from = filters.get("date_from")
        date_to = filters.get("date_to")
        if not date_from and not date_to:
            return []

        domain = []
        field_type = model._fields[field_name].type
        if date_from:
            domain.append((field_name, ">=", self._domain_date_value(date_from, field_type, lower=True)))
        if date_to:
            domain.append((field_name, "<=", self._domain_date_value(date_to, field_type, lower=False)))
        return domain

    def _domain_date_value(self, value, field_type, *, lower):
        if field_type != "datetime":
            return value
        suffix = "00:00:00" if lower else "23:59:59"
        return f"{value} {suffix}"

    def _keyword_domain(self, model, source, keyword):
        if not keyword:
            return []
        conditions = []
        for field_name in source.get("keyword_fields") or ():
            if field_name in model._fields:
                conditions.append((field_name, "ilike", keyword))
        if keyword.isdigit():
            conditions.append(("id", "=", int(keyword)))
        if not conditions:
            return []
        return expression.OR([[condition] for condition in conditions])

    def _order_for_source(self, model, source):
        order_fields = []
        for field_name in ("write_date", "create_date", *source.get("date_fields", ())):
            if field_name in model._fields and field_name not in order_fields:
                order_fields.append(field_name)
        if not order_fields:
            return "id desc"
        order_fields.append("id")
        return ", ".join(f"{field_name} desc" for field_name in order_fields)

    def _serialize_records(self, records, source):
        return [self._serialize_record(record, source) for record in records]

    def _serialize_record(self, record, source):
        model = record._name
        name = self._record_text(record, source.get("name_fields") or ("display_name", "name"))
        business_value = self._record_value(record, source.get("date_fields") or ("create_date",))
        updated_value = self._record_value(record, ("write_date", "create_date"))
        state_field = self._first_existing_field(record, source.get("state_fields") or ())
        amount_field = self._first_existing_field(record, source.get("amount_fields") or ())
        amount_value = self._record_value(record, (amount_field,)) if amount_field else None
        currency = self._record_currency(record)
        return {
            "id": f"{model}:{record.id}",
            "model": model,
            "res_id": record.id,
            "document_type": source["key"],
            "document_type_label": source["label"],
            "category": source["category"],
            "name": name or record.display_name,
            "partner": self._record_name(record, source.get("partner_fields") or ()),
            "business_date": self._format_date_value(business_value),
            "business_date_sort": self._sort_value(business_value),
            "updated_at": self._format_date_value(updated_value),
            "updated_at_display": self._format_date_value(updated_value, with_time=True),
            "updated_at_sort": self._sort_value(updated_value),
            "state": self._record_value(record, (state_field,)) if state_field else "",
            "state_label": self._selection_label(record, state_field) if state_field else "",
            "amount": self._format_amount(amount_value, currency),
            "amount_raw": float(amount_value or 0.0) if isinstance(amount_value, (int, float)) else 0.0,
            "warehouse": self._record_name(record, source.get("warehouse_fields") or ()),
            "owner": self._record_name(record, ("user_id", "approval_user_id", "create_uid")),
            "source": self._record_text(record, ("origin", "source_shipment_no", "batch_ref", "route_name", "reference")),
            "hint": self._build_record_hint(record, source),
            "action": {
                "type": "ir.actions.act_window",
                "name": source["label"],
                "res_model": model,
                "res_id": record.id,
                "views": [[False, "form"]],
                "target": "current",
            },
        }

    def _build_record_hint(self, record, source):
        values = [
            self._record_name(record, ("company_id",)),
            self._record_text(record, ("return_reason", "logistics_note", "delivery_note", "note")),
        ]
        return " / ".join(value for value in values if value)

    def _record_text(self, record, field_names):
        for field_name in field_names:
            if not field_name or field_name not in record._fields:
                continue
            value = self._record_value(record, (field_name,))
            if value:
                if hasattr(value, "display_name"):
                    return value.display_name
                return str(value)
        return ""

    def _record_name(self, record, field_names):
        for field_name in field_names:
            if field_name not in record._fields:
                continue
            value = self._record_value(record, (field_name,))
            if value:
                if hasattr(value, "display_name"):
                    return value.display_name
                return str(value)
        return ""

    def _record_currency(self, record):
        for field_name in ("currency_id", "company_currency_id"):
            if field_name in record._fields:
                currency = self._record_value(record, (field_name,))
                if currency:
                    return currency
        company = self._record_value(record, ("company_id",))
        return company.currency_id if company and getattr(company, "currency_id", False) else request.env.company.currency_id

    def _record_value(self, record, field_names):
        for field_name in field_names:
            if field_name and field_name in record._fields:
                try:
                    return record[field_name]
                except Exception:
                    return False
        return False

    def _selection_label(self, record, field_name):
        value = self._record_value(record, (field_name,))
        if not value:
            return ""
        field = record._fields[field_name]
        selection = field.selection
        if callable(selection) or isinstance(selection, str):
            return str(value)
        labels = dict(selection or [])
        return labels.get(value, str(value))

    def _format_amount(self, value, currency):
        if value in (False, None, ""):
            return ""
        try:
            number = float(value)
        except (TypeError, ValueError):
            return str(value)
        symbol = currency.symbol if currency else ""
        if abs(number - round(number)) < 0.00001:
            rendered = f"{number:,.0f}"
        else:
            rendered = f"{number:,.2f}"
        return f"{symbol}{rendered}" if symbol else rendered

    def _format_date_value(self, value, *, with_time=False):
        if not value:
            return ""
        if isinstance(value, str):
            return value[:16] if with_time else value[:10]
        if isinstance(value, datetime):
            value = fields.Datetime.context_timestamp(request.env.user, value)
            return value.strftime("%Y-%m-%d %H:%M") if with_time else value.strftime("%Y-%m-%d")
        if hasattr(value, "strftime"):
            return value.strftime("%Y-%m-%d")
        return str(value)

    def _sort_record_key(self, item):
        return item.get("updated_at_sort") or item.get("business_date_sort") or ""

    def _sort_value(self, value):
        if not value:
            return ""
        if isinstance(value, str):
            return value
        if isinstance(value, datetime):
            return value.isoformat()
        if hasattr(value, "isoformat"):
            return datetime.combine(value, time.min).isoformat()
        return str(value)

    def _first_existing_field(self, model_or_record, field_names):
        fields_map = model_or_record._fields
        for field_name in field_names:
            if field_name in fields_map:
                return field_name
        return ""

    def _empty_payload(self, filters):
        return {
            "filters": filters,
            "types": [{"key": "all", "label": "全部单据", "category": "全部", "count": 0, "active": True}],
            "summary": {
                "total": 0,
                "current_page_count": 0,
                "active_type_count": 0,
                "latest_updated_at": "",
                "date_range": self._date_range_label(filters),
            },
            "records": [],
            "pagination": {
                "page": filters["page"],
                "page_size": filters["page_size"],
                "total": 0,
                "total_pages": 1,
                "has_previous": False,
                "has_next": False,
            },
        }

    def _handle_payload(self, request_prefix, callback):
        try:
            data = callback()
        except AccessError as exc:
            return self._json_response(
                {
                    "code": 4003,
                    "message": "forbidden",
                    "data": {"errors": [{"error_code": "ERP_DOCUMENT_ACCESS_FORBIDDEN", "error_message": str(exc)}]},
                    "request_id": self._build_request_id(request_prefix),
                },
                status=403,
            )
        except (ValidationError, ValueError, TypeError) as exc:
            return self._json_response(
                {
                    "code": 4001,
                    "message": "bad_request",
                    "data": {"errors": [{"error_code": "ERP_DOCUMENT_BAD_REQUEST", "error_message": str(exc)}]},
                    "request_id": self._build_request_id(request_prefix),
                },
                status=400,
            )
        return self._json_response(
            {
                "code": 0,
                "message": "success",
                "data": data,
                "request_id": self._build_request_id(request_prefix),
            }
        )

    def _merged_payload(self):
        payload = dict(request.params)
        if request.httprequest.mimetype == "application/json":
            json_payload = request.httprequest.get_json(silent=True) or {}
            if isinstance(json_payload, dict):
                payload.update({key: value for key, value in json_payload.items() if value is not None})
        return payload

    def _json_response(self, payload, *, status=200):
        return Response(
            json.dumps(payload, ensure_ascii=False),
            status=status,
            headers=[("Content-Type", "application/json; charset=utf-8")],
        )

    def _build_request_id(self, prefix):
        return f"{prefix}_{uuid.uuid4().hex[:12]}"
