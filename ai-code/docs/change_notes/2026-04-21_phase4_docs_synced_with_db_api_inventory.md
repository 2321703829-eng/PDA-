# 2026-04-21 phase4 docs synced with db api inventory

## Summary

- synced core findings from the teammate's 2026-04-21 database and API inventory note into the active phase4 design docs
- clarified that `customer_line_id` is mostly supported today, while `customer_line_no` still requires model, constraint, index, and import-chain changes
- clarified that `manifest` is not a current business object and would require a dedicated object layer if formally introduced later
- synced current image-chain realities: single-image oriented upload/access exists, but true business batch export is still missing

## Updated Files

- `ai-code/前端设计/四期前端优化设计/00_导航与总纲/2026-04-20_Odoo物流后台四期前端优化设计总纲.md`
- `ai-code/前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/2026-04-21_四期后端数据库与接口影响面调研稿.md`
- `ai-code/前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/2026-04-21_四期图片模块字段与校验规则清单.md`

## Key Decisions

- import-chain changes remain the first required backend adaptation layer
- mini endpoints can stay mostly unchanged in phase4 first round unless customer-line or future manifest dimensions must be exposed there
- website/detail read paths also need coordinated field/view/domain updates because some pages read directly through ORM/searchRead
