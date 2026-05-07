> 状态说明：本文档已过期。
>
> 原因：本文的推进顺序仍围绕“订单留痕体系 Odoo 化”，已不符合当前 `波次 -> 批次 -> 运单 -> 留痕 -> 证据` 的主线。
>
> 当前请优先参考：
> - `ai-code/前端相关设计/00_导航与总纲/前端设计新工作计划安排.md`
> - `ai-code/Odoo19物流留痕系统运单主对象与留痕主流程设计.md`

# 下一步工作计划（2026-04-10 重校正版）

## 1. 计划背景

根据 D:\Desktop\ai-code-main\ai-code\系统设计\ 中已有设计重新校正后，当前项目不应再默认主数据模块已经设计完成。

下一步工作应围绕已经较成熟的订单留痕体系推进，而不是继续扩写客户、门店、工作人员、仓库的假设性功能。

## 2. 新的工作主线

### P1. 完成 Odoo 侧订单和批次映射设计

目标：

- 把 shipment_order、shipment_batch 在 Odoo 中如何表达梳理清楚
- 决定是否新建 logistics.order、logistics.batch 模型
- 决定哪些最新状态、最新留痕、最新图片字段保留为快照

交付物：

- docs/architecture/logistics_order_mapping.md
- 更新后的 logistics_order_addon_design.md

### P2. 完成 Odoo 侧留痕和图片映射设计

目标：

- 把 trace_record、trace_record_image 在 Odoo 中如何表达梳理清楚
- 明确图片服务与 Odoo 的边界
- 明确 image_access_key、业务图片关系、留痕时间线的口径

交付物：

- docs/architecture/logistics_trace_mapping.md
- 更新后的 logistics_trace_addon_design.md

### P3. 完成异常领域边界设计

目标：

- 明确异常是独立模型，还是订单和留痕异常状态的聚合视图
- 明确当前异常列表、历史异常、详情页面的领域边界

交付物：

- docs/architecture/logistics_exception_boundary.md
- 更新后的 logistics_exception_addon_design.md

### P4. 回头做主数据专题确认

目标：

- 分别确认客户、门店、工作人员、仓库到底要不要正式进入 Odoo 主数据
- 只有确认后，才继续正式推进 logistics_base

交付物：

- docs/context/master_data_workshop_questions.md
- 更新后的 odoo_logistics_master_data_draft.md
- 更新后的 logistics_base_addon_design.md

## 3. 近期最推荐的具体执行顺序

1. 先写订单和批次 Odoo 映射文档
2. 再写留痕和图片 Odoo 映射文档
3. 再收紧异常边界文档
4. 最后再决定 logistics_base 是轻量存在还是正式推进

## 4. 暂缓事项

以下内容建议先暂停继续扩写：

- 客户字段大表
- 门店履约细则字段
- 员工角色体系细分
- 仓库深度作业字段
- 围绕 logistics_base 的页面和权限膨胀

## 5. 当前结论

新的下一步，不是继续补齐所有物流模块，而是：

- 先把已经成熟的订单留痕体系 Odoo 化
- 再把主数据模块从草图推进到正式设计
