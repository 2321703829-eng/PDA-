# 2026-04-10 document rebaseline

## Summary

Rebased the ai-code working documents according to the real project status learned from D:\Desktop\ai-code-main\ai-code\系统设计\.

## What changed

- rewrote docs/context/odoo_logistics_context.md
- rewrote docs/context/odoo_logistics_master_data_draft.md
- rewrote docs/architecture/custom_addons_blueprint.md
- rewrote docs/architecture/logistics_base_addon_design.md
- added docs/dev/next_step_plan_2026-04-10.md

## Key decision

The current project should no longer assume that customer, store, employee, and warehouse modules are already concretely designed.

The next main line should move to:

- order mapping
- trace and image mapping
- exception boundary design

logistics_base remains useful as a technical scaffold, but not as the current highest-priority business module.

## Verification

- document-only changes
- no compilation
- no service startup
- no module upgrade
