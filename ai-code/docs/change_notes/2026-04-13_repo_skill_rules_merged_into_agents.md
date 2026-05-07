# 2026-04-13 仓库级 skill 规则并入 AGENTS

## 背景

仓库内已存在 `odoo-reconstruct/.codex/skills/odoo-logistics-spec-first/`，其中定义了面向物流项目实现工作的 `spec first`、`OBB`、`先比对 Odoo 原生能力`、`验证优先`、`文档沉淀` 等工作规则。

为了让这些规则在当前仓库中成为默认入口约束，而不是只在显式引用 skill 时才生效，本轮将关键规则提炼并并入根目录 `AGENTS.md`。

## 本轮更新

- 更新 `AGENTS.md`
  - 新增默认工作流：`Understand -> Spec -> Plan -> Implement -> Verify -> Document`
  - 新增 `Outcome / Behavior / Boundary` 约束
  - 新增 Odoo 原生能力基线比较要求
  - 新增 spec-first 触发条件
  - 并入当前项目的关键业务边界基线
- 更新 `docs/review/doc_sync.md`
  - 增加“仓库规则同步补充”小节
  - 明确仓库级规则变化时需要联查 `AGENTS.md`、`docs/ai/`、仓库内 `.codex` skill 与 `docs/change_notes/`

## 本轮未改动的文档

- `docs/ai/`
  - 本轮不改。原因：当前需求是把 skill 的关键规则提升为仓库入口级默认约束，优先落在 `AGENTS.md`；现有 `docs/ai/` 暂未与本次新增规则发生直接冲突。
- `docs/context/`
  - 本轮不改。原因：本次变更不涉及业务边界事实、模块设计事实或上下文结论变化。
- `docs/architecture/ARCHITECTURE.md`
  - 本轮不改。原因：本次变更不涉及系统架构或模块结构调整。
- `docs/dev/upgrade_and_verify.md`
  - 本轮不改。原因：本次变更没有新增运行、升级或验证命令要求。

## 结果

现在在 `ai-code` 仓库内工作时，根目录 `AGENTS.md` 已经承载这套默认规则。即使没有显式提到仓库内的 `.codex` skill，后续仓库级任务也会按这套入口规则执行。
