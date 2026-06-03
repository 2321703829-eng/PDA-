# 2026-04-16 天枢科技品牌壳层与导航收口

## Objective

将后台品牌壳层和一级导航进一步收口到二期总纲口径，统一系统名、浏览器标题、主题色和根入口显隐。

## Scope

- [logistics_dispatch_menus.xml](/d:/Desktop/Odoo/custom_addons/logistics_dispatch/views/logistics_dispatch_menus.xml)
- [ui_label_sync.py](/d:/Desktop/Odoo/custom_addons/logistics_web/models/ui_label_sync.py)
- [logistics_web_templates.xml](/d:/Desktop/Odoo/custom_addons/logistics_web/views/logistics_web_templates.xml)
- [home_action.js](/d:/Desktop/Odoo/custom_addons/logistics_web/static/src/js/actions/home_action.js)
- [logistics_web.scss](/d:/Desktop/Odoo/custom_addons/logistics_web/static/src/scss/logistics_web.scss)
- [tianshu_title_service.js](/d:/Desktop/Odoo/custom_addons/logistics_web/static/src/js/services/tianshu_title_service.js)
- [webmanifest.py](/d:/Desktop/Odoo/custom_addons/logistics_web/controllers/webmanifest.py)

## Changes

1. 将根应用品牌统一为 `天枢科技物流系统`，保留 `首页` 作为一级导航中的独立入口。
2. 将后台 HTML 默认标题收口为 `天枢科技物流系统`，并通过标题服务补丁让切换业务页时仍保留系统品牌前缀。
3. 将 `web.webclient_bootstrap` 的 `theme-color` 收口为深蓝色，并同步覆盖 `/web/manifest.webmanifest` 的 `name / background_color / theme_color`。
4. 继续隐藏不应暴露给当前业务用户的根入口：
   - `spreadsheet_dashboard.spreadsheet_dashboard_menu_root`
   - `base.menu_tests`
5. 进一步补强蓝色品牌主题，覆盖常见主按钮、链接、选中态、表单勾选态和焦点态，减少默认紫色残留。
6. 将首页品牌文案从“天枢科技首页”收口为“天枢科技物流系统”，并同步调整加载/报错提示语。

## Verify

计划验证以下结果：

- 浏览器标题默认显示 `天枢科技物流系统`
- 切换到运单、客户明细等业务页后，标题仍保留系统品牌
- `/web/manifest.webmanifest` 返回蓝色主题和系统名
- 根菜单仅保留 `天枢科技物流系统`
- 一级导航顺序保持 `首页 / 物流 / 车队 / 员工 / 库存 / 所有统计图表 / 发票 / 设置`
- 顶栏和常见主交互不再残留默认紫色主题感
