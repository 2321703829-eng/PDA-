# 2026-05-13 A/B integration checklist added

## Summary

Added a dedicated A/B integration checklist for the current shared-environment phase after both lines were deployed to `19129`.

## Main changes

- added `专题设计/ODOO原生模块设计/01_模块设计/2026-05-13_A_B联调清单.md`
- rewrote `专题设计/ODOO原生模块设计/01_模块设计/README.md` into a clean current-phase index
- rewrote `专题设计/ODOO原生模块设计/主文档清单.md` into a clean package-level master document list

## Why

Once A line and B line both became independently available on the shared environment, the next execution focus shifted from single-line development to cross-line integration. The prior document set already covered scope, structure, status, pages, and acceptance, but it did not yet provide one dedicated checklist for shared-field coordination, cross-module chain validation, and integration pass/fail rules.

## Impact

- A/B integration now has one direct execution document instead of being scattered across acceptance notes and split tables
- the current package indexes are cleaner and easier to use during active implementation and integration
- next-step work can move into integration, defect convergence, and merge preparation with less ambiguity
