# 2026-04-27 企业隔离 `P1` trace 事件对象归属与 `customer_line` 反读链细稿

## 状态说明

- 本文形成于“`customer_line` 计划作为 `P1` 主阅读入口”的讨论阶段，是当时小包 A 的首份细稿。
- 2026-04-27 已确认当前业务按“一运单一门店”强约束收口后，本文不再作为当前 `P1` 小包 A 的现行口径细稿。
- 2026-04-28 已从“接口与数据”正式目录移入“来源资料与历史草图”目录。
- 本文保留为历史讨论留痕，可用于回看“正式对象归属”和“页面阅读入口”曾经如何拆分。
- 当前现行口径请优先阅读：
  - `../00_导航与总纲/2026-04-27_企业隔离P1_一运单一门店口径调整说明.md`
  - `../00_导航与总纲/2026-04-27_企业隔离P1_trace_evidence_exception设计推进总纲.md`

## 1. 文档定位

- 本文是企业隔离 `P1` 下小包 A 的首份正式细稿。
- 本文只回答两件事：
  - `trace_event` 的正式对象归属如何锁定
  - `customer_line` 如何承担门店节点主阅读入口，并稳定反读留痕上下文
- 本文不扩展到 `evidence / exception` 全量设计，不扩展到 `P2 / P3` 平台能力。

## 2. 前置基线

本文默认以前提一致的 4 份文档为准：

- `专题设计/企业隔离设计/00_导航与总纲/2026-04-27_企业隔离P1_trace_evidence_exception设计推进总纲.md`
- `专题设计/企业隔离设计/02_跨模块规范/04_实施规范/2026-04-27_企业隔离P1_trace_evidence_exception差距盘点表.md`
- `专题设计/前端设计/四期前端优化设计/00_导航与总纲/2026-04-21_四期页面信息架构与阅读链方案.md`
- `专题设计/前端设计/四期前端优化设计/01_专题方案/2026-04-21_四期门店节点阅读区结构草案.md`

当前统一业务口径继续使用：

- 企业之间靠数据库隔离
- 主链：`wave -> batch -> waybill -> customer_line -> order_line -> goods_line`
- 页面主阅读链：`waybill -> customer_line -> order_line`
- 图片阅读链：`waybill -> customer_line -> 图片预览 / 留痕 / 证据`
- 正式证据对象围绕 `trace_event`
- 异常优先围绕 `waybill / batch / trace_event`

## 3. OBB

### Outcome

- `trace_event` 在企业隔离 `P1` 下继续作为正式留痕事实对象，且主归属不被页面阅读链带偏。
- `customer_line` 成为门店节点级留痕主阅读入口，但不替代 `trace_event` 的正式归属层。
- 开发和联调时，团队能区分“正式对象归属”和“页面主阅读入口”这两层职责。

### Behavior

- 正式留痕对象继续围绕 `batch / waybill`。
- 门店节点页可反读与本节点相关的到店、签收、异常上报等事件摘要。
- 反读链默认通过 `waybill + customer_line 业务上下文` 建立，不直接要求 `trace_event` 首轮强挂 `customer_line_id`。
- 权限上，查看、提交、处理动作继续在模型层做最终校验。

### Boundary

- 不把 `customer_line_id` 直接加成 `trace_event` 首轮强主归属字段。
- 不在本轮为 `trace_event` 增加 `order_line` 或 `goods_line` 主归属。
- 不把 `customer_line` 页扩成独立留痕录入终端方案。

## 4. 当前现实

## 4.1 已存在的正式对象层

当前代码已经具备稳定的正式留痕对象骨架：

- `custom_addons/logistics_trace_core/models/logistics_trace_event.py`
  - 模型：`logistics.trace.event`
  - 正式主挂点：`batch_id / waybill_id`
  - `object_type`：只支持 `batch / waybill`
  - 现有事件类型已覆盖：
    - `arrive_loading_point`
    - `start_loading`
    - `finish_loading`
    - `departed`
    - `arrive_store`
    - `deliver_finish`
    - `signoff`
    - `exception_report`

## 4.2 已存在的页面阅读层

当前代码也已经具备稳定的门店节点对象页：

