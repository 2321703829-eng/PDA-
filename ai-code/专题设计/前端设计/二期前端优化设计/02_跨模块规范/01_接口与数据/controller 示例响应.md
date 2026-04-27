# 浜屾湡 controller 绀轰緥鍝嶅簲

閫傜敤鑼冨洿锛?- 褰撳墠浜屾湡閲囩敤 `JSON controller` 鎵挎帴鐨勬柊澧炴帴鍙?- 閲嶇偣鍖呮嫭锛氶椤点€佺粺璁″浘琛ㄣ€佹爣鍑嗗鍏ユā鏉夸富璺緞

> 鐘舵€佽鏄庯細
> - 鏈枃妗ｅ彧琛ヤ簩鏈熸柊澧?controller 绀轰緥銆?> - 涓€鏈熷伐浣滃彴銆佹椂闂寸嚎銆佽瘉鎹煡鐪嬨€佽€佹澘椤电ず渚嬶紝缁х画鍙傝€冧竴鏈?`controller 绀轰緥鍝嶅簲.md`銆?> - 褰撳墠浜屾湡 controller 鏂规硶鐩綍涓庡瓧娈靛彛寰勶紝浼樺厛浠ヤ簩鏈?`鏈€缁堟帴鍙ｆ€昏〃.md` 涓哄噯銆?
---

## 1. 閫氱敤杩斿洖缁撴瀯

```json
{
  "code": "OK",
  "message": "success",
  "data": {},
  "request_id": "req_demo_001"
}
```

---

## 2. 棣栭〉鎬昏鎺ュ彛绀轰緥

鎺ㄨ崘鎺ュ彛锛?- `GET /api/admin/logistics/home/overview`

绀轰緥鍝嶅簲锛?
```json
{
  "code": "OK",
  "message": "success",
  "data": {
    "date": "2026-04-16",
    "role_code": "ops_manager",
    "todo_exception_count": 12,
    "todo_evidence_count": 8,
    "todo_waybill_count": 46,
    "timeout_risk_waybill_count": 5,
    "signed_rate": 0.93,
    "evidence_completion_rate": 0.88,
    "exception_waybill_rate": 0.07,
    "store_signoff_rate": 0.91
  },
  "request_id": "req_home_overview_001"
}
```

---

## 3. 棣栭〉鏈€杩戝姩鎬佹帴鍙ｇず渚?
鎺ㄨ崘鎺ュ彛锛?- `GET /api/admin/logistics/home/recent-activities`

绀轰緥鍝嶅簲锛?
```json
{
  "code": "OK",
  "message": "success",
  "data": {
    "items": [
      {
        "activity_type": "new_exception",
        "activity_type_label": "鏈€鏂板紓甯?,
        "object_type": "waybill",
        "object_id": 10001,
        "title": "杩愬崟 WB260416-0001 鏂板寮傚父",
        "summary": "闂ㄥ簵鎷掓敹锛屽緟琛ヨ瘉鎹?,
        "occurred_at": "2026-04-16 10:20:00",
        "target_path": "/web#id=10001&model=logistics.dispatch.waybill"
      }
    ]
  },
  "request_id": "req_home_recent_001"
}
```

## 4. 棣栭〉瑙掕壊鍖栧紩瀵兼帴鍙ｇず渚?
鎺ㄨ崘鎺ュ彛锛?- `GET /api/admin/logistics/home/guide`

绀轰緥鍝嶅簲锛?
```json
{
  "code": "OK",
  "message": "success",
  "data": {
    "role_code": "dispatcher",
    "role_label": "璋冨害",
    "guide_items": [
      {
        "entry_code": "dispatch_batch",
        "entry_label": "杩涘叆鐗╂祦璋冨害鍖?,
        "entry_path": "/web#action=logistics_dispatch.action_batch_list",
        "priority": 1
      },
      {
        "entry_code": "risk_waybill",
        "entry_label": "鏌ョ湅瓒呮椂椋庨櫓杩愬崟",
        "entry_path": "/web#action=logistics_dispatch.action_waybill_list",
        "priority": 2
      }
    ]
  },
  "request_id": "req_home_guide_001"
}
```

---

## 5. 缁熻鎬昏鎺ュ彛绀轰緥

鎺ㄨ崘鎺ュ彛锛?- `GET /api/admin/logistics/stats/overview`

绀轰緥鍝嶅簲锛?
```json
{
  "code": "OK",
  "message": "success",
  "data": {
    "waybill_total": 1260,
    "batch_total": 84,
    "in_transit_waybill_count": 96,
    "signed_waybill_count": 1134,
    "exception_waybill_rate": 0.07,
    "timeout_waybill_rate": 0.03,
    "evidence_completion_rate": 0.88,
    "signoff_completion_rate": 0.91
  },
  "request_id": "req_stats_overview_001"
}
```

---

## 6. 缁熻瓒嬪娍鎺ュ彛绀轰緥

鎺ㄨ崘鎺ュ彛锛?- `GET /api/admin/logistics/stats/trend`

