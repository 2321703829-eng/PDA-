# logistics_trace Mapping Bridge

> 状态说明：本文档已转为历史桥接说明。
>
> 原因：当前有效设计已不再以 `logistics_trace` 单模块同时承接留痕事件与证据图片；留痕事实层已回调为 `logistics_trace_core`，证据层已回调为 `logistics_trace_evidence`，异常层由 `logistics_trace_exception` 单独承接。
>
> 当前请优先参考：
> - `ai-code/Odoo19物流留痕系统运单主对象与留痕主流程设计.md`
> - `ai-code/docs/architecture/logistics_trace_core_addon_design.md`
> - `ai-code/docs/architecture/logistics_trace_evidence_addon_design.md`
> - `ai-code/docs/architecture/ARCHITECTURE.md`
> - `ai-code/docs/architecture/custom_addons_blueprint.md`
> - `ai-code/docs/context/odoo_logistics_feasibility.md`

---

## 当前桥接结论

这份文档不再承担当前“留痕事件与证据模型正式映射稿”的职责。

它现在保留的主要价值，是帮助后续阅读旧草图、旧评审记录、旧字段设计时，把下面这组旧命名：

- `logistics_trace`
- `logistics.trace`
- `logistics.trace.image`

正确桥接到当前已经稳定下来的结构：

- `logistics_trace_core`
- `logistics.trace.event`
- `logistics_trace_evidence`
- `logistics.trace.evidence`
- `logistics_trace_exception`

当前应按下面这条主线理解：

```text
dispatch -> trace_core -> evidence -> exception
```

而不应再把“留痕事件 + 证据图片”压在一个粗粒度 `logistics_trace` 模块里。

## 当前替代文档

后续如果要继续设计或实现留痕与证据层，请优先看：

1. `Odoo19物流留痕系统运单主对象与留痕主流程设计.md`
2. `docs/architecture/logistics_trace_core_addon_design.md`
3. `docs/architecture/logistics_trace_evidence_addon_design.md`
4. `docs/architecture/ARCHITECTURE.md`
5. `docs/architecture/custom_addons_blueprint.md`
6. `docs/context/odoo_logistics_feasibility.md`

补充说明：

- 当前仓库中留痕核心层已有正式 addon 设计稿
- 证据层当前正式口径主要分散在架构总纲、蓝图与可实现性文档中
- 因此本文档现在只承担历史桥接作用，不再作为现行设计稿继续维护

## 保留方式

以下第 `1` 到 `11` 节保留的是旧阶段“留痕 + 图片组合映射稿”的详细内容。

它们现在仍可用于：

- 对照历史字段语义
- 阅读旧计划和旧评审记录
- 解释为什么当前口径从 `logistics.trace / logistics.trace.image` 迁移到了 `trace.event / trace.evidence`

但不应再直接作为当前实现模型的落地依据。

## 1. 文档目标

本文档用于把当前已明确的现场留痕事实与图片证据，映射到 Odoo 的事实层模型设计。

本版以最新业务前提为准：

- 留痕是事实层，不是快照层
- 图片始终挂在留痕事件之下
- 留痕主粒度不再是订单级，而是运单级与批次级

## 2. 当前源模型口径

当前成熟业务链路中的事实层主要有两张表：

- `trace_record`：留痕事实表
- `trace_record_image`：留痕图片业务表

它们分别承担：

- 记录某一时点发生了什么
- 记录某条留痕对应了哪些图片及业务元信息

## 3. Odoo 侧建议模型

建议在 `logistics_trace` 模块中落两个核心模型：

- `logistics.trace`
- `logistics.trace.image`

建议关系：

- `logistics.batch` 1 -> n `logistics.trace`
- `logistics.waybill` 1 -> n `logistics.trace`
- `logistics.trace` 1 -> n `logistics.trace.image`

如果当前短期仍沿用 `logistics.order` 模型名，则文档中应明确它在此处语义等同于运单主对象，而不是订单明细。

## 4. 关键设计原则

### 4.1 留痕事件是事实，不是状态快照

`logistics.trace` 不替代 `logistics.batch` / `logistics.waybill` 的当前状态字段。

它只记录事实：

- 谁在什么时间提交了什么类型的留痕
- 留痕发生在运单粒度还是批次粒度
- 是否包含异常信息
- 是否附带图片证据

### 4.2 图片不直接挂订单明细

当前稳定口径应为：

- 图片主挂载对象是 `trace_id`
- 批次和运单只保留最新图片摘要
- 运单下订单明细不直接承接现场图片主挂载

### 4.3 图片二进制不进入 Odoo 主存储

更稳的做法仍然是：

- Odoo 存业务元数据
- 图片服务继续存对象文件
- Odoo 通过 `image_access_key` 打开、预览、查询图片

### 4.4 留痕粒度必须显式区分

当前必须保留两类留痕主体：

- 批次级留痕事件
- 运单级留痕事件

不再建议用“订单级留痕”作为默认主口径。

## 5. logistics.trace 映射建议

### 5.1 建议模型定位

`logistics.trace` 承接留痕事件的事实记录语义。

### 5.2 建议字段映射

