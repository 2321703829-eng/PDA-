# 2026-04-13 Odoo 原生模块复用源码入口索引

## 背景

随着前端设计与自定义模块开始进入真实实现阶段，需要一份能直接指导阅读 Odoo 原生源码的入口索引。

此前 `ai-code` 中已有多份文档说明“哪些模块可以复用”，但缺少统一的：

- 模块目录
- 关键模型文件
- 关键视图文件
- 当前项目中的推荐用途
- 不建议硬套的地方

## 本次新增

- `docs/context/Odoo原生模块复用源码入口索引.md`

## 本次实查覆盖

- `contacts`
- `hr`
- `stock`
- `stock_picking_batch`
- `fleet`
- `sale`
- `purchase`
- `account`
- `mail`
- `odoo/addons/base/models`
- `stock_fleet`

## 关键结论

### 1. 现有方向性文档大体正确

以下文档中的模块级判断基本成立：

- `docs/context/odoo_logistics_feasibility.md`
- `docs/architecture/logistics_dispatch_addon_design.md`
- `前端相关设计/01_模块设计/06_业务单据/业务单据前端接入设计草案.md`
- `前端相关设计/01_模块设计/07_商品与基础资料/商品与基础资料模块前端设计草案.md`
- `前端相关设计/01_模块设计/04_运输与调度/运输与调度模块前端设计草案.md`

### 2. 当前最需要的是文件级索引，而不是继续停留在模块名级说明

### 3. 发现的重点差异

- `stock_picking_batch` 存在
- `stock_fleet` 存在
- `stock_delivery_trip` 在当前仓库中不存在

因此：

- `stock_delivery_trip` 不能再被理解成当前仓库中的现成复用模块
- 应将其视为历史设想或未来扩展方向

### 4. 一个常见入口误区

- `contacts` 适合看菜单与联系人入口
- 但 `res.partner` 的核心 Python 定义在 `odoo/addons/base/models/res_partner.py`

## 结果

现在 `ai-code` 中已经同时具备：

- 模块级设计文档
- 前端接入设计文档
- Odoo 原生模块源码入口索引文档

这能更直接支撑后续边读源码边做自定义模块实现。
