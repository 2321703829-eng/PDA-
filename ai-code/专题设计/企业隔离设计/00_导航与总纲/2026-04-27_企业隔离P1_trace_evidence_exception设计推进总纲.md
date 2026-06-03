# 2026-04-27 企业隔离 `P1` trace / evidence / exception 设计推进总纲

## 1. 文档目标

- 本文用于把企业隔离专题当前这轮设计工作收口成统一推进口径。
- 本文只覆盖企业隔离 `P1`，不扩展到 `P2 / P3` 平台控制面、套餐、跨租户汇总和商用运营能力。
- 本文的作用不是直接替代各 addon 详细设计，而是先把这轮设计的总边界、三块 OBB、差距盘点方法、设计拆包和开发拆分顺序锁定。

## 2. 本轮总边界

### 2.1 阶段边界

- 只做企业隔离 `P1`。
- 不碰 `P2 / P3`。
- 不把当前物流项目拉回平台级 SaaS 总设计。

### 2.2 统一口径

- 企业之间靠数据库隔离。
- 同一企业内部如有多个法人或公司，才考虑 `multi-company`。
- 租户内执行与数据主链统一按：
  - `wave -> batch -> waybill -> customer_line -> order_line -> goods_line`
- 页面主阅读入口统一按：
  - `waybill`
- 页面主阅读链统一按：
  - `waybill -> order_line`
- 图片业务阅读统一围绕：
  - `waybill`
- 正式证据对象统一围绕：
  - `trace_event`
- 异常主挂点统一优先围绕：
  - `waybill / batch / trace_event`
- `customer_line` 在当前 `P1` 下按“一运单一门店”强约束收口为兼容 / 扩展结构层

### 2.3 本轮不做

- 不新增 `tenant_plan / tenant_feature_snapshot / tenant_job` 一类平台表。
- 不设计跨租户汇总报表、套餐控制、到期降级、自动开租户。
- 不把 `trace / evidence / exception` 重写成另一套 `tms_*` 对象体系。
- 不把 `customer_line` 提升成正式 `trace_event` 主归属对象。
- 不把图片正式主挂点改成 `order_line` 或纯 `customer_line`。

## 3. 设计推进顺序

1. 先锁总边界。
2. 再锁 `trace / evidence / exception` 的 OBB。
3. 再按“已有 / 缺失 / 口径冲突 / 可以后置”做差距盘点。
4. 再按四个小包补设计小稿。
5. 等小稿稳定后，再转成开发任务拆分。
6. 最后按固定联调顺序推进。

## 4. 三块 OBB

## 4.1 `trace`

### Outcome

- 每个租户库都能独立安装并运行 `logistics_trace_core`。
- `trace_event` 继续作为正式留痕事实对象存在，承担 `batch / waybill` 现场事件留痕。
- `waybill` 与 `batch` 能稳定阅读留痕摘要，且 `waybill` 继续承担门店级主阅读职责。

### Behavior

- 页面怎么读：
  - `waybill` 详情页继续保留留痕摘要、时间线和入口。
  - `batch` 继续作为装车、发车、仓侧事实的上层上下文。
  - `customer_line` 当前只承担结构、快照与兼容层职责，不作为主阅读入口。
- 数据怎么挂：
  - `logistics.trace.event` 正式主挂点仍是 `batch_id / waybill_id`。
  - `object_type` 首轮只保留 `batch / waybill`。
  - 到店、签收、异常上报等店侧事件，仍通过 `waybill + 业务映射规则` 关联回门店节点阅读链。
- 权限怎么控：
  - 至少区分查看、提交、处理三类动作。
  - 新增和改写动作必须在模型层校验，不只靠按钮显示控制。
  - 默认只读当前租户库数据，不写任何跨库读写逻辑。

### Boundary

- 不把 `customer_line_id` 直接做成 `trace_event` 首轮强主键。
- 不在 `P1` 内扩展跨租户留痕总览。
- 不在本轮顺手重做 mini/open 端留痕接口体系。

## 4.2 `evidence`

### Outcome

- 每个租户库都能独立安装并运行 `logistics_trace_evidence`。
- 图片业务阅读链在当前 `P1` 下统一收口到 `waybill` 主阅读入口。
- 正式证据对象继续围绕 `trace_event` 组织，不被页面阅读链反向带偏。

