# 2026-04-23 phase4_interface_data_docs_rebased_on_database_spec

## Objective

继续把 `前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/` 中除数据库底表设计稿外的字段级文档，同步到当前数据库基线口径。

## Scope

- `2026-04-21_四期导入模板字段级映射与校验规则清单.md`
- `2026-04-21_四期单表字段逐字段全量映射表.md`
- `2026-04-21_四期图片模块字段与校验规则清单.md`
- `2026-04-21_四期后端数据库与接口影响面调研稿.md`

## Key Sync Points

1. 明确 `waybill_no` 是正式运单键，`waybill_group_no` 只作导入控制字段。
2. 明确 `customer_line_no` 是运单内稳定业务键，数据库唯一性按 `(waybill_id, customer_line_no)` 收口。
3. 移除“首轮强制 1 order_line -> 1 goods_line”的旧判断，统一到数据库 `1 -> n` 结构。
4. 把导入任务审计链 `import_source_file / import_task / import_task_line / import_error_line` 纳入字段级文档表述。
5. 把图片导入任务对象类型收口为 `image_package`，主数据导入对象类型收口为 `dispatch_main`。
6. 修正后端影响面文档中的旧表名 `logistics_dispatch_waybill_customer_goods_line`，统一为 `logistics_dispatch_waybill_goods_line`。

## Verify

- 回扫以下冲突词是否已只作为“风险/废弃说明”存在，而非当前规则：
  - `无运单号时的聚合主键`
  - `运单号 可选`
  - `1 order_line -> 1 goods_line`
  - `logistics_dispatch_waybill_customer_goods_line`
- 确认图片规则、字段映射和后端影响面文档都与数据库底表稿中的唯一键、FK、导入对象类型保持一致。

## Risk

- `02_跨模块规范/01_接口与数据` 下后续若再补接口返回样例和错误码清单，仍需继续遵守本次更新后的数据库口径。
