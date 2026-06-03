# logistics_dispatch Addon 设计稿

适用范围：
- 执行主线模块 `logistics_dispatch`
- 波次、批次、运单、车辆、司机、仓侧执行上下文等对象的 Odoo 承接设计

优先基准：
- `ai-code/docs/context/Odoo19物流留痕系统运单主对象与留痕主流程设计.md`
- `ai-code/docs/dev/project_coordination/Odoo19物流留痕系统五人分工与前端改造安排.md`
- `ai-code/docs/architecture/ARCHITECTURE.md`
- `ai-code/docs/architecture/custom_addons_blueprint.md`

---

## 1. 文档定位

本文档是当前执行主线模块的正式设计入口。

它要解决的不是“留痕怎么记”，而是先把留痕发生之前的执行组织对象稳定下来。

也就是说，这份文档的核心任务是明确：

1. 波次、批次、运单在 Odoo 中分别是什么
2. 这些对象之间如何关联
3. 哪些信息属于执行组织上下文
4. 这些对象如何给留痕、证据、异常、前端页面提供稳定主线

---

## 2. 模块目标

`logistics_dispatch` 的目标不是做传统调度算法平台，而是先成为当前系统的“执行主线承接模块”。

它至少要稳定承接下面这条主线：

```text
波次记录 -> 批次 -> 运单号 -> 运单下订单列表
```

并为下游模块提供这些能力：

- 给 `logistics_trace_core` 提供批次级与运单级留痕挂载对象
- 给 `logistics_trace_exception` 提供异常关联上下文
- 给后台前端提供“波次 / 批次 / 运单”的管理页和追溯页入口
- 给司机端和工作台提供执行对象查询基础

---

## 3. 模块边界

## 3.1 本模块负责

- 波次记录对象
- 批次对象
- 运单主对象
- 运单与订单归并关系
- 车辆、司机、装车位、路线顺序等执行上下文
- 执行状态流转的基础承接
- 后台执行主线页面的核心数据来源

## 3.2 本模块不负责

- 留痕事件明细
- 证据图片与元数据
- 异常处理记录
- 看板聚合与老板页聚合
- 司机端具体页面实现

这些职责应分别留给：

- `logistics_trace_core`
- `logistics_trace_evidence`
- `logistics_trace_exception`
- `logistics_trace_dashboard`
- `logistics_trace_mobile`

---

## 4. 设计原则

## 4.1 运单是执行主线中的现场主对象

`logistics_dispatch` 必须承认：

- 订单不是留痕主对象
- 运单才是现场交付与留痕的直接对象

因此，模块设计里应把：

- 订单视为运单下明细
- 运单视为与留痕、异常、前端追溯页直接衔接的核心对象

## 4.2 批次与运单分层

- 批次负责承接“车辆这次装什么、去哪、谁执行”
- 运单负责承接“某店本次配送交付对象是什么”

批次不能替代运单。

## 4.3 波次是调度组织层，不抢执行事实层

波次记录负责更高层的组织与调度批次，不直接承担门店交付事实表达。

## 4.4 尽量复用 Odoo 原生对象，但不被原生对象限制主线表达

可复用：
- `sale.order`
- `stock.picking`
- `stock.picking.batch`
- `fleet.vehicle`

但这些原生对象主要是底座，不直接替代：
- 波次记录
- 批次执行对象
- 运单主对象

---

## 5. 推荐模型

## 5.1 logistics.dispatch.wave

定位：
- 调度组织对象

建议字段：
- `name`
- `dispatch_date`
- `warehouse_id`
- `planned_depart_time`
- `state`
- `batch_ids`
- `total_batch_count`
- `total_waybill_count`
- `total_order_count`
- `remark`

主要作用：
- 从更高层组织一波批次
- 供管理者查看当日或当次调度结果

## 5.2 logistics.dispatch.batch

定位：
- 执行组织对象

建议字段：
- `name`
- `wave_id`
- `vehicle_id`
- `driver_id`
- `warehouse_id`
- `loading_position`
- `planned_depart_time`
- `actual_depart_time`
- `state`
- `route_summary`
- `waybill_ids`
- `total_waybill_count`
- `finished_waybill_count`
- `exception_waybill_count`
- `remark`

主要作用：
- 承接一车一趟或一组执行任务
- 承接装车侧上下文
- 给批次级留痕提供挂载对象

## 5.3 logistics.dispatch.waybill

定位：
- 现场留痕主对象

建议字段：
- `name`
- `delivery_date`
- `store_id`
- `batch_id`
- `vehicle_id`
- `driver_id`
- `route_seq`
- `state`
- `arrive_trace_status`
- `signoff_trace_status`
- `has_exception`
- `latest_trace_time`
- `latest_trace_type`
- `evidence_completeness`
- `remark`

