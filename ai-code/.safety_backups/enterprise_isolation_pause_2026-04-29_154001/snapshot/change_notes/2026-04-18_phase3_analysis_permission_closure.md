# 2026-04-18 Phase3 Analysis Permission Closure

## Objective

将三期 `所有统计图表`、`物流工作台`、`管理看板` 收口到同一套分析入口权限，避免菜单可见性、统计接口和工作台数据读取口径不一致。

## Outcome

- 新增 `物流分析中心查看 / 管理` 两个共享组
- `所有统计图表`、`物流工作台`、`管理看板` 菜单统一按共享组显示
- `统计图表` 服务层补统一鉴权，无权限时接口返回 `403 forbidden`
- `物流工作台`、`管理看板` 改为走受控 summary 接口，不再直接读取异常模型
- `统计图表` 双指标趋势图补成两条序列分别可点击，避免 `signed_rate` / `timeout_rate` 共用下钻入口

## Changed Files

- `custom_addons/logistics_web/security/logistics_web_security.xml`
- `custom_addons/logistics_web/views/logistics_web_menus.xml`
- `custom_addons/logistics_web/models/__init__.py`
- `custom_addons/logistics_web/models/logistics_stats_service.py`
- `custom_addons/logistics_web/models/logistics_dashboard_service.py`
- `custom_addons/logistics_web/controllers/logistics_web_stats.py`
- `custom_addons/logistics_web/controllers/logistics_web_dashboard.py`
- `custom_addons/logistics_web/static/src/js/actions/dashboard_action_v2.js`
- `custom_addons/logistics_web/static/src/js/actions/boss_trace_action_v2.js`
- `custom_addons/logistics_web/static/src/xml/stats_center_templates.xml`
- `custom_addons/logistics_web/static/src/scss/stats_center.scss`
- `ai-code/前端设计/三期前端优化设计/02_跨模块规范/03_权限与状态/三期物流分析中心权限与状态说明.md`

## Verify

- 待执行 `logistics_web` 模块升级
- 待验证低权限账号的菜单树隐藏与 `403 forbidden`
- 待验证分析查看组账号可正常读取统计页、工作台、管理看板摘要
