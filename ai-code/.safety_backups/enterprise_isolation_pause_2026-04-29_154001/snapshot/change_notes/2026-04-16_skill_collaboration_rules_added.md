# 2026-04-16 补本地 skill 通用协作约束

## 本次变更

更新：

- `.agents/skills/doc-sync-review/SKILL.md`
- `.agents/skills/odoo-addon-scaffold/SKILL.md`
- `.agents/skills/odoo-model-review/SKILL.md`
- `.agents/skills/odoo-view-security-check/SKILL.md`

## 变更目的

- 为当前工作区的本地 skill 统一补充协作约束
- 明确完成编码工作后，默认需要给用户提供详细的人工复核操作流程
- 明确开启设计文档编写前，默认需要先与用户讨论思路并得到确认
- 明确每次完成文档编写或编码后，默认需要回扫当前阶段对应的设计文档并同步修正过期内容
- 明确当无法判断当前工作属于哪一期时，默认需要先询问用户再决定是否回扫和修改设计文档

## 当前边界

- 本次仅更新本地 skill 规则说明
- 没有修改业务代码、接口、模型、视图或权限实现
- 没有涉及测试执行
