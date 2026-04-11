# Odoo19物流留痕系统统一命名状态机与编号规则

本文档用于统一当前 Odoo 物流留痕系统中的：

- 命名规则
- 状态机口径
- 编号规则

目的只有一个：避免每个模块各写一套，后面接口、页面、数据库、报表都难以收敛。

相关文档：

- `Odoo19物流留痕系统总体设计与边界说明.md`
- `Odoo19物流留痕系统跨模块接口与数据约束总规范.md`
- `Odoo19物流留痕系统模块重设方案.md`

---

## 1. 命名总原则

统一遵守 5 条原则：

1. 模块名用 `snake_case`
2. 模型技术名用 `dot.case`
3. 字段名用 `snake_case`
4. 状态字段统一使用 `state`
5. 外部编号和内部主键分离

简化理解就是：

- 人看的是业务编号
- 系统连的是内部主键

---

## 2. 模块命名规则

自定义模块统一使用 `logistics_` 前缀。

当前约定如下：

- `logistics_base`
- `logistics_dispatch`
- `logistics_trace_core`
- `logistics_trace_evidence`
- `logistics_trace_rule`
- `logistics_trace_mobile`
- `logistics_trace_exception`
- `logistics_trace_dashboard`
- `logistics_trace_integration`
- `logistics_trace_cn`

不建议：

- 同时出现 `trace`, `tracing`, `track`, `tracking` 混用
- 同时出现 `proof`, `evidence`, `image` 混用为同一层概念

当前统一口径：

- 留痕用 `trace`
- 证据用 `evidence`
- 图片只是证据的一种表现形式

---

## 3. 模型命名规则

模型技术名统一使用：

- `logistics.trace.event`
- `logistics.trace.evidence`
- `logistics.trace.rule`
- `logistics.trace.exception`

建议命名风格如下：

- 留痕主对象：`logistics.trace.event`
- 留痕规则：`logistics.trace.rule`
- 证据主对象：`logistics.trace.evidence`
- 异常主对象：`logistics.trace.exception`
- 调度扩展对象：`logistics.dispatch.task`

不建议：

- `trace.record`
- `trace.log`
- `image.record`
- `proof.item`

因为这些名字会让“事实对象”和“附件对象”的边界变模糊。

---

## 4. 字段命名规则

## 4.1 通用字段

统一字段：

- 主键：`id`
- 展示编号：`name`
- 状态：`state`
- 公司：`company_id`
- 创建人：`create_uid`
- 创建时间：`create_date`
- 更新人：`write_uid`
- 更新时间：`write_date`
- 备注：`remark`
- 描述：`description`

## 4.2 关系字段

统一使用：

- 单对象：`xxx_id`
- 多对象：`xxx_ids`

例如：

- `picking_id`
- `waybill_id`
- `batch_id`
- `trip_id`
- `driver_id`
- `vehicle_id`
- `trace_id`
- `evidence_ids`

## 4.3 枚举类字段

建议统一使用：

- `state`
- `biz_type`
- `trace_type`
- `trace_source`
- `evidence_type`
- `exception_type`
- `storage_provider`

不建议：

- 同时用 `type`、`biz_type`、`event_type` 指代同一件事
- 同时用 `source`、`from_type`、`origin_type` 指代同一件事

---

## 5. XML ID、菜单、视图命名规则

统一采用：

- 菜单：`logistics_trace_core.menu_trace_root`
- 动作：`logistics_trace_core.action_trace_event`
- 列表视图：`logistics_trace_core.view_trace_event_tree`
- 表单视图：`logistics_trace_core.view_trace_event_form`
- 搜索视图：`logistics_trace_core.view_trace_event_search`
- 安全组：`logistics_base.group_trace_manager`

规则是：

- 先模块名
- 再对象名
- 最后是用途

---

## 6. 接口与路由命名规则

## 6.1 外部 HTTP 路由

建议统一分成 3 类前缀：

- 后台接口：`/api/admin/logistics/...`
- 小程序/H5 接口：`/api/mini/logistics/...`
- 对外集成接口：`/api/open/logistics/...`

这样做的原因是：

- 后台和小程序职责天然不同
- 权限、限流、日志更容易分开控制
- 后面联调时，一眼就知道接口给谁用

示例：

- `/api/admin/logistics/waybills`
- `/api/admin/logistics/waybills/{waybill_no}`
- `/api/admin/logistics/waybills/{waybill_no}/orders`
- `/api/admin/logistics/traces/{trace_no}`
- `/api/admin/logistics/evidences/{evidence_no}`
- `/api/mini/logistics/tasks/current`
- `/api/mini/logistics/waybills/{waybill_no}`
- `/api/mini/logistics/traces`
- `/api/mini/logistics/evidences`
- `/api/open/logistics/dispatch-jobs`
- `/api/open/logistics/events/callback`

## 6.2 路由命名原则

- 必须坚持 RESTful 风格
- 集合名用复数
- 单资源详情用 ID 或业务编号
- 子资源挂在父资源下面
- 不在路径里混入动作词

推荐理解为：

- `GET /resources`：查列表
- `GET /resources/{id}`：查详情
- `POST /resources`：创建
- `PUT /resources/{id}`：整体更新
- `PATCH /resources/{id}`：局部更新
- `DELETE /resources/{id}`：逻辑删除或废弃

不建议：

- `/getTraceList`
- `/uploadImageForWaybill`
- `/doSubmitTrace`

建议写成：

