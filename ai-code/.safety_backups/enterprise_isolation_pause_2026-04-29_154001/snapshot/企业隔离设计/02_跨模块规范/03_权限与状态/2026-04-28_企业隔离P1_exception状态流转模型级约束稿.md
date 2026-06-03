# 2026-04-28 企业隔离 `P1` `exception` 状态流转模型级约束稿

## 1. 文档定位

- 本文用于把企业隔离 `P1` 下 `exception` 的状态流转要求进一步压成模型级约束稿。
- 本文重点不是讲页面怎么点按钮，而是讲模型层必须兜住哪些规则。
- 本文直接服务于 `logistics_trace_exception` 模块编码和联调。

本文主要回答：

- `state` 的真实来源和合法值是什么
- 新建异常时模型层允许什么、不允许什么
- 各状态之间模型层允许怎么流转
- 进入最终态前必须满足哪些条件
- 处理日志、`closed_time`、关联对象如何由模型层兜底

## 2. 前置基线

本文以前置文档与当前代码为准：

- `../01_接口与数据/2026-04-27_企业隔离P1_exception状态流转与详情联动细稿.md`
- `../04_实施规范/2026-04-27_企业隔离P1_开发任务拆分单_v2.md`
- `custom_addons/logistics_trace_exception/models/logistics_trace_exception.py`
- `custom_addons/logistics_trace_exception/models/logistics_trace_exception_process_log.py`

## 3. OBB

### Outcome

- 异常状态流转在模型层可校验、可追溯、可复现。
- 即使页面按钮或接口入口控制失误，模型层仍能拦住非法状态变更。
- 异常过程日志和关闭时间不依赖人工填写，而由模型层统一生成和维护。

### Behavior

- 新建异常只允许从合法初始状态进入。
- 状态流转必须命中预定义迁移矩阵。
- 最终态必须满足关闭摘要等硬条件。
- 处理日志由系统自动生成，不允许普通用户手工改写。

### Boundary

- 本文只覆盖单个租户库内的异常状态机。
- 本文不扩展到平台级到期、降级、只读状态机。
- 本文不扩展到完整工单平台的 SLA、审批链、转派链。

## 4. 当前模型层真实状态口径

### 4.1 当前状态枚举

当前代码中的 `state` 枚举为：

- `draft`
- `open`
- `processing`
- `resolved`
- `closed`
- `cancelled`

### 4.2 当前设计解释

当前 `P1` 的用户侧最小主流口径仍建议理解为：

- `draft`
- `open`
- `processing`
- `resolved`
- `closed`

但模型层当前已经存在：

- `cancelled`

因此本稿建议这样收口：

- `cancelled` 继续保留为模型兼容态
- 它可以作为技术上允许的最终态
- 但它不是当前 `P1` 首轮标准业务主路径
- 首轮页面主按钮链仍优先围绕 `open -> processing -> resolved -> closed`

## 5. 新建约束

### 5.1 允许的新建初始状态

模型层新建仅允许：

- `draft`
- `open`

不允许新建时直接进入：

- `processing`
- `resolved`
- `closed`
- `cancelled`

### 5.2 新建时禁止手工写的字段

模型层应禁止在创建时手工传入：

- `closed_time`

原因：

- `closed_time` 属于最终态派生字段
- 必须由状态流转统一生成

### 5.3 新建时对象引用自动补齐

当前模型层已具备并建议继续保留：

- 传入 `trace_event_id` 且未传 `waybill_id` 时，自动补 `waybill_id`
- 同时优先补 `batch_id`
- 传入 `waybill_id` 且未传 `batch_id` 时，自动补 `batch_id`

这条规则的目的不是偷懒，而是保证异常对象不会脱离正式主对象上下文漂浮。

## 6. 状态迁移矩阵

### 6.1 当前建议矩阵

当前模型层建议继续使用如下矩阵：

| 当前状态 | 允许流向 |
| --- | --- |
| `draft` | `open`、`cancelled` |
| `open` | `processing`、`resolved`、`cancelled` |
| `processing` | `resolved`、`closed`、`cancelled` |
| `resolved` | `processing`、`closed`、`cancelled` |
| `closed` | 无 |
| `cancelled` | 无 |

