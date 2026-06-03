# Agent Kit Upstream Screening Round 1

## Objective

- 对 `ai-code/_upstream/agent-kit` 中的 `skills/`、`rules/`、`docs/` 做第一轮引入筛选
- 给出三类结论：`可直接复用` / `需改写` / `不建议引入`
- 为后续逐条吸收进 `ai-code` 主链提供名单和理由

## Boundary

- 本轮只看上游仓库的 `skills/`、`rules/`、`docs/`
- 本轮不处理 `mcp/`、`src/`、`bin/`、`scripts/`、`tools/`
- 本轮只做筛选，不直接把任何上游规则接入当前项目主链

## Benchmark

当前项目的有效基线以以下内容为准：

- `AGENTS.md`
- `docs/ai/AI总控提示词.md`
- `docs/ai/AI开发协作规范.md`
- `docs/ai/AI开发守门员补充提示词.md`
- `docs/context/odoo_logistics_context.md`
- `docs/architecture/ARCHITECTURE.md`
- `.agents/skills/`

判断标准：

1. **可直接复用**
   - 不依赖私有平台、私有 CLI、私有服务或特定技术栈
   - 不会改写当前 Odoo 物流项目的业务边界
   - 不与现有 `AGENTS.md`、`docs/ai`、本地 skills 明显冲突

2. **需改写**
   - 方法论有价值
   - 但术语、流程、工具依赖或输出模板与当前项目不完全匹配
   - 需要转译成 Odoo 物流项目自己的版本后再进入主链

3. **不建议引入**
   - 强绑定 WPS / Docmini / Go / xfx / KDesign / 内部平台 / 内部 CLI
   - 或者和当前项目规则冲突过大
   - 或者能力已在系统层或项目层重复存在

## Inventory Summary

- 上游 `skills`: 80 个
- 上游 `rules`: 13 条 `.mdc`
- 上游 `docs`: 1 篇

第一轮结论：

- `可直接复用`: 1 个 skill
- `需改写`: 15 个 skills，3 条 rules，1 篇 doc
- `不建议引入`: 64 个 skills，10 条 rules

## Skills

### 可直接复用

1. `skills/security/skill-auditor`
   - 适合作为后续审查第三方 skills / rules 的安全入口
   - 目标和当前 `ai-code` 场景高度一致：先隔离、先审查、再决定是否引入
   - 虽然文案里提到多种 Agent 平台，但核心流程是通用的
   - 引入方式建议：先保留隔离副本，后续如要正式接入，优先作为“外部 skill 审查器”单独接入，不默认自动触发

### 需改写

以下 skills 有方法论价值，但不能原样并入：

1. `skills/common/ai-coach`
   - 有助于团队培训 AI 协作流程
   - 但其交互模式强依赖选择题驱动、AskQuestion 节奏、SDD/OpenSpec 话术
   - 应改写成更贴合当前 `AGENTS.md` 的 Odoo 项目 onboarding 版

2. `skills/common/project-overview`
   - 适合做新仓库 onboarding
   - 但当前项目已经有 `AGENTS.md`、`context`、`ARCHITECTURE.md` 这一整套入口
   - 应改写成“补全局部模块概览”的能力，而不是再生成一个平行总览体系

3. `skills/common/code-review-sdd`
   - 审查维度、证据意识和修复清单思路有价值
   - 但它依赖 OpenSpec / subagent / 四维评分体系
   - 应改写成适配你们当前 Odoo 模块开发和文档同步要求的 review skill

4. `skills/backend/backend-tech-proposal`
   - 适合写技术方案、详细设计
   - 但它默认的“后端方案调研”框架并没有内置 Odoo 原生能力比对和 OBB 约束
   - 应改写成你们自己的“Odoo 物流方案文档 skill”

5. `skills/backend/compatible-upgrade`
   - 兼容升级思路对 ToB 项目有价值
   - 但原文主要围绕 API schema / Redis / Kafka / 双版本并行运行
   - 应改写成 Odoo addon 升级、字段演进、接口兼容、数据迁移检查表

