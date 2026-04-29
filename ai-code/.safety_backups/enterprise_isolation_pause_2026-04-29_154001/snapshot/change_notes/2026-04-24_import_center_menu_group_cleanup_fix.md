# 2026-04-24 Import Center Menu Group Cleanup Fix

## What Changed

- Enhanced `logistics_web.models.ui_label_sync.IrUiMenu._sync_menu` to support explicit menu group synchronization through `group_xmlids`.
- Cleared residual menu groups for:
  - `logistics_dispatch.menu_logistics_dispatch_import_customer_line`
  - `logistics_dispatch.menu_logistics_dispatch_import_customer_goods_line`
- Kept the two import-center submenu entries active and visible for normal backend users during label sync.

## Why

- The two submenu entries were still hidden after activation because old database state retained `Technical Features` on `ir.ui.menu.group_ids`.
- XML-level activation alone was not enough because the label-sync function runs during module upgrade and needed to own menu group cleanup as well.

## Verification

- Python AST parsing for `custom_addons/logistics_web/models/ui_label_sync.py`
- Module upgrade required to apply the menu sync write path to the database