| 来源语义 | Odoo 字段 | 类型建议 | 说明 |
|---|---|---|---|
| trace_id | `external_trace_id` | Char 或 Integer, index | 外部留痕主键 |
| client_id | `external_client_id` | Char, index | 租户隔离口径 |
| waybill_no | `waybill_no` | Char, index | 运单号快照 |
| waybill_ref | `waybill_id` | Many2one(`logistics.waybill`) | 可选关联 |
| batch_no | `batch_name` | Char, index | 批次号快照 |
| batch_ref | `batch_id` | Many2one(`logistics.batch`) | 可选关联 |
| record_granularity | `record_granularity` | Selection | `waybill` / `batch` |
| trace_type | `source_trace_type` | Char | 原始留痕类型 |
| location_text | `location_text` | Char | 位置描述 |
| submit_source | `submit_source` | Char | 提交来源 |
| submit_user | `submit_user_name` | Char | 提交人快照 |
| plate_no | `plate_no` | Char | 车牌快照 |
| trace_time | `trace_time` | Datetime, index | 留痕发生时间 |
| is_exception | `is_exception` | Boolean | 是否异常 |
| exception_type | `exception_type` | Char | 异常类型 |
| exception_desc | `exception_desc` | Text | 异常说明 |
| source_trace_status | `source_trace_status` | Char | 原始留痕状态 |
| is_written_back | `is_written_back` | Boolean | 是否已回写 |
| writeback_msg | `writeback_msg` | Text | 回写说明 |
| source_channel | `source_channel` | Char | 来源渠道 |
| source_record_id | `source_record_id` | Char | 来源记录标识 |
| source_file_name | `source_file_name` | Char | 来源文件名 |
| source_row_no | `source_row_no` | Integer | 来源行号 |

### 5.3 建议补充字段

| 字段 | 类型建议 | 说明 |
|---|---|---|
| `name` | Char | 展示名，例如 TRACE-20260411-0001 |
| `image_ids` | One2many(`logistics.trace.image`) | 关联图片 |
| `image_count` | Integer, compute/store | 图片数量 |
| `active` | Boolean | 归档控制 |
| `company_id` | Many2one(`res.company`) | 多公司预留 |

## 6. logistics.trace.image 映射建议

### 6.1 建议模型定位

`logistics.trace.image` 承接业务图片元数据。

它记录的是：

- 图片属于哪条留痕
- 图片业务顺序、分类、备注
- 图片访问键
- 存储元信息

它不负责存储图片二进制本体。

### 6.2 建议字段映射

| 来源语义 | Odoo 字段 | 类型建议 | 说明 |
|---|---|---|---|
| image_id | `external_image_id` | Char 或 Integer, index | 外部图片主键 |
| client_id | `external_client_id` | Char, index | 租户隔离口径 |
| trace_id | `trace_id` | Many2one(`logistics.trace`), required | 所属留痕 |
| waybill_no | `waybill_no` | Char | 运单号快照 |
| batch_no | `batch_name` | Char | 批次号快照 |
| trace_type | `trace_type` | Char | 留痕类型快照 |
| image_category | `image_category` | Char | 图片分类 |
| image_seq | `sequence` | Integer | 同留痕下排序 |
| file_name | `file_name` | Char | 系统文件名 |
| original_file_name | `original_file_name` | Char | 原始文件名 |
| file_ext | `file_ext` | Char | 文件扩展名 |
| storage_relative_path | `storage_relative_path` | Char | 相对存储路径 |
| image_access_key | `image_access_key` | Char, required, index | 图片访问键 |
| storage_provider | `storage_provider` | Char | 存储提供方 |
| storage_bucket | `storage_bucket` | Char | 存储桶或目录标识 |
| storage_status | `storage_status` | Char | `ACTIVE / MISSING / INVALID / DELETED` |
| upload_user_id | `external_upload_user_id` | Char 或 Integer | 外部上传人主键 |
| upload_user_name | `upload_user_name` | Char | 上传人快照 |
| remark | `remark` | Text | 图片备注 |
| external_created_at | `external_created_at` | Datetime | 外部创建时间 |

## 7. 人员关系当前建议

当前仍不建议强制把 `submit_user` / `upload_user` 映射到 `hr.employee` 或 `res.users`。

当前建议：

- 先保留 `submit_user_name`
- 先保留 `upload_user_name`
- 后续若人员主数据稳定，再补 `submit_employee_id`、`upload_employee_id`

## 8. 留痕粒度策略

### 8.1 必须保留 record_granularity

因为当前既有业务已明确区分：

- 批次级留痕
- 运单级留痕

所以 Odoo 侧必须显式保留 `record_granularity`。

### 8.2 关联策略

建议：

- `record_granularity = waybill` 时，优先关联 `logistics.waybill`
- `record_granularity = batch` 时，优先关联 `logistics.batch`
- 同时保留 `waybill_no` / `batch_name` 快照字段，避免因关联缺失丢数据

## 9. 图片服务边界

当前稳定边界建议继续保留：

- 图片服务负责 `upload / read / meta`
- Odoo 负责业务关系与业务元数据
- `image_access_key` 是主访问键

因此 Odoo 模型中需要保留的不是文件本体，而是：

- `image_access_key`
- `storage_provider`
- `storage_bucket`
- `storage_relative_path`
- `storage_status`

## 10. Odoo 页面建议

### 10.1 留痕页

建议优先提供：

- 留痕列表
- 留痕详情
- 时间、类型、异常字段筛选
- 关联图片 smart button

### 10.2 图片页

建议优先提供：

- 某条留痕下的图片列表
- 图片分类
- 排序号
- 存储状态
- 查看按钮

## 11. 旧阶段映射结论（历史保留）

在旧阶段，这份组合映射稿曾建议：

- `logistics.trace` 承接批次级与运单级留痕事件
- `logistics.trace.image` 承接业务图片元数据层
- 图片二进制继续留在外部图片服务
- 批次、运单只保留最新留痕和最新图片摘要

这样既能保留当前成熟链路，也不会把 Odoo 过早拖进图片存储实现细节。
