## 变更摘要

- 回滚企业首页顶部错误加上的快捷总导航
- 企业首页顶层重新收口为 `首页 / 所有统计图表`
- 显式停用上批次已经写进数据库的企业快捷菜单
- 物流恢复为独立业务 app，并将核心业务入口直接挂到物流根下

## 变更原因

- 企业首页顶部快捷菜单直接绑定原生 action，破坏了 Odoo 原生菜单上下文
- 这导致点击 `物流` 只打开工作台 action，无法继续看到运单、导入等菜单入口
- 点击 `员工` 等快捷菜单时也可能直接进入不正确的视图状态
- 需要回到稳定规则：
  - 企业首页只保留企业自有页面
  - 有自研页的模块优先走自研页
  - 没有完整替代页的模块保留原生入口

## 涉及文件

- `custom_addons/logistics_web/views/logistics_web_menus.xml`
- `custom_addons/logistics_dispatch/views/logistics_dispatch_menus.xml`
- `custom_addons/logistics_web/models/ui_label_sync.py`
- `docs/dev/page_conflict_resolution_checklist.md`

## 预期结果

- 企业首页顶部不再伪装成全系统总导航
- 物流 app 作为独立入口可直接看到工作台、调度、运单、异常、导入、司机管理、车辆管理等一级菜单
- 员工、车队、库存、发票、设置继续使用原生 app 入口，不再通过企业首页顶部快捷菜单强行跳转
