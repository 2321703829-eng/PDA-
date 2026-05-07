# 2026-04-15 导航收口与统计入口上提

## 本次处理

- 顶部一级导航顺序调整为：首页、物流、车队、员工、库存、所有统计图表、发票、设置。
- 将用户可见的 `数据看板` 入口统一改名为 `所有统计图表`。
- 首页系统模块卡片顺序同步调整为：物流、车队、员工、库存、所有统计图表、发票、设置。
- 隐藏当前阶段不面向业务用户的模块入口：
  - `讨论`
  - `联系人`
  - `链接追踪器`
  - `应用`
- 隐藏桌面端左上角 Odoo apps menu 入口，避免继续暴露 Odoo 风格应用切换器。

## 影响文件

- `custom_addons/logistics_web/models/ui_label_sync.py`
- `custom_addons/logistics_web/views/logistics_web_menus.xml`
- `custom_addons/logistics_web/static/src/js/actions/home_action.js`
- `custom_addons/logistics_web/static/src/scss/logistics_web.scss`

## 目的

- 让顶层导航与最新版品牌化重构方案保持一致。
- 避免 `链接追踪器 / 应用` 等无关模块继续从顶栏入口泄漏。
- 让统计入口以 `所有统计图表` 的业务化名称直接呈现在一级导航与首页模块区中。
