# 2026-04-23 四 Sheet 字段落库差距补齐第一轮

## Objective

- 按四 Sheet 字段清单核对 `Waybill / CustomerLine / OrderLine / GoodsLine` 当前落库情况。
- 先补齐真正缺少落点或正式导入写入的字段，不再停留在“只会解析、不真正落库”。

## Scope

- 更新 [四 Sheet 正式模板字段清单 v1](</d:/Desktop/Odoo/ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-23_四 Sheet 正式模板字段清单 v1.md>)，新增逐 Sheet 已落库/本轮补齐对照。
- 补齐 `logistics.dispatch.batch` 的 `driver_name_snapshot / driver_phone_snapshot`。
- 更新 `waybill_standard_import_service_v2.py`：
  - `Waybill` 导入时写入批次司机快照
  - `CustomerLine` 导入时同步回写 `res.partner + logistics.customer.profile + logistics.store.profile`
  - 保留 `CustomerLine / OrderLine / GoodsLine` 既有事实快照写入

## Result

- `Waybill` Sheet 当前正式可承接 `driver_name / driver_phone`。
- `CustomerLine` Sheet 当前不再只写门店节点快照，还会把客户/门店主档及画像字段回写到正式主数据对象。
- `OrderLine / GoodsLine` 经过对照确认，当前冻结字段已具备模型字段和正式写入链。

## Boundary

- `order_line_no` 仍是模板内关系键，不单独新增数据库字段。
- `registered_phone / registered_address` 仍与 `contact_phone / address_full` 共用 `res.partner` 基础字段，这是当前数据库设计本身的归属方式。
- 本轮未做模块升级和运行态 smoke，只做文档同步与静态层实现补齐。
