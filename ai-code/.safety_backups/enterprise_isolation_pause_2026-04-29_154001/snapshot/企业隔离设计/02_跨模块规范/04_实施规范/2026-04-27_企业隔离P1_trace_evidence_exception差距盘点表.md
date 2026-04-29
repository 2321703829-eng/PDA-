# 2026-04-27 企业隔离 `P1` trace / evidence / exception 差距盘点表

## 1. 文档定位

- 本文不是新方案稿。
- 本文只基于当前代码和现有页面，按 `已有 / 缺失 / 口径冲突 / 可以后置` 做差距盘点。
- 盘点范围只覆盖企业隔离 `P1` 下的 `trace / evidence / exception` 与其联动阅读链。

## 2. 盘点基线

- 前端基线：
  - `专题设计/前端设计/四期前端优化设计/00_导航与总纲/2026-04-20_四期前端优化设计总纲.md`
  - `专题设计/前端设计/四期前端优化设计/00_导航与总纲/2026-04-21_四期页面信息架构与阅读链方案.md`
- 当前代码基线：
  - `custom_addons/logistics_dispatch`
  - `custom_addons/logistics_trace_core`
  - `custom_addons/logistics_trace_evidence`
  - `custom_addons/logistics_trace_exception`
  - `custom_addons/logistics_web`

## 3. `trace` 差距盘点

| 项目 | 当前现实 | 判定 | 处理方向 |
| --- | --- | --- | --- |
| 正式留痕对象 | `custom_addons/logistics_trace_core/models/logistics_trace_event.py` 已有 `logistics.trace.event`，正式主挂点为 `batch_id / waybill_id` | 已有 | 继续沿用，不改成 `customer_line` 主挂点 |
| 留痕对象类型 | `object_type` 只支持 `batch / waybill` | 已有 | 与 `P1` 边界一致，保持收口 |
| 核心事件枚举 | 已覆盖 `arrive_loading_point / start_loading / finish_loading / departed / arrive_store / deliver_finish / signoff / exception_report` | 已有 | 先按现有枚举推进，后续只补缺口不改骨架 |
| waybill 侧留痕入口 | `logistics_trace_core/views/logistics_trace_event_views.xml` 与 `logistics_trace_core/models/logistics_dispatch_waybill.py` 已有运单侧入口和聚合字段 | 已有 | 继续作为 `waybill` 主阅读入口之一 |
| customer_line 侧留痕入口 | 当前视图搜索只有 `waybill` 侧 smart button，`customer_line` 页面未见直达留痕入口 | 可以后置 | 在“一运单一门店”强约束下不作为 `P1` 必补项 |
| 留痕权限分层 | 当前主要是 `base.group_user` 与 trace manager 两层 | 缺失 | 补租户内查看、提交、处理三层角色矩阵 |
| 模型层动作校验 | `create / write` 已有基本校验，不完全依赖前端按钮 | 已有 | 保留模型层校验思路，后续只补角色细化 |

## 4. `evidence` 差距盘点

| 项目 | 当前现实 | 判定 | 处理方向 |
| --- | --- | --- | --- |
| 正式证据对象 | `custom_addons/logistics_trace_evidence/models/logistics_trace_evidence.py` 已有 `logistics.trace.evidence`，且 `trace_event_id` 必填 | 已有 | 继续保持正式主挂点围绕 `trace_event` |
| 运单侧证据聚合 | `logistics_trace_evidence/models/logistics_dispatch_waybill.py` 已补 `evidence_ids / evidence_count / evidence_status` | 已有 | 保留运单摘要职责 |
| customer_line 主阅读入口 | 证据模块本身未见 `customer_line` 视图入口或反查字段 | 可以后置 | 在“一运单一门店”强约束下不作为 `P1` 主阅读链要求 |
| 现有证据阅读页 | `custom_addons/logistics_web/static/src/js/views/logistics_waybill_form_view.js` 直接按 `waybill_id` 拉取证据列表 | 已有 | 与 `waybill` 主阅读入口口径一致，继续沿用 |
| 图片命中规则 | 证据模块当前未见 `waybill_no + customer_line_no` 或 `waybill_no + store_no` 补链规则 | 缺失 | 在 evidence 小稿中单独补命中和补链规则 |
| `image_package` 审计链落点 | `logistics_dispatch/models/selection_options.py` 已有 `image_package` 枚举，但 `logistics_web/services` 未搜到对应图片包导入服务 | 缺失 | 单列为图片导入补链任务，不与 `dispatch_main` 混写 |
| 预览 / 导出 / 审计权限 | 当前以普通用户和 manager 粗分，未见独立导出权限层 | 缺失 | 在角色边界包中补导出权限与审计要求 |
| 外部图片访问 key | `image_access_key / preview_url / full_url` 已有元数据字段 | 已有 | 保持元数据方向，不回退成 Odoo 附件主存储 |
| 图片对象存储命名空间、回收策略 | 当前未落地租户级命名空间和回收策略 | 可以后置 | 属于后续实现细化，不阻塞本轮 `P1` 设计收口 |

