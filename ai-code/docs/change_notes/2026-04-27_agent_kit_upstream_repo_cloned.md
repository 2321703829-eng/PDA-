# Change Notes

## 本轮目标

- 将外部 `agent-kit` 仓库以隔离方式拉入 `ai-code`，作为后续筛选和适配的上游参考库

## 修改文件

- 新增目录 `d:\Desktop\Odoo\ai-code\_upstream\agent-kit`
- 新增本文档 `docs/change_notes/2026-04-27_agent_kit_upstream_repo_cloned.md`

## 修改原因

- 用户希望先完整拉取外部 skills 和 rules 仓库，再在后续阶段做筛选
- 为避免与当前 Odoo 物流项目规则直接冲突，采用隔离目录承载

## 改动摘要

- 使用 Git 将 `https://github.com/tian-shu-keji/agent-kit.git` 克隆到 `ai-code/_upstream/agent-kit`
- 当前仅作为参考库保存，未并入现有 `AGENTS.md`、`.agents/skills`、`docs/ai` 主链
- 拉取结果基于 `main` 分支，最新本地记录提交为 `b1d323f38a2b25a991af342036c58691f350bd78`

## 影响范围

- 影响 `ai-code` 的参考资料目录结构
- 不影响当前项目既有业务规则、模块边界、前端规范和文档主链

## 是否影响模型 / 视图 / 权限 / 数据兼容性

- 不影响

## 验证方法

- 确认目录 `d:\Desktop\Odoo\ai-code\_upstream\agent-kit` 已生成
- 确认仓库包含 `rules`、`skills`、`docs`、`openspec` 等上游内容
- 确认当前仅为隔离存放，未修改现有项目规则入口

## 风险点

- 团队成员可能误认为 `_upstream/agent-kit` 中的 rules 已自动成为当前项目生效规则
- 后续若直接复制其中内容到项目主链，可能引入与 Odoo 物流上下文不一致的约束

## 回滚建议

- 若后续判断该上游仓库不需要保留，可删除 `ai-code/_upstream/agent-kit`
- 删除前应先确认没有从其中复制或改写出的项目内正式规则仍在使用

## 后续待办

- 对 `agent-kit` 中的 `skills/`、`rules/`、`docs/` 进行分类审查
- 输出 `可直接复用 / 需改写 / 不建议引入` 清单
- 仅将筛选后的内容适配进项目自己的 `.agents/skills` 或 `docs/ai`