- `custom_addons/logistics_dispatch/views/logistics_dispatch_waybill_views.xml`
  - `waybill` 页已具备 `customer_line` 入口
  - `customer_line` 已有 list / form / search
  - `customer_line` 页已经展示门店名称、地址、停靠顺序、货物明细等主阅读信息

这说明本轮缺口不是“重新造对象”，而是“把留痕阅读职责正确挂进现有门店节点页”。

## 5. 正式对象归属结论

## 5.1 为什么 `trace_event` 不能改成 `customer_line` 主归属

原因有 5 个：

1. 当前仓侧事实天然以 `batch / waybill` 为主上下文。  
   例如到仓、装车、发车这类事件，不属于某一个门店节点。

2. 当前 `logistics.trace.event` 已经围绕 `batch / waybill` 形成模型约束和状态逻辑。  
   直接改主归属会破坏现有 `object_type`、`batch_id / waybill_id` 校验和 waybill 聚合逻辑。

3. `customer_line` 是门店节点阅读层，不是天然的全部留痕事实归属层。  
   它适合承接“和某个门店节点相关的阅读上下文”，不适合把所有留痕对象都压到自己下面。

4. 后续 `evidence` 与 `exception` 都已经围绕 `trace_event` 建骨架。  
   如果现在把 `trace_event` 主归属改掉，会连带打散后续两层。

5. 企业隔离 `P1` 的目标是稳定租户化，不是重做追溯对象体系。  
   本轮应该优先保住现有对象骨架，再补门店节点反读链。

## 5.2 本轮正式归属结论

企业隔离 `P1` 下，`trace_event` 正式归属继续锁定为：

- `batch` 级事件：
  - 主归属 `batch_id`
  - `waybill_id` 为空
- `waybill` 级事件：
  - 主归属 `waybill_id`
  - `batch_id` 与运单所属批次保持一致

首轮不新增：

- `customer_line_id` 正式强归属
- `order_line_id` 正式强归属
- `goods_line_id` 正式强归属

## 5.3 `customer_line` 在这套结构里的角色

`customer_line` 的角色不是“留痕主对象”，而是：

- 门店节点主阅读入口
- 店侧事实反读入口
- 图片、留痕、证据、订单归属的阅读汇聚点

一句话收口：

**`trace_event` 负责正式记事实，`customer_line` 负责把和本门店节点有关的事实读出来。**

## 6. `customer_line` 反读链设计

## 6.1 反读链目标

在不改 `trace_event` 正式归属的前提下，让门店节点页能稳定看到与当前节点相关的留痕摘要。

## 6.2 反读链的最小输入

当前 `customer_line` 已天然具备反读所需上下文：

- `waybill_id`
- `customer_line_no`
- `partner_id`
- `store_no`
- `stop_seq_in_waybill`
- 门店联系人与地址快照

这意味着 `customer_line` 已经可以作为“留痕阅读查询条件”的稳定起点。

## 6.3 反读链分层

### 第一层：强归属反读

直接通过 `waybill_id` 读取该运单下所有 `trace_event`。

用途：

- 运单级时间线
- 运单级留痕总数
- 运单级最新留痕摘要

这层继续由 `waybill` 页主读。

### 第二层：门店节点过滤反读

在 `waybill` 范围内，再按门店节点业务上下文筛选“与当前 `customer_line` 有关”的事件。

首轮只纳入以下事件进入门店节点留痕阅读区：

- `arrive_store`
- `deliver_finish`
- `signoff`
- `exception_report`

可选纳入但不首轮强制：

- 未来若出现明确的门店节点级补充事件类型，再单独加白名单

### 第三层：摘要化反读

`customer_line` 页首轮不直接复制整条运单时间线，而是优先展示：

- 最新相关留痕
- 相关留痕数
- 是否已有到店留痕
- 是否已有签收留痕
- 是否存在异常相关留痕

这样可以避免把 `customer_line` 页做成第二个运单页。

## 6.4 门店节点相关事件的判定规则

首轮判定规则按“从稳到弱”分 3 级：

### A 级：后续明确补字段的直接命中

如果后续在服务层或辅助映射层有稳定的 `customer_line` 命中结果，则优先按该结果反读。

特点：

- 最稳定
- 最适合后续和图片、证据、异常联动

### B 级：按 `waybill + store` 上下文命中

若事件录入或来源数据中存在稳定的门店标识，可按：

- `waybill_id`
- `partner_id / store_no`

