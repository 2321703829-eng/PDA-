# 2026-04-23 phase4 formal four sheet template field inventory v1 added

## What changed

- 新增 [四 Sheet 正式模板字段清单 v1](</d:/Desktop/Odoo/ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-23_四 Sheet 正式模板字段清单 v1.md:1>)。
- 已在原文档上继续回写，使模板列头命名尽量贴合：
  - [副本客户信息完整版0421.xlsx](</d:/Desktop/Odoo/ai-code/副本客户信息完整版0421.xlsx>)
  - [数据库底表，更新日期4.22.xlsx](</d:/Desktop/Odoo/ai-code/数据库底表，更新日期4.22.xlsx>)

## Why

- 四 Sheet 已经被确定为正式标准模板，需要继续冻结各 Sheet 的主键列、关联列、必填列和首轮上线字段。
- 只有把这些结构先定死，后续模板文件、预校验和导入实现才不会反复返工。

## Key decisions

- `Waybill` 以 `waybill_no` 为模板主键
- `CustomerLine` 以 `waybill_no + customer_line_no` 为模板主键
- `OrderLine` 正式引入模板内关系键 `order_line_no`
- `GoodsLine` 通过 `order_line_no` 关联 `OrderLine`
- 模板面对业务时优先采用现有 Excel 里的业务列头叫法，系统字段名保留在映射层
- `CustomerLine` Sheet 明确扩展承接客户/门店画像层常用输入字段
- 正式模板数据字段按“业务表头与数据库底表交集”收口，非交集字段从冻结表移出

## Scope

- 仅新增设计文档
- 未修改代码
- 未修改接口
- 未做运行验证

## Next

- 继续补 `四 Sheet 模板校验规则与错误口径 v1`
- 冻结各 Sheet 的查重规则、跨 Sheet 命中规则和错误码口径
