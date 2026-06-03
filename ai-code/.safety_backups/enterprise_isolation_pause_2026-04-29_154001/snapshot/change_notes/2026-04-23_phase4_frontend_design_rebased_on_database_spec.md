# 2026-04-23 phase4_frontend_design_rebased_on_database_spec

## Objective

把四期 `00_导航与总纲`、`01_专题方案` 中已经落后于数据库底表设计稿的导入与对象口径做一批同步，统一以数据库设计为当前有效基线。

## Scope

- `前端设计/四期前端优化设计/00_导航与总纲/2026-04-20_Odoo物流后台四期前端优化设计总纲.md`
- `前端设计/四期前端优化设计/00_导航与总纲/数据库与接口现状盘点说明-2026-04-21.md`
- `前端设计/四期前端优化设计/00_导航与总纲/2026-04-21_四期业务评审问题清单.md`
- `前端设计/四期前端优化设计/01_专题方案/2026-04-21_Odoo物流后台单表快捷导入映射规则专题方案.md`
- `前端设计/四期前端优化设计/01_专题方案/2026-04-21_Odoo物流后台导入模板结构重构专题方案.md`

## Key Sync Points

1. 明确 `waybill_no` 是正式运单业务唯一键，`waybill_group_no` 只作导入控制字段。
2. 明确 `customer_line_no` 是运单内稳定业务键，数据库唯一性按 `(waybill_id, customer_line_no)` 收口。
3. 移除“首轮强制 `1 order_line -> 1 goods_line`”的旧判断，改为与数据库 `1 -> n` 结构一致。
4. 不再把旧标准模板或“三 Sheet”写成四期总契约，只保留为兼容输入模式。
5. 把 `import_source_file / import_task / import_task_line / import_error_line` 及 `dispatch_main / image_package` 纳入正式导入设计表述。
6. 收回超出当前数据库基线的 `trace / evidence` 扩展性表述，避免和本批导入结构稿混层。

## Verify

- 通过全文搜索复核 `00_导航与总纲`、`01_专题方案` 中最关键的旧冲突词：
  - `waybill_group_no`
  - `customer_line_no`
  - `1 order_line -> 1 goods_line`
  - `三 Sheet`
- 确认更新后的口径与数据库底表设计稿中的唯一键、FK、导入对象类型、任务状态一致。

## Risk

- `02_跨模块规范/01_接口与数据` 目录下除数据库底表稿外，仍可能有部分字段级文档保留旧口径，后续还需继续回扫同步。
