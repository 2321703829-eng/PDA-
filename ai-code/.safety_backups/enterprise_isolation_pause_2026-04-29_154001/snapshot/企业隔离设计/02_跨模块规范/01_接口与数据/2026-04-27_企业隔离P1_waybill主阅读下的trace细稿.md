# 2026-04-27 企业隔离 `P1` `waybill` 主阅读下的 `trace` 细稿

## 1. 文档定位

- 本文是企业隔离 `P1` 小包 A 的现行正式细稿。
- 本文用于替代早先基于 `customer_line` 主阅读入口假设形成的小包 A 讨论稿。
- 本文只回答三件事：
  - `trace_event` 的正式归属保持什么不变
  - `waybill` 页如何承担留痕主阅读入口职责
  - `batch / waybill / trace_event` 三层如何形成稳定联动

## 2. 前置基线

本文默认以下文档为准：

- `../../00_导航与总纲/企业隔离方案可行性与分期落地调整说明.md`
- `../../00_导航与总纲/2026-04-27_企业隔离P1_一运单一门店口径调整说明.md`
- `../../00_导航与总纲/2026-04-27_企业隔离P1_trace_evidence_exception设计推进总纲.md`
- `../04_实施规范/2026-04-27_企业隔离P1_trace_evidence_exception实施清单.md`

当前统一口径：

- 企业之间靠数据库隔离
- 数据主链：`wave -> batch -> waybill -> customer_line -> order_line -> goods_line`
- 页面主阅读入口：`waybill`
- 页面主阅读链：`waybill -> order_line`
- 正式留痕链：`waybill -> trace_event -> evidence -> exception`
- `customer_line` 当前是兼容 / 扩展结构层，不是 `P1` 主阅读入口

## 3. OBB

### Outcome

- `trace_event` 在企业隔离 `P1` 下继续作为正式留痕事实对象存在。
- `waybill` 稳定承担当前 `P1` 的留痕主阅读入口职责。
- `batch / waybill / trace_event` 三层关系清晰，开发与联调时不再混淆“上层上下文”“主阅读页”“正式事件对象”。

### Behavior

- `trace_event` 正式主归属继续围绕 `batch_id / waybill_id`。
- `waybill` 页负责留痕摘要、留痕时间线入口、关键事件回读。
- `batch` 页负责仓侧和装车发车类上层上下文展示。
- `trace_event` 详情页负责单条事件的事实、提交人、时间、备注、证据与异常联动。

### Boundary

- 不把 `customer_line_id` 提升为 `trace_event` 的当前首轮主归属字段。
- 不把 `trace_event` 首轮主归属扩到 `order_line / goods_line`。
- 不在本轮设计 mini/open 端独立留痕录入体系。

## 4. 正式对象归属

### 4.1 不变项

- `logistics.trace.event` 继续是正式留痕对象。
- 主挂点继续使用：
  - `batch_id`
  - `waybill_id`
- `object_type` 当前最小集继续保持：
  - `batch`
  - `waybill`

### 4.2 不应改写的点

- 不能因为页面主阅读入口收口到 `waybill`，就把 `trace_event` 简化成 `waybill` 页上的纯展示行。
- 不能因为保留了 `customer_line` 结构层，就倒推要求 `trace_event` 必须强挂 `customer_line_id`。
- 不能把店侧事实直接绕开 `trace_event` 写进图片或异常对象。

## 5. `waybill` 页的留痕阅读职责

### 5.1 摘要区

`waybill` 页应稳定提供最小留痕摘要区，至少包括：

- 最新留痕时间
- 最新留痕事件类型
- 留痕总数
- 是否存在异常相关留痕
- 最近一次提交人

### 5.2 时间线

`waybill` 页的时间线建议按“当前运单相关事件”统一阅读，首轮至少覆盖：

- `arrive_loading_point`
- `start_loading`
- `finish_loading`
- `departed`
- `arrive_store`
- `deliver_finish`
- `signoff`
- `exception_report`

时间线排序口径建议统一为：

- 先按 `trace_time`
- 再按创建时间或主键兜底

### 5.3 入口动作

`waybill` 页至少提供：

- 查看全部留痕
- 查看最新留痕详情
- 从异常摘要反开相关留痕
- 从证据摘要反开相关留痕

首轮不要求：

- 在 `customer_line` 页复制同等级别的留痕入口
- 在 `order_line` 页直接承接留痕时间线

## 6. `batch / waybill / trace_event` 三层联动

### 6.1 `batch` 的职责

- 承接仓侧与装车发车类上层上下文
- 作为一批运单共享的作业现场容器
- 允许从 `batch` 反读当前批次下的相关 `trace_event`

### 6.2 `waybill` 的职责

- 承接当前 `P1` 下的主阅读入口职责
- 汇总本运单相关的留痕、证据、异常摘要
- 把批次侧作业上下文和运单侧门店交付上下文接起来

### 6.3 `trace_event` 的职责

- 承接单条事实事件
- 作为证据和异常的正式联动锚点
- 保留可审计、可追溯、可回读的最小事实粒度

### 6.4 联动规则

- `batch -> trace_event`：读取批次侧作业事件
- `waybill -> trace_event`：读取当前运单完整事件视图
- `trace_event -> waybill / batch`：详情页可稳定回跳
- `trace_event -> evidence / exception`：详情页可稳定查看相关证据与相关异常

## 7. 与 `customer_line` 的边界

- `customer_line` 当前保留为结构层，不承担主阅读入口职责。
- 如店侧导入、图片命中、结构快照需要使用 `customer_line`，应视为辅助映射层，而不是留痕主读层。
- 如后续业务重新开放“一运单多门店”能力，再另起补充稿讨论是否恢复节点级主阅读层。

## 8. 权限与校验

租户内至少区分三类留痕动作：

- 查看
- 提交
- 处理

校验分层建议：

- 页面层：控制入口显隐与只读态
- 接口层：校验请求来源、参数完整性、权限前提
- 模型层：校验角色、状态、对象归属和可写条件

默认约束：

- 只读当前租户库数据
- 不做跨库留痕汇总
- 不允许仅靠页面隐藏替代真实权限边界

## 9. 开发与联调重点

- 先稳 `trace_event` 的对象归属与最小字段口径
- 再稳 `waybill` 页的摘要区、时间线和入口动作
- 再打通 `batch / waybill / trace_event` 回跳关系
- 最后再接证据和异常

## 10. 一句话结论

当前企业隔离 `P1` 下，`trace` 的正确做法不是把正式对象层改写，而是继续让 `trace_event` 保持正式归属稳定，并由 `waybill` 稳定承担主阅读入口职责。
