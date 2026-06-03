# logistics_trace_exception Addon 设计稿

适用范围：
- 异常层模块 `logistics_trace_exception`
- 建立在批次 / 运单上下文与留痕事实之上的异常对象与处理流程设计

优先基准：
- `ai-code/docs/context/Odoo19物流留痕系统运单主对象与留痕主流程设计.md`
- `ai-code/docs/dev/project_coordination/Odoo19物流留痕系统五人分工与前端改造安排.md`
- `ai-code/docs/architecture/logistics_dispatch_addon_design.md`
- `ai-code/docs/architecture/logistics_trace_core_addon_design.md`
- `ai-code/docs/architecture/ARCHITECTURE.md`

---

## 1. 文档定位

本文档是当前异常层的正式设计入口。

它要解决的不是“现场发生了什么”，也不是“图片怎么查看”，而是把“哪里出了问题、问题现在处于什么状态、谁在处理、处理到哪一步”稳定表达出来。

也就是说，这份文档要回答：

1. 异常对象在 Odoo 中是什么
2. 异常与批次、运单、留痕、证据的关系是什么
3. 异常层和执行主线、留痕核心层、证据层如何分工
4. 后台异常列表、异常详情、工作台待处理队列到底读取什么对象

---

## 2. 模块目标

`logistics_trace_exception` 的目标是成为当前系统的“问题与处理主模块”。

它至少要稳定承接下面这些能力：

- 异常主对象
- 异常类型
- 异常状态流转
- 处理记录
- 异常与运单 / 批次 / 留痕 / 证据的关联

并为下游页面提供这些能力：

- 当前异常列表
- 历史异常列表
- 待处理争议列表
- 异常详情页
- 工作台待处理异常区
- 老板页争议对象摘要

---

## 3. 模块边界

## 3.1 本模块负责

- 异常对象主模型
- 异常类型与严重度
- 异常状态流转
- 处理责任人与处理记录
- 异常与运单 / 批次 / 留痕事件的关系
- 异常列表与详情所需的摘要字段来源

## 3.2 本模块不负责

- 执行主线对象本体
- 留痕事件主模型
- 图片二进制与证据元数据主存储
- 工作台与老板页的聚合看板逻辑

这些职责分别留给：

- `logistics_dispatch`
- `logistics_trace_core`
- `logistics_trace_evidence`
- `logistics_trace_dashboard`

---

## 4. 设计原则

## 4.1 异常是问题对象，不是事实对象

留痕事件回答的是：
- 发生过什么

异常对象回答的是：
- 这里有没有问题
- 问题是什么
- 现在谁在处理
- 问题处理到哪一步

因此，异常不应反向替代留痕事实层。

## 4.2 异常优先挂运单和批次上下文

当前基线已经明确：

- 运单是现场留痕主对象
- 批次是执行组织对象

因此，异常应优先建立在：
- `waybill`
- `batch`
- `trace_event`

这组上下文之上，而不是默认挂在订单对象上。

## 4.3 异常处理要轻于工单系统

一期目标是：
- 支撑问题登记
- 支撑责任跟进
- 支撑状态流转
- 支撑阅读与判断

当前不建议把异常层做成完整工单平台。

## 4.4 异常详情必须能读到证据链

异常本身不是孤立记录。

一个真正有价值的异常详情页，必须能让用户看到：

- 对应运单 / 批次
- 关键留痕
- 关键证据
- 当前处理记录

---

## 5. 推荐模型

## 5.1 logistics.trace.exception

定位：
- 异常主对象

建议字段：
- `name`
- `exception_type`
- `severity_level`
- `state`
- `waybill_id`
- `batch_id`
- `trace_event_id`
- `report_time`
- `reporter_user_id`
- `reporter_user_name`
- `process_owner_id`
- `process_owner_name`
- `description`
- `close_summary`
- `closed_time`
- `is_overdue`
- `remark`

说明：
- 异常可以同时带有 `waybill_id` 与 `batch_id`
- 若异常由某次留痕直接触发，建议关联 `trace_event_id`

## 5.2 logistics.trace.exception.process.log

定位：
- 异常处理记录

建议字段：
- `exception_id`
- `action_type`
- `operator_id`
- `operator_name`
- `action_time`
- `from_state`
- `to_state`
- `note`

主要作用：
- 记录每次处理动作
- 为详情页处理记录区提供数据来源

## 5.3 exception_type 建议

第一阶段建议至少支持：

