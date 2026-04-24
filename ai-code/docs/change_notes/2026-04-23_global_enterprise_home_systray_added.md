# 2026-04-23 全局企业首页返回入口补齐

## 背景

此前只在物流工作台内补了返回企业首页入口，员工、发票、库存等原生模块仍然缺少统一返回方式，导致跨模块切换后用户不知道如何回到企业首页。

## 本次调整

- 在 `logistics_web` 增加全局顶栏 systray 组件 `企业首页`
- 该按钮常驻于系统顶栏，可在任意模块内点击返回企业首页
- 返回逻辑优先走菜单上下文：
  - `logistics_web.menu_tianshu_enterprise_root`
  - 回退到 `logistics_web.menu_logistics_web_home`
  - 再回退到 `logistics_web.action_logistics_web_home`

## 涉及文件

- `custom_addons/logistics_web/static/src/js/components/enterprise_home_systray.js`
- `custom_addons/logistics_web/static/src/xml/widget_templates.xml`
- `custom_addons/logistics_web/static/src/scss/enterprise_home_systray.scss`

## 验证

- `node --check custom_addons/logistics_web/static/src/js/components/enterprise_home_systray.js`
- `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_web --stop-after-init`

## 预期结果

- 在 `物流 / 员工 / 车队 / 库存 / 发票 / 设置` 等页面顶部，都能看到同一颗 `企业首页` 按钮
- 点击后返回 `天枢科技企业系统 / 首页`