6. `skills/security/security-coding`
   - 安全审查框架有价值
   - 但原 skill 横跨 Go / Node / C/C++ / Web 安全，并带有 WPS 场景表述
   - 应缩成适配 Python/Odoo/前端资源上传接口的版本

7. `skills/product/PM-workflow/mermaid-diagram`
   - 画流程图、状态图、架构图的能力有用
   - 但文案强绑定 KDesign 色板、S1/S2 流程和 PM 工作流
   - 应改写成项目中立版 Mermaid 规范，适配你们现有文档目录

8. `skills/product/PM-workflow/S1-requirement-brief`
   - 可借鉴需求摘要的结构化产出方式
   - 但应改写为 Odoo 物流业务术语和阶段边界

9. `skills/product/PM-workflow/S2-structured-prd`
   - 可借鉴结构化 PRD 模板
   - 但不能原样并入，因为当前项目文档体系已不是通用互联网 PRD 体系

10. `skills/product/PM-workflow/S2R-requirement-review`
   - 需求复核方法可用
   - 但应转成当前项目的“Outcome / Behavior / Boundary + Odoo baseline compare”版本

11. `skills/product/PM-workflow/S5-consistency-check`
   - 对跨文档一致性检查有参考价值
   - 但应结合当前 `docs/context`、`architecture`、`change_notes` 体系重写

12. `skills/product/PM-workflow/workflow-conventions`
   - 能提供方法论骨架
   - 但其阶段命名、工具习惯和你们当前工作流并不一致

13. `skills/ops/perf-analysis`
   - 可保留其“压测分析入口”思路
   - 但应改写为适配你们自己的性能排查入口，而不是依赖上游观测工具链

14. `skills/ops/perf-analysis-e2e`
   - 分析框架可借鉴
   - 但当前项目没有对应的 Grafana / RCA / 内部服务画像体系

15. `skills/ops/perf-analysis-regression`
   - 可借鉴“版本对比防劣化”的思路
   - 但原 skill 的数据源和流程仍是上游私有平台导向

### 不建议引入

以下 skills 第一轮建议不引入。没有单独点名的同类项，按其所在分组一并处理。

1. `skills/frontend/**` 全部 32 个
   - 明显绑定 `docmini`、`kdrive`、`admin`、`message`、`preview`、`module federation`、`KDesign React`
   - 与当前 Odoo Web / OWL / backend client action 体系不兼容
   - 这些内容不该进入你们当前项目的默认上下文

2. `skills/backend/approval-hub-sdk`
3. `skills/backend/diag-plugin-codegen`
4. `skills/backend/go-performance`
5. `skills/backend/go-security`
6. `skills/backend/go-unit-test`
7. `skills/backend/iam/admin/module-ternary-tagging`
8. `skills/backend/pki-sdk`
9. `skills/backend/private/module-docs-gen`
10. `skills/backend/private/private-xfx`
   - 以上均强绑定 Go、xfx、审批中心、PKI 或私有工程体系

11. `skills/common/agent-kit-metrics`
   - 依赖 `kai telemetry`

12. `skills/common/cli-creator`
   - 当前 `ai-code` 不是 CLI 工具仓库，优先级低

13. `skills/common/code-review-debate`
   - 容易把 review 流程复杂化，且和当前仓库“先发现问题、再给修复建议”的节奏不一致

14. `skills/common/ecis-extension-skill`
   - 明显绑定 ECIS 体系

15. `skills/common/git-commit-helper`
   - 和当前仓库“是否提交由用户明确触发”的策略容易打架
   - 更适合当临时模板，不适合作为默认 skill 并入

16. `skills/common/gitlab-mr-review-private`
   - 绑定 GitLab MR 场景和私有流程

17. `skills/common/skill-creator`
   - 当前运行环境已经自带系统级 `skill-creator`
   - 本地再引入一份，收益低且容易重复

18. `skills/common/wps-doc-cli`
   - 强绑定 WPS/金山文档平台