- `POST /api/mini/logistics/traces`
- `POST /api/mini/logistics/evidences`
- `PATCH /api/admin/logistics/waybills/{waybill_no}`

---

## 7. 状态机总原则

统一遵守 5 条原则：

1. `state` 只表达生命周期
2. 状态值尽量少，先简单再扩展
3. 业务节点用 `trace_type`、`biz_type` 表达，不全部塞进 `state`
4. 页面展示可以中文化，但底层状态值必须稳定
5. 优先用短英文，避免长句式状态名

---

## 8. 推荐状态机

## 8.1 执行类对象状态

适用于：

- 波次
- 批次
- 运单
- 调度任务

推荐状态只保留 5 个：

- `new`
- `ready`
- `doing`
- `done`
- `cancel`

说明：

- `new`：新建
- `ready`：待执行
- `doing`：执行中
- `done`：已完成
- `cancel`：已取消

像“装车、到店、签收”这些，不建议放进 `state`，而应该放进：

- `trace_type`
- 时间字段
- 留痕事件记录

## 8.2 留痕事件状态

留痕是业务事实，状态要尽量轻。

推荐状态：

- `new`
- `done`
- `void`

说明：

- `new`：已创建，尚未完成最终提交
- `done`：已生效事实
- `void`：作废，不再参与正常统计

不建议把留痕做成复杂审批流状态机。

## 8.3 证据对象状态

推荐状态：

- `new`
- `ok`
- `bad`
- `del`

说明：

- `new`：已上传，待校验
- `ok`：有效证据
- `bad`：文件损坏、校验失败或规则判定无效
- `del`：逻辑删除

## 8.4 异常对象状态

推荐状态：

- `new`
- `doing`
- `done`
- `cancel`

说明：

- `new`：已发现，待处理
- `doing`：处理中
- `done`：已处理
- `cancel`：误报或取消

## 8.5 规则对象状态

推荐状态：

- `on`
- `off`

---

## 9. 关键枚举值统一口径

## 9.1 `biz_type`

建议统一：

- `wave`
- `batch`
- `waybill`
- `order`

说明：

- 第一阶段留痕主对象优先使用 `batch` 和 `waybill`
- `order` 保留为明细和兼容扩展

## 9.2 `trace_type`

建议第一阶段统一：

- `load`
- `arrive`
- `sign`
- `exception`

## 9.3 `trace_source`

建议统一：

- `admin`
- `mini`
- `system`
- `open`

## 9.4 `evidence_type`

建议统一：

- `image`
- `sign`
- `file`
- `video`
- `other`

## 9.5 `storage_provider`

建议统一：

- `odoo`
- `minio`
- `s3`
- `oss`

---

## 10. 编号规则

## 10.1 基本原则

统一原则如下：

- 数据库主键 `id` 只做内部关联
- 面向人和面向接口的对象尽量有可读业务编号
- 业务编号统一放在 `name` 字段或专用 `*_no` 字段

## 10.2 推荐业务编号

建议对象使用如下前缀：

- 波次：`WV`
- 批次：`BT`
- 运单：`WB`
- 留痕：`TR`
- 证据：`EV`
- 异常：`EX`
- 规则：`RL`

推荐格式：

```text
WV20260410-0001
BT20260410-0001
WB20260410-0001
TR20260410-0001
EV20260410-0001
EX20260410-0001
RL20260410-0001
```

说明：

- 前缀表达对象类型
- 日期表达生成日期
- 序号表达当日顺序

## 10.3 外部访问键

证据对象建议有稳定访问键。

长期推荐统一口径为：

- `evidence_key`

如果首期仍以图片为主，也可兼容：

- `image_access_key`

但中长期建议向 `evidence_key` 收敛，避免未来签名、文档、视频进入系统后名称失真。

## 10.4 请求链路编号

`request_id` 建议格式：

```text
20260410-abc123
```

要求：

- 每次请求唯一
- 可进入日志
- 可用于排障与追踪

---

## 11. 中文展示口径

底层状态值统一用英文稳定值，页面展示统一转中文。

例如：

- `new` -> 新建
- `ready` -> 待执行
- `doing` -> 执行中
- `done` -> 已完成
- `cancel` -> 已取消
- `ok` -> 有效
- `bad` -> 无效
- `on` -> 启用
- `off` -> 停用

不建议把中文直接写成底层状态值，否则后期接口、报表、脚本都会更难维护。

---

## 12. 当前执行要求

从现在开始，所有模块设计文档和接口文档都应该默认遵守下面这些规则：

1. 后台接口统一走 `/api/admin/logistics/...`
2. 小程序/H5 接口统一走 `/api/mini/logistics/...`
3. 对外集成接口统一走 `/api/open/logistics/...`
4. 新模块名必须符合 `logistics_` 前缀规则
5. 新模型名必须符合 `logistics.xxx.yyy` 规则
6. 状态字段统一使用 `state`
7. 业务节点优先放在 `trace_type`、`biz_type`，不要塞满 `state`
8. 编号统一按前缀 + 日期 + 序号生成
9. 页面中文可自由优化，但底层状态值和编号口径不能乱改

---

## 13. 结论

统一命名、状态机和编号规则的目标，不是写得“很规范”，而是为了避免后面出现这些高频返工：

- 前后端字段名对不上
- 模块之间状态口径不一致
- 报表和页面展示口径不同
- 数据库里只能靠 ID 猜对象类型

因此，当前统一结论是：

**接口按后台、小程序、对外集成三层拆开，路径坚持 RESTful，状态值只保留少量短词，页面展示再做中文化。**
