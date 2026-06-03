# logistics_trace_evidence Addon 设计稿

适用范围：
- 证据层模块 `logistics_trace_evidence`
- 图片、备注、签名等证据对象的 Odoo 承接设计

优先基准：
- `ai-code/docs/context/Odoo19物流留痕系统运单主对象与留痕主流程设计.md`
- `ai-code/docs/dev/project_coordination/Odoo19物流留痕系统五人分工与前端改造安排.md`
- `ai-code/docs/architecture/ARCHITECTURE.md`
- `ai-code/docs/architecture/custom_addons_blueprint.md`
- `ai-code/docs/architecture/logistics_trace_core_addon_design.md`
- `ai-code/docs/context/odoo_logistics_feasibility.md`

---

## 1. 文档定位

本文档是当前证据层的正式设计入口。

它要解决的不是“现场到底发生了什么”，而是把已经发生过的事实所对应的材料，稳定承接到 Odoo 中。

也就是说，这份文档要回答：

1. 证据对象在 Odoo 中是什么
2. 证据和留痕事件之间如何挂接
3. 图片服务和 Odoo 之间怎么分边界
4. 后台详情页、证据查看区、老板摘要页到底读取什么对象

---

## 2. 模块目标

`logistics_trace_evidence` 的目标是成为当前系统的“证据材料主模块”。

它至少要稳定承接下面这些能力：

- 图片证据对象
- 备注、签名等轻量证据材料
- 访问 key 与外部存储元数据
- 留痕事件下的证据列表与证据阅读入口

并为上下游模块提供这些支持：

- 给 `logistics_trace_core` 提供证据挂接后的阅读补充
- 给 `logistics_trace_exception` 提供异常详情中的关键证据来源
- 给后台前端提供证据查看区、证据总览页、预览 widget
- 给聚合层提供 `evidence_count`、`latest_evidence_time`、`evidence_completeness` 等来源

---

## 3. 模块边界

## 3.1 本模块负责

- 证据对象主模型
- 证据与留痕事件之间的关系
- 证据类型、顺序、备注、访问 key
- 外部存储元数据与证据访问状态
- 证据基础查询与证据阅读入口
- 证据相关聚合的原始来源

## 3.2 本模块不负责

- 留痕事件事实对象本体
- 异常状态流转与处理日志
- 图片二进制主存储
- 工作台或老板页的聚合页面本体
- 司机端上传流程细节

这些职责分别留给：

- `logistics_trace_core`
- `logistics_trace_exception`
- 外部图片服务
- `logistics_trace_dashboard`
- `logistics_trace_mobile`

---

## 4. 设计原则

## 4.1 证据必须挂在留痕事件之下

当前稳定口径应为：

```text
batch / waybill -> trace.event -> trace.evidence
```

不要直接把证据主挂到订单明细、运单或批次主对象上。

运单、批次可以保留证据摘要字段，但证据事实主归属仍应是留痕事件。

## 4.2 二进制继续放在外部图片服务

本模块负责的是：

- 业务关系
- 访问 key
- 元数据
- 阅读入口

不负责把图片二进制写进 Odoo 主存储。

## 4.3 证据层服务阅读，不主导事实判断

证据对象回答的是：

- 有哪些材料
- 材料是否可访问
- 材料属于哪条留痕

它不直接替代下面这些结论：

- 当前问题是否成立
- 当前风险是否关闭
- 当前异常由谁负责

这些结论仍应建立在 `trace_core + trace_exception + 聚合规则` 之上。

## 4.4 证据对象要兼容图片优先、材料扩展

一期证据主对象仍以图片为主，但模型不要被“只有图片”锁死。

因此建议：

- 用 `evidence_type` 区分图片、签名、文本备注等材料
- 但页面和聚合优先围绕图片证据落地

---

## 5. 推荐模型

## 5.1 logistics.trace.evidence

定位：
- 证据主对象

建议字段：
- `name`
- `trace_event_id`
- `waybill_id`
- `batch_id`
- `evidence_type`
- `sequence`
- `remark`
- `image_access_key`
- `thumbnail_access_key`
- `file_name`
- `original_file_name`
- `file_ext`
- `mime_type`
- `content_length`
- `storage_provider`
- `storage_bucket`
- `storage_relative_path`
- `storage_status`
- `capture_time`
- `upload_user_id`
- `upload_user_name`
- `external_evidence_id`
- `external_source_id`
- `active`
- `company_id`

说明：

- `trace_event_id` 为主归属字段，应必填
- `waybill_id`、`batch_id` 可作为冗余快照或 related 查询字段
- `image_access_key` 是主访问键，一期应保留唯一性约束

## 5.2 evidence_type 建议

第一阶段建议至少支持：

- `image`
- `signature`
- `text_note`
- `receipt`

说明：

- 一期主页面与聚合规则优先围绕 `image`
- 其他类型先满足结构兼容，不要求一开始都做复杂阅读器

## 5.3 storage_status 建议

建议最小支持：

- `active`
- `missing`
- `invalid`
- `deleted`

说明：

