# 2026-04-13 logistics_web 模块骨架

## 背景

在完成 `logistics_web` 正式 addon 设计稿后，需要把前端增强层的真实模块骨架先落下来，作为后续前端编码与 GitHub 协作的主承载目录。

## 本次新增

新增目录：

- `custom_addons/logistics_web/`

新增核心文件：

- `custom_addons/logistics_web/__manifest__.py`
- `custom_addons/logistics_web/__init__.py`
- `custom_addons/logistics_web/controllers/`
- `custom_addons/logistics_web/views/`
- `custom_addons/logistics_web/static/src/js/`
- `custom_addons/logistics_web/static/src/xml/`
- `custom_addons/logistics_web/static/src/scss/`

## 当前骨架内容

- 管理工作台 client action 占位
- 老板追溯摘要 client action 占位
- 前端组件占位
- 时间线与证据 widget 占位
- controller 路由占位
- 后端资源与样式入口占位

## 说明

本次仅落模块骨架，不包含：

- 模块安装验证
- Odoo 升级验证
- 前端交互完整实现
- 真实聚合数据接入
