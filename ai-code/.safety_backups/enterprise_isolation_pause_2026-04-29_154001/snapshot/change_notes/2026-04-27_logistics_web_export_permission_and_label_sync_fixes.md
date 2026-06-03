# 2026-04-27 logistics_web export permission and label sync fixes

## Objective

收口 `logistics_web` 中 3 个已确认风险点：

1. 司机路线 Excel 直下接口缺少独立导出权限护栏。
2. 客户/商品画像导出按钮可绕过专用导出分组。
3. `ui_label_sync` 在模块升级时会触发全局菜单副作用和资产重建。

## Scope

- `custom_addons/logistics_dispatch/security/ir.model.access.csv`
- `custom_addons/logistics_web/services/dispatch_main_export_service.py`
- `custom_addons/logistics_web/services/driver_route_excel_export_service.py`
- `custom_addons/logistics_web/views/logistics_web_batch_views.xml`
- `custom_addons/logistics_web/views/logistics_web_profile_views.xml`
- `custom_addons/logistics_web/models/ui_label_sync.py`

## Changes

### 1. 导出能力统一收口到 export group

- 将 `logistics.export.source.scope` 和 `logistics.export.task` 的 `create` 权限从 `base.group_user` 收紧到 `group_logistics_export_user / group_logistics_export_manager`。
- 在 `DispatchMainExportService._check_export_model_access()` 中新增显式导出分组校验，并把 ACL 拒绝统一转成 `EXPORT_PERMISSION_DENIED`。
- 在 `DriverRouteExcelExportService.export_by_delivery_date()` 中新增独立导出权限校验，防止普通内部用户继续按日期直下全量路线。

### 2. 前端入口和后端服务一起收口

- 给批次页司机路线导出按钮补了 `groups="logistics_dispatch.group_logistics_export_user"`。
- 给客户画像、商品画像、商品规格画像 3 个导出按钮都补了相同的 `groups` 限制。
- 这样 UI 层和 service 层口径一致，既不会误展示按钮，也不会留下对象方法直调绕过口。

### 3. 缩小 label sync 升级副作用

- `ui_label_sync` 保留对物流自有菜单和 action 的名称同步。
- 删除了对 `contacts / hr / fleet / stock / account / base` 等非物流根菜单的重排逻辑。
- 删除了对 `mail / utm / spreadsheet / base` 等无关菜单的统一停用逻辑。
- 删除了升级后强制 `regenerate_assets_bundles()` 的全局资产重建动作。

## Verify

### Static

- Python AST parse 通过：
  - `dispatch_main_export_service.py`
  - `driver_route_excel_export_service.py`
  - `ui_label_sync.py`
- XML parse 通过：
  - `logistics_web_profile_views.xml`
  - `logistics_web_batch_views.xml`

### Upgrade

已执行：

```powershell
python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_dispatch,logistics_web --stop-after-init
```

结果：升级成功。

### Minimal smoke

使用普通内部用户 `export_smoke_owner (id=8)` 验证：

- 司机路线导出：`EXPORT_PERMISSION_DENIED`
- 客户画像导出任务创建：`EXPORT_PERMISSION_DENIED`
- 商品画像导出任务创建：`EXPORT_PERMISSION_DENIED`

源码级复查确认 `ui_label_sync.py` 中已不存在以下副作用调用：

- `regenerate_assets_bundles`
- `contacts.menu_contacts`
- `mail.menu_root_discuss`
- `base.menu_management`

## Risk / Follow-up

- 当前 `odoo_logistics_phase4_v1` 库里没有任何已分配 `group_logistics_export_user` 的测试账号，因此这轮没有做“授权用户仍可成功导出”的运行态正向 smoke。
- 这次修复保证了未来升级不再继续放大全局菜单和资产副作用，但不会自动回滚历史升级已经写入数据库的无关菜单状态。如果后续需要，可单独补一次“非物流菜单状态回正”治理脚本。
