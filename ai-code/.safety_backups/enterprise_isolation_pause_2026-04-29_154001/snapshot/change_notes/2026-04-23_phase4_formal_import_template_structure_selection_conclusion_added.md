# 2026-04-23 phase4 formal import template structure selection conclusion added

## What changed

- 新增 [四期正式导入模板结构评估与选型结论](</d:/Desktop/Odoo/ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-23_四期正式导入模板结构评估与选型结论.md:1>)。

## Why

- 当前全量字段需求已经不适合继续由单表作为唯一正式标准模板承接。
- 需要先冻结“正式标准模板、多 Sheet、快捷单表、历史三 Sheet”三者的定位，再继续后续设计和实现。

## Conclusion

- 正式标准模板：四 Sheet
- 快捷导入模板：单表
- 历史兼容模板：旧三 Sheet

## Scope

- 仅新增设计结论文档
- 未修改代码
- 未修改接口
- 未做运行验证

## Next

- 继续补 `四 Sheet 正式模板字段清单 v1`
- 先冻结各 Sheet 的主键列、关联列、必填列，再回到实现
