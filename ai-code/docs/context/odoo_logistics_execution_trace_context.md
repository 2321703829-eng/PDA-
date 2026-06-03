# Odoo Logistics Execution / Trace Context

> 状态说明：
> - 本文档当前作为执行主线与追溯主线的现行中间上下文文档使用。
> - 本文档不替代正式 addon 设计稿，但可作为项目级上下文与 addon 设计稿之间的统一桥接层。
> - 原 `odoo_logistics_order_trace_exception_draft.md` 命名已回调，不再保留 `draft` 作为主入口命名。

适用范围：
- `ai-code/docs/context/` 下的中间上下文文档
- 用于在项目级上下文与正式 addon 设计稿之间，提供一份更偏业务草图、但已经符合当前主线口径的设计说明

优先基准：
- `ai-code/docs/context/Odoo19物流留痕系统运单主对象与留痕主流程设计.md`
- `ai-code/docs/context/odoo_logistics_context.md`
- `ai-code/docs/architecture/logistics_dispatch_addon_design.md`
- `ai-code/docs/architecture/logistics_trace_core_addon_design.md`
- `ai-code/docs/architecture/logistics_trace_evidence_addon_design.md`
- `ai-code/docs/architecture/logistics_trace_exception_addon_design.md`

---

## 1. 文档定位

这份文档当前的定位是：

**用一份中间上下文稿，把执行主线、追溯主线和正式 addon 设计之间的理解接起来。**

它要回答的不是某个模块的所有技术细节，而是下面这些更适合当前阶段统一理解的问题：

1. 一期真正围绕哪些对象设计
2. 这些对象之间如何串起来
3. 后台页面到底在读什么对象
4. 哪些地方已经可以下钻到正式 addon 设计稿
5. 哪些地方仍然只能按“草图”理解，不能误判为已经定死

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

### 2.3 页面阅读链

```text
运单 -> customer_line -> order_line
运单 -> customer_line -> 图片预览 / 留痕 / 证据
```

---

## 3. 当前建议围绕的核心对象

当前建议统一围绕下面这组对象理解：

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

- 波次：调度组织层对象
- 批次：执行组织层对象
- 运单：现场追溯主对象
- 门店节点：运单下核心阅读层与门店事实层
- 订单行：业务明细层
- 货物行：底层货物事实层
- 留痕事件：事实层对象
- 证据对象：材料层对象
- 异常对象：问题与处理层对象

---

## 4. 关键关系草图

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

## 5. 当前后台页面到底围绕什么展开

### 5.1 追溯中心

主入口应是：

- 运单追溯
- 门店节点阅读区
- 批次追溯
- 留痕时间线
- 证据查看

不是订单追溯中心。

### 5.2 异常中心

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

### 5.3 管理工作台与老板页

工作台和老板页是聚合阅读层，不是主事实层。

它们更适合聚合这些内容：

- 待处理异常数
- 证据不足对象数
- 高风险批次数
- 最近变化流
- 优先处理对象列表

---

## 6. 当前已成熟与未成熟的边界

### 6.1 已较成熟，可以继续往正式设计推进

- 波次 / 批次 / 运单主线
- `customer_line` 门店节点阅读链
- 运单级与批次级留痕
- 证据挂留痕的结构
- 异常围绕运单 / 批次 / 留痕展开的口径
- 后台前端的追溯阅读链

### 6.2 仍然只是方向草图，不能高估成熟度

- 客户模块完整业务方案
- 门店模块完整业务方案
- 人员模块完整业务方案
- 仓库模块项目侧深度扩展
- 基础资料中心的大而全整合方案

---

## 7. 当前不再建议沿用的旧口径

下面这些旧理解，不应再在后续设计里继续沿用：

- “订单是系统追溯主对象”
- “门店节点只是兼容层，不是正式阅读层”
- “留痕围绕订单展开”
- “异常围绕订单展开”
- “图片可以直接挂订单主体”
- “先做订单留痕，再回头补运单语义”

如果历史文档里仍出现这些说法，应默认按新口径重解释。

---

## 8. 这份文档与正式设计稿的关系

这份文档是中间上下文稿。

后续如果要进入更细的设计，应优先下钻到：

- `docs/architecture/logistics_dispatch_addon_design.md`
- `docs/architecture/logistics_trace_core_addon_design.md`
- `docs/architecture/logistics_trace_evidence_addon_design.md`
- `docs/architecture/logistics_trace_exception_addon_design.md`

也就是说，这份文档负责把“项目上下文”落到“中间上下文层”，而正式字段、depends、文件结构、页面建议等，再交给各个 addon 设计稿承接。

---

## 9. 当前结论

这份文档现在应被理解为：

**一份围绕执行主线和追溯主线的现行中间上下文稿。**

它的核心任务不是继续强化“订单中心”，而是帮助团队统一理解：

- 执行对象怎么组织
- 追溯对象怎么挂接
- 后台页面在读什么
- 哪些模块已经能往正式设计推进
- 哪些内容还要继续保持审慎
