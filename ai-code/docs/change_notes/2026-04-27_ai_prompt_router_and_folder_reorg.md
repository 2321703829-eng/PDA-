# 2026-04-27 AI Prompt Router And Folder Reorg

## Objective

- 为本地 skills 和 prompt/rule 文档补一个统一路由入口
- 把 `docs/ai/` 下分散的提示词工程文档收口到一个正式目录
- 在不破坏现有引用习惯的前提下，提升目录规范性

## Changed Files

- 更新 `README.md`
- 更新 `.agents/skills/external-skill-auditor/SKILL.md`
- 新增 `docs/ai/skill_router.md`
- 新增 `docs/ai/prompt_engineering/`
- 在 `docs/ai/` 顶层保留 5 个兼容跳转文件：
  - `AI总控提示词.md`
  - `AI开发协作规范.md`
  - `AI开发守门员补充提示词.md`
  - `AI外部资产接入与治理说明.md`
  - `AI验证与回归规则.md`

## Why

- 团队已经积累了多份本地 prompt / rule / skill 文档，但入口分散
- 仅靠文件名记忆成本较高，不利于团队直接按场景触发
- 直接移动旧文件会影响现有仓库内的历史引用与使用习惯

## Current Decision

- `docs/ai/prompt_engineering/` 作为 prompt/rule 的正式维护目录
- `docs/ai/skill_router.md` 作为统一入口
- `.agents/skills/` 继续保持 skill 的固定落点，不参与本轮搬迁
- `docs/ai/` 顶层旧路径保留轻量 redirect，避免硬切换造成断链

## Verify

- 检查 `docs/ai/skill_router.md` 是否存在并可作为入口
- 检查 `docs/ai/prompt_engineering/` 下 5 份正式文档是否存在
- 检查 `README.md` 的目录说明是否已更新
- 检查 `external-skill-auditor` 是否已改为引用新路径

## Risks

- 旧路径目前保留 redirect 壳文件，短期内会同时存在“入口文件”和“正式文件”
- 历史 change note 里仍可能提到旧路径，这是兼容保留而不是语义错误

## Next Suggestion

- 后续新增 prompt/rule 文档默认只放进 `docs/ai/prompt_engineering/`
- 团队在提需求时，优先从 `docs/ai/skill_router.md` 选 skill / rule
