# 2026-04-27 企业隔离 `P1` trace / evidence / exception 实施清单

## 1. 文档定位

- 本文用于把企业隔离专题下 `P1` 范围内的 `trace / evidence / exception` 实施动作收口成可执行清单。
- 本文只覆盖“每个租户数据库安装同一套现有物流模块后，如何保持留痕、证据、异常三层可用且不偏离当前前端主链”。
- 本文不扩展到：
  - 平台控制面
  - 自动开租户
  - 跨租户汇总
  - 套餐自动同步
  - 商用运营增强

## 2. 当前基线

实施时统一以以下文档为准：

- `专题设计/企业隔离设计/00_导航与总纲/企业隔离方案可行性与分期落地调整说明.md`
- `docs/architecture/logistics_trace_core_addon_design.md`
- `docs/architecture/logistics_trace_evidence_addon_design.md`
- `docs/architecture/logistics_trace_exception_addon_design.md`
- `专题设计/前端设计/四期前端优化设计/00_导航与总纲/2026-04-20_四期前端优化设计总纲.md`
- `专题设计/前端设计/四期前端优化设计/00_导航与总纲/2026-04-21_四期页面信息架构与阅读链方案.md`
- `专题设计/前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/2026-04-21_四期图片模块字段与校验规则清单.md`
- `专题设计/前端设计/四期前端优化设计/02_跨模块规范/02_交互与组件/2026-04-21_四期图片模块前端交互与结果反馈方案.md`

## 3. OBB

### 3.1 Outcome

- 每个租户数据库可以独立安装并运行 `logistics_trace_core`、`logistics_trace_evidence`、`logistics_trace_exception`。
- 留痕、证据、异常三层与当前 `waybill` 主阅读入口和 `order_line` 业务明细阅读链兼容。
- 图片导入、图片阅读、异常处理继续围绕 `waybill` 主阅读入口稳定成立，同时不打坏 `customer_line` 的结构层职责。

### 3.2 Behavior

- 留痕层继续围绕 `batch / waybill` 承接事实事件。
- 证据层正式挂在 `trace_event` 下，前端图片业务阅读优先围绕 `waybill`，命中与补链仍可借助 `customer_line`。
- 异常层继续优先挂在 `waybill / batch / trace_event`，并可从异常详情反读关键留痕与关键证据。

### 3.3 Boundary

- 本文不冻结 `trace / evidence / exception` 的跨租户平台表。
- 本文不定义 `P2 / P3` 的套餐、能力快照和平台任务状态机。
- 本文不替代各 addon 正式设计稿，只负责企业隔离 `P1` 落地时的最小实施闭环。

## 4. 实施总原则

- 不同企业之间仍以数据库级隔离为前提，不用 `multi-company` 替代企业隔离。
- 不为企业隔离重起另一套 `tms_*` 主对象体系。
- 在“一运单一门店”强约束下，将 `customer_line` 收口为兼容 / 扩展结构层，不再要求其承担 `P1` 主阅读入口职责。
- 不把图片证据直接主挂到订单上。
- 不把 `image_package` 与 `dispatch_main` 混成同一任务对象类型。
- 关键权限不能只做页面隐藏，模型层、接口层、记录规则层都要校验。

## 5. 前置检查清单

- [ ] 多数据库底盘已验证可用，目标租户库可独立访问。
- [ ] 目标租户库已安装 `logistics_base`、`logistics_dispatch`。
- [ ] 租户库内 `waybill / customer_line / order_line / goods_line` 主链可正常读取。
- [ ] 四期图片导入任务链已明确区分 `dispatch_main` 与 `image_package`。
- [ ] 企业隔离专题当前口径已同步到四期前端最新基线。

## 6. `logistics_trace_core` 实施清单

### 6.1 模块与依赖

- [ ] 清点 `logistics_trace_core` 对 `logistics_dispatch` 的依赖是否只使用当前有效对象。
- [ ] 确认模块不反向强依赖 `evidence`、`exception` 才能安装。
- [ ] 确认每个租户库可单独安装、升级和回滚该模块。

### 6.2 对象与字段

- [ ] 明确 `logistics.trace.event` 仍以 `batch_id / waybill_id` 为主归属。
- [ ] 明确 `object_type` 最小只支持 `batch`、`waybill`，不引入 `order`。
- [ ] 清点 `event_type` 是否覆盖仓侧与店侧最小闭环：
  - `arrive_loading_point`
  - `start_loading`
  - `finish_loading`
  - `departed`
  - `arrive_store`
  - `deliver_finish`
  - `signoff`
  - `exception_report`
- [ ] 统一 `trace_time / submit_user / remark / is_exception / source_channel` 等基础字段口径。

### 6.3 页面与阅读链

- [ ] 运单详情页可读当前运单关联留痕摘要。
- [ ] 批次详情页可读当前批次关联留痕摘要。
- [ ] `waybill` 详情页的门店级事实展示不应绕过留痕层定义事件上下文。
- [ ] 留痕时间线页与详情区命名仍围绕 `waybill` 和 `batch`，不重新抬高 `order_line`。

### 6.4 权限与数据范围

- [ ] 租户内角色至少区分查看、提交、处理三类能力。
- [ ] 留痕新增动作在模型层校验用户角色，不只靠按钮可见性。
- [ ] 留痕查询默认只读当前租户数据库，不写任何跨租户聚合逻辑。
- [ ] 如存在司机、仓库、客服等角色差异，需明确谁能新增哪类 `event_type`。

### 6.5 与 `customer_line` 的映射边界

