## 变更摘要

- 将登录默认落点从物流根首页拆出，改成独立的企业总入口
- 新增顶层菜单 `logistics_web.menu_tianshu_enterprise_root`
- 首页和“所有统计图表”改挂到企业总入口下
- 物流根菜单收口为纯物流业务入口，不再承担首页默认 action
- 首页品牌、浏览器标题和 web manifest 名称统一从“天枢科技物流系统”调整为“天枢科技企业系统”

## 变更原因

- 当前登录后虽然原生 `Contacts / HR / Fleet` 已经从物流根里拆出，但用户第一屏仍直接进入物流系统首页
- 首页文案强调“先进入企业模块”，但实际挂载位置仍在物流 App 内部，体验和信息架构不一致
- 需要把首页升级成中性的企业总入口，再从首页卡片进入物流、车队、员工、库存、发票等模块

## 涉及文件

- `custom_addons/logistics_web/views/logistics_web_menus.xml`
- `custom_addons/logistics_web/views/logistics_web_actions.xml`
- `custom_addons/logistics_dispatch/views/logistics_dispatch_menus.xml`
- `custom_addons/logistics_web/models/ui_label_sync.py`
- `custom_addons/logistics_web/static/src/js/actions/home_action.js`
- `custom_addons/logistics_web/static/src/xml/home_action_templates.xml`
- `custom_addons/logistics_web/static/src/js/services/tianshu_title_service.js`
- `custom_addons/logistics_web/views/logistics_web_templates.xml`
- `custom_addons/logistics_web/controllers/webmanifest.py`
- `docs/dev/page_conflict_resolution_checklist.md`

## 预期结果

- 登录默认先进入“企业首页”
- 顶层会同时存在“企业首页”和“物流”两个独立入口
- 物流 App 不再自动承接全局首页角色
- 首页文案与挂载位置一致，不再出现“在物流里提示先进入企业模块”的冲突
