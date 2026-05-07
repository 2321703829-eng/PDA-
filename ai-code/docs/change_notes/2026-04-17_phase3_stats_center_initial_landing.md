# 2026-04-17 三期统计图表首版落地

## 本次变更

- 为三期统计图表新增独立入口 `统计图表中心`
- 保留原有 `物流工作台 / 管理看板`，不把二期页面硬改成三期统计中心
- 新增统计聚合服务：
  - `get_stats_page_overview_payload`
  - `get_stats_trend_metrics_payload`
  - `get_stats_distribution_metrics_payload`
  - `get_stats_ranking_metrics_payload`
- 新增统计接口：
  - `GET /api/admin/logistics/stats/overview`
  - `GET /api/admin/logistics/stats/trends`
  - `GET /api/admin/logistics/stats/distributions`
  - `GET /api/admin/logistics/stats/rankings`
- 新增统计前端 action、模板和样式，首版覆盖：
  - 执行概览
  - 风险概览
  - 司机与资源
  - 区域与质量
- 统计排行中的司机项支持继续进入司机画像页

## 主要代码位置

- `custom_addons/logistics_web/models/logistics_stats_service.py`
- `custom_addons/logistics_web/controllers/logistics_web_stats.py`
- `custom_addons/logistics_web/static/src/js/actions/stats_center_action.js`
- `custom_addons/logistics_web/static/src/xml/stats_center_templates.xml`
- `custom_addons/logistics_web/static/src/scss/stats_center.scss`
- `custom_addons/logistics_web/views/logistics_web_actions.xml`
- `custom_addons/logistics_web/views/logistics_web_menus.xml`

## 验证

- 模块升级通过：
  - `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_dev -u logistics_web --stop-after-init`
- 服务侧临时样例数据自测通过：
  - 概览、趋势、分布、排行 4 个接口域均返回有效数据

## 当前已知边界

- 目前未补统计图表本地 mock 模式
- 统计页的最终浏览器级人工点点看还需要继续做一轮
- 旧 `logistics_web_dashboard.py` 仍有 Odoo 19 `type='json'` 弃用告警，但不是本次新增统计接口导致
