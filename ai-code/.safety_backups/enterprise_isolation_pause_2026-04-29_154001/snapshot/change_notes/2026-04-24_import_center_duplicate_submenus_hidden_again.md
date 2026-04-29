# 2026-04-24 Import Center Duplicate Submenus Hidden Again

## What Changed

- Hid the two duplicate import-center submenu entries again:
  - `配送节点明细导入`
  - `货物明细导入`
- Restored the intended product shape where the left navigation only keeps a single `导入中心`.
- Kept the import-center page itself intact, including the export shortcut area inside the page.

## Why

- The two submenu entries pointed to nearly the same import-center page and created confusion about where standard waybill import should happen.
- The correct interaction is:
  - left navigation keeps one `导入中心`
  - standard import stays in that single center
  - customer/product export shortcuts live inside the page rather than as duplicate submenu entries

## Verification

- Python AST parse for `custom_addons/logistics_web/models/ui_label_sync.py`
- XML parse for `custom_addons/logistics_dispatch/views/logistics_dispatch_menus.xml`
- Module upgrade required for menu state refresh