- [ ] 保持 `waybill` 作为当前 `P1` 门店级主阅读入口，不再把 `customer_line` 设为必经阅读入口。
- [ ] 不把 `customer_line` 直接写成 `trace_event` 主归属字段。
- [ ] 如店侧事件需要回读门店节点，应通过 `waybill + 业务快照 / 查询规则` 间接建立上下文。

## 7. `logistics_trace_evidence` 实施清单

### 7.1 模块与依赖

- [ ] 清点 `logistics_trace_evidence` 仅依赖 `logistics_trace_core`，不反向耦合异常层。
- [ ] 确认每个租户库可单独安装该模块，并能读取本租户内图片元数据。

### 7.2 对象与字段

- [ ] 明确 `logistics.trace.evidence.trace_event_id` 为主归属且必填。
- [ ] 明确 `waybill_id / batch_id` 只作为冗余查询或 related/store 字段，不替代 `trace_event_id`。
- [ ] 清点首轮 `evidence_type`、`storage_status` 枚举是否足够支撑当前页面与结果反馈。
- [ ] 保留 `image_access_key` 唯一性和外部存储元数据字段边界。

### 7.3 图片导入与图片阅读

- [ ] 企业隔离 `P1` 下，图片导入任务仍按 `import_task.object_type = image_package` 进入审计链。
- [ ] 图片包命中规则继续保持：
  - `waybill_no + customer_line_no`
  - 兜底 `waybill_no + store_no`
- [ ] 不允许通过门店名称、地址自由猜测命中目标。
- [ ] 运单页继续承担图片主阅读、汇总与导出入口。
- [ ] `customer_line` 如保留页面入口，仅承担结构信息与兼容层职责，不与 `waybill` 争主阅读入口。

### 7.4 业务挂点与追溯挂点

- [ ] 页面业务阅读挂点与结果反馈挂点当前优先保持在 `waybill`。
- [ ] 追溯正式证据对象挂点保持在 `trace_event`。
- [ ] 若需要从图片包生成证据对象，明确“先命中 `customer_line`，再关联到对应 `trace_event`”的补链规则。
- [ ] 不把图片直接主挂到 `order_line`。

### 7.5 权限与导出

- [ ] 图片预览权限与图片导出权限分开定义。
- [ ] 图片导出必须保留租户内操作审计。
- [ ] 结果页、预览页、下载接口都要重复校验当前租户和当前用户权限。
- [ ] 普通用户是否可导出整单运单包，以及是否允许额外导出结构层明细包，需在租户内角色矩阵中明确。

## 8. `logistics_trace_exception` 实施清单

### 8.1 模块与依赖

- [ ] 清点 `logistics_trace_exception` 与 `logistics_dispatch`、`logistics_trace_core` 的依赖边界。
- [ ] 如首轮需要读证据摘要，可通过 `trace_event` 或服务层聚合读取，不强制异常层直接重复存证据主数据。
- [ ] 确认每个租户库可独立安装、升级与回滚该模块。

### 8.2 对象与状态

- [ ] 明确 `logistics.trace.exception` 主归属优先为 `waybill / batch / trace_event`。
- [ ] 明确首轮 `exception_type`、`severity_level`、`state` 最小枚举。
- [ ] `process_owner / reporter / closed_time / close_summary` 等处理字段完整可追。
- [ ] `logistics.trace.exception.process.log` 存在最小处理记录闭环。

### 8.3 页面与阅读链

- [ ] 异常列表页可从运单、批次、当前状态、严重度筛选。
- [ ] 异常详情页可反读：
  - 关联运单
  - 关联批次
  - 关联留痕
  - 关键证据摘要
- [ ] 门店节点、运单详情中的异常入口不应直接改写异常主归属关系。
- [ ] 不把异常默认挂到订单上。

### 8.4 权限与操作

- [ ] 至少区分提报、跟进、关闭、只读四类角色动作。
- [ ] `create / write / action_*` 在模型层校验角色与状态，不只靠页面按钮控制。
- [ ] 列表页、详情页、关闭动作、指派动作都受当前租户数据库约束。
- [ ] 若存在只读/到期/降级场景，异常历史应可读，写动作应可控关闭。

## 9. 联动实施清单

### 9.1 导入与审计

- [ ] `dispatch_main` 与 `image_package` 的任务模型、结果页、错误行查询仍保持独立口径。
- [ ] `trace / evidence / exception` 如新增自己的结果或日志对象，不要挤占现有导入任务模型的职责。

### 9.2 菜单与入口

- [ ] 企业隔离 `P1` 下，每个租户菜单树独立可见。
- [ ] `trace / evidence / exception` 菜单是否默认显示，按租户内角色而不是跨租户平台逻辑控制。

### 9.3 数据隔离

- [ ] 三个模块都不写跨数据库引用。
- [ ] 任何摘要、计数、导出都只对当前租户库内数据生效。
- [ ] 访问 key、下载地址、结果页都不暴露其他租户的对象标识。

## 10. 当前明确不做

- 不补 `tenant_plan / tenant_feature_snapshot / tenant_job` 等平台表实现细节。
- 不补跨租户老板页、平台仓、指标同步任务。
- 不补自动化套餐升级、降级、到期策略实现。
- 不把 `trace / evidence / exception` 改写成完整工单平台或对象存储平台。

## 11. 交付前回扫清单

- [ ] 企业隔离专题与四期前端基线没有冲突口径。
- [ ] `customer_line` 已按“一运单一门店”强约束正确收口为兼容 / 扩展结构层。
- [ ] 图片导入命中可借助 `customer_line`，但图片业务阅读当前优先围绕 `waybill`。
- [ ] 正式证据对象仍挂在 `trace_event`。
- [ ] 异常仍优先挂在 `waybill / batch / trace_event`。
- [ ] 已同步补充本专题验收文档与 `docs/change_notes/`。