### Behavior

- 页面怎么读：
  - `waybill` 是图片主阅读入口，并承担证据摘要、汇总和导出入口。
  - `customer_line` 如保留页面入口，仅作为辅助结构信息，不承担主阅读职责。
  - 证据详情仍可反读关联 `trace_event` 和异常。
- 数据怎么挂：
  - `logistics.trace.evidence.trace_event_id` 必填，继续作为正式主挂点。
  - 图片命中规则优先按 `waybill_no + customer_line_no`，兜底按 `waybill_no + store_no`。
  - 如需补链，顺序必须是“先命中 `customer_line`，再关联到对应 `trace_event`”。
- 权限怎么控：
  - 至少区分预览、导出、审计三类能力。
  - 结果页、预览页、导出动作都要重复校验当前租户和当前用户权限。
  - 图片导入必须继续走 `import_task.object_type = image_package` 的独立审计链。

### Boundary

- 不把图片正式主挂点改成 `customer_line` 或 `order_line`。
- 不允许通过门店名称、地址自由猜测命中目标对象。
- 不在本轮把图片长期存储方案扩展成完整对象存储平台设计。

## 4.3 `exception`

### Outcome

- 每个租户库都能独立安装并运行 `logistics_trace_exception`。
- 异常对象、状态流转、处理日志和证据反读链形成最小闭环。
- 异常详情能稳定回到 `waybill / batch / trace_event / evidence` 上下文。

### Behavior

- 页面怎么读：
  - `waybill` 详情继续保留异常摘要和入口。
  - `customer_line` 当前不作为异常主阅读入口，但可在需要时保留辅助上下文展示。
  - 异常详情页可反读关联运单、批次、留痕和证据摘要。
- 数据怎么挂：
  - `logistics.trace.exception` 正式主挂点仍优先围绕 `waybill / batch / trace_event`。
  - `process_log` 继续作为最小处理留痕对象。
  - 首轮不把异常默认挂到 `order_line`。
- 权限怎么控：
  - 至少区分提报、跟进、关闭、只读四类动作。
  - 状态流转在模型层校验，不只靠前端按钮。
  - 历史异常可读，写动作受角色和状态约束。

### Boundary

- 不在 `P1` 内把异常做成完整工单平台。
- 不在本轮扩展到跨租户异常汇总。
- 不在本轮引入套餐到期、只读降级一类平台状态机。

## 5. 四个设计小包

## 5.1 `trace` 事件对象与页面阅读链

- 只回答：`trace_event` 的正式归属、`waybill` 主阅读入口和辅助结构层怎么落。

## 5.2 `evidence` 图片命中、补链、导出与审计

- 只回答：图片如何命中 `customer_line`、如何补到 `trace_event`、如何保留 `image_package` 审计链。

## 5.3 `exception` 状态流转、详情联动、权限

- 只回答：异常状态流、详情联动、证据反读和角色控制怎么落。

## 5.4 三层联动与租户内角色边界

- 只回答：`trace / evidence / exception` 三层如何连起来，以及租户内查看、提交、处理、导出等角色如何切开。

## 6. 固定联调顺序

1. 先 `trace_core`
2. 再 `evidence`
3. 再 `exception`
4. 最后做三层联动回归

原因：

- `evidence` 依赖 `trace_event` 挂点稳定。
- `exception` 依赖 `trace_event` 与证据反读稳定。
- 三层联动回归必须放在最后做整体口径验证。

## 7. 本轮设计产物

- `00_导航与总纲/2026-04-27_企业隔离P1_trace_evidence_exception设计推进总纲.md`
- `02_跨模块规范/04_实施规范/2026-04-27_企业隔离P1_trace_evidence_exception差距盘点表.md`
- `02_跨模块规范/04_实施规范/2026-04-27_企业隔离P1_trace_evidence_exception设计小稿拆分与开发任务单.md`

## 8. 使用方式

- 先读本文，锁定本轮设计边界。
- 再读差距盘点表，确认当前代码和页面的真实起点。
- 再按设计小包和开发任务单推进补稿、拆单和联调。
