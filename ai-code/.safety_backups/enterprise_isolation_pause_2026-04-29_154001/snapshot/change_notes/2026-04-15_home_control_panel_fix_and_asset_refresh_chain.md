# 2026-04-15 首页白条修复与前端资源刷新链路收口

## 本次处理

- 将 `logistics_web.home` 首页 client action 改为 Odoo 19 标准 `Layout` 接法。
- 首页 action 显式传入 `display.controlPanel = false`，避免空控制栏在首页顶部渲染出白色留白区域。
- 在 `logistics_web` 升级数据函数中加入 `ir.attachment.regenerate_assets_bundles()`，升级模块时自动失效旧的 `/web/assets/*` 资源附件。
- 收口首页 hero 区品牌胶囊、日期胶囊和副标题的颜色层级，避免浅色胶囊继续继承白字导致“看起来像空白残留”。

## 影响文件

- `custom_addons/logistics_web/static/src/js/actions/home_action.js`
- `custom_addons/logistics_web/static/src/xml/dashboard_templates.xml`
- `custom_addons/logistics_web/models/ui_label_sync.py`

## 目的

- 修复首页顶部白条问题。
- 避免模块已升级但前端仍持续加载旧 bundle，导致首页新样式和新结构不生效。
- 提高首页 hero 区可读性，避免白底浅字和低对比度副标题继续造成视觉误判。
