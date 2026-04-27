# Change Notes

## 本轮目标

- 将剩余最高价值候选中的 `skill-auditor`、`S1-requirement-brief`、`testing.mdc` 改写为适配当前 Odoo 物流项目的本地资产
- 继续补齐外部资产审查、需求摘要、验证与回归规则三类高频能力

## 修改文件

- 新增 `.agents/skills/external-skill-auditor/SKILL.md`
- 新增 `.agents/skills/logistics-requirement-brief/SKILL.md`
- 新增 `docs/ai/AI验证与回归规则.md`
- 新增 `docs/change_notes/2026-04-27_agent_kit_adaptation_v4.md`

## 修改原因

- 当前本地 skill 已覆盖结构化需求、需求评审、技术方案、一致性检查、模块概览等能力
- 仍缺三块高频入口：
  - 外部 skill / rule / prompt 接入前的本地审查
  - 比结构化 PRD 更轻量的需求摘要层
  - 更适合 Odoo 物流项目现实的验证与回归规则
- 上游 `testing.mdc` 的 “80% 覆盖率 + 强制 TDD” 不适合直接并入当前项目，需要本地化收口

## 改动摘要

- 新增 `external-skill-auditor`
  - 用于审查外部 AI 资产是否适合接入当前项目
  - 输出聚焦冲突面、接入建议和推荐落点
- 新增 `logistics-requirement-brief`
  - 用于把散乱想法先收成轻量需求摘要
  - 位于完整结构化需求和技术方案之前
- 新增 `AI验证与回归规则`
  - 吸收上游 testing 方法论，但改写为更贴近 Odoo 升级、权限、页面、接口和主链路回归的版本

## 影响范围

- 影响当前项目的本地 AI 协作能力层与规则文档层
- 不影响业务代码、模型、视图、接口、权限、数据库结构或页面运行行为

## 是否影响模型 / 视图 / 权限 / 数据兼容性

- 不影响

## 验证方法

- 检查 2 个新增 skill 目录是否存在且包含 `SKILL.md`
- 检查 `AI验证与回归规则.md` 是否对齐当前项目，而不是沿用上游统一 80% / 强制 TDD 口径
- 检查新增内容是否与当前 `AGENTS.md`、`docs/ai/` 和本地 skill 主线一致

## 风险点

- `external-skill-auditor` 目前更偏项目内接入治理，不是操作系统级恶意代码审计器
- `AI验证与回归规则` 仍需要在几轮真实代码改动中继续试跑，才能进一步收口成更细的验证模板

## 回滚建议

- 若后续判断不适合当前项目，可删除：
  - `.agents/skills/external-skill-auditor/`
  - `.agents/skills/logistics-requirement-brief/`
  - `docs/ai/AI验证与回归规则.md`
  - `docs/change_notes/2026-04-27_agent_kit_adaptation_v4.md`

## 后续待办

- 用一次真实外部资产筛选任务试跑 `external-skill-auditor`
- 用一次早期模糊需求试跑 `logistics-requirement-brief`
- 在下一次真实代码任务中，用 `AI验证与回归规则` 回看验证口径是否需要继续收紧