进行反读命中。

特点：

- 比全文本匹配稳
- 不要求改 `trace_event` 主归属

### C 级：按事件类型进入节点摘要

在没有更强命中结果前，`arrive_store / signoff / exception_report` 这类明显是店侧语义的事件，可先进入门店节点摘要区。

限制：

- 只允许用于首轮阅读摘要
- 不允许作为后续正式证据或异常归属的唯一依据

## 6.5 首轮推荐做法

企业隔离 `P1` 首轮推荐做法：

1. 先保留 `trace_event` 正式主挂点不变。
2. 在读取 `customer_line` 留痕摘要时，先从 `waybill_id` 范围内读事件。
3. 首轮只对白名单店侧事件做节点摘要反读。
4. 后续若图片包或证据补链已稳定，再把 `customer_line` 命中结果接入更强反读。

## 7. 页面职责分工

## 7.1 `waybill` 页职责

- 继续承担运单级时间线主视图
- 展示全运单留痕摘要
- 作为留痕总入口
- 不负责替代门店节点局部阅读

## 7.2 `customer_line` 页职责

- 展示本门店节点的店侧留痕摘要
- 展示与本节点相关的到店、签收、异常上报上下文
- 作为门店节点级图片 / 留痕 / 证据主阅读入口
- 不重做完整运单级时间线

## 7.3 `batch` 页职责

- 继续承担仓侧、装车、发车等上游事实的批次上下文
- 不承担门店节点阅读职责

## 8. 首轮字段与实现建议

## 8.1 首轮不建议直接改的字段

- 不建议在 `logistics.trace.event` 上直接新增 `customer_line_id` 作为强必填字段
- 不建议扩展 `object_type = customer_line`
- 不建议在 `trace_event` 上堆一批仅页面使用的弱文本字段当正式归属

## 8.2 首轮可接受的实现方向

- 在 `customer_line` 侧增加只读聚合字段或服务层聚合方法，用于：
  - `related_trace_count`
  - `latest_trace_time`
  - `latest_trace_type`
  - `latest_trace_summary`
  - `arrive_store_trace_status`
  - `signoff_trace_status`
  - `has_exception_trace`
- 在动作层增加：
  - `action_open_related_trace_events`

注意：

- 这些都属于“反读辅助层”
- 不应被写回成 `trace_event` 的正式主归属替代品

## 8.3 服务层建议

如后续实现需要单独查询封装，建议统一收口为：

- 输入：
  - `customer_line.id`
  - 或 `waybill_id + customer_line_no`
- 输出：
  - 当前节点相关留痕摘要
  - 当前节点相关留痕列表

不要一开始就做成：

- 跨库汇总服务
- 平台级租户中心服务
- 套餐能力控制服务

## 9. 权限与动作边界

## 9.1 查看

- `customer_line` 页可见留痕摘要，不代表用户可编辑留痕
- 门店节点页的留痕入口默认服从当前 trace 查看权限

## 9.2 提交

- 留痕提交动作继续走 `trace_event` 的模型校验
- 即便以后从门店节点页发起录入，也不能绕过 `trace_event` 模型层权限

## 9.3 处理

- 留痕状态、失效、修正等动作继续围绕 `trace_event`
- 不在 `customer_line` 层新增另一套处理状态机

## 10. 验收口径

补完小包 A 后，至少满足下面 6 条：

1. `trace_event` 正式主归属仍是 `batch / waybill`
2. `customer_line` 已成为门店节点级留痕主阅读入口
3. `customer_line` 页可反读相关到店、签收、异常上报事件摘要
4. `waybill` 页仍保留运单级留痕总入口
5. 没有新增第二套留痕主对象体系
6. 没有把页面阅读链误写成正式对象归属链

## 11. 本轮明确不做

- 不把 `customer_line` 变成正式 `trace_event` 主归属
- 不重写 `logistics_trace_core` 事件枚举体系
- 不扩写 `evidence / exception` 细稿
- 不进入 `P2 / P3` 平台设计

## 12. 下一步建议

小包 A 细稿稳定后，下一步应顺着这份文档继续补两类材料：

1. `customer_line` 页留痕摘要区和“查看相关留痕”入口的页面细稿
2. `trace_event` 到 `evidence` 的补链规则，也就是小包 B