## 5. `exception` 差距盘点

| 项目 | 当前现实 | 判定 | 处理方向 |
| --- | --- | --- | --- |
| 正式异常对象 | `custom_addons/logistics_trace_exception/models/logistics_trace_exception.py` 已有 `logistics.trace.exception` | 已有 | 继续沿用，不重起对象 |
| 正式主挂点 | 当前主挂点围绕 `waybill_id / batch_id / trace_event_id` | 已有 | 与 `P1` 收口一致，保持不变 |
| 状态流转 | 已有 `draft / open / processing / resolved / closed / cancelled` 与模型层状态迁移校验 | 已有 | 后续只补角色矩阵和联动口径 |
| 处理日志 | `logistics.trace.exception.process.log` 已存在，且通过 sudo 自动写日志 | 已有 | 继续作为最小处理闭环 |
| 异常详情联动 | 当前详情页已可打开 `waybill / batch / trace_event / evidence` | 已有 | 保持反读链，不再另起一套入口 |
| customer_line 侧异常入口 | 当前异常入口仍主要在 `waybill` 与异常列表，未见门店节点页入口 | 可以后置 | 当前 `P1` 不要求 customer_line 成为异常主阅读入口 |
| 异常角色分层 | 当前主要仍是普通用户和 manager 两层 | 缺失 | 补提报、跟进、关闭、只读四类动作边界 |
| 到期只读 / 降级写关闭 | 当前没有与套餐到期相关的只读策略 | 可以后置 | 属于 `P2 / P3` 平台能力，不在本轮展开 |

## 6. 三层联动与页面差距盘点

| 项目 | 当前现实 | 判定 | 处理方向 |
| --- | --- | --- | --- |
| 四期主链对象 | `logistics_dispatch` 已有 `waybill / customer_line / order_line / goods_line` 模型和页面 | 已有 | 作为三层联动的真实主链起点 |
| `customer_line` 页面存在性 | `logistics_dispatch/views/logistics_dispatch_waybill_views.xml` 已有 `customer_line` 列表、表单、搜索页 | 已有 | 当前保留为结构、快照、导入导出与后续扩展层 |
| 三层入口挂在 customer_line | 当前未见 `customer_line` 表单上的 trace / evidence / exception 直达入口 | 可以后置 | 当前 `P1` 不再要求补 customer_line 主阅读入口 |
| 运单页现有联动 | waybill 页已有时间线、证据、异常摘要与 widget | 已有 | 保留摘要层，不承担全部阅读职责 |
| 运单页承担主要图片阅读 | 当前 JS widget 明显以运单为证据主入口 | 已有 | 与“一运单一门店”后的 `waybill` 主阅读口径一致 |
| `dispatch_main` 审计链 | `logistics_web/services/waybill_standard_import_service_v2.py` 与 `dispatch_main_export_service.py` 已落主数据导入导出 | 已有 | 不要与图片包任务混为一类 |
| `image_package` 专项实现 | 枚举已在，但实际服务和结果链未形成清晰落点 | 缺失 | 单独补图片包导入与补链设计 |
| 跨库引用 | 当前三个 trace addon 都是单库模型，没有跨数据库引用实现 | 已有 | 与企业隔离 `P1` 前提一致 |
| 平台控制面 | 当前没有租户计划、套餐、平台任务模型 | 可以后置 | 明确留在 `P2 / P3`，不作为本轮缺口修补目标 |

## 7. 当前结论

### 7.1 当前最稳的起点

- `trace / evidence / exception` 三块都已经有真实 addon，不是空目录。
- 当前最成熟的是：
  - `waybill / trace_event` 这条骨架
  - 异常状态流与处理日志
  - 运单侧的时间线、证据、异常摘要

### 7.2 当前最明显的缺口

- 当前最需要做的不是把 `customer_line` 抬成主阅读入口，而是把 `waybill` 主阅读口径和 `customer_line` 结构层职责重新收口一致。
- `image_package` 虽然已经进入任务对象枚举，但图片包补链与证据化流程还没落到模块里。
- 租户内角色边界仍偏粗，离 `P1` 落地需要的查看 / 提交 / 处理 / 导出分层还有差距。

### 7.3 当前最需要避免的偏移

- 不能为了补页面阅读链，把正式证据对象从 `trace_event` 改成 `customer_line`。
- 不能在已确认“一运单一门店”强约束后，又把 `customer_line` 误抬成当前 `P1` 主阅读入口。
- 不能把本轮缺口修补扩写成 `P2 / P3` 平台设计。
