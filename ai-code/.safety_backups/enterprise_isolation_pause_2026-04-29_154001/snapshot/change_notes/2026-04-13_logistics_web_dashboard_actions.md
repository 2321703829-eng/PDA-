# 2026-04-13 Management Dashboard 跳转动作接入

## 背景

`Management Dashboard` 第一版页面已经可展示，但此前仍然只是展示型入口，卡片和队列项未接真实跳转。

## 本次调整

更新文件：

- `custom_addons/logistics_web/static/src/js/actions/dashboard_action.js`
- `custom_addons/logistics_web/static/src/xml/dashboard_templates.xml`
- `custom_addons/logistics_web/static/src/scss/logistics_web.scss`

## 已接入的真实跳转

当前基于仓库里已经存在的 `logistics_dispatch` act_window，接入了这些真实动作：

- 概览卡 -> 运单列表 / 批次列表 / 波次列表
- 优先处理队列 -> 运单或批次详情入口列表
- 下钻目标区 -> 运单 / 批次追踪入口

## 当前限制

由于异常模块的真实 act_window 还未落地：

- “Current Exceptions” 暂时回落到“需要异常审核的运单列表”
- 后续在 `logistics_trace_exception` 落地后，应替换为真正的异常列表页跳转
