# Change Notes

## 本轮目标

- 将第一轮筛选中最值得落地的上游内容改写成当前项目自己的 `.agents/skills` 和 `docs/ai` 资产

## 修改文件

- 新增 `.agents/skills/odoo-compatible-upgrade-guard/SKILL.md`
- 新增 `.agents/skills/odoo-security-baseline/SKILL.md`
- 新增 `.agents/skills/spec-review-evidence-first/SKILL.md`
- 新增 `.agents/skills/logistics-mermaid-diagram/SKILL.md`
- 新增 `docs/ai/AI外部资产接入与治理说明.md`
- 新增 `docs/change_notes/2026-04-27_agent_kit_adaptation_v1.md`

## 修改原因

- 上游 `agent-kit` 中有一部分方法论值得保留
- 但原内容强绑定私有平台、Go/xfx、WPS/Docmini 体系，不能原样进入当前 Odoo 物流项目主链
- 因此需要做一版项目化适配

## 改动摘要

- 基于上游候选内容，落地 4 个本地 skill：
  - 兼容升级检查
  - 安全基线检查
  - 证据优先 review
  - Mermaid 图表生成
- 基于上游治理思路，新增 1 份本地 `docs/ai` 文档：
  - 外部 AI 资产接入与治理说明
- 本轮保留方法论，去掉了私有平台依赖、错误技术栈绑定和不适配当前项目的强约束

## 影响范围

- 影响当前项目的 AI 协作规则层与复用能力层
- 不影响业务代码、模块实现、数据库结构、接口行为或页面功能

## 是否影响模型 / 视图 / 权限 / 数据兼容性

- 不影响

## 验证方法

- 检查 4 个 skill 目录及 `SKILL.md` 是否存在
- 检查 `docs/ai/AI外部资产接入与治理说明.md` 是否存在
- 检查新内容是否使用当前项目语境，而非上游私有平台语境
- 检查本轮没有把上游原始 rules 直接并入当前主链

## 风险点

- 新 skill 仍需要在真实任务中跑几轮，才能继续收口触发语和检查项
- 当前只完成第一版适配，还没有把所有高价值上游资产都改写完

## 回滚建议

- 若后续判断这批适配版不合适，可删除：
  - `.agents/skills/odoo-compatible-upgrade-guard/`
  - `.agents/skills/odoo-security-baseline/`
  - `.agents/skills/spec-review-evidence-first/`
  - `.agents/skills/logistics-mermaid-diagram/`
  - `docs/ai/AI外部资产接入与治理说明.md`
  - `docs/change_notes/2026-04-27_agent_kit_adaptation_v1.md`

## 后续待办

- 在真实任务中试跑这 4 个 skill
- 根据使用反馈收口触发描述和检查清单
- 再决定是否继续改写第二批候选资产
