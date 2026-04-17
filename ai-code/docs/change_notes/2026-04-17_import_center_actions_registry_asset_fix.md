# 2026-04-17 导入中心 actions registry 资产修复

## 问题

进入“导入中心”时前端报错：

- `KeyNotFoundError: Cannot find key "logistics_web.import_center" in the "actions" registry`

表现为客户端动作 `logistics_web.import_center` 已在 XML 中定义，但浏览器端 action registry 中没有对应注册项。

## 原因

`logistics_web` 模块的 `__manifest__.py` 中，`web.assets_backend` 只显式加载了：

- `home_action.js`
- `dashboard_action_v2.js`
- `boss_trace_action_v2.js`

而导入中心的前端动作文件：

- `logistics_web/static/src/js/actions/import_center_action.js`

没有进入后台资产包，导致：

1. 菜单/客户端动作能跳到 `tag = logistics_web.import_center`
2. 但前端实际没有执行 `registry.category("actions").add("logistics_web.import_center", ...)`
3. 最终触发 actions registry 缺 key 报错

## 修复

在 `custom_addons/logistics_web/__manifest__.py` 的 `web.assets_backend` 中显式补充：

- `logistics_web/static/src/js/actions/import_center_action.js`

## 为什么不直接改成 `actions/*.js`

当前 `static/src/js/actions/` 目录里同时存在旧版和 V2 版文件：

- `dashboard_action.js`
- `dashboard_action_v2.js`
- `boss_trace_action.js`
- `boss_trace_action_v2.js`

它们会重复注册相同的 action key：

- `logistics_web.dashboard`
- `logistics_web.boss_trace`

如果直接改成 `actions/*.js`，会引入重复注册风险，可能把当前可用页面一并打坏。

因此本次采用最小修复面：

- 只补 `import_center_action.js`

## 建议验证

1. 重启 Odoo 常驻服务
2. 升级 `logistics_web` 模块
3. 浏览器 `Ctrl + F5` 强刷
4. 再次进入“导入中心”，确认不再出现 actions registry 缺 key 报错
