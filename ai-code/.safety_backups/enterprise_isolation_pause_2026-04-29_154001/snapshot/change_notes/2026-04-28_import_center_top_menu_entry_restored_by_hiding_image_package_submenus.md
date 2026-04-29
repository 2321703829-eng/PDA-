# 2026-04-28 Import Center Top Menu Entry Restored By Hiding Image Package Submenus

## Background

After wiring `image_package` into the existing import center, two visible submenu entries were added under:

- `logistics_dispatch.menu_logistics_dispatch_import_center`

The import-center client action itself still worked by direct action id, but the top navigation entry no longer behaved like the original direct-entry menu during manual verification.

## Change

- kept the `image_package` feature in the import-center page flow
- kept the backend actions for image-package import/task access
- marked these submenu entries inactive so the top `导入中心` menu returns to direct-entry behavior:
  - `menu_logistics_trace_image_package_import`
  - `menu_logistics_trace_image_package_tasks`

## Result

- original top `导入中心` menu can continue to act as the primary direct entry
- `image_package` remains reachable from the import-center page buttons instead of competing with the top menu tree

