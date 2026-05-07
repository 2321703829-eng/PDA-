# Odoo Logistics Feasibility

适用范围：
- `ai-code/docs/context/` 下的可实现性判断文档
- 用于说明当前物流项目在 Odoo 中哪些能力可以复用原生模块，哪些能力需要通过自定义 addon 承接

优先基准：
- `ai-code/Odoo19物流留痕系统运单主对象与留痕主流程设计.md`
- `ai-code/docs/context/odoo_logistics_context.md`
- `ai-code/docs/architecture/ARCHITECTURE.md`
- `ai-code/docs/architecture/custom_addons_blueprint.md`

---

## 1. 文档定位

这份文档不负责定义最终业务方案，它负责回答更务实的问题：

1. 当前项目哪些部分可以直接建立在 Odoo 原生能力上
2. 哪些部分不能硬套原生模型，必须自定义设计
3. 当前仓库是否具备继续推进这些设计的基础
4. 后续做模块设计时，哪些目录最值得优先阅读

所以它的核心不是“业务怎么想象”，而是：

**在当前 Odoo 仓库里，这套物流系统到底能不能落，以及应该借谁的力。**

---

## 2. 当前结论

当前这套物流执行与追溯系统，完全可以建立在当前仓库中的 Odoo 能力之上继续推进设计。

但实现方式必须分成两类：

### 2.1 直接复用或轻扩展原生能力

- 客户 / 门店：主要基于 `res.partner`
- 工作人员：主要基于 `hr.employee`
- 仓库：主要基于 `stock.warehouse`
- 车辆：主要基于 `fleet.vehicle`
- 附件、消息、活动：主要基于 `mail` 和附件机制

### 2.2 必须通过自定义 addon 承接的能力

- 波次 / 批次 / 运单执行主线
- 批次级 / 运单级留痕事件
- 证据层对象与证据阅读口径
- 异常对象、异常状态流转、处理记录
- 工作台、老板页、追溯页等业务化后台体验

也就是说：

**Odoo 原生足够做底座，但不足以直接表达你当前这套物流执行与追溯主线。**

---

## 3. 当前仓库的基础条件

当前仓库是标准的 Odoo 19.0 单仓结构，核心目录包括：

```text
d:\Desktop\Odoo\
  odoo/          # Odoo 核心框架
  addons/        # 官方业务模块
  custom_addons/ # 项目自定义模块目录
  ai-code/       # 文档与设计体系
```

从静态设计角度看，当前基础条件是够的：

- 有 Odoo Web 后台框架
- 有 ORM、视图、菜单、权限、附件、消息能力
- 有 `contacts / hr / stock / sale / purchase / fleet / mail` 这些可复用模块
- 有 `custom_addons/` 目录可以承接项目级 addon

需要注意的是：

当前 `custom_addons/` 下已经同时存在：

- 已开始真实落地的模块：`logistics_base`、`logistics_dispatch`
- 历史阶段保留的目录：`logistics_order`、`logistics_trace`、`logistics_exception`

后面这组旧目录可以保留为历史过渡现实，但不应再被理解成当前最终模块边界。

---

## 4. 按主线拆看的可实现性判断

## 4.1 执行主线：波次 / 批次 / 运单

### 是否可实现

可以，而且必须自定义实现。

### 为什么不能直接硬套原生对象

虽然 Odoo 里有：
- `sale.order`
- `stock.picking`
- `stock.picking.batch`
- `fleet.vehicle`

但这些对象无法直接、清晰地表达：

```text
波次记录 -> 批次 -> 运单号 -> 运单下订单列表
```

尤其是“运单是现场留痕主对象”这一点，原生对象并没有直接对应。

### 推荐实现方式

通过自定义执行主线模块承接：
- `logistics_dispatch`

推荐对象：
- `logistics.dispatch.wave`
- `logistics.dispatch.batch`
- `logistics.dispatch.waybill`
- `logistics.dispatch.waybill.order.line`

### 可复用的原生底座

- `sale.order`：作为业务订单来源或反查对象
- `stock.picking`：作为出入库与履约底座
- `stock.picking.batch`：作为批处理参考对象
- `fleet.vehicle`：作为车辆底座
- `res.partner`：作为门店/客户底座

---

## 4.2 追溯主线：留痕事件

### 是否可实现

可以，而且非常适合在 Odoo 中自定义承接。

### 为什么需要自定义

留痕事件不是普通备注，也不是 chatter 消息本身。

它需要稳定表达：
- 事件类型
- 归属对象类型
- 归属批次或运单
- 提交人
- 提交时间
- 地点、车辆、司机等执行上下文
- 是否异常触发节点

这类“事实事件对象”必须有独立模型。

### 推荐实现方式

通过自定义事实层模块承接：
- `logistics_trace_core`

推荐对象：
- `logistics.trace.event`

### 可复用的原生底座

- `mail.thread`：提供消息、关注者、活动等协同基础
- `ir.attachment`：提供附件承接能力
- Odoo 原生表单 / 列表 / 搜索视图：提供后台时间线阅读入口

---

## 4.3 证据层：图片 / 备注 / 签名等材料

### 是否可实现

可以，但不建议让 Odoo 直接承担全部图片存储职责。

### 当前更合理的边界

- Odoo 负责证据对象与业务关联
- 外部图片服务负责图片对象存储与访问 key

### 推荐实现方式

