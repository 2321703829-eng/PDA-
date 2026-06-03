# 2026-04-22 Phase4 Database Design Add Odoo Model And SQL Checklists

## Summary

- extended the phase4 database implementation draft with an Odoo model field checklist
- added a SQL constraint and index checklist that can be used as the direct implementation baseline
- kept the new sections aligned with the existing table overview, PK/FK matrix, required-field list, enum rules, import logs, and build-implementation draft

## Updated Files

- `前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/2026-04-21_四期数据库底表设计稿 v1（第二次修正版）.md`

## Main Additions

### 1. Odoo model field checklist

- added `_inherit` / `_name` modeling conventions
- translated official master-data extensions into Odoo field definitions for:
  - `res.partner`
  - `product.template`
  - `hr.employee`
  - `fleet.vehicle`
- translated custom profile, dispatch-state, history, execution-chain, import, and audit tables into Odoo model field lists
- clarified `required` / `default` / `index` / relation notes for implementation handoff

### 2. SQL constraint checklist

- added recommended `_sql_constraints` grouped by master data, dispatch state, history, execution chain, and import logs
- added check-constraint guidance for non-negative numeric fields and enum legality
- reserved time-window legality checks for Odoo-level constraints where string storage is used in phase1

### 3. SQL index checklist

- added explicit manual index recommendations for:
  - execution-chain joins
  - master/profile lookup
  - dispatch availability queries
  - history tracing
  - import/audit queries
- listed fields that should not get normal indexes in phase1 to avoid low-value write cost

## Result

- the document now covers both design-level structure and implementation-level Odoo/SQL landing guidance
- backend developers can continue from the same source file toward model creation, `_sql_constraints`, and index implementation