- `delay`
- `damage`
- `missing`
- `rejected`
- `store_closed`
- `signoff_problem`
- `evidence_missing`
- `other`

## 5.4 severity_level 建议

建议最小支持：

- `low`
- `medium`
- `high`
- `critical`

---

## 6. 关键关系

推荐核心关系如下：

```text
logistics.dispatch.waybill 1 -> n logistics.trace.exception
logistics.dispatch.batch   1 -> n logistics.trace.exception
logistics.trace.event      1 -> n logistics.trace.exception

logistics.trace.exception 1 -> n logistics.trace.exception.process.log
```

同时在阅读层应支持：

- 异常详情 -> 关联运单
- 异常详情 -> 关联批次
- 异常详情 -> 关联留痕
- 异常详情 -> 关联证据

其中“关联证据”建议通过：

- `trace_event_id`
- 或业务规则查询

来间接读取，不要求异常对象自身重复存证据主数据。

---

## 7. 依赖建议

推荐 depends：

- `mail`
- `hr`
- `logistics_base`
- `logistics_dispatch`
- `logistics_trace_core`

可选后续依赖：

- `logistics_trace_evidence`

说明：

- `mail`：用于 chatter、活动、附件等基础能力
- `hr`：用于责任人、处理人基础关系
- `logistics_dispatch`：用于批次与运单主对象依赖
- `logistics_trace_core`：用于关联触发留痕事件

---

## 8. 文件结构建议

```text
logistics_trace_exception/
├─ __init__.py
├─ __manifest__.py
├─ models/
│  ├─ __init__.py
│  ├─ logistics_trace_exception.py
│  └─ logistics_trace_exception_process_log.py
├─ security/
│  └─ ir.model.access.csv
├─ data/
│  └─ exception_type_data.xml
├─ views/
│  ├─ logistics_trace_exception_views.xml
│  ├─ logistics_trace_exception_process_log_views.xml
│  └─ logistics_trace_exception_menus.xml
└─ demo/
```

---

## 9. 页面建议

第一阶段最推荐先落这些页面：

### 9.1 异常列表

- 当前异常列表
- 历史异常列表
- 待处理争议列表

### 9.2 异常详情

建议分区：
- 基本信息
- 关联运单 / 批次
- 关键留痕
- 关键证据
- 处理记录
- chatter / 附件

### 9.3 关联入口

- 从运单详情跳异常详情
- 从批次详情跳异常列表
- 从工作台跳待处理异常

---

## 10. 状态建议

建议最小状态：

- `draft`
- `open`
- `processing`
- `resolved`
- `closed`
- `cancelled`

说明：

- `resolved` 表示业务上已确认处理方案
- `closed` 表示流程正式闭环

当前不建议加太多中间态。

---

## 11. 聚合字段来源建议

虽然聚合字段不一定全部存放在本模块，但本模块应提供这些来源：

- `has_exception`
- `exception_status_summary`
- `latest_exception_time`
- `pending_exception_count`
- `process_owner_name`
- `severity_level`

这些字段将被：

- `logistics_dispatch`
- `logistics_trace_dashboard`
- 后台列表与详情页

间接消费。

---

## 12. 与前端设计的关系

`logistics_trace_exception` 直接支撑这些前端文档：

- `当前异常列表页草图.md`
- `异常详情页草图.md`
- `管理工作台草图.md`
- `老板追溯查看页草图.md`
- `后台页面改造清单.md`

它在前端里的主要表现形式是：

- 异常列表
- 异常详情
- 工作台待处理队列
- 争议对象摘要

也就是说，后台里“问题层”是否成立，很大程度取决于这个模块设计是否清晰。

---

## 13. 实施顺序建议

建议按下面顺序推进：

1. 先落 `logistics.trace.exception` 主模型
2. 稳定 `exception_type / severity_level / state` 三套口径
3. 落处理记录模型
4. 落异常列表与详情基础视图
5. 从 `logistics_dispatch` 和 `logistics_trace_core` 接入 smart button
6. 最后再增强与证据层和看板层的联动

---

## 14. 当前结论

如果要把旧的 `logistics_exception` 设计真正回调到当前正确主线，最合理的做法不是继续把异常挂在订单对象上，而是直接采用：

**`logistics_trace_exception` 作为异常层模块。**

它应正式承接：

- 异常对象
- 异常状态流转
- 处理责任人与处理记录
- 与运单 / 批次 / 留痕事件的关联

后续工作台、老板页、异常中心都应建立在这层之上。