通过自定义证据层模块承接：
- `logistics_trace_evidence`

推荐对象：
- `logistics.trace.evidence`

### 可复用的原生底座

- `mail` / 附件机制：做轻量证据承接或协同补充
- Odoo 后台图片预览、列表、详情视图：做证据阅读入口

### 关键提醒

证据不应直接挂在订单上，也不应直接跳过留痕事件挂在主对象上。更合理的关系是：

```text
trace_event 1 -> n evidence
```

---

## 4.4 异常层：问题对象与处理记录

### 是否可实现

可以，而且是 Odoo 非常适合承接的一类对象。

### 为什么适合 Odoo

异常层天然需要：
- 状态流转
- 责任人
- 处理记录
- 列表页 / 详情页 / 搜索筛选
- 与消息、活动、附件、备注的协同

这些都和 Odoo 的后台能力很贴合。

### 推荐实现方式

通过自定义异常层模块承接：
- `logistics_trace_exception`

推荐对象：
- `logistics.trace.exception`
- `logistics.trace.exception.process.log`

### 可复用的原生底座

- `mail.thread`
- `mail.activity.mixin`
- `hr.employee`
- `res.partner`

### 关键提醒

异常当前应优先挂在：
- 运单
- 批次
- 留痕事件

而不是默认挂订单。

---

## 4.5 工作台与老板页

### 是否可实现

可以，但它们更偏聚合展示层，不是底层主对象层。

### 推荐实现方式

通过聚合展示模块承接：
- `logistics_trace_dashboard`

### 需要的基础条件

- 已有执行主线对象
- 已有留痕事实层
- 已有异常层
- 已有聚合字段或统计查询策略

### 可复用的原生底座

- Odoo 看板、列表、搜索、图表能力
- Odoo Web 后台菜单与动作系统

### 关键提醒

工作台与老板页不是主事实来源，它们依赖下层对象稳定以后才值得正式深化。

---

## 5. 按模块看的可实现性矩阵

| 模块层 | 当前建议 | 可实现性 | 主要依托 |
|---|---|---|---|
| `logistics_base` | 保持基础扩展层定位 | 高 | `base / contacts / hr / stock / mail / fleet` |
| `logistics_dispatch` | 承接执行主线 | 高 | `stock / sale / purchase / fleet / contacts` + 自定义模型 |
| `logistics_trace_core` | 承接留痕事实层 | 高 | `mail` + 自定义模型 |
| `logistics_trace_evidence` | 承接证据层 | 高 | 外部图片服务 + Odoo 关联对象 |
| `logistics_trace_exception` | 承接问题与处理层 | 高 | `mail / hr / contacts` + 自定义模型 |
| `logistics_trace_dashboard` | 承接聚合展示层 | 中高 | Odoo Web + 聚合字段 / 聚合查询 |
| `logistics_trace_rule` | 承接规则配置层 | 中高 | Odoo 配置模型与字典能力 |
| `logistics_trace_mobile` | 承接司机端或移动端协同 | 中高 | Odoo controller / RPC + 现有对象层 |

---

## 6. Odoo 原生模块最值得优先阅读的目录

如果后续继续做设计细化，当前最值得优先阅读的是：

1. `addons/contacts`
2. `addons/hr`
3. `addons/stock`
4. `addons/sale`
5. `addons/mail`
6. `addons/fleet`
7. `odoo/addons/base/models`

阅读目的分别是：

- `contacts`：理解客户、门店、联系人与层级结构
- `hr`：理解员工、责任人、岗位关联
- `stock`：理解仓库、库位、调拨、批处理底座
- `sale`：理解订单来源与履约反查参考
- `mail`：理解消息、活动、附件、协同底座
- `fleet`：理解车辆对象与二期扩展入口
- `base/models`：理解 `res.partner`、`ir.attachment` 等底层对象

---

## 7. 当前最重要的实现原则

### 7.1 不硬改官方源码

继续坚持：
- 不直接修改官方核心 addon 去替代自定义模块
- 优先用继承、扩展、关联、视图扩展来完成项目设计

### 7.2 不把原生单据硬套成现场主对象

尤其要避免：
- 把 `sale.order` 硬当成运单
- 把 `stock.picking` 硬当成现场留痕主对象
- 把订单直接当成异常主挂点

### 7.3 原生负责底座，自定义负责主线

一个更稳的理解是：
- Odoo 原生模块负责基础设施和通用业务对象
- 项目自定义模块负责物流执行主线和追溯主线

### 7.4 先收口主线，再扩大主数据

当前更合理的顺序不是先把客户、门店、人员、仓库全部做全，而是：

1. 先收口执行主线
2. 再收口追溯主线
3. 最后再回补主数据深化方案

---

## 8. 当前结论

站在 2026-04-13 这个时间点看，当前仓库完全足以继续支撑这套物流系统的 Odoo 设计推进。

最核心的判断是：

- `客户 / 门店 / 人员 / 仓库 / 车辆` 可以大量借助 Odoo 原生底座
- `波次 / 批次 / 运单 / 留痕 / 证据 / 异常 / 工作台` 必须由项目自定义模块承接
- 当前最值得继续推进的不是“主数据全覆盖设计”，而是“执行主线 + 追溯主线”的进一步收口

所以，这份文档现在的结论应该被理解成：

**这套系统在 Odoo 中是可落地的，但不能靠原生模块直接拼出来，必须以原生为底座、自定义模块为主线。**
