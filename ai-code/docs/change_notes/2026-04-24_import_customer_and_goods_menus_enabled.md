# 2026-04-24 配送节点明细导入与货物明细导入菜单已改为可见

## 本次变更

- 在 `custom_addons/logistics_dispatch/views/logistics_dispatch_menus.xml` 放开以下菜单的隐藏限制：
  - `menu_logistics_dispatch_import_customer_line`
  - `menu_logistics_dispatch_import_customer_goods_line`
- 移除了这两个菜单上的 `base.group_no_one` 限制。
- 删除了这两个菜单对应的 `active = False` 记录，避免安装后默认隐藏。
- 在 `custom_addons/logistics_web/models/ui_label_sync.py` 将以下菜单的同步状态改为可见：
  - `logistics_dispatch.menu_logistics_dispatch_import_customer_line`
  - `logistics_dispatch.menu_logistics_dispatch_import_customer_goods_line`

## 当前状态

- XML 解析已通过：
  - `custom_addons/logistics_dispatch/views/logistics_dispatch_menus.xml`
- Python AST 检查已通过：
  - `custom_addons/logistics_web/models/ui_label_sync.py`
- 尚未执行：
  - 模块升级
  - 页面人工核验

## 下一步建议

- 升级 `logistics_dispatch` 与 `logistics_web`。
- 升级后到 `物流 -> 导入中心` 下确认以下两个菜单已可见：
  - 配送节点明细导入
  - 货物明细导入
