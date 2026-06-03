## 变更摘要

- 为物流 app 顶栏补充 `企业首页` 返回入口
- 为物流工作台页头补充 `返回企业首页` 和 `查看统计图表` 按钮
- 物流工作台 client action 切回标准 `Layout` 外壳

## 变更原因

- 用户进入物流 app 后缺少明确的返回企业首页入口
- 物流工作台未使用标准 `Layout` 容器，页面滚动和页面框架行为不稳定
- 需要同时修复导航可回退性和页面容器稳定性

## 涉及文件

- `custom_addons/logistics_web/static/src/js/actions/dashboard_action_v2.js`
- `custom_addons/logistics_web/static/src/xml/dashboard_action_templates.xml`
- `custom_addons/logistics_web/static/src/scss/dashboard.scss`
- `custom_addons/logistics_dispatch/views/logistics_dispatch_menus.xml`
- `custom_addons/logistics_web/models/ui_label_sync.py`
- `docs/dev/page_conflict_resolution_checklist.md`

## 预期结果

- 在物流 app 顶栏可直接点击 `企业首页`
- 在物流工作台页头可直接点击 `返回企业首页`
- 物流工作台恢复正常滚动，不再出现底部内容无法继续浏览的问题
