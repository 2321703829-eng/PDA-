# 2026-04-17 三期司机管理本地模拟页文案汉化

## 本次变更

- 保留司机管理 `v2` 本地模拟逻辑不变。
- 将司机管理模拟页的按钮、标题、空态、提示语统一改为中文。
- 将模拟数据中的司机状态、风险标签、最近记录状态、区域与门店示例一并改为中文显示。
- 统一画像页中的区块标题、表头、分页按钮、卡片名称和只读提示语。

## 影响范围

- `custom_addons/logistics_web/static/src/js/actions/driver_management_action_v2.js`
- `custom_addons/logistics_web/static/src/xml/driver_management_templates_safe.xml`

## 说明

- 本次仅调整前端展示文案，不改 mock 行为、不改接口路径、不改事件绑定逻辑。
- 改动后需重新升级 `logistics_web` 并强制刷新浏览器静态资源。
