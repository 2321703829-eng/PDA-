# AI Entry Guide For Odoo Logistics

## Scope

This file is the `ai-code/` mirror of the repository-level guide in [`../AGENTS.md`](d:/Desktop/Odoo/AGENTS.md).

The root file is the canonical version for the whole `Odoo` workspace.

Use this local file as a convenient entry when working inside `ai-code/`, but keep it aligned with the root guide.

## Project Summary

Odoo 19.0 logistics customization project.

Current effective business baseline:

- execution main line: `wave -> batch -> waybill -> waybill order lines`
- trace main line: `waybill -> trace -> evidence -> exception`
- `waybill` is the current trace main object
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

For the full working rules, follow the root guide in [`../AGENTS.md`](d:/Desktop/Odoo/AGENTS.md).