绀轰緥鍝嶅簲锛?
```json
{
  "code": "OK",
  "message": "success",
  "data": {
    "metric_code": "exception_waybill_rate",
    "metric_label": "寮傚父杩愬崟鐜?,
    "granularity": "day",
    "current_value": 0.07,
    "previous_value": 0.05,
    "change_rate": 0.4,
    "points": [
      {
        "point_date": "2026-04-10",
        "metric_value": 0.04
      },
      {
        "point_date": "2026-04-11",
        "metric_value": 0.05
      }
    ]
  },
  "request_id": "req_stats_trend_001"
}
```

## 7. 缁熻鎺掕鎺ュ彛绀轰緥

鎺ㄨ崘鎺ュ彛锛?- `GET /api/admin/logistics/stats/ranking`

绀轰緥鍝嶅簲锛?
```json
{
  "code": "OK",
  "message": "success",
  "data": {
    "dimension_code": "driver",
    "dimension_label": "鍙告満",
    "metric_code": "exception_waybill_rate",
    "items": [
      {
        "rank_no": 1,
        "object_id": 301,
        "object_code": "DRV-301",
        "object_label": "寮犲笀鍌?,
        "metric_value": 0.14
      }
    ]
  },
  "request_id": "req_stats_rank_001"
}
```

## 8. 标准模板下载接口示例

推荐接口：
- `GET /api/admin/logistics/imports/waybill-standard/template`

示例响应：
```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "template_code": "TSL-IMPORT-WAYBILL-V2",
    "template_version": "v2",
    "default_template_locale": "zh_CN",
    "file_name": "TSL-IMPORT-WAYBILL-V2.zh_CN.xlsx",
    "download_url": "/api/admin/logistics/imports/waybill-standard/template/download?template_code=TSL-IMPORT-WAYBILL-V2&template_version=v2&template_locale=zh_CN",
    "available_templates": [
      {
        "template_locale": "en_US",
        "template_label": "标准模板（英文列头）",
        "file_name": "TSL-IMPORT-WAYBILL-V2.xlsx",
        "download_url": "/api/admin/logistics/imports/waybill-standard/template/download?template_code=TSL-IMPORT-WAYBILL-V2&template_version=v2&template_locale=en_US"
      },
      {
        "template_locale": "zh_CN",
        "template_label": "标准模板（中文列头）",
        "file_name": "TSL-IMPORT-WAYBILL-V2.zh_CN.xlsx",
        "download_url": "/api/admin/logistics/imports/waybill-standard/template/download?template_code=TSL-IMPORT-WAYBILL-V2&template_version=v2&template_locale=zh_CN"
      }
    ]
  },
  "request_id": "req_import_template_001"
}
```

---

## 9. 标准导入预校验接口示例
推荐接口：
- `POST /api/admin/logistics/imports/waybill-standard/precheck`

示例响应：
```json
{
  "code": 0,
  "message": "预校验完成",
  "data": {
    "template_code": "TSL-IMPORT-WAYBILL-V2",
    "template_version": "v2",
    "import_batch_no": "IMP-20260417-001",
    "precheck_token": "pre_001",
    "error_report_url": "/api/admin/logistics/imports/waybill-standard/error-report?import_batch_no=IMP-20260417-001",
    "total_row_count": 6,
    "passed_row_count": 4,
    "failed_row_count": 2,
    "can_confirm_import": false,
    "errors": [
      {
        "sheet_name": "客户明细",
        "row_no": 2,
        "field_code": "customer_no",
        "field_label": "客户编号",
        "error_code": "CUSTOMER_NO_NOT_FOUND",
        "error_message": "客户编号不存在，请先维护客户主数据。"
      },
      {
        "sheet_name": "货物明细",
        "row_no": 3,
        "field_code": "qty",
        "field_label": "数量",
        "error_code": "FIELD_VALUE_INVALID",
        "error_message": "数量必须大于 0。"
      }
    ]
  },
  "request_id": "req_import_precheck_001"
}
```

## 10. 标准导入确认接口示例

推荐接口：
- `POST /api/admin/logistics/imports/waybill-standard/confirm`

示例响应：
```json
{
  "code": 0,
  "message": "正式导入完成",
  "data": {
    "import_batch_no": "IMP-20260417-001",
    "status": "finished",
    "status_label": "已完成",
    "created_waybill_count": 1,
    "created_customer_line_count": 2,
    "created_goods_line_count": 3,
    "updated_record_count": 0,
    "skipped_record_count": 0,
    "failed_record_count": 0,
    "error_report_url": false,
    "failure_reason": false
  },
  "request_id": "req_import_confirm_001"
}
```

---

## 11. 标准导入结果接口示例

推荐接口：
- `GET /api/admin/logistics/imports/waybill-standard/result`

示例响应：
```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "import_batch_no": "IMP-20260417-001",
    "status": "finished",
    "status_label": "已完成",
    "created_waybill_count": 1,
    "created_customer_line_count": 2,
    "created_goods_line_count": 3,
    "updated_record_count": 0,
    "skipped_record_count": 0,
    "failed_record_count": 0,
    "error_report_url": false,
    "failure_reason": false
  },
  "request_id": "req_import_result_001"
}
```