- `active`：访问正常
- `missing`：业务记录存在，但外部存储文件缺失
- `invalid`：访问 key 或元数据异常
- `deleted`：业务上已删除或不可再读

---

## 6. 关键关系

建议关系：

```text
logistics.dispatch.batch 1 -> n logistics.trace.event
logistics.dispatch.waybill 1 -> n logistics.trace.event

logistics.trace.event 1 -> n logistics.trace.evidence

logistics.trace.exception n -> 1 logistics.trace.event
logistics.trace.exception   -> read evidence summary
```

补充说明：

- 证据主关系不要求一期直接反挂异常对象
- 异常详情页可以优先通过 `trace_event_id` 和聚合摘要读取关键证据

---

## 7. 依赖建议

建议最小依赖：

- `base`
- `mail`
- `logistics_dispatch`
- `logistics_trace_core`

可选依赖：

- `contacts`
- `hr`

说明：

- `mail` 主要用于轻量附件、chatter、活动协同能力复用
- `contacts / hr` 不是一期证据层落地的强依赖
- 证据层不应反向依赖异常层

---

## 8. 文件结构建议

```text
logistics_trace_evidence/
├─ __init__.py
├─ __manifest__.py
├─ models/
│  ├─ __init__.py
│  └─ logistics_trace_evidence.py
├─ security/
│  ├─ ir.model.access.csv
│  └─ logistics_trace_evidence_security.xml
├─ views/
│  ├─ logistics_trace_evidence_views.xml
│  ├─ logistics_trace_evidence_search_views.xml
│  └─ logistics_trace_evidence_menus.xml
├─ data/
│  └─ logistics_trace_evidence_sequence.xml
└─ static/
   └─ src/
      └─ js/
         └─ evidence_viewer_widget.js
```

说明：

- 一期先保证模型、基础视图、搜索视图、viewer widget 入口
- 更复杂的预览器可以后续继续增强

---

## 9. 页面建议

建议优先提供：

1. 证据总览列表页
2. 留痕详情内嵌证据区
3. 运单详情页关键证据区
4. 异常详情页关键证据摘要区

建议基础能力：

- 按 `trace_event_id / waybill_id / batch_id / evidence_type / storage_status` 搜索
- 列表查看缩略图、备注、上传人、时间、状态
- 通过 `image_access_key` 打开原图或外部预览
- 支持从证据快速跳回留痕事件

---

## 10. 聚合字段来源建议

证据层至少应为下游提供这些聚合来源：

- `evidence_count`
- `has_evidence`
- `latest_evidence_time`
- `latest_evidence_access_key`
- `evidence_completeness`

说明：

- `evidence_count`、`latest_evidence_time` 主要由证据层事实直接提供
- `evidence_completeness` 属于“证据事实 + 规则”的组合判断
- 因此最终聚合可落在运单、批次、异常、工作台对象上，但原始事实来源仍来自本模块

---

## 11. 状态与约束建议

## 11.1 证据状态

建议保留：

- `storage_status`
- `active`

补充说明：

- `storage_status` 解决外部文件可访问性问题
- `active` 解决业务归档与前台默认可见性问题

## 11.2 关键约束

建议至少保留：

- `trace_event_id` 必填
- `evidence_type` 必填
- `image_access_key` 在图片类证据下应唯一
- `sequence` 在同一 `trace_event_id` 下应稳定排序
- 不允许证据主对象绕过留痕事件直接孤立存在

---

## 12. 与前端设计的关系

`logistics_trace_evidence` 直接支撑这些前端文档：

1. `专题设计/前端设计/一期前端相关设计/00_导航与总纲/管理员后台界面改造方案.md`
2. `专题设计/前端设计/一期前端相关设计/00_导航与总纲/老板追溯界面改造方案.md`
3. `专题设计/前端设计/一期前端相关设计/03_落地与联调/P0页面Odoo落地实现清单.md`
4. `专题设计/前端设计/一期前端相关设计/02_跨模块规范/02_交互与组件/时间线与证据区widget结构草案.md`

主要支撑场景：

- 运单详情页证据查看区
- 留痕详情页证据列表
- 异常详情页关键证据摘要
- 老板页“摘要证据”阅读入口

---

## 13. 实施顺序建议

建议顺序：

1. 先稳定 `logistics_trace_core`
2. 再起 `logistics_trace_evidence` 主模型与基础视图
3. 接通证据列表、证据详情、viewer widget
4. 回填运单 / 批次 / 异常上的证据聚合字段
5. 最后再增强证据总览页与老板页摘要证据体验

---

## 14. 当前结论

当前最稳的证据层落法应为：

- `logistics_trace_evidence` 作为证据主模块
- `logistics.trace.evidence` 作为证据主对象
- 证据主归属挂在 `logistics.trace.event`
- 图片二进制继续留在外部图片服务
- 运单、批次、异常只读取证据摘要或聚合结果

这条设计能同时兼顾：

- 当前追溯阅读链
- 前端证据查看需求
- 外部图片服务边界
- 后续继续扩展签名、备注、票据类证据的空间

