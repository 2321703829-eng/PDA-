## 变更摘要

- 企业首页模块卡片从直接 `doAction(actionXmlid)` 改成优先按菜单上下文进入
- 首页卡片现在通过 Odoo `menuService.selectMenu(menu)` 进入 `物流 / 车队 / 员工 / 库存 / 发票 / 设置 / 所有统计图表`

## 变更原因

- 直接跳原生 action 会绕开 Odoo 菜单上下文
- 这会导致点击 `员工`、`车队` 等模块时进入错误视图，甚至直接落到新建页
- 模块卡片应该和真实菜单入口保持一致，先进入菜单上下文，再打开对应页面

## 涉及文件

- `custom_addons/logistics_web/static/src/js/actions/home_action.js`
- `docs/dev/page_conflict_resolution_checklist.md`

## 预期结果

- 首页卡片点击行为与顶部/原生菜单保持一致
- `员工 / 车队 / 库存 / 发票 / 设置` 不再因为裸跳 action 而丢失菜单上下文
- `物流` 卡片进入物流 app 上下文，不再只打开一个脱离菜单树的工作台 action
