# Odoo 19 系统总览（自上而下）

本文档基于 Odoo 19 源码目录的静态分析整理，现归档于本仓库中，目标是帮助你快速建立从业务层到技术层的完整心智模型。

## 1. 这套系统本质上是什么

你下载的不是代码托管平台（如 GitLab/Gitea），而是 **Odoo 19 开源 ERP 平台**。  
它是“模块化业务操作系统”：CRM、销售、电商、库存、制造、财务、人事、营销等都以模块形式存在，并可按需组合。

官方仓库描述：`Odoo is a suite of web based open source business apps.`

---

## 2. 一句话架构图

`Web/移动端` -> `HTTP Controller + 路由` -> `ORM(Environment/Model/Registry)` -> `PostgreSQL`  
同时通过 `模块系统(addons)` 装配业务能力，通过 `bus/websocket + cron` 处理实时与异步任务。

---

## 3. 仓库结构（你最先该认识的目录）

- `odoo/`: 框架内核（HTTP、ORM、模块加载、服务进程、配置、工具）
- `addons/`: 官方业务模块（绝大部分功能都在这里）
- `odoo/addons/base`: 最基础内核业务模块（所有模块都绕不开）
- `odoo-bin`: 启动入口脚本
- `requirements.txt`: Python 依赖
- `debian/`: Linux 包装与服务部署配置

---

## 4. 规模与模块地图

### 4.1 模块规模（本仓库实测）

- 模块总数：`642`
- 应用级模块（`application=True`）：`34`
- `auto_install=True` 模块：`389`
- 本地化模块（`l10n_*`）：`216`（占比非常高）

### 4.2 依赖中心（被大量模块依赖）

- `account`
- `mail`
- `web`
- `sale`
- `website`
- `payment`

这几个可以理解为“平台关键枢纽”。

### 4.3 重点业务域（应用级）

- 财务：`account`（Invoicing/Accounting）
- 销售：`sale_management`
- CRM：`crm`
- 采购：`purchase`
- 库存：`stock`
- 制造：`mrp`
- 项目：`project`
- 人事：`hr`、`hr_attendance`、`hr_expense` 等
- 电商与站点：`website`、`website_sale`
- 门店收银：`point_of_sale`、`pos_restaurant`
- 协同沟通：`mail`（Discuss）

---

## 5. 技术栈清单

## 5.1 后端

- 语言：Python 3.10~3.13（仓库定义）
- 框架：Odoo 自研框架（并非 Django/Flask 应用）
- ORM：Odoo ORM（Model/Field/Environment/Registry）
- 数据库：PostgreSQL（最小版本 13）
- 驱动：`psycopg2`
- Web 层：`Werkzeug`（WSGI）
- 并发/服务模式：Threaded / Prefork / Gevent（按配置切换）

### 5.2 前端

- Odoo Web Client（模块化资产管线）
- OWL（Odoo 前端组件框架）
- QWeb 模板
- SCSS + Bootstrap
- 常见库：jQuery、Luxon、Chart、FullCalendar 等（仓库内置）

### 5.3 异步与实时

- 实时消息：`bus` 模块 + WebSocket
- 通知机制：PostgreSQL LISTEN/NOTIFY（`imbus` 频道）
- 定时任务：`ir.cron`

### 5.4 对外 API

- `/json/2/<model>/<method>`（bearer）
- `/jsonrpc`
- `/xmlrpc/2/<service>`

---

## 6. 系统如何启动（启动主链）

1. `odoo-bin` 进入 `odoo.cli.main()`
2. 默认命令是 `server`
3. 解析配置（端口、数据库、addons-path、workers 等）
4. 加载 server-wide 模块（默认 `base,rpc,web`）
5. 启动服务（Threaded / Prefork / Gevent）
6. 预加载数据库 Registry，加载模块图并构建模型

你可以把它理解成：
- `odoo-bin` 负责“把系统拉起来”
- `registry + module loading` 负责“把业务能力装进去”

---

## 7. 框架核心机制（必懂）

## 7.1 HTTP + Controller + Route

- `odoo.http.Controller` + `@route(...)` 定义路由
- 请求会按 `type='http'/'jsonrpc'` 走不同 dispatcher
- 在 DB 请求里会自动创建 `request.env`（ORM 环境）

## 7.2 ORM 四件套

- `Model`: 业务模型（如 `sale.order`）
- `Field`: 字段系统（Many2one/One2many/compute/related/...）
- `Environment`: 当前请求上下文（`cr/uid/context/su`）
- `Registry`: 当前数据库下所有模型的注册表与缓存中心

## 7.3 模块加载机制

- 每个模块由 `__manifest__.py` 描述依赖、数据、资产
- 加载顺序由依赖图 `ModuleGraph` 计算
- `base` 永远先加载
- 安装/升级会触发 schema、data、views、translations、hooks

