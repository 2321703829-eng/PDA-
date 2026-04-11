---
name: odoo-logistics-spec-first
description: Design-first and validation-first workflow for the odoo-reconstruct logistics trace project. Use when implementing or modifying Odoo modules, driver/mobile pages, admin pages, APIs, events, SQL tables, indexes, or design docs in this repo. Enforce requirement understanding, OBB (Outcome, Behavior, Boundary), spec updates before code, module-boundary discipline, validation, and Markdown documentation sedimentation.
---

# Odoo Logistics Spec First

## Overview

Use this skill to keep work in `odoo-reconstruct` aligned with the project's design baseline.

Always treat the repo docs as the source of truth, and always prefer:

1. design first
2. validation first
3. implementation after spec is stable
4. documentation sedimentation at the end

Read [references/project-doc-map.md](references/project-doc-map.md) before doing substantial work.

## Core Workflow

Follow this sequence unless the user explicitly asks for read-only discussion:

1. Understand the request.
2. Lock OBB.
3. Read only the relevant project docs.
4. Compare the target capability with Odoo native capability first.
5. Write a gap analysis: what Odoo already has, what is missing, what should be extended, and what should be custom.
6. Update or create the spec before coding if behavior, interface, event, table, index, or page structure changes.
7. Write a short implementation plan.
8. Implement only inside the relevant module boundary.
9. Validate function, boundary, exception, and regression impact.
10. Update Markdown documentation.

Do not jump directly to code when OBB is still unclear.
Do not jump to custom implementation before checking whether Odoo native modules, models, views, fields, or flows already cover part of the need.

## openSpec Rule

Follow this sequence explicitly for implementation work:

1. `Understand`
2. `Spec`
3. `Plan`
4. `Implement`
5. `Verify`
6. `Document`

Map each step like this:

- `Understand`: clarify requirement and read the correct project docs
- `Spec`: lock OBB, compare Odoo native capability, and update the module/interface/data design
- `Plan`: define files, modules, risks, and verification approach
- `Implement`: change only what is required by the approved spec
- `Verify`: perform function, boundary, exception, and regression checks
- `Document`: update the Markdown source of truth

Do not skip a step silently.

## OBB Rule

For every non-trivial change, explicitly define:

- `Outcome`: what result must be true after the change
- `Behavior`: inputs, outputs, flow, rules, and user-visible/system-visible behavior
- `Boundary`: edge cases, abnormal cases, ownership, compatibility, and what is out of scope

If any of these are missing and the task is implementation-oriented, update the relevant doc first or add a short design note before coding.

## Odoo Baseline Comparison Rule

Before designing a new module capability or extending an existing one:

1. identify the related Odoo native module, model, view, or workflow
2. state what Odoo already supports
3. state what the project still lacks
4. choose one path explicitly:
   - reuse directly
   - extend Odoo
   - create custom capability

Default preference:

1. reuse Odoo native capability when it already fits
2. extend Odoo when the native object is correct but the business capability is incomplete
3. build custom capability only when the business object or evidence flow is not naturally represented by Odoo

Use [references/odoo-gap-analysis-template.md](references/odoo-gap-analysis-template.md) when the task affects a module, page, API, event, or table.

## Spec-First Rule

Before code changes, add or update the relevant spec when the change affects any of these:

- module responsibilities
- business flow
- API path, request, response, or DTO
- event names or event payloads
- SQL tables, fields, indexes, or query paths
- page information architecture or interaction flow
- naming, enum, or state rules

Use [references/module-design-template.md](references/module-design-template.md) as the default structure.
Use [references/odoo-gap-analysis-template.md](references/odoo-gap-analysis-template.md) when comparing with Odoo native capability.

## Hard Constraints

Keep these constraints stable unless the user explicitly changes project direction:

- Do not reintroduce IAM as a default module.
- Treat `waybill` as the current trace main object; treat orders as subordinate fulfillment details unless the task explicitly targets a future order-level design.
- Keep warehouse-side trace and loading trace as high-priority evidence points.
- Treat store-side trace as light proof with multiple images; do not assume store-side photos can prove per-item quantity.
- Keep batch and dock/location association explicit when dispatch or loading is involved.
- Keep image binary storage out of long-term Odoo default attachment architecture for production-scale evidence storage; use metadata plus object storage direction.
- Keep API style RESTful and separate prefixes by terminal:
  - admin: `/api/admin/logistics/...`
  - mini: `/api/mini/logistics/...`
  - open: `/api/open/logistics/...`
- Keep enums short and easy for a Chinese team to read; prefer simple English words, and use pinyin only when it is genuinely clearer.
- Design indexes together with any new business table that serves list/query pages.
- Let frontends consume stable DTOs; do not expose raw Odoo internal object structure as the external contract.
- Respect module ownership; do not let one module directly own another module's primary data.
- If implementation must deviate from an existing design doc, update the design doc first or in the same change set before finalizing code.
- Do not treat undocumented behavior as acceptable completion.
- Do not expand scope or perform unrelated refactors.

## Recommended Constraints

Prefer these defaults:

- Keep event names short and concrete, such as `dispatch.done`, `trace.add`, `image.ok`.
- Keep statuses simple, such as `new`, `ready`, `doing`, `done`, `cancel`.
- Define high-frequency query paths before finalizing tables.
- Define pagination, sorting, and key filters together with list APIs.
- When adding images or evidence metadata, define retention, preview, and traceability expectations together.
- When changing a front-end flow, define the user path and the API consumption list together.

Read [references/change-checklist.md](references/change-checklist.md) before closing the task.

## Module Boundary Discipline

When touching code or design:

- prefer changing one module and its contract, not many modules implicitly
- describe upstream/downstream dependencies clearly
- avoid cross-module direct writes when an event or service contract is the proper boundary
- if a task crosses modules, update the cross-module spec first

For project-specific boundaries, read:

- [references/project-doc-map.md](references/project-doc-map.md)

## Design Deviation Rule

If implementation discovers that the current design is wrong, incomplete, or impractical:

1. stop treating the old design as authoritative
2. update the relevant design doc or add a design delta note
3. explain why implementation is changing direction
4. only then finalize the code change

Never leave code and design in silent disagreement.

## Validation Rule

Every meaningful change should be validated in four dimensions:

- function validation
- boundary validation
- exception validation
- regression validation

If code cannot be run, state what was not verified and why.

## Documentation Rule

Every meaningful change should leave a Markdown artifact or an updated Markdown spec that covers:

- background
- goal
- solution
- impact
- risks
- validation
- conclusion

Do not leave important design decisions only in chat.

## Done Definition

Treat a module or feature change as complete only when all of these are true:

- requirement understanding is written
- OBB is written
- Odoo native comparison is written
- relevant design/spec is updated
- implementation is aligned with the design
- validation coverage is stated
- Markdown documentation is updated

## Default Output Structure

Use this structure unless the user wants a lighter answer:

- `# 需求理解`
- `# OBB 分析`
- `# 开发计划`
- `# 改动方案`
- `# 代码实现`
- `# 验证方案`
- `# 文档沉淀`
- `# 本次总结`

## Resources

- [references/project-doc-map.md](references/project-doc-map.md): which project docs to read for each task type
- [references/module-design-template.md](references/module-design-template.md): default module/spec template
- [references/odoo-gap-analysis-template.md](references/odoo-gap-analysis-template.md): compare project needs with Odoo native capability
- [references/change-checklist.md](references/change-checklist.md): pre-change and post-change checklist
