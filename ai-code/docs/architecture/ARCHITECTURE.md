# ARCHITECTURE

适用范围：
- `d:\Desktop\Odoo` 当前仓库的 Odoo 物流项目设计层架构说明
- `ai-code` 文档体系中的系统级结构、模块分层、目录约定、依赖边界

优先基准：
- `ai-code/Odoo19物流留痕系统运单主对象与留痕主流程设计.md`
- `ai-code/Odoo19物流留痕系统五人分工与前端改造安排.md`
- `ai-code/前端相关设计/00_导航与总纲/Odoo物流后台前端总体设计总览.md`

---

## 1. 文件目的

本文档用于统一回答下面这些问题：

1. 当前项目的系统主线是什么
2. 当前仓库里实际有哪些目录和模块
3. 设计层推荐的目标模块体系是什么
4. Odoo 原生模块和自定义模块如何分工
5. 文档、前端设计、后端模块设计应当挂在哪个结构下

这份文档不是某个模块的实现说明，而是整个项目的架构入口文档。

---

## 2. 当前架构结论

当前项目必须同时承认两层现实：

### 2.1 业务与对象现实

当前有效的业务对象主线已经明确为：

```text
波次记录 -> 批次 -> 运单号 -> 运单下订单列表 -> 留痕事件 -> 证据图片/备注
```

其中：
- `波次记录` 是调度组织对象
- `批次` 是执行组织对象
- `运单号` 是现场留痕主对象
- `订单` 是运单下的履约明细对象
- `留痕事件` 是事实对象
- `证据` 是留痕事件下的材料对象

### 2.2 仓库现实

当前仓库中既有历史命名的占位目录，也已经开始出现按新主线落地的真实模块，例如：

- `custom_addons/logistics_base`
- `custom_addons/logistics_dispatch`
- `custom_addons/logistics_order`
- `custom_addons/logistics_trace`
- `custom_addons/logistics_exception`

其中：

- `logistics_dispatch` 已经开始承接当前执行主线的真实代码
- `logistics_order / logistics_trace / logistics_exception` 主要保留历史过渡意义

因此，后续设计与实现都应遵守一个原则：

**现状目录可以保留过渡，但新的系统理解必须以 `wave / batch / waybill / trace / evidence / exception` 主线为准。**

---

## 3. 当前仓库结构

当前仓库的核心目录如下：

```text
d:\Desktop\Odoo\
├─ odoo\                 # Odoo 核心框架
├─ addons\               # 官方业务模块
├─ custom_addons\        # 项目自定义模块
├─ ai-code\              # 文档、设计、AI 协作体系
├─ debian\
└─ setup\
```

其中当前最关键的 3 层是：

### 3.1 Odoo 核心框架层

由 `odoo/` 提供：
- ORM
- Web 后台
- 视图、菜单、动作
- 权限体系
- 附件与消息机制
- 模块安装与升级机制

### 3.2 官方业务底座层

由 `addons/` 提供可复用业务基础：
- `stock`
- `sale`
- `purchase`
- `contacts`
- `mail`
- `fleet`
- `base`
- `web`

### 3.3 项目自定义业务层

由 `custom_addons/` 承接项目特有的调度、运单、留痕、证据、异常、看板等能力。

---

## 4. 当前 custom_addons 现状

当前仓库中已存在的自定义目录包括：

```text
custom_addons\
├─ logistics_base\
├─ logistics_dispatch\
├─ logistics_order\
├─ logistics_trace\
└─ logistics_exception\
```

需要明确：

1. `logistics_base` 是实际可用的基础扩展模块
2. `logistics_dispatch` 是当前已经开始承接真实代码的执行主线模块
3. `logistics_order / logistics_trace / logistics_exception` 这组名称代表较早阶段的拆分思路
4. 这组旧命名不能再直接代表当前最终业务边界

也就是说，当前仓库的目录现状是“历史技术现实 + 新主线已开始落地”，不是“只有旧占位目录”。

---

## 5. 推荐的目标模块分层

基于当前有效设计，推荐把目标模块体系理解成下面 4 层。

## 5.1 基础扩展层

模块：
- `logistics_base`

职责：
- 承接对 Odoo 官方模型的轻量扩展
- 放置共用字典、基础混入、通用字段扩展
- 提供项目级基础工具和共用约定

说明：
- 这是基础层，不承担执行主线本体

## 5.2 执行组织层

推荐模块：
- `logistics_dispatch`

职责：
- 承接波次、批次、运单主对象
- 承接车辆、司机、装车位、路线顺序等执行上下文
- 定义后台执行主线

说明：
- 这是当前系统最关键的一层之一
- 后续很多“运单管理 / 批次管理 / 波次管理”页面都应挂在这层

## 5.3 事实与问题层

推荐模块：
- `logistics_trace_core`
- `logistics_trace_evidence`
- `logistics_trace_exception`

职责：
- `logistics_trace_core`：承接批次级和运单级留痕事件
- `logistics_trace_evidence`：承接证据图片、备注、访问口径、元数据
- `logistics_trace_exception`：承接异常对象、状态流转、处理记录

说明：
- 这是后台追溯阅读链的核心承载层

## 5.4 规则与展示层

推荐模块：
- `logistics_trace_rule`
- `logistics_trace_dashboard`
- `logistics_trace_integration`

职责：
- `logistics_trace_rule`：承接留痕规则、异常类型、编号规则等配置
- `logistics_trace_dashboard`：承接工作台、老板页、统计看板聚合
- `logistics_trace_integration`：承接与外部系统的接入

---

## 6. 当前前端设计与后端模块的关系

当前前端设计已经明确围绕两条主线展开：

### 6.1 执行主线

```text
波次 -> 批次 -> 运单
```

主要承载模块：
- `logistics_dispatch`

### 6.2 追溯主线

```text
运单 -> 留痕 -> 证据 -> 异常
```

主要承载模块：
- `logistics_trace_core`
- `logistics_trace_evidence`
- `logistics_trace_exception`

这意味着：

- 前端设计已经可以指导模块落地
- 模块实现也必须逐步回到这些页面语义上

---

## 7. 当前实施状态判断

### 已开始真实落地

- `logistics_base`
- `logistics_dispatch`

### 已有正式设计稿但尚未进入真实模块骨架阶段

- `logistics_trace_core`
- `logistics_trace_evidence`
- `logistics_trace_exception`
- `logistics_trace_dashboard`

### 主要保留历史过渡意义

- `logistics_order`
- `logistics_trace`
- `logistics_exception`

---

## 8. 当前结论

当前这套项目架构不能再被理解成：

```text
logistics_base + logistics_order + logistics_trace + logistics_exception
```

更准确的理解应该是：

```text
当前仓库现实：
  logistics_base + logistics_dispatch + 旧占位目录

目标系统架构：
  logistics_base
  + logistics_dispatch
  + logistics_trace_core
  + logistics_trace_evidence
  + logistics_trace_exception
  + logistics_trace_rule
  + logistics_trace_dashboard
  + logistics_trace_integration
```

而当前最重要的动作，是继续保持：

- 架构文档
- 前端设计文档
- 真实模块实现

三者的状态同步。
