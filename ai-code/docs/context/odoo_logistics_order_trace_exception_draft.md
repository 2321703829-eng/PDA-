# Odoo Logistics Dispatch / Trace / Exception Draft

> 状态说明：
> - 当前正式入口已转到 `docs/context/odoo_logistics_execution_trace_context.md`。
> - 本文件保留为兼容旧引用的历史别名入口。
> - 如继续推进当前设计，请优先阅读新文件，不再以本文件作为主入口维护。

适用范围：
- `ai-code/docs/context/` 下的中间草图文档
- 用于在项目级上下文与正式 addon 设计稿之间，提供一份更偏业务草图、但已经符合当前主线口径的设计说明

优先基准：
- `ai-code/docs/context/Odoo19物流留痕系统运单主对象与留痕主流程设计.md`
- `ai-code/docs/context/odoo_logistics_context.md`
- `ai-code/docs/architecture/logistics_dispatch_addon_design.md`
- `ai-code/docs/architecture/logistics_trace_core_addon_design.md`
- `ai-code/docs/architecture/logistics_trace_exception_addon_design.md`

---

## 1. 文档定位

这份文档不再是旧阶段的“订单 / 留痕 / 异常三件套草图”。

它现在的定位是：

**用一份更轻的上下文草图，把当前系统的执行主线和追溯主线串起来。**

也就是说，它要回答的不是某个模块的所有技术细节，而是下面这些更适合设计阶段统一理解的问题：

1. 一期真正要围绕哪些对象设计
2. 这些对象之间怎么串起来
3. 后台页面到底在读什么对象
4. 哪些地方已经可以往正式 addon 设计推进
5. 哪些地方还不该被误判成“需求已经定死”

---

## 2. 一期主线

当前一期最核心的业务主线是：

```text
波次记录 -> 批次 -> 运单号 -> 门店节点 customer_line -> 订单行 order_line -> 货物行 goods_line
```

可以把它理解成两条互相咬合的链：

### 2.1 执行主线

```text
波次 -> 批次 -> 运单 -> customer_line -> order_line -> goods_line
```

这条线回答的是：
- 今天怎么组织发货
- 哪辆车执行哪批任务
- 这一批里有哪些运单
- 某张运单当前属于哪次执行任务

### 2.2 追溯主线

```text
运单 / customer_line 上下文 -> 留痕 -> 证据 -> 异常
```

这条线回答的是：
- 这张运单现场发生过什么
- 哪些留痕已经形成
- 有哪些图片和备注证据
- 当前有没有异常，异常处理到哪一步

最关键的一句话是：

**运单是现场追溯主对象，`customer_line` 是门店节点主阅读层，订单只是门店节点下的业务明细。**

---

## 3. 当前建议围绕的核心对象

### 3.1 波次记录

定位：调度组织对象。

它更偏计划和组织层，主要负责：
- 表达某天或某次集中发货组织
- 归拢多个批次
- 提供更高层的调度视角

它不是现场留痕主对象，也不是异常主对象。

### 3.2 批次

定位：执行组织对象。

它主要负责：
- 表达某辆车或某条执行路线承接的一组任务
- 记录车辆、司机、仓库、装车位、出发时间等上下文
- 承接批次级留痕事件
- 提供批次聚合风险和批次下钻入口

批次是重要对象，但它不替代运单。

### 3.3 运单

定位：现场追溯主对象。

它主要负责：
- 表达某店铺本次配送的交付对象
- 作为正式留痕、正式证据、异常的主要归属点
- 提供后台追溯列表和详情页的主要入口

后续大部分后台页面，实际都是围绕运单在阅读。

### 3.4 门店节点、订单与货物明细

定位：业务明细层。

它主要负责：
- 先以 `customer_line` 承接门店节点级阅读与业务汇总
- 在 `customer_line` 下承接销售单、出库单或外部订单明细
- 继续向下承接货物行 `goods_line`
- 支持从门店节点、订单、货物反查所属运单

这层重要，但不应再反客为主地占据留痕中心位置。

### 3.5 留痕事件

定位：事实层对象。

它主要负责：
- 记录现场发生过什么
- 支持批次级与运单级两类留痕
- 为时间线页、详情页、异常联动区提供事实来源

留痕回答的是“发生过什么”，而不是“问题处理得怎么样”。

### 3.6 证据对象

定位：材料层对象。

它主要负责：
- 挂在留痕事件之下
- 承接图片、备注、签名等证据材料
- 支持后台证据查看页和异常详情的证据阅读

证据层应和留痕事件层分开，不要混成一个对象。

### 3.7 异常对象

定位：问题与处理层对象。

它主要负责：
- 记录哪里出了问题
- 记录问题状态和严重度
- 记录谁在处理、处理到哪一步
- 关联运单、批次、留痕和证据

异常回答的是“问题当前处于什么处理状态”，而不是“事实本身是什么”。

---

## 4. 一期建议的模型草图口径

