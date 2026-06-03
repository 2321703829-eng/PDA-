# Change Notes

## 本轮目标

- 把本地 skill 的“按意图自动匹配”从人工查表，提升为 `ai-code/` 内的默认协作约定

## 修改文件

- `AGENTS.md`
- `docs/ai/skill_router.md`
- `docs/change_notes/2026-04-27_local_skill_auto_routing_enabled.md`

## 修改原因

- 当前仓库已经沉淀了较多本地 `.agents/skills/`，但默认入口更多还是“用户点名使用”
- 用户希望像“模型设计相关问题”这类场景，不需要额外提醒，也能自动走对应 skill
- 现有 `docs/ai/skill_router.md` 可作为路由入口，但尚未在 `AGENTS.md` 中明确成默认自动行为，且缺少 `odoo-model-review` 的单独路由提示

## 改动摘要

- 在 `AGENTS.md` 中新增 `Local Skill Auto Routing` 段落
- 明确要求：当用户请求明显匹配本地 skill 时，默认主动读取并应用对应 `SKILL.md`
- 指定 `docs/ai/skill_router.md` 作为默认路由索引
- 补充常见自动路由示例，包括：
  - 模型设计 / 模型评审 -> `odoo-model-review`
  - Odoo 前端资产链路问题 -> `odoo-frontend-asset-guard`
  - 页面风格对齐 -> `logistics-style-alignment`
  - review -> `spec-review-evidence-first`
  - 升级兼容 -> `odoo-compatible-upgrade-guard`
  - 文档同步 -> `doc-sync-review`
- 在 `docs/ai/skill_router.md` 中补充“默认自动触发”说明，并新增模型设计相关路由项

## 影响范围

- 影响 `ai-code/` 下 AI / Codex 协作文档入口和本地 skill 使用习惯
- 不影响业务代码、数据库结构、接口、视图或权限实现

## 是否影响模型 / 视图 / 权限 / 数据兼容性

- 不影响

## 验证方法

- 检查 `AGENTS.md` 是否新增本地 skill 自动路由规则
- 检查 `docs/ai/skill_router.md` 是否新增“默认自动触发”说明
- 检查 `docs/ai/skill_router.md` 是否补入 `odoo-model-review` 路由项

## 风险点

- 当前根级 `../AGENTS.md` 仍是全仓 canonical guide，本次仅在 `ai-code/AGENTS.md` 先补本地补充规则
- 如果后续希望整个 `Odoo` 仓都统一采用同一自动路由规则，还需要把同样约定同步到根级入口

## 回滚建议

- 如果后续发现自动路由描述过强或与上层入口冲突，可回退 `AGENTS.md` 中新增的 `Local Skill Auto Routing` 段落，并保留 `skill_router` 作为人工入口

## 后续待办

- 视使用效果决定是否把同类自动路由规则同步到仓库根级 `AGENTS.md`
- 后续新增本地 skill 时，同步补充 `docs/ai/skill_router.md` 的常见需求路由表
