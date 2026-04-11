# Odoo Gap Analysis Template

Use this template before implementing or redesigning a module capability.

## 1. Requirement Summary

- What business capability is needed
- Which role needs it
- What outcome is expected

## 2. Relevant Odoo Native Capability

- Related Odoo module(s)
- Related model(s)
- Related view(s) or workflow(s)
- Related search/list/report capability

## 3. What Odoo Already Supports

- Which parts can be used directly
- Which parts are close but incomplete
- Which data objects already exist

## 4. What Is Missing for This Project

- Missing business object
- Missing evidence or trace flow
- Missing page or interaction
- Missing API or DTO
- Missing event or data contract
- Missing query/index support

## 5. Decision

Choose one:

- `reuse`
- `extend`
- `custom`
- `mixed`

Explain why.

## 6. Final Design Direction

- What stays on Odoo native objects
- What becomes a custom module
- What interfaces/events need to be defined
- What tables/indexes need to be added

## 7. Risks

- Over-customization risk
- Wrong-boundary risk
- Query/performance risk
- UI/UX mismatch risk

## 8. Follow-up Docs

- Which design doc must be updated
- Which API or SQL doc must be updated
- Which page doc must be updated
