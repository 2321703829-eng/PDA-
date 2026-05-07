# controller 示例响应

适用范围：
- 当前采用 `JSON controller` 承接的聚合与增强读取接口
- 当前一期重点包括：工作台、留痕时间线增强版、证据查看区、老板追溯摘要页

> 状态说明：
> - 本文档当前继续作为 `JSON controller` 返回示例文档使用。
> - 当前 controller 方法目录、接口用途与最新字段口径，优先以 `最终接口总表.md` 为准。
> - 本文档主要负责补充返回包结构与典型示例，不再单独承担完整接口目录职责。

优先基准：
- `最终接口总表.md`
- `接口路线决策文档.md`
- `前后端接口字段级契约清单.md`
- `聚合字段实现策略文档.md`

关联文档：
- `P0页面Odoo落地实现清单.md`
- `工作台模块前端设计草案.md`
- `老板追溯页前端设计草案.md`
- `留痕与追溯模块前端设计草案.md`

---

## 1. 文档定位

这份文档用于补足“字段级契约清单”之后的下一层信息：

- controller 返回结构到底长什么样
- 前端拿到后按什么方式消费
- 哪些字段一定有，哪些字段可以为空

这不是最终 API 文档，但已经足够支撑前端 mock、状态管理和组件开发。

---

## 2. 通用返回结构

当前建议所有 `JSON controller` 统一按下面结构返回：

```json
{
  "code": "OK",
  "message": "success",
  "data": {},
  "request_id": "req_demo_001"
}
```

说明：
- `code`：程序判断是否成功
- `message`：保留给调试或页面提示
- `data`：真正业务数据
- `request_id`：排查问题时用于日志追踪

失败示例：

```json
{
  "code": "FORBIDDEN",
  "message": "当前用户无权查看该对象",
  "data": null,
  "request_id": "req_demo_002"
}
```

---

## 3. 管理工作台概览接口示例

推荐接口：
- `GET /api/logistics/dashboard/summary`

用途：
- 工作台顶部卡片
- 今日处理总览

示例响应：

```json
{
  "code": "OK",
  "message": "success",
  "data": {
    "date": "2026-04-13",
    "open_exception_count": 18,
    "processing_exception_count": 7,
    "evidence_missing_count": 12,
    "high_risk_batch_count": 5,
    "today_trace_count": 236,
    "today_closed_exception_count": 9
  },
  "request_id": "req_dashboard_summary_001"
}
```

前端用途：
- 工作台顶部 6 张概览卡
- 红黄标签提示

---

## 4. 管理工作台优先处理队列接口示例

推荐接口：
- `GET /api/logistics/dashboard/priority-queue`

用途：
- 工作台“今天先处理什么”列表

示例响应：

```json
{
  "code": "OK",
  "message": "success",
  "data": {
    "items": [
      {
        "object_type": "waybill",
        "object_id": 101,
        "waybill_no": "WB202604130001",
        "batch_name": "BATCH-20260413-01",
        "store_name": "浦东世纪大道店",
        "priority_level": "high",
        "priority_level_label": "高优先级",
        "reason_summary": "破损异常未闭环，证据不足",
        "exception_count": 1,
        "latest_trace_at": "2026-04-13 09:18:00",
        "owner_name": "李四"
      }
    ]
  },
  "request_id": "req_dashboard_queue_001"
}
```

前端用途：
- 优先处理队列
- 点击跳转运单详情或异常详情

---

## 5. 运单时间线增强读取接口示例

推荐接口：
- `GET /api/logistics/traces/waybill/{waybill_id}/timeline`

用途：
- 运单详情页中的时间线阅读区
- 独立时间线页

示例响应：

```json
{
  "code": "OK",
  "message": "success",
  "data": {
    "waybill_id": 101,
    "waybill_no": "WB202604130001",
    "items": [
      {
        "id": 90001,
        "trace_type": "arrive_store",
        "trace_type_label": "到店",
        "trace_at": "2026-04-13 08:42:00",
        "operator_name": "张三",
        "content_summary": "运单到店，等待交接",
        "remark": null,
        "has_evidence": true,
        "evidence_count": 1,
        "is_exception_related": false,
        "exception_id": null
      },
      {
        "id": 90002,
        "trace_type": "exception_reported",
        "trace_type_label": "异常上报",
        "trace_at": "2026-04-13 09:18:00",
        "operator_name": "李四",
        "content_summary": "上报外包装破损",
        "remark": "客户反映外箱破损",
        "has_evidence": true,
        "evidence_count": 2,
        "is_exception_related": true,
        "exception_id": 30001
      }
    ],
    "page": 1,
    "page_size": 20,
    "total": 2
  },
  "request_id": "req_trace_timeline_001"
}
```