---

## 8. 关键业务链路（从销售到履约到财务）

下面是最典型的端到端链路之一：

### 8.1 销售确认

- `sale.order.action_confirm()` 将订单状态从报价转为销售订单
- 之后调用 `_action_confirm()`
- 在 `sale_stock` 中重写的 `_action_confirm()` 会触发库存规则：`order_line._action_launch_stock_rule()`

### 8.2 库存/补货规则

- 销售行会准备 procurement values（仓库、路线、截止日期、收货地址等）
- `stock.rule.run(...)` 按规则执行：
  - `_run_pull`（拉式补货）
  - `_run_buy`（采购）
  - `_run_manufacture`（生产，来自 `mrp` 扩展）
- 对应创建 `stock.move` 并 `_action_confirm()`，进入库存执行链

### 8.3 库存动作确认

- `stock.move._action_confirm()` 负责：
  - 状态迁移（draft -> confirmed/waiting）
  - make_to_order 触发后续 procurement
  - 分配拣货单、预留、合并 move、处理 push 规则等

### 8.4 开票

- `sale.order._create_invoices()` 从可开票的销售行生成 `account.move`
- 后续 `account.move.action_post()` 完成记账过账

这条链路体现了 Odoo 的核心设计：  
**销售、库存、采购、制造、财务通过同一个 ORM/模块机制串联，而不是分散在多个独立服务里。**

---

## 9. 实时与异步机制

## 9.1 实时通知（bus）

- 路由：`/websocket`
- 前端可 `peek_notifications`
- 后端通过 `bus.bus` 写消息，事务提交后触发 PG notify
- 监听线程收到通知后分发到 websocket 连接

## 9.2 定时任务（cron）

- 模型：`ir.cron`
- 负责自动化业务（邮件、清理、同步、批处理）
- 多 worker 下有锁与并发处理逻辑，避免重复执行

---

## 10. 认证与安全能力

内置多个认证增强模块：

- `auth_oauth`: OAuth2 登录
- `auth_passkey`: WebAuthn Passkey
- `auth_totp`: 双因素 TOTP
- `auth_ldap`: LDAP 集成
- `auth_signup`, `auth_timeout`, `auth_password_policy` 等

补充：Odoo 的权限体系在模型层做得很重：
- ACL（`ir.model.access.csv`）
- Record Rule（行级过滤）
- 组与角色（`res.groups`）

---

## 11. 前端组织方式（为什么看起来“不像普通前端项目”）

Odoo 不以传统 `package.json + 单独前端工程` 组织，而是：

- 每个模块在 `__manifest__.py` 的 `assets` 声明前端资源
- 后端按 bundle 汇总并生成可加载资产
- 同时支持 backend / frontend / test / lazy 等多种 bundle

这意味着：
- 前后端同模块共存（`models/ + views/ + static/`）
- 模块安装即可把前后端能力一并挂载

---

## 12. 如何“从上到下”继续学习（建议路径）

### 第 1 层：先跑起来、会看模块

1. 读 `odoo-bin`、`odoo/cli/server.py`、`odoo/service/server.py`
2. 读一个简单模块 `__manifest__.py` + `models` + `views`
3. 在 UI 中找到该模块菜单，建立“代码 -> 页面”映射

### 第 2 层：掌握框架骨架

1. `odoo/http.py`（Controller/route/dispatcher）
2. `odoo/orm/models.py` + `environments.py` + `registry.py`
3. `odoo/modules/loading.py`（模块安装升级主流程）

### 第 3 层：深挖业务链路

推荐从这条线开始：
- `sale.order.action_confirm`
- `sale_stock` 的 `_action_confirm`
- `stock.rule.run` / `stock.move._action_confirm`
- `sale.order._create_invoices`
- `account.move.action_post`

---

## 13. 二开（自定义模块）落地点

一个标准自定义模块通常至少包含：

- `__manifest__.py`：模块元数据与依赖
- `models/*.py`：业务模型/逻辑
- `views/*.xml`：界面与菜单
- `security/ir.model.access.csv`：访问权限
- `data/*.xml`：初始化数据或计划任务
- `static/src/*`：前端资源（可选）

关键原则：
- 优先“继承扩展”而非改核心源码
- 明确依赖链，避免循环依赖
- 在权限规则、公司隔离、多币种、多语言场景下做回归测试

---

## 14. 给你这份仓库的结论总结

1. 这是一个完整、成熟、超大规模的 ERP 代码库，不是单一功能系统。  
2. 模块生态极其庞大，`l10n_*` 和行业扩展占很大比重。  
3. 技术上是“单体 + 强模块化”，核心价值是跨业务域的统一数据模型与流程编排。  
4. 想真正掌握它，不是先背模块名，而是抓住“启动链 + ORM + 模块加载 + 核心业务链路”这四条主线。  
