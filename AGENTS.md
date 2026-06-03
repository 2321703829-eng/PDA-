# AI Entry Guide For Odoo Logistics

## Scope

This file is the repository-level agent guide for the whole `Odoo` workspace.

It applies to:

- `addons/`
- `odoo/`
- `custom_addons/`
- `ai-code/`
- other repository files and supporting directories

If a more local `AGENTS.md` exists in a subdirectory, treat it as a narrower supplement rather than a replacement unless it explicitly says otherwise.

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

1. Read this file first.
2. Read `ai-code/docs/context/odoo_logistics_context.md`.
3. Read `ai-code/docs/context/odoo_logistics_feasibility.md`.
4. Read `ai-code/docs/context/Odoo原生模块复用源码入口索引.md`.
5. Read `ai-code/docs/architecture/ARCHITECTURE.md`.
6. Read the relevant frontend or module design notes under `ai-code/`.
7. Then read the related official addons and any custom addons.

## Default Working Mode

For non-trivial implementation work, follow this sequence explicitly:

1. `Understand`
2. `Spec`
3. `Plan`
4. `Implement`
5. `Verify`
6. `Document`

Before coding, lock OBB for the target change:

- `Outcome`: what must become true after the change
- `Behavior`: input, output, flow, rules, and visible behavior
- `Boundary`: ownership, compatibility, exception cases, and what is out of scope

If OBB is unclear, do not jump directly into code. Update or add the relevant design note or spec first.

## Odoo Baseline Comparison

Before designing a new capability or extending an existing one:

1. Identify the related Odoo native module, model, view, or workflow.
2. State what Odoo already supports.
3. State what the project still lacks.
4. Choose one path explicitly:
   - reuse directly
   - extend Odoo
   - create custom capability

Default preference:

1. Reuse Odoo native capability when it already fits.
2. Extend Odoo when the native object is correct but incomplete for the business.
3. Build custom capability only when the business object or evidence flow is not naturally represented by Odoo.

## Spec-First Change Rule

Before code changes, update or add the relevant spec when the change affects:

- module responsibilities
- business flow
- API path, request, response, or DTO
- event names or event payloads
- SQL tables, fields, indexes, or query paths
- page information architecture or interaction flow
- naming, enum, or state rules

Implementation should happen only after the spec is stable enough to verify.

## Official Vs Custom

- `contacts`, `hr`, and `stock` are the main official master-data foundation.
- `sale` is a reference for document flow and status design, not the logistics business master model.
- `mail` is the base capability for trace, exception, chatter, attachment, and activity.
- `fleet` and `stock_fleet` are reusable official foundations when vehicle context is needed.
- `stock_delivery_trip` is not present in the current repository. Do not treat it as an available base module.
- Logistics business objects should be implemented in custom addons, not by directly modifying official addon logic.

## Current Module Direction

Current active custom direction is:

- `logistics_base`
- `logistics_dispatch`
- `logistics_trace_core`
- `logistics_trace_evidence`
- `logistics_trace_exception`
- future `logistics_trace_dashboard`

Historical names such as `logistics_order`, `logistics_trace`, and `logistics_exception` should be treated as bridge or archive terminology unless a document explicitly says it is historical.

## Hard Rules

- Do not directly modify official core addons unless explicitly approved and unavoidable.
- Do not treat `sale.order` as the logistics execution order.
- Prefer extension inheritance over copying official models.
- Prefer minimal and compatible changes unless a refactor is explicitly requested.
- For implementation-oriented tasks, do not skip `Understand -> Spec -> Plan -> Implement -> Verify -> Document`.
- Compare Odoo native capability before creating new custom business capability.
- For non-trivial changes, define `Outcome`, `Behavior`, and `Boundary` before coding.
- If module boundary, behavior, interface, event, table, index, page structure, naming, enum, or state rules change, update the spec before code.
- Treat `waybill` as the current trace main object; orders are subordinate fulfillment details unless a task explicitly targets a future order-level design.
- Treat `customer_line` as the current page-level reading entry for store-side facts, images, trace summaries, and related order details.
- Do not turn `customer_line` into the formal replacement for `trace_event` or `evidence` object anchoring unless a task explicitly updates the trace-object design first.
- Keep warehouse-side trace and loading trace as high-priority evidence points.
- Treat store-side trace as light proof with multiple images; do not assume store-side photos prove per-item quantity.
- Keep batch and dock/location association explicit when dispatch or loading is involved.
- Keep image binary storage out of long-term Odoo default attachment architecture for production-scale evidence storage; prefer metadata plus object storage direction.
- Keep API style RESTful and separate prefixes by terminal:
  - admin: `/api/admin/logistics/...`
  - mini: `/api/mini/logistics/...`
  - open: `/api/open/logistics/...`
- Keep enums short and easy for the team to read; prefer simple English words and use pinyin only when it is genuinely clearer.
- Any real code or document change must update `ai-code/docs/change_notes/`.

## Default Response Skeleton

- Objective
- Boundary
- Benchmark
- Current Understanding
- Development Plan
- Change Notes
- Verify
- Risks
- Next Suggestion

## Documentation Requirement

If a task changes code, structure, scope, or rules, sync the related docs when applicable:

- `ai-code/docs/context/`
- `ai-code/docs/architecture/ARCHITECTURE.md`
- `ai-code/docs/dev/upgrade_and_verify.md`
- `ai-code/docs/review/doc_sync.md`
- `ai-code/docs/change_notes/`