### 6.2 模型层约束要求

- 任何不在矩阵中的流转，模型层必须直接报错
- 相同状态写回自身可放过，但不应产生伪流转日志
- `closed` 和 `cancelled` 进入后，不允许再打开

### 6.3 当前 `P1` 的设计说明

这里有两点要刻意说明：

- `open -> resolved` 当前仍保留，适合轻量场景直接确认问题已解决
- `resolved -> processing` 当前也保留，适合“已解决后又被打回继续处理”的场景

这两条都属于当前代码与设计可以接受的 `P1` 简化路径，不必首轮再人为删掉。

## 7. 最终态约束

### 7.1 最终态定义

当前模型层最终态为：

- `closed`
- `cancelled`

### 7.2 进入最终态前的硬条件

模型层必须保证：

- `close_summary` 非空

也就是说：

- 关闭前必须有处理结论
- 取消前也必须有取消说明或最终说明

### 7.3 `closed_time` 规则

模型层应继续保持：

- 进入最终态时自动写入 `closed_time`
- 非状态迁移路径不允许手工修改 `closed_time`

补充建议：

- 当前代码已经实现“进入最终态自动写时间”
- 后续如果允许撤销最终态，再单独讨论是否清理 `closed_time`
- 在当前 `P1` 下，不讨论最终态回退，因此不需要扩展这条规则

## 8. 处理日志约束

### 8.1 日志对象

过程日志对象继续使用：

- `logistics.trace.exception.process.log`

### 8.2 自动生成规则

模型层建议继续自动生成三类日志：

- `create`
- `state_change`
- `note`

### 8.3 生成触发时机

- 新建异常后自动写一条 `create`
- 状态变化后自动写一条 `state_change`
- `remark` 或 `close_summary` 改变但状态未变时，自动写一条 `note`

### 8.4 日志只读约束

普通用户不允许：

- 手工创建处理日志
- 手工改写处理日志
- 手工删除处理日志

这条约束当前代码已经通过 `sudo` 生成和 `AccessError` 限制基本体现，建议继续保留。

## 9. 关联对象约束

### 9.1 正式主挂点

异常对象继续优先围绕：

- `waybill_id`
- `batch_id`
- `trace_event_id`

### 9.2 模型层一致性要求

建议模型层继续保证：

- 如果有 `trace_event_id`，则 `waybill_id` 不应与其所属 `waybill` 冲突
- 如果有 `waybill_id`，则 `batch_id` 不应与其所属 `batch` 冲突

当前代码已具备基础自动补齐逻辑，但还没有把“冲突校验”单独收成强约束；这条建议应作为后续实现补强项。

### 9.3 不应允许的挂点漂移

模型层不应放开：

- 把异常主挂到 `customer_line`
- 把异常主挂到 `order_line`
- 让异常脱离 `waybill / batch / trace_event` 漂浮存在

## 10. 页面动作与模型动作的对应关系

当前标准对象方法可继续理解为：

- `action_mark_processing` -> 写入 `state=processing`
- `action_mark_resolved` -> 写入 `state=resolved`
- `action_mark_closed` -> 写入 `state=closed`

这三类按钮动作都只是页面入口，真正是否允许，仍由模型层的：

- 迁移矩阵校验
- 最终态校验
- 日志生成规则

共同兜底。

## 11. 当前代码与设计的对齐结论

### 11.1 已基本对齐

- 只允许 `draft / open` 作为初始状态
- `closed_time` 受模型层管理
- 最终态要求 `close_summary`
- 过程日志系统生成
- `closed / cancelled` 不可再流转

### 11.2 需要在后续编码时继续补强

- 把 `trace_event / waybill / batch` 的冲突关系做成更明确的模型校验
- 把“谁能关闭、谁能跟进”的角色判断继续从页面层下沉到更清晰的模型层校验
- 如后续保留 `cancelled`，应明确它的页面入口是否开放；若不开，则继续作为兼容态保留

## 12. 一句话收口

这份模型级约束稿的核心，是把异常状态流转从“页面怎么点”收口为“模型层必须拦什么、自动补什么、自动记什么”，这样后续编码才不会只停留在按钮显隐层面。
