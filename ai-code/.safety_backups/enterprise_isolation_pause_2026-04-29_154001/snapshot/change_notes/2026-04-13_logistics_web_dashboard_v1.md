# 2026-04-13 Management Dashboard 第一版

## 背景

`logistics_web` 模块骨架已经建立，需要先把 `Management Dashboard` 从占位 client action 推进成第一版可展示页面。

## 本次调整

更新文件：

- `custom_addons/logistics_web/static/src/js/actions/dashboard_action.js`
- `custom_addons/logistics_web/static/src/xml/dashboard_templates.xml`
- `custom_addons/logistics_web/static/src/scss/logistics_web.scss`

## 第一版包含内容

- 顶部标题区
- 今日概览卡区
- 优先处理队列
- 最近变化区
- 下一步下钻入口提示

## 当前数据策略

- 优先读取 `/api/admin/logistics/dashboard/summary`
- 如果接口暂未就绪，则自动回退到本地占位数据

## 说明

本次仅完成第一版可展示页面，不包含：

- 真实聚合字段接入
- 跳转行为接入
- 卡片点击下钻
- 权限态差异渲染
