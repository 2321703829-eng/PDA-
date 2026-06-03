# 2026-05-29 Internal Web Design Refresh

## Scope

- `custom_addons/logistics_web`

## Source Of Truth

- The live kebi web code was synced from `/mnt/extra-addons/logistics_web` before editing.
- The current web UI is treated as the baseline for menus, actions, and workflow behavior.

## Changes

- Added a generated internal dashboard network hero asset:
  - `logistics_web/static/src/img/tianshu-data-network-hero.png`
- Reworked the enterprise home template visual structure:
  - Added a clean SaaS-style top bar.
  - Kept the existing live module card data and click handlers.
  - Added module `data-module` attributes for visual-only tile styling.
  - Converted the module entry area into responsive tile blocks.
- Expanded backend visual overrides in `99_kebi_visual_consistency.scss`:
  - White SaaS-style top navigation.
  - Neutral grey app canvas.
  - Network-image hero treatment for custom logistics pages.
  - Unified list, form, kanban, dropdown, modal, button, and input surfaces.
- Added a final theme layer in `zz_tianshu_final_theme.scss`:
  - Restores readable dark text in the white backend navigation.
  - Removes the large homepage hero headline from the visual layout.
  - Replaces the old blue homepage block with a compact network-console banner.
  - Fixes the business workspace heading/card overlap and card text layout.
- Refined the backend top bar and account menu:
  - Renamed the product shell from `天枢科技企业系统` to `天枢科技物流系统`.
  - Added stronger nav text overrides for Odoo's user/company menu selectors.
  - Deduplicated avatar-only systray buttons visually.
  - Cleaned the user menu to keep `个人中心` and `退出登录` while hiding Odoo help/account entries.
  - Added a stricter fix for Odoo's image-brand navbar text and duplicate initial-only avatar buttons.
  - Replaced the native Odoo user menu with a dedicated Tianshu account systray, then hid `.o_user_menu`.

## Non-Goals

- No business model changes.
- No workflow/action changes.
- No changes to button meaning, domains, permissions, or data processing.

## Verification

- Parsed `home_action_templates.xml` as XML.
- Parsed all `logistics_web` XML files as XML.
- Ran `node --check` on `home_action.js`.
- Ran `node --check` on the visual text patch, title service, and home systray component.
- Parsed changed Python files with `ast.parse`.
- Upgraded `logistics_web` on `tenant_kebi`; Odoo reported `0 failed, 0 error(s)`.
- Verified `web.assets_backend.css` compiles and contains the new homepage/topbar styles.
- Verified the new hero image is served at `/logistics_web/static/src/img/tianshu-data-network-hero.png`.
