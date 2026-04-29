## 变更摘要

- 为企业首页顶层补充一排快捷总导航
- 新增顶部快捷菜单：`物流`、`车队`、`员工`、`库存`、`发票`、`设置`
- 快捷菜单直接指向各模块的原生 action，不重挂原生根菜单树

## 变更原因

- 企业首页拆出来后，顶部横向导航只剩 `首页 / 所有统计图表`
- 用户仍需要一条稳定的企业级总导航，快速在首页直接进入各模块
- 需要补齐总导航，但不能回退到“原生模块树被挂到企业根下面”的旧问题

## 涉及文件

- `custom_addons/logistics_web/views/logistics_web_menus.xml`
- `custom_addons/logistics_web/models/ui_label_sync.py`
- `docs/dev/page_conflict_resolution_checklist.md`

## 预期结果

- 企业首页顶部横条可直接进入 `物流 / 车队 / 员工 / 库存 / 发票 / 设置`
- 原生 `Contacts / 车队 / 员工 / 库存 / 发票 / 设置` 仍作为独立 app 保持存在
- 顶部总导航是快捷入口，不再造成菜单树打架
