# skill_router

## 目的

作为 `docs/ai/` 的统一入口，帮助团队快速判断：

- 当前需求更适合走哪个本地 `skill`
- 哪些 `rule` 需要一起参考
- 哪些文件是正式维护位置

## 正式维护位置

- prompt / rule 正式目录：[`docs/ai/prompt_engineering/`](d:/Desktop/Odoo/ai-code/docs/ai/prompt_engineering)
- skill 正式目录：[`.agents/skills/`](d:/Desktop/Odoo/ai-code/.agents/skills)

说明：

- `docs/ai/` 顶层保留稳定入口与兼容跳转
- 需要复用或修改提示词工程文档时，优先改 `prompt_engineering/`
- 不要把本地 skill 挪出 `.agents/skills/`，否则会破坏固定落点

## 使用方法

如果你已经知道要什么，可以直接点名：

- “用 `logistics-requirement-brief` 帮我整理一下”
- “用 `odoo-backend-tech-proposal` 出一版方案”
- “按 `AI验证与回归规则` 给我列验证项”

如果你还不确定，可以先按下面的路由表分流。

## 默认自动触发

- 对当前 `ai-code/` 工作区，local skill 不只用于“用户点名”。
- 如果用户的请求意图已经明显匹配某个本地 skill，默认应主动读取并应用对应 `SKILL.md`，不需要等用户额外强调。
- 判断顺序默认是：
  1. 先看用户意图
  2. 再按本页路由表匹配最贴近的 local skill
  3. 如果同时命中多个 skill，只用最小必要组合
- 典型例子：
  - “帮我看这个模型设计合不合理” -> `odoo-model-review`
  - “这个 client action 为什么报 Missing template” -> `odoo-frontend-asset-guard`
  - “这个仓库页面要和物流模块风格一致” -> `logistics-style-alignment`
  - “帮我 review 一下这轮改动” -> `spec-review-evidence-first`
  - “这个字段改动会不会影响升级” -> `odoo-compatible-upgrade-guard`

## 常见需求路由

| 需求类型 | 优先 skill / rule | 主要作用 | 常见产出 |
| --- | --- | --- | --- |
| 看模型设计、判断该复用官方模型还是新建 custom model、审模型边界 | `odoo-model-review` | 检查模型落点、关系、状态、mail/thread、边界和复杂度 | 模型评审意见、边界建议、字段/关系风险 |
| 先把想法压成一页需求摘要 | `logistics-requirement-brief` | 把零散输入压成 brief | brief 文档、范围、开放问题 |
| 把需求整理成正式规格 | `logistics-structured-prd` | 输出结构化 PRD 和 OBB | PRD、流程、规则、验收 |
| 审需求稿质量 | `structured-requirement-review` | 检查范围、异常流、术语、验收 | findings、gate 结论 |
| 写 Odoo 后端技术方案 | `odoo-backend-tech-proposal` | 先比 Odoo 原生，再落模型/服务/API | 技术方案、模块落点、验证建议 |
| 检查文档和实现是否一致 | `cross-doc-consistency-check` | 比较 brief / PRD / proposal / code / change note | 一致性 findings、同步建议 |
| 给新人补模块上下文 | `odoo-module-overview` | 输出模块级 onboarding 说明 | 模块概览、入口、风险点 |
| 把物流链路画成图 | `logistics-mermaid-diagram` | 生成流程图、状态图、结构图 | Mermaid 图块 |
| 做升级兼容评估 | `odoo-compatible-upgrade-guard` | 检查字段、状态、XML ID、接口等兼容面 | 升级风险清单、守门意见 |
| 做安全基线检查 | `odoo-security-baseline` | 检查输入、权限、`sudo`、上传下载、错误暴露 | 安全风险点、补强建议 |
| 先看证据再审规格/实现 | `spec-review-evidence-first` | 先读代码和 smoke 证据，再给 review 结论 | 证据优先 review |
| 审核外部 skill / rule / prompt 是否适合引入 | `external-skill-auditor` + `AI外部资产接入与治理说明` | 判断隔离、改写还是放弃 | 接入建议、落点建议 |
| 列最小验证和回归要求 | `AI验证与回归规则` | 按改动类型定义验证下限 | verify 清单、证据要求 |
| 处理 Odoo 前端资产、OWL、模板注册问题 | `odoo-frontend-asset-guard` | 聚焦 bundle、registry、模板和升级联调 | debug 路径、修复清单 |
| 新页面要和现有物流风格一致 | `logistics-style-alignment` | 对齐结构、交互节奏和视觉组织 | 参考页、样式对齐建议 |

## 推荐组合

- `brief -> PRD -> review -> proposal -> verify`
  - `logistics-requirement-brief`
  - `logistics-structured-prd`
  - `structured-requirement-review`
  - `odoo-backend-tech-proposal`
  - `AI验证与回归规则`

- `方案落地前质量守门`
  - `odoo-compatible-upgrade-guard`
  - `odoo-security-baseline`
  - `cross-doc-consistency-check`

- `接入外部 AI 资产`
  - `external-skill-auditor`
  - `AI外部资产接入与治理说明`

- `前端联调`
  - `logistics-style-alignment`
  - `odoo-frontend-asset-guard`

## Prompt / Rule 索引

- [AI总控提示词](d:/Desktop/Odoo/ai-code/docs/ai/prompt_engineering/AI总控提示词.md)
- [AI开发协作规范](d:/Desktop/Odoo/ai-code/docs/ai/prompt_engineering/AI开发协作规范.md)
- [AI开发守门员补充提示词](d:/Desktop/Odoo/ai-code/docs/ai/prompt_engineering/AI开发守门员补充提示词.md)
- [AI外部资产接入与治理说明](d:/Desktop/Odoo/ai-code/docs/ai/prompt_engineering/AI外部资产接入与治理说明.md)
- [AI验证与回归规则](d:/Desktop/Odoo/ai-code/docs/ai/prompt_engineering/AI验证与回归规则.md)

## 技能目录提示

本地高价值 skill 主要分成 4 组：

- 需求与方案：`logistics-requirement-brief`、`logistics-structured-prd`、`structured-requirement-review`、`odoo-backend-tech-proposal`
- 质量与风险：`cross-doc-consistency-check`、`odoo-compatible-upgrade-guard`、`odoo-security-baseline`、`spec-review-evidence-first`
- 表达与认知：`odoo-module-overview`、`logistics-mermaid-diagram`
- 接入与联调：`external-skill-auditor`、`logistics-style-alignment`、`odoo-frontend-asset-guard`

## 默认判断

如果一个需求同时像“写需求”又像“写方案”，先走需求侧，再走方案侧。

如果一个需求同时像“做实现”又像“做验收”，先锁变更边界，再按 `AI验证与回归规则` 反推最小验证要求。
