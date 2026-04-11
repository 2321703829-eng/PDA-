# Change Checklist

Use this checklist before implementation and before closing the task.

## 1. Pre-Change Checklist

- Have I written a short requirement understanding?
- Have I defined Outcome, Behavior, and Boundary?
- Have I identified which project docs are relevant?
- Have I compared the requirement with the relevant Odoo native capability?
- Have I written what can be reused, extended, or must be custom?
- If behavior or data changes, have I updated or created the design/spec first?
- Do I know which module owns the primary data?
- Do I know which files and modules I will touch?
- Do I know the risk and what I will not change?

## 2. Implementation Checklist

- Keep changes inside the intended module boundary.
- Use RESTful paths if APIs are added or changed.
- Keep admin, mini, and open interfaces separated when relevant.
- Keep enums simple and readable.
- Add indexes together with new query tables.
- Do not leak raw Odoo internal structures as external contracts.
- Do not store large-scale evidence binary in the wrong place.
- Do not widen scope into unrelated refactors.

## 3. Validation Checklist

- Function validation: does the main path work?
- Boundary validation: do edge cases behave correctly?
- Exception validation: do error paths or missing-data paths behave correctly?
- Regression validation: what existing behavior could be affected?

If not all checks were run, state the gap explicitly.

## 4. Documentation Checklist

- Was a Markdown doc created or updated?
- Does it cover background, goal, solution, impact, risk, validation, and conclusion?
- Does it record the Odoo native comparison and final design direction when relevant?
- If the change affects API, event, table, index, enum, or page flow, is that reflected in docs?
- If implementation deviates from existing docs, were the docs corrected?

## 5. Final Response Checklist

Default answer structure:

- `# 需求理解`
- `# OBB 分析`
- `# 开发计划`
- `# 改动方案`
- `# 代码实现`
- `# 验证方案`
- `# 文档沉淀`
- `# 本次总结`