前端用途：
- 时间线卡片渲染
- 图标、标签、异常标识
- 从时间线卡片跳证据区

---

## 6. 证据列表接口示例

推荐接口：
- `GET /api/logistics/evidence/waybill/{waybill_id}`

用途：
- 运单详情页证据区
- 证据查看页

示例响应：

```json
{
  "code": "OK",
  "message": "success",
  "data": {
    "waybill_id": 101,
    "waybill_no": "WB202604130001",
    "items": [
      {
        "id": 50001,
        "trace_id": 90002,
        "trace_type_label": "异常上报",
        "image_access_key": "img_abc_001",
        "preview_url": "/api/images/img_abc_001/preview",
        "full_url": "/api/images/img_abc_001",
        "uploaded_at": "2026-04-13 09:18:12",
        "uploader_name": "李四",
        "remark": "外箱正面",
        "is_exception_related": true,
        "sequence": 1
      },
      {
        "id": 50002,
        "trace_id": 90002,
        "trace_type_label": "异常上报",
        "image_access_key": "img_abc_002",
        "preview_url": "/api/images/img_abc_002/preview",
        "full_url": "/api/images/img_abc_002",
        "uploaded_at": "2026-04-13 09:18:25",
        "uploader_name": "李四",
        "remark": "破损细节",
        "is_exception_related": true,
        "sequence": 2
      }
    ],
    "page": 1,
    "page_size": 50,
    "total": 2
  },
  "request_id": "req_evidence_list_001"
}
```

前端用途：
- 缩略图带
- 大图切换
- 图片信息侧栏

---

## 7. 证据详情接口示例

推荐接口：
- `GET /api/logistics/evidence/{evidence_id}`

用途：
- 单张证据元数据展示

示例响应：

```json
{
  "code": "OK",
  "message": "success",
  "data": {
    "id": 50002,
    "trace_id": 90002,
    "trace_type": "exception_reported",
    "trace_type_label": "异常上报",
    "waybill_id": 101,
    "waybill_no": "WB202604130001",
    "batch_id": 11,
    "batch_name": "BATCH-20260413-01",
    "image_access_key": "img_abc_002",
    "preview_url": "/api/images/img_abc_002/preview",
    "full_url": "/api/images/img_abc_002",
    "uploaded_at": "2026-04-13 09:18:25",
    "uploader_name": "李四",
    "remark": "破损细节",
    "is_exception_related": true
  },
  "request_id": "req_evidence_detail_001"
}
```

---

## 8. 老板追溯摘要接口示例

推荐接口：
- `GET /api/logistics/boss/summary`

用途：
- 老板追溯页顶部摘要区

示例响应：

```json
{
  "code": "OK",
  "message": "success",
  "data": {
    "open_dispute_count": 14,
    "high_risk_batch_count": 3,
    "evidence_missing_count": 9,
    "today_closed_exception_count": 9,
    "focus_items": [
      {
        "object_type": "waybill",
        "object_id": 101,
        "waybill_no": "WB202604130001",
        "issue_summary": "破损争议待确认",
        "evidence_status_label": "证据不足",
        "owner_name": "李四"
      }
    ]
  },
  "request_id": "req_boss_summary_001"
}
```

---

## 9. 异常相关证据摘要接口示例

推荐接口：
- `GET /api/logistics/exceptions/{exception_id}/evidence-summary`

用途：
- 异常详情页关键证据区

示例响应：

```json
{
  "code": "OK",
  "message": "success",
  "data": {
    "exception_id": 30001,
    "exception_no": "EX202604130001",
    "waybill_no": "WB202604130001",
    "evidence_status": "partial",
    "evidence_status_label": "证据不足",
    "items": [
      {
        "evidence_id": 50001,
        "preview_url": "/api/images/img_abc_001/preview",
        "remark": "外箱正面",
        "trace_type_label": "异常上报"
      },
      {
        "evidence_id": 50002,
        "preview_url": "/api/images/img_abc_002/preview",
        "remark": "破损细节",
        "trace_type_label": "异常上报"
      }
    ]
  },
  "request_id": "req_exception_evidence_001"
}
```

---

## 10. 当前推荐的前端消费方式

建议前端统一这样处理：

1. `code === "OK"` 视为成功
2. `data.items` 永远按数组处理
3. 大图、预览图、摘要卡使用同一套字段名
4. 页面状态不要自己猜，优先用后端返回的 `*_label`、`*_summary`

---

## 11. 当前最值得先 mock 的接口

建议先 mock 这 5 个：

1. `dashboard/summary`
2. `dashboard/priority-queue`
3. `traces/waybill/{id}/timeline`
4. `evidence/waybill/{id}`
5. `boss/summary`

这 5 个一旦有 mock，工作台、运单详情增强区、老板页就都能先做起来。
