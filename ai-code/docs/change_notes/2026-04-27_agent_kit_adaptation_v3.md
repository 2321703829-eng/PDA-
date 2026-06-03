# Change Notes

## 本轮目标

- 将上游第二批候选中的 `requirement-review` 与 `project-overview` 改写为适配当前 Odoo 物流项目的本地 skills
- 继续补齐“审需求”和“做局部上手概览”这两类高频协作能力

## 修改文件

- 新增 `.agents/skills/structured-requirement-review/SKILL.md`
- 新增 `.agents/skills/odoo-module-overview/SKILL.md`
- 新增 `docs/change_notes/2026-04-27_agent_kit_adaptation_v3.md`

## 修改原因

- 第二批 v2 已经补齐了后端方案、结构化需求和跨文档一致性检查
- 当前还缺两段常见协作场景：
  - 在进入方案或开发前，对需求文档本身做质量评审
  - 在接手局部能力时，快速生成模块级上下文概览
- 上游 `S2R-requirement-review` 与 `project-overview` 有方法论价值，但原始写法带有上游流程命名和整仓总览倾向，需要本地化改写

## 改动摘要

- 新增 `structured-requirement-review`
  - 用于评审需求文档、结构化 PRD、设计草案的质量
  - 聚焦完整性、无歧义性、一致性、可验证性、边界和门禁判断
- 新增 `odoo-module-overview`
  - 用于生成模块级、专题级、能力域级的局部概览
  - 明确不替代全局 `ARCHITECTURE.md`，避免重复维护第二套整仓总览

## 影响范围

- 影响当前项目的 AI 协作能力层与本地 skill 资产
- 不影响业务代码、模型、视图、权限、接口、数据库结构或页面行为

## 是否影响模型 / 视图 / 权限 / 数据兼容性

- 不影响

## 验证方法

- 检查 2 个新增 skill 目录是否存在且包含 `SKILL.md`
- 检查需求评审 skill 是否对齐当前项目基线，而不是沿用上游流程门禁话术
- 检查模块概览 skill 是否明确限定为模块级 / 专题级，不与现有架构总览冲突
- 检查两者都沿用了当前项目的主链与边界约束

## 风险点

- `structured-requirement-review` 在真实评审场景里，后续可能还要继续收口 findings 模板
- `odoo-module-overview` 如果被错误用于整仓级目标，仍可能生成过宽的概览，需要靠 skill 本身的范围约束和使用习惯来控制

## 回滚建议

- 若后续判断不适合当前项目，可删除：
  - `.agents/skills/structured-requirement-review/`
  - `.agents/skills/odoo-module-overview/`
  - `docs/change_notes/2026-04-27_agent_kit_adaptation_v3.md`

## 后续待办

- 在一次真实需求评审中试跑 `structured-requirement-review`
- 在一次模块接手或 onboarding 任务中试跑 `odoo-module-overview`
- 根据实际效果再决定是否继续改写更细分的 requirement-review 衍生能力