19. `skills/ops/perf-code-analysis`
20. `skills/ops/perf-report`
21. `skills/ops/rca-analysis`
22. `skills/ops/rca-logs`
23. `skills/ops/rca-metrics`
24. `skills/ops/rca-pprof`
25. `skills/ops/rca-setup`
26. `skills/ops/rca-traces`
27. `skills/ops/service-profiles/docmini`
28. `skills/ops/service-profiles/docs`
   - 强依赖 `rca-cli`、内部观测平台、内部服务画像

29. `skills/product/PM-workflow/figma-to-pencil`
30. `skills/product/PM-workflow/kdesign-system`
31. `skills/product/PM-workflow/S3-pencil-prototype`
32. `skills/product/PM-workflow/S4-interactive-demo`
   - 工具链和设计资产都不在当前项目边界内

33. `skills/3rd/**`
   - 当前为空，第一轮无引入动作

## Rules

### 需改写

1. `rules/org/common/compatible-upgrade.mdc`
   - 兼容演进意识有价值
   - 但要改写为 Odoo addon、字段演进、数据迁移、接口向后兼容检查表

2. `rules/org/common/security-coding-standards.mdc`
   - 可作为安全基线来源
   - 但不应原样 `alwaysApply`
   - 建议改写成面向 Python / Odoo / 上传接口 / 权限控制 / API controller 的版本

3. `rules/org/common/testing.mdc`
   - 测试意识有价值
   - 但“80% 覆盖率 + 强制 TDD”不适合当前项目直接落地
   - 建议改成更务实的“升级可跑、关键流程可验、补回归点”的验证规则

### 不建议引入

1. `rules/org/common/coding-style.mdc`
   - “绝对不可变”“文件长度硬阈值”等规则过于强硬
   - 与 Python/Odoo ORM、现有代码现实不完全兼容

2. `rules/org/golang/api-wps365-standards.mdc`
3. `rules/org/golang/go-error-and-log.mdc`
4. `rules/org/golang/go-performance.mdc`
5. `rules/org/golang/go-reliability.mdc`
6. `rules/org/golang/go-testing.mdc`
7. `rules/org/golang/xfx-service-layering.mdc`
   - 全部强绑定 Go / xfx / WPS API 规范

8. `rules/team/docmini/api-docmini-v1-standards.mdc`
9. `rules/team/docmini/torm-quickref.mdc`
10. `rules/team/private/private-xfx/el-error-and-log.mdc`
   - 全部为上游团队私有实现细节，不应进入当前项目主链

## Docs

### 需改写

1. `docs/ai-capability-platform-design.md`
   - 适合作为“团队 AI 资产治理平台”参考材料
   - 但不是当前 Odoo 物流项目的直接执行文档
   - 可抽取其中的治理思路，改写成你们自己的“AI 资产接入与治理说明”

## First-Round Recommendation

1. 不要全量复制 `agent-kit` 内容到 `.agents/skills`、`docs/ai`、`AGENTS.md`
2. 先只保留 `_upstream/agent-kit` 作为参考库
3. 第二轮优先处理以下高价值改写候选：
   - `backend/compatible-upgrade`
   - `security/security-coding`
   - `common/code-review-sdd`
   - `product/PM-workflow/mermaid-diagram`
   - `docs/ai-capability-platform-design.md`
4. 如果要正式接入一个“上游原样能力”，优先试点 `skills/security/skill-auditor`

## Risks

- 如果团队忽略这份分类，直接从 `_upstream/agent-kit` 拷贝 rules，最容易引入的是技术栈错配
- 如果把 `alwaysApply` 的通用规则直接启用，AI 可能被 Go / xfx / WPS 平台术语带偏
- 如果把 PM 工作流整套照搬，容易形成和现有 `AGENTS.md` 并行竞争的第二套流程

## Next Suggestion

下一轮建议直接做“高价值改写包 v1”，只改写 3 到 5 个最值得落地的项，优先放到：

- `.agents/skills/`
- `docs/ai/`
- `docs/review/`

而不是继续扩大上游原样镜像的生效范围。
