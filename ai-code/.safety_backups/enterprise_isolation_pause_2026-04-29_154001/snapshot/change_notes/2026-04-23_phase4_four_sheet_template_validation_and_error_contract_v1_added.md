# 2026-04-23 phase4 four sheet template validation and error contract v1 added

## What changed

- 新增 [四 Sheet 模板校验规则与错误口径 v1](</d:/Desktop/Odoo/ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-23_四 Sheet 模板校验规则与错误口径 v1.md:1>)。

## Why

- 四 Sheet 正式模板的字段已经冻结，下一步必须把校验规则和错误口径一起冻结。
- 否则后续预校验实现、错误报告导出和结果页展示会再次各自为政。

## Scope

- 纳入：
  - 模板级校验
  - Sheet 级校验
  - 跨 Sheet 关系校验
  - 字段格式校验
  - 错误明细结构
  - 错误码冻结表
- 未纳入：
  - 代码实现
  - 前端展示样式
  - 旧三 Sheet 与单表快捷模板规则

## Next

- 继续把 [四期导入错误码清单](</d:/Desktop/Odoo/ai-code/前端设计/四期前端优化设计/02_跨模块规范/01_接口与数据/2026-04-23_四期导入错误码清单.md:1>) 同步到四 Sheet 口径
- 后续预校验实现按本文直接落地
