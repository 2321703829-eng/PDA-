# 2026-04-23 物流顶栏重复企业首页入口下线

## 背景

在补齐全局顶栏 `企业首页` 按钮后，`物流` 模块顶栏仍保留了一颗同名菜单，形成重复入口，容易让页面结构显得混乱。

## 本次调整

- 移除 `logistics_dispatch` 菜单定义中的 `menu_logistics_dispatch_enterprise_home`
- 在升级时将该菜单记录显式设为 `active = False`
- 在 `ui_label_sync` 中同步约束该菜单为停用状态，避免后续升级再次被激活

## 涉及文件

- `custom_addons/logistics_dispatch/views/logistics_dispatch_menus.xml`
- `custom_addons/logistics_web/models/ui_label_sync.py`

## 验证

- `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_dispatch,logistics_web --stop-after-init`
- `env.ref('logistics_dispatch.menu_logistics_dispatch_enterprise_home').active == False`

## 预期结果

- 物流顶栏不再出现重复的 `企业首页`
- 系统全局只保留右上角统一的 `企业首页` 返回入口