主要作用：
- 承接门店级交付对象
- 承接运单级留痕、证据、异常的主关联对象
- 承接后台运单详情页与运单追溯列表页

## 5.4 logistics.dispatch.waybill.order.line

定位：
- 运单下订单归并关系

建议字段：
- `waybill_id`
- `sale_order_id`
- `stock_picking_id`
- `external_order_no`
- `store_id`
- `qty_summary`
- `weight_summary`
- `volume_summary`
- `line_state`

主要作用：
- 让订单回到“运单下业务明细”位置
- 支持从运单下查看订单列表
- 支持从订单反查所属运单

---

## 6. 关键关系

推荐核心关系如下：

```text
wave 1 -> n batch
batch 1 -> n waybill
waybill 1 -> n waybill_order_line

batch 1 -> n batch_trace_event         # 由 logistics_trace_core 承接
waybill 1 -> n waybill_trace_event     # 由 logistics_trace_core 承接
```

如果未来需要兼容原生对象，可以进一步建立：

- `waybill -> sale.order`
- `waybill -> stock.picking`
- `batch -> stock.picking.batch`
- `batch -> fleet.vehicle`

---

## 7. 依赖建议

推荐 depends：

- `mail`
- `contacts`
- `stock`
- `sale`
- `purchase`
- `fleet`
- `logistics_base`

说明：

- `mail`：保留消息、附件、活动等基础能力
- `contacts`：用于门店/客户关系
- `stock`：用于仓储与出入库基础
- `sale` / `purchase`：用于单据关联与反查
- `fleet`：用于车辆与司机底座
- `logistics_base`：用于项目级基础扩展

---

## 8. 文件结构建议

```text
logistics_dispatch/
├─ __init__.py
├─ __manifest__.py
├─ models/
│  ├─ __init__.py
│  ├─ logistics_dispatch_wave.py
│  ├─ logistics_dispatch_batch.py
│  ├─ logistics_dispatch_waybill.py
│  └─ logistics_dispatch_waybill_order_line.py
├─ security/
│  └─ ir.model.access.csv
├─ data/
│  └─ sequence_data.xml
├─ views/
│  ├─ logistics_dispatch_wave_views.xml
│  ├─ logistics_dispatch_batch_views.xml
│  ├─ logistics_dispatch_waybill_views.xml
│  └─ logistics_dispatch_menus.xml
└─ demo/
```

---

## 9. 页面建议

第一阶段最推荐先落这些页面：

### 9.1 波次管理

- 波次列表
- 波次详情

### 9.2 批次管理

- 批次列表
- 批次详情

### 9.3 运单管理

- 运单列表
- 运单详情中的执行上下文区

### 9.4 关联入口

- 从批次跳运单
- 从运单跳订单明细
- 从运单跳留痕
- 从运单跳异常

---

## 10. 状态建议

## 10.1 波次

建议最小状态：
- `draft`
- `planned`
- `in_progress`
- `done`
- `cancel`

## 10.2 批次

建议最小状态：
- `draft`
- `loading`
- `departed`
- `delivering`
- `done`
- `cancel`

## 10.3 运单

建议最小状态：
- `draft`
- `pending_delivery`
- `arrived`
- `delivered`
- `exception`
- `closed`

---

## 11. 与前端设计的关系

`logistics_dispatch` 直接支撑这些前端文档：

- `运输与调度模块前端设计草案.md`
- `后台按波次批次运单追溯页面设计.md`
- `前端总体设计总览.md`

对应的前端页面至少包括：

- 波次管理页
- 批次管理页
- 运单管理页
- 批次追溯页
- 运单追溯页的执行上下文区

也就是说，`logistics_dispatch` 不是一个“纯后端组织模块”，它直接决定后台前端主链能不能成立。

---

## 12. 实施顺序建议

建议按下面顺序推进：

1. 先落 `wave / batch / waybill` 三个核心对象
2. 再落运单与订单归并关系
3. 再落批次和运单基础视图
4. 再对接 `logistics_trace_core`
5. 再补状态流转与聚合字段

---

## 13. 当前结论

如果要把旧的 `logistics_order` 设计真正回调到当前正确主线，最合理的做法不是继续修补 `logistics_order`，而是直接采用：

**`logistics_dispatch` 作为执行主线模块。**

它应正式承接：

- 波次记录
- 批次对象
- 运单主对象
- 运单与订单归并关系
- 车辆、司机、仓侧执行上下文

后续留痕、证据、异常、前端追溯页都应建立在这条主线上。

