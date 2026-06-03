# AI Entry Guide For Odoo Logistics

## Scope

This file is the `ai-code/` mirror of the repository-level guide in [`../AGENTS.md`](d:/Desktop/Odoo/AGENTS.md).

The root file is the canonical version for the whole `Odoo` workspace.

Use this local file as a convenient entry when working inside `ai-code/`, but keep it aligned with the root guide.

## Project Summary

Odoo 19.0 logistics customization project.

Current effective business baseline:

- execution main line: `wave -> batch -> waybill -> customer_line -> order_line -> goods_line`
- page main reading chain: `waybill -> customer_line -> order_line`
- image reading chain: `waybill -> customer_line -> 图片预览 / 留痕 / 证据`
- trace main line: `waybill -> trace -> evidence -> exception`
- `waybill` is the current trace main object
- `customer_line` is the current store-side reading entry, but it does not replace `trace_event` as the formal trace event anchor
- logistics core capability should be carried by custom addons

## Read Order

1. Read the root guide at `../AGENTS.md`.
2. Read `docs/context/odoo_logistics_context.md`.
3. Read `docs/context/odoo_logistics_feasibility.md`.
4. Read `docs/context/Odoo原生模块复用源码入口索引.md`.
5. Read `docs/architecture/ARCHITECTURE.md`.
6. Read the relevant frontend or module design notes under `ai-code/`.
7. Then read the related official addons and any custom addons.

## Key Reminder

- `stock_delivery_trip` is not present in the current repository.
- Historical names such as `logistics_order`, `logistics_trace`, and `logistics_exception` should be treated as bridge or archive terminology unless a document explicitly says it is historical.
- Any real code or document change must update `docs/change_notes/`.

## Local Skill Auto Routing

- Treat `.agents/skills/` as the local scenario playbook for this workspace.
- If the user's request clearly matches a local skill, proactively read and apply that `SKILL.md` without waiting for the user to name it explicitly.
- Use `docs/ai/skill_router.md` as the default routing index when deciding which local skill to read first.
- Typical auto-routing examples:
  - model design, model review, official-vs-custom model choice: `odoo-model-review`
  - Odoo backend frontend asset, client action, OWL template, bundle, registry issue: `odoo-frontend-asset-guard`
  - warehouse or logistics backend page design alignment: `logistics-style-alignment`
  - code or implementation review: `spec-review-evidence-first`
  - upgrade compatibility, field/state/XML ID/API contract risk: `odoo-compatible-upgrade-guard`
  - doc impact and change-note sync: `doc-sync-review`
- If a request matches multiple local skills, use the smallest useful combination and state the order briefly in the working update.

## Design Consistency Standard

- For warehouse module pages and other adjacent backend modules, default to the existing logistics module style.
- Reuse logistics page structure, interaction rhythm, button placement, state display, and page flow before introducing new patterns.
- Treat warehouse and logistics as sibling modules inside one system: business content may differ, but overall backend style should stay aligned.
- Before proposing a new warehouse page layout, first identify the closest logistics reference page and adapt from it.

For the full working rules, follow the root guide in [`../AGENTS.md`](d:/Desktop/Odoo/AGENTS.md).
