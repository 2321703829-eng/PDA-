# logistics_trace_core Addon 设计稿

适用范围：
- 留痕核心模块 `logistics_trace_core`
- 批次级与运单级留痕事件的 Odoo 承接设计

优先基准：
- `ai-code/Odoo19物流留痕系统运单主对象与留痕主流程设计.md`
- `ai-code/Odoo19物流留痕系统五人分工与前端改造安排.md`
- `ai-code/docs/architecture/logistics_dispatch_addon_design.md`
- `ai-code/docs/architecture/ARCHITECTURE.md`

---

## 1. 文档定位

本文档是当前留痕核心层的正式设计入口。

它要解决的不是“图片怎么存”，也不是“异常怎么处理”，而是先把现场事实事件稳定表达出来。

也就是说，这份文档要回答：

1. 留痕事件在 Odoo 中是什么
2. 批次级留痕和运单级留痕如何共存
3. 留痕核心层和执行主线、证据层、异常层如何分工
4. 后台时间线、详情页、证据页到底读取什么对象

---

## 2. 模块目标

`logistics_trace_core` 的目标是成为当前系统的“事实事件主模块”。

它至少要稳定承接下面这两类事件：

- 批次级留痕事件
- 运单级留痕事件

并为下游模块提供这些能力：

- 给 `logistics_trace_evidence` 提供明确证据挂载点
- 给 `logistics_trace_exception` 提供异常关联上下文
- 给后台前端提供时间线、最近留痕、留痕详情、留痕筛选能力
- 给工作台和聚合层提供最新留痕与留痕统计来源

---

## 3. 模块边界

## 3.1 本模块负责

- 留痕事件主对象
- 批次级与运单级事件归属关系
- 留痕类型与事件基础字段
- 留痕时间线查询基础
- 留痕与执行主线对象之间的关系
- 最近留痕摘要与事件基础统计来源

## 3.2 本模块不负责

- 图片二进制或图片元数据主存储
- 异常处理流程
- 工作台聚合页面
- 调度主线对象本体
- 司机端上传实现细节

这些职责分别留给：

- `logistics_trace_evidence`
- `logistics_trace_exception`
- `logistics_trace_dashboard`
- `logistics_dispatch`
- `logistics_trace_mobile`

---

## 4. 设计原则

## 4.1 事实层优先

本模块的核心是回答：

**现场到底发生过什么。**

它不直接负责回答：

- 当前最终结论是什么
- 谁负责异常处理
- 证据是不是完整

这些问题可以建立在留痕事实之上，但不应反向塞回留痕核心层。

## 4.2 留痕必须支持两类主体

当前基线已经明确：

- 装车前留痕是批次级留痕
- 到店 / 签收 / 异常上报是运单级留痕

因此，本模块不能只支持单一对象类型。

## 4.3 事件层和证据层分开

留痕事件负责：
- 时间
- 类型
- 提交人
- 备注
- 所属对象

证据层负责：
- 图片
- 签名
- 访问 key
- 存储状态
- 证据元数据

## 4.4 事件类型要强于页面类型

不要为了页面结构反向设计事件模型。

应先稳定事件类型，再让页面按事件类型组织时间线。

---

## 5. 推荐模型

## 5.1 logistics.trace.event

定位：
- 留痕事件主对象

建议字段：
- `name`
- `event_type`
- `object_type`
- `batch_id`
- `waybill_id`
- `trace_time`
- `submit_user_id`
- `submit_user_name`
- `submit_source`
- `location_text`
- `plate_no`
- `driver_name`
- `remark`
- `is_exception`
- `source_channel`
- `source_record_id`
- `state`

说明：
- `object_type` 建议至少支持 `batch` 和 `waybill`
- `batch_id` 与 `waybill_id` 二选一或按规则约束

## 5.2 event_type 建议

第一阶段建议至少支持：

- `arrive_loading_point`
- `start_loading`
- `finish_loading`
- `departed`
- `arrive_store`
- `deliver_finish`
- `signoff`
- `exception_report`

说明：
- 这些类型既能覆盖仓侧，也能覆盖店侧
- 同时适配后台时间线和司机端流程

## 5.3 object_type 建议

