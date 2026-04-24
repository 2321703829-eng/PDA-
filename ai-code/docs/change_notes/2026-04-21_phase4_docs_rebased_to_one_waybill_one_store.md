# 2026-04-21 phase4 docs rebased to one waybill one store

## Summary

Rebased the phase4 design docs to the new business premise:

- `1 waybill = 1 store/customer`
- `waybill` directly carries store snapshot fields
- phase4 core structure becomes `waybill -> order_line -> goods_line`
- `customer_line` exits the phase4 core structure and is kept only as a compatibility concept when needed
- images now attach to `waybill` in phase4 first round

## Updated docs

- `ai-code/前端设计/四期前端优化设计/00_导航与总纲/2026-04-20_Odoo物流后台四期前端优化设计总纲.md`
- `ai-code/前端设计/四期前端优化设计/00_导航与总纲/2026-04-21_四期页面信息架构与阅读链方案.md`
- `ai-code/前端设计/四期前端优化设计/00_导航与总纲/2026-04-21_四期业务评审问题清单.md`
- `ai-code/前端设计/四期前端优化设计/00_导航与总纲/数据库与接口现状盘点说明-2026-04-21.md`
- `ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-21_Odoo物流后台导入模板结构重构专题方案.md`
- `ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-21_Odoo物流后台单表快捷导入映射规则专题方案.md`
- `ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-21_四期运单详情页结构草案.md`
- `ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-21_四期订单阅读区结构草案.md`
- `ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-21_四期门店节点阅读区结构草案.md`
- `ai-code/前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/2026-04-21_四期导入模板字段级映射与校验规则清单.md`
- `ai-code/前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/2026-04-21_四期单表字段逐字段全量映射表.md`
- `ai-code/前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/2026-04-21_四期图片模块字段与校验规则清单.md`
- `ai-code/前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/2026-04-21_四期后端数据库与接口影响面调研稿.md`
- `ai-code/前端设计/四期前端优化设计/02_跨模块规范/02_交互与组件/2026-04-21_四期图片模块前端交互与结果反馈方案.md`
- `ai-code/前端设计/四期前端优化设计/02_验收与联调/2026-04-21_四期联调与验收清单.md`
- `ai-code/前端设计/四期前端优化设计/02_验收与联调/2026-04-21_四期开发任务拆分清单.md`
- `ai-code/前端设计/四期前端优化设计/02_验收与联调/2026-04-21_四期实现差距清单.md`

## Main design shifts

1. Removed `customer_line` as the center of the phase4 import, page, image, and API design.
2. Moved store snapshot responsibility to `waybill`.
3. Simplified image packaging from multi-level store-package design to a single `waybill package`.
4. Changed the main reading chain from `waybill -> customer_line -> order_line` to `waybill -> order_line`.
5. Reframed the old “store node reading page” as a compatibility note instead of a primary phase4 page.