这份文档不直接替代正式 addon 设计稿，但为了统一中间设计理解，建议按下面这组对象草图去想：

- `logistics.dispatch.wave`
- `logistics.dispatch.batch`
- `logistics.dispatch.waybill`
- `logistics.dispatch.waybill.customer.line`
- `logistics.dispatch.waybill.order.line`
- `logistics.dispatch.waybill.customer.goods.line`
- `logistics.trace.event`
- `logistics.trace.evidence`
- `logistics.trace.exception`
- `logistics.trace.exception.process.log`

其中：

### 4.1 执行主线对象

- `logistics.dispatch.wave`
- `logistics.dispatch.batch`
- `logistics.dispatch.waybill`
- `logistics.dispatch.waybill.customer.line`
- `logistics.dispatch.waybill.order.line`
- `logistics.dispatch.waybill.customer.goods.line`

### 4.2 事实与问题对象

- `logistics.trace.event`
- `logistics.trace.evidence`
- `logistics.trace.exception`
- `logistics.trace.exception.process.log`

这组命名和旧的：
- `logistics.order`
- `logistics.trace`
- `logistics.exception`

已经不是同一层理解了。旧命名现在最多只适合作为历史过渡名，不应继续当成当前草图基线。

---

## 5. 对象之间的关系草图

建议统一按下面这条关系去理解：

```text
wave 1 -> n batch
batch 1 -> n waybill
waybill 1 -> n customer_line
customer_line 1 -> n order_line
order_line 1 -> n goods_line

batch 1 -> n trace_event
waybill 1 -> n trace_event
trace_event 1 -> n evidence

waybill 1 -> n exception
batch 1 -> n exception
trace_event 1 -> n exception
exception 1 -> n exception_process_log
```

这里要特别注意 4 点：

1. 运单可以有多条留痕
2. 批次也可以有自己的留痕
3. 证据优先挂在留痕事件下
4. 异常优先挂在运单 / 批次 / 留痕上下文上，而不是挂订单

---

## 6. 当前后台页面到底围绕什么展开

### 6.1 追溯中心

主入口应是：
- 运单追溯
- 门店节点阅读区
- 批次追溯
- 留痕时间线
- 证据查看

不是订单追溯中心。

### 6.2 异常中心

主入口应是：
- 当前异常列表
- 历史异常列表
- 待处理争议列表
- 异常详情

异常详情里最应该看的是：
- 关联运单
- 关联批次
- 关键留痕
- 关键证据
- 当前处理记录

### 6.3 管理工作台

工作台是聚合阅读层，不是主事实层。

它更适合聚合这些内容：
- 待处理异常数
- 证据不足对象数
- 高风险批次数
- 最近变化流
- 优先处理对象列表

### 6.4 老板页

老板页不是用来读所有过程字段的。

它更适合：
- 先看结论
- 再看摘要证据
- 最后按需下钻到运单与异常详情

---

## 7. 当前已成熟与未成熟的边界

### 7.1 已较成熟，可以继续往正式设计推进

- 波次 / 批次 / 运单主线
- `customer_line` 门店节点阅读链
- 运单级与批次级留痕
- 证据挂留痕的结构
- 异常围绕运单 / 批次 / 留痕展开的口径
- 后台前端的追溯阅读链

### 7.2 仍然只是方向草图，不能高估成熟度

- 客户模块完整业务方案
- 门店模块完整业务方案
- 人员模块完整业务方案
- 仓库模块项目侧深度扩展
- 基础资料中心的大而全整合方案

所以后续推进时，不要再把这份文档理解成“主数据已经定稿，只剩开发”。

---

## 8. 当前不再建议保留的旧口径

下面这些旧理解，不应再在后续设计里继续沿用：

- “订单是系统追溯主对象”
- “门店节点只是兼容层，不是正式阅读层”
- “留痕围绕订单展开”
- “异常围绕订单展开”
- “图片可以直接挂订单主体”
- “先做订单留痕，再回头补运单语义”

如果历史文档里仍出现这些说法，应默认按新口径重解释。

---

## 9. 这份文档与正式设计稿的关系

这份文档是中间层草图。

后续如果要进入更细的设计，应优先下钻到：

- `docs/architecture/logistics_dispatch_addon_design.md`
- `docs/architecture/logistics_trace_core_addon_design.md`
- `docs/architecture/logistics_trace_exception_addon_design.md`

也就是说，这份文档负责把“项目上下文”落到“中间草图层”，而正式字段、depends、文件结构、页面建议等，再交给各个 addon 设计稿承接。

---

## 10. 当前结论

这份草图文档现在应被理解为：

**一份围绕执行主线和追溯主线的中间设计草图。**

它的核心任务不再是继续强化“订单中心”，而是帮助团队统一理解：

- 执行对象怎么组织
- 追溯对象怎么挂接
- 后台页面在读什么
- 哪些模块已经能往正式设计推进
- 哪些内容还要继续保持审慎
