# 2026-04-17 logistics_web action registry 与模板资产加固

## 问题

联调环境实际运行的前端 bundle 中出现了两类不一致：

- `logistics_web.dashboard` 与 `logistics_web.boss_trace` 的 action registry key 未进入产物
- `logistics_web.HomeAction` 模板在页面运行时未能从 OWL 模板库中找到

源码侧虽然已有对应 action class、template 名称与 asset 声明，但最终产物不稳定，说明问题更接近资产编译结果不确定，而不只是 XML tag 或浏览器缓存。

## 本次修复

为了降低大文件尾部注册语句或多模板合并文件在 bundle 中丢失的风险，改为更显式的资产组织方式：

1. 新增独立 action 注册引导文件  
   `custom_addons/logistics_web/static/src/js/actions/logistics_action_registry.js`

2. 将以下 action 的 `registry.category("actions").add(...)` 从各自实现文件中移除，统一收口到 registry 引导文件：
   - `home_action.js`
   - `dashboard_action_v2.js`
   - `boss_trace_action_v2.js`
   - `import_center_action.js`
   - `driver_management_action_v2.js`

3. 将原本合并在 `dashboard_templates.xml` 中的模板拆成独立文件：
   - `home_action_templates.xml`
   - `dashboard_action_templates.xml`
   - `boss_trace_action_templates.xml`

4. 更新 `custom_addons/logistics_web/__manifest__.py`
   - 在 `web.assets_backend` 中显式加入 `logistics_action_registry.js`
   - 不再声明旧的 `dashboard_templates.xml`
   - 改为显式声明上述 3 个独立模板文件

## 目的

- 让 `logistics_web.home / dashboard / boss_trace / import_center / driver_management` 的 action 注册进入一个很小、可单独 grep 的稳定入口
- 让首页、工作台、管理看板模板不再共享同一个大 XML 文件，降低整段模板在 bundle 里丢失的风险
- 保持现有 `ir.actions.client` tag、组件类名、模板名和业务行为不变，只加固资产装配链路

## 影响范围

- `logistics_web` 前端资产组织方式
- 不改数据库模型
- 不改 `ir.actions.client` tag
- 不改页面交互语义

## 验证建议

升级 `logistics_web` 后重点检查：

1. bundle 中可 grep 到以下 action key：
   - `logistics_web.home`
   - `logistics_web.dashboard`
   - `logistics_web.boss_trace`
   - `logistics_web.import_center`
   - `logistics_web.driver_management`

2. bundle 中可 grep 到以下模板名：
   - `logistics_web.HomeAction`
   - `logistics_web.DashboardAction`
   - `logistics_web.BossTraceAction`

3. 后台页面验证：
   - 首页不再报 `Missing template: "logistics_web.HomeAction"`
   - 物流工作台不再报 `Cannot find key "logistics_web.dashboard" in the "actions" registry`
   - 管理看板可正常打开
