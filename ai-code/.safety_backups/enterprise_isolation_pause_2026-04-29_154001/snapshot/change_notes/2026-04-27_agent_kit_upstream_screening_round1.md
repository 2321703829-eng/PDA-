# Change Notes

## 本轮目标

- 对 `ai-code/_upstream/agent-kit` 中的 `skills/`、`rules/`、`docs/` 做第一轮引入筛选
- 产出项目内可追踪的筛选结论文档

## 修改文件

- 新增 `docs/review/agent_kit_upstream_screening_round1.md`
- 新增 `docs/change_notes/2026-04-27_agent_kit_upstream_screening_round1.md`

## 修改原因

- 外部上游仓库已经隔离拉入
- 需要在不污染当前项目规则主链的前提下，明确哪些内容可以复用、哪些需要改写、哪些不应引入

## 改动摘要

- 盘点上游仓库：
  - `skills/` 80 个
  - `rules/` 13 条 `.mdc`
  - `docs/` 1 篇
- 形成三类结论：
  - `可直接复用`：1 个 skill
  - `需改写`：15 个 skills、3 条 rules、1 篇 doc
  - `不建议引入`：64 个 skills、10 条 rules
- 文档中同步写明了筛选基准、分类理由、首批高价值改写候选和风险点

## 影响范围

- 影响 `ai-code` 对外部 AI 资产的治理与后续接入节奏
- 不影响当前项目业务代码、模块结构、接口、数据库或前端实现

## 是否影响模型 / 视图 / 权限 / 数据兼容性

- 不影响

## 验证方法

- 检查 `docs/review/agent_kit_upstream_screening_round1.md` 是否存在
- 检查文档是否包含：
  - 三类筛选标准
  - `skills` / `rules` / `docs` 三部分结论
  - 下一轮改写建议
- 检查本轮没有把上游规则接入 `AGENTS.md`、`.agents/skills`、`docs/ai`

## 风险点

- 第一轮筛选仍属于人工归类，后续改写时还需要逐项复核细节
- 如果团队绕过筛选文档直接复制上游规则，仍可能引入技术栈错配

## 回滚建议

- 若不需要保留本轮筛选结果，可删除：
  - `docs/review/agent_kit_upstream_screening_round1.md`
  - `docs/change_notes/2026-04-27_agent_kit_upstream_screening_round1.md`
- 删除前应确认没有后续文档引用该筛选结论

## 后续待办

- 按文档中的优先级，启动“高价值改写包 v1”
- 优先改写：
  - `compatible-upgrade`
  - `security-coding`
  - `code-review-sdd`
  - `mermaid-diagram`
  - `ai-capability-platform-design`
