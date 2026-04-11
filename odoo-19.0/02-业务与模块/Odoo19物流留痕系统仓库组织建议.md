# Odoo19物流留痕系统仓库组织建议

本文档用于明确一个很实际的问题：

**当前这套系统开发时，不同模块应该放在同一个仓库，还是拆成多个仓库。**

先给结论：

**当前阶段建议采用“一个主仓库 + 少量可独立拆分仓库”的方式，而不是一开始就把所有模块拆成很多仓库。**

更具体一点：

- Odoo 原生代码、Odoo 自定义模块、设计文档，建议放在同一个主仓库
- 小程序前端，如果是独立技术栈，建议单独仓库
- 路径规划算法，如果是独立服务，建议单独仓库
- 如果只是算法脚本、尚未独立部署，也可以先放主仓库，后面再拆

---

## 1. 为什么当前不建议一开始多仓

你现在这套系统还处在“领域模型、接口口径、模块边界快速收敛”的阶段。

这个阶段如果一开始就拆成很多仓库，会带来几个问题：

- 接口变更要跨仓同步
- 设计文档和实际代码容易脱节
- 一个字段调整，可能要改 3 到 4 个仓库
- 本地联调成本明显变高
- 小团队维护多个仓库，管理成本会很重

尤其你现在最核心的对象还是：

- 波次
- 批次
- 运单
- 留痕事件
- 证据对象

这些对象之间关联非常紧，放在同一个仓库里更容易统一推进。

---

## 2. 当前阶段最推荐的方案

建议采用：

```text
主仓库：odoo-reconstruct
  - Odoo 主体代码
  - custom_addons 自定义模块
  - 文档
  - 部署脚本

可独立拆分仓库：
  - miniapp 仓库
  - route-planner 仓库
```

也就是说：

**业务主干先单仓，真正独立技术栈的部分再拆仓。**

---

## 3. 哪些内容建议放在同一个主仓库

下面这些建议放在同一个仓库里：

## 3.1 Odoo 主体与自定义模块

建议放在同一个仓库：

- `odoo/`
- `addons/`
- `custom_addons/logistics_base`
- `custom_addons/logistics_dispatch`
- `custom_addons/logistics_trace_core`
- `custom_addons/logistics_trace_evidence`
- `custom_addons/logistics_trace_rule`
- `custom_addons/logistics_trace_exception`
- `custom_addons/logistics_trace_dashboard`
- `custom_addons/logistics_trace_integration`
- `custom_addons/logistics_trace_cn`

原因很简单：

- 它们运行在同一个 Odoo 服务里
- 它们共享同一套数据库
- 它们版本发布要一起走
- 它们接口和模型耦合很强

## 3.2 设计文档

设计文档也建议和主仓库放在一起。

因为你现在这套项目非常依赖文档驱动开发：

- 数据模型文档
- 接口规范
- 模块边界
- 前端页面清单
- 分工说明

如果文档和代码分仓，后面非常容易出现：

- 文档改了，代码没改
- 代码改了，文档没同步

## 3.3 部署与初始化脚本

建议也放主仓库：

- `docker-compose`
- 环境变量模板
- 初始化 SQL
- Odoo 启动脚本
- 开发环境脚本

原因是这些内容和 Odoo 自定义模块属于同一套交付物。

---

## 4. 哪些内容值得单独仓库

## 4.1 小程序前端

如果你的小程序或 H5 是独立前端项目，建议单独仓库。

推荐单独仓库的原因：

- 技术栈通常不是 Odoo/Python
- 前端发版节奏和 Odoo 后端不一样
- 前端负责人可以独立维护
- CI/CD 可以独立

建议仓库名类似：

- `logistics-trace-miniapp`
- `logistics-trace-frontend`

但要注意：

- 接口文档仍然以主仓库为准
- 小程序仓库不要自己定义另一套业务模型

## 4.2 路径规划算法服务

如果你的路径规划算法已经是一个独立可运行服务，建议单独仓库。

比如：

- 独立 Python 服务
- 独立容器部署
- 独立输入输出协议

推荐仓库名类似：

- `logistics-route-planner`
- `dispatch-solver`

原因是它和 Odoo 自定义模块虽然业务相关，但技术职责不同：

- Odoo 负责业务编排
- 算法服务负责求解

这两者天然适合分仓。

## 4.3 可选的第三方网关或中间层

如果后面出现下面这些独立系统，也可以单独仓库：

- OCR/AI 审核服务
- 文件中转服务
- 外部集成网关

但这些都不建议一开始就拆。

---

## 5. 当前阶段不建议拆仓的部分

下面这些暂时不建议拆：

- `logistics_dispatch`
- `logistics_trace_core`
- `logistics_trace_evidence`
- `logistics_trace_rule`
- `logistics_trace_exception`
- `logistics_trace_dashboard`

原因是这些模块虽然业务职责不同，但它们：

- 共用 Odoo ORM
- 共用数据库
- 共用同一套发布
- 调整字段时往往一起变

如果把这些模块拆成多个仓库，实际收益很小，反而会增加大量同步成本。

---

## 6. 适合你的仓库结构建议

结合你当前项目，我更建议最后长成下面这种结构：

```text
odoo-reconstruct/
├── README.md
├── odoo-19.0/
│   ├── odoo/
│   ├── addons/
│   ├── custom_addons/
│   │   ├── logistics_base/
│   │   ├── logistics_dispatch/
│   │   ├── logistics_trace_core/
│   │   ├── logistics_trace_evidence/
│   │   ├── logistics_trace_rule/
│   │   ├── logistics_trace_exception/
│   │   ├── logistics_trace_dashboard/
│   │   ├── logistics_trace_integration/
│   │   └── logistics_trace_cn/
│   ├── deploy/
│   └── doc/
└── scripts/
```

另外再单独有两个仓库：

```text
logistics-trace-miniapp/
logistics-route-planner/
```

---

## 7. 团队协作上的好处

如果按上面这个方案走，团队分工会更顺：

- 你负责总览、接口规范、数据模型审核，在主仓库推进
- Odoo 后端同学都在主仓库开发模块
- 小程序负责人在前端仓库开发
- 算法负责人在算法仓库开发

这样既不会把主业务拆碎，也不会把不同技术栈硬塞进一个仓库里。

---

## 8. 什么时候再考虑进一步拆仓

只有出现下面这些情况时，才值得继续拆：

1. 小程序团队已经完全独立发版
2. 算法服务已经独立部署并单独监控
3. 对外开放平台已经变成单独网关系统
4. 某个模块已经不再依赖 Odoo ORM 和 Odoo 发布流程

如果还没到这一步，就不要为了“看起来更架构化”而过早拆仓。

---

## 9. 最终建议

如果你现在就准备开始开发，我建议直接这样定：

1. `odoo-reconstruct` 作为主仓库
2. Odoo 自定义模块全部放主仓库
3. 设计文档全部放主仓库
4. 小程序单独一个仓库
5. 路径规划算法如果独立部署，就单独一个仓库；否则先放主仓库

一句话总结就是：

**当前阶段最稳的方案不是“所有东西都一个仓库”，也不是“每个模块一个仓库”，而是“业务主干单仓、独立技术栈拆仓”。**
