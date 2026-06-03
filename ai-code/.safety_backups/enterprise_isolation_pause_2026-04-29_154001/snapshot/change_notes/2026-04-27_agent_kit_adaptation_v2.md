# Change Notes

## 本轮目标

- 将上游 `agent-kit` 中第二批高价值候选内容，改写为适配当前 Odoo 物流项目的本地 skills
- 补齐“写方案、整需求、查一致性”这一段 AI 协作能力

## 修改文件

- 新增 `.agents/skills/odoo-backend-tech-proposal/SKILL.md`
- 新增 `.agents/skills/logistics-structured-prd/SKILL.md`
- 新增 `.agents/skills/cross-doc-consistency-check/SKILL.md`
- 新增 `docs/change_notes/2026-04-27_agent_kit_adaptation_v2.md`

## 修改原因

- 第一批改写已经覆盖兼容升级、安全基线、证据优先 review、Mermaid 图表生成
- 当前仍缺三块高频协作能力：
  - 把想法收敛成可执行后端技术方案
  - 把零散需求整理成结构化规格
  - 在多份文档与实现之间做一致性收口
- 上游 `backend-tech-proposal`、`S2-structured-prd`、`S5-consistency-check` 的方法论有保留价值，但原内容绑定上游流程和术语，不能原样并入

## 改动摘要

- 新增 `odoo-backend-tech-proposal`
  - 用于后端方案、模块设计、接口设计和 Odoo 原生能力对比
  - 强制纳入 Outcome / Behavior / Boundary 与升级验证视角
- 新增 `logistics-structured-prd`
  - 用于把需求输入整理为适合当前项目继续推进的结构化文档
  - 明确主流程、异常流程、规则、数据、接口与验收维度
- 新增 `cross-doc-consistency-check`
  - 用于检查 `AGENTS.md`、`docs/context/`、`ARCHITECTURE.md`、设计说明、代码实现、`docs/change_notes/` 之间的一致性
  - 输出聚焦冲突、漏同步、表达漂移和最小同步动作

## 影响范围

- 影响当前项目的 AI 协作能力层与本地 skill 资产
- 不影响业务代码、模型、视图、权限、接口或数据库结构

## 是否影响模型 / 视图 / 权限 / 数据兼容性

- 不影响

## 验证方法

- 检查 3 个新增 skill 目录是否存在且都包含 `SKILL.md`
- 检查 skill 内容是否使用当前 Odoo 物流项目术语，而不是上游仓库术语
- 检查 skill 内容是否对齐当前项目规则：
  - Odoo 原生能力先对比
  - Outcome / Behavior / Boundary 先锁定
  - custom addons 承载物流核心能力
  - 真实变更需要同步 `docs/change_notes/`

## 风险点

- 这一批仍是方法论本地化，不代表已经在真实任务中验证到最佳触发语
- `cross-doc-consistency-check` 在跨代码与跨文档场景里还需要再跑几轮，才能继续收口输出模板

## 回滚建议

- 若后续判断不适合当前项目，可删除：
  - `.agents/skills/odoo-backend-tech-proposal/`
  - `.agents/skills/logistics-structured-prd/`
  - `.agents/skills/cross-doc-consistency-check/`
  - `docs/change_notes/2026-04-27_agent_kit_adaptation_v2.md`

## 后续待办

- 在真实任务里试跑这 3 个 skill
- 根据产出质量继续收口模板和触发描述
- 再决定是否继续改写第二批其它候选项，例如 `requirement-review` 或 `project-overview`