建议最小支持：

- `batch`
- `waybill`

当前不建议：

- 直接支持 `order`

因为订单不是现场留痕主对象。

---

## 6. 关键关系

推荐核心关系如下：

```text
logistics.dispatch.batch 1 -> n logistics.trace.event
logistics.dispatch.waybill 1 -> n logistics.trace.event

logistics.trace.event 1 -> n logistics.trace.evidence   # 由 evidence 模块承接
logistics.trace.event 1 -> n logistics.trace.exception  # 由 exception 模块承接
```

其中需要明确：

- 批次级事件必须能挂到 `batch`
- 运单级事件必须能挂到 `waybill`
- 一个事件下允许挂多个证据对象

---

## 7. 依赖建议

推荐 depends：

- `mail`
- `logistics_base`
- `logistics_dispatch`

说明：

- `mail`：用于消息、活动、附件框架等基础能力
- `logistics_base`：用于项目共用基础扩展
- `logistics_dispatch`：用于批次、运单主对象依赖

当前不建议为了留痕核心层强依赖证据或异常模块。

---

## 8. 文件结构建议

```text
logistics_trace_core/
├─ __init__.py
├─ __manifest__.py
├─ models/
│  ├─ __init__.py
│  └─ logistics_trace_event.py
├─ security/
│  └─ ir.model.access.csv
├─ data/
│  └─ trace_event_type_data.xml
├─ views/
│  ├─ logistics_trace_event_views.xml
│  └─ logistics_trace_event_menus.xml
└─ demo/
```

---

## 9. 页面建议

第一阶段最推荐先落这些页面和区块：

### 9.1 留痕时间线页

- 按运单查看时间线
- 按批次查看时间线

### 9.2 详情页中的留痕区

- 运单详情页中的时间线区
- 批次详情页中的留痕摘要区
- 异常详情页中的关联留痕区

### 9.3 留痕事件查看页

- 留痕事件基础详情
- 留痕下证据入口

---

## 10. 聚合字段来源建议

虽然聚合字段本身不一定存放在本模块，但本模块应提供这些来源：

- `latest_trace_time`
- `latest_trace_type`
- `latest_trace_user_name`
- `trace_count`
- `batch_trace_count`
- `waybill_trace_count`

这些字段将被：

- `logistics_dispatch`
- `logistics_trace_dashboard`
- 后台列表与详情页

间接消费。

---

## 11. 状态与约束建议

## 11.1 留痕状态

如果需要事件状态，建议最小化为：

- `draft`
- `submitted`
- `invalid`

当前不建议做过深状态机。

## 11.2 关键约束

- 运单级事件必须关联 `waybill_id`
- 批次级事件必须关联 `batch_id`
- 事件类型必须在受控字典中
- 一个事件必须有明确 `trace_time`

---

## 12. 与前端设计的关系

`logistics_trace_core` 直接支撑这些前端文档：

- `留痕时间线页草图.md`
- `运单详情页草图.md`
- `批次详情页草图.md`
- `页面字段清单.md`
- `后台接口_查询消费清单.md`

它在前端里的主要表现形式是：

- 时间线
- 最新留痕摘要
- 留痕详情
- 留痕筛选与事件类型阅读

也就是说，后台里“过程层”是否成立，很大程度取决于这个模块设计是否清晰。

---

## 13. 实施顺序建议

建议按下面顺序推进：

1. 先落 `logistics.trace.event` 主模型
2. 先稳定 `event_type / object_type` 两套口径
3. 落基础列表与表单视图
4. 从 `logistics_dispatch` 的批次和运单模型接入 smart button
5. 再对接 `logistics_trace_evidence`
6. 最后对接 `logistics_trace_exception`

---

## 14. 当前结论

如果要把旧的 `logistics_trace` 设计真正回调到当前正确主线，最合理的做法不是继续把留痕和证据塞在一个模块里，而是直接采用：

**`logistics_trace_core` 作为留痕核心层模块。**

它应正式承接：

- 批次级留痕事件
- 运单级留痕事件
- 留痕时间线能力
- 最近留痕摘要和事件基础统计来源

后续证据、异常、看板和前端时间线都应建立在这层之上。

