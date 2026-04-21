---
name: odoo-frontend-asset-guard
description: Use when working on Odoo backend frontend assets, especially client actions, OWL templates, registry wiring, and asset bundles. Trigger for missing template errors, action registry KeyNotFoundError, manifest asset review, bundle verification, or when preparing or reviewing logistics_web style frontend联调 changes that must survive module upgrade and asset rebuild.
---

# odoo-frontend-asset-guard

## Purpose

Reduce regressions where Odoo frontend source code looks correct but the real bundle misses:

- `registry.category("actions").add(...)`
- OWL templates such as `t-name="..."`
- manifest asset declarations
- module-upgrade or asset-refresh verification

Use this skill both for reactive debugging and for preventive review before联调.

## Core chain

Treat Odoo frontend wiring as one full chain, not separate files:

1. `ir.actions.client` tag
2. JS registry key
3. component `static template`
4. XML `t-name`
5. manifest asset declaration
6. upgraded bundle content

Any link missing can break the page even when the source tree looks mostly correct.

## When to inspect first

For project code, usually inspect these files first:

- `custom_addons/logistics_web/__manifest__.py`
- `custom_addons/logistics_web/views/logistics_web_actions.xml`
- `custom_addons/logistics_web/static/src/js/actions/`
- `custom_addons/logistics_web/static/src/xml/`
- `custom_addons/logistics_web/models/ui_label_sync.py`

If the task is in another addon, map the same chain to that addon rather than assuming `logistics_web`.

## Required workflow

### 1. Source check

Confirm all four mappings line up:

- XML action tag matches JS registry key
- component `static template` matches XML `t-name`
- JS and XML files are both declared in `web.assets_backend`
- module upgrade path still triggers asset regeneration when the project relies on it

### 2. Product check

Never stop at source review for bundle-related bugs. Verify the real built asset result:

- grep the actual bundle for action keys
- grep the actual bundle for template names
- compare bundle reality with source reality

If source has the registration but bundle does not, classify it as an asset assembly problem, not a simple “forgot to write the line” problem.

### 3. Fix strategy

Prefer asset-hardening changes over fragile one-line patches:

- move action registration into a small dedicated bootstrap file
- split critical templates into separate XML files
- use explicit manifest asset entries for key JS/XML files
- avoid relying on large mixed files for critical registry or template loading

### 4. Upgrade verification

After code changes, require this sequence:

1. update code
2. upgrade target addon
3. restart Odoo if needed
4. open with `?debug=assets`
5. force-refresh browser
6. verify real page behavior
7. verify built bundle content if the bug class is asset-related

## Prevention rules

Use these as default review standards for new or changed client actions.

### Code organization

- keep client action registration in a dedicated small registry entry file when the page is important
- prefer one page / one action file / one template file for critical pages
- split homepage, dashboard, boss/manager pages instead of combining them in one large XML
- use explicit manifest entries for critical assets instead of broad `*.xml` or `*.js` when stability matters

### Review checklist

- does `ir.actions.client.tag` equal the JS registry key
- does `static template` equal the XML `t-name`
- are both JS and XML present in manifest assets
- if `*_v2.js` exists, is the manifest clearly using the active version
- is there any old file that could confuse reviewers or future edits

### Bundle checklist

For asset-sensitive pages, verify the built bundle contains:

- action keys such as `logistics_web.dashboard`
- template names such as `logistics_web.HomeAction`

Do not rely only on “page opens for me”.

## Recommended debug pattern

When you see these errors, bias toward these diagnoses:

- `Missing template: "..."`
  Usually component JS loaded but template asset did not land in the template registry.

- `Cannot find key "..." in the "actions" registry`
  Usually XML action exists but the JS registration did not land in the real bundle.

- both errors together
  Usually the asset bundle is incomplete, stale, or assembled in a fragile way.

## Minimal validation commands

Use lightweight static checks before upgrade:

```powershell
node --check custom_addons/logistics_web/static/src/js/actions/home_action.js
node --check custom_addons/logistics_web/static/src/js/actions/dashboard_action_v2.js
node --check custom_addons/logistics_web/static/src/js/actions/boss_trace_action_v2.js
```

For XML parsing:

```powershell
@'
from pathlib import Path
import xml.etree.ElementTree as ET
for p in [
    Path(r'custom_addons/logistics_web/static/src/xml/home_action_templates.xml'),
    Path(r'custom_addons/logistics_web/static/src/xml/dashboard_action_templates.xml'),
    Path(r'custom_addons/logistics_web/static/src/xml/boss_trace_action_templates.xml'),
]:
    ET.parse(p)
    print(f"OK {p}")
'@ | python -
```

For source grep:

```powershell
rg -n --fixed-strings 'registry.category("actions").add' custom_addons/logistics_web/static/src/js/actions
rg -n --fixed-strings 'logistics_web.HomeAction' custom_addons/logistics_web
rg -n --fixed-strings 'logistics_web.dashboard' custom_addons/logistics_web
```

## Output expectation

When using this skill, respond with:

1. source-chain conclusion
2. bundle/product conclusion
3. likely root cause class
4. safest fix path
5. explicit upgrade and verification steps

If code changes are made, also update:

- `ai-code/docs/change_notes/`

## Project-specific reminder

For this repository, if a frontend asset issue is fixed in real code:

- sync the related `change_notes`
- prefer narrow, compatible fixes
- avoid reverting unrelated work in a dirty tree
