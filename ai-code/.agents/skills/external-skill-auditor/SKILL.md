# external-skill-auditor

## Purpose

在把外部 `skills`、`rules`、提示词、模板或 AI 协作资产接入当前项目之前，先做一轮项目内审查，避免把错误技术栈、私有平台依赖、越权行为或与当前规则冲突的内容直接带进来。

这个 skill 的目标不是做操作系统级安全渗透分析，而是帮助当前 Odoo 物流项目判断：

- 这个外部资产值不值得引入
- 它会不会把项目话语体系带偏
- 它更适合隔离参考、改写接入，还是直接放弃

## Use When

- 用户想引入第三方 skill、rule、prompt、agent kit、模板仓库
- 用户问“这个 skill / rule 能不能接进我们项目”
- 已经把外部仓库拉进 `_upstream/`，准备做筛选或试点
- 需要对单个外部 skill/rule 做风险审查和接入建议
- 需要判断一个外部 AI 资产是否适合进入 `.agents/skills/`、`docs/ai/` 或主链规则

## Trigger Phrases

出现下面这类话时，优先考虑用这个 skill：

- “帮我审一下这个 skill / rule”
- “这个外部 AI 资产安全吗 / 适合接入吗”
- “这个仓库能不能并进我们本地”
- “先做一轮外部规则筛选”
- “看看这套 prompt / skill 会不会和我们项目冲突”

## Not For

下面这些情况，优先不要用这个 skill：

- 重点是审业务代码、controller、上传接口安全
- 重点是写需求、写方案或查文档一致性
- 已经决定引入，只是在做具体实现落地

## Core Standard

默认遵守 6 条审查基线：

1. 项目本地规则永远高于外部资产。
2. 外部资产先隔离，再筛选，再改写，最后试点。
3. 优先识别技术栈错配、私有平台依赖和流程冲突。
4. 外部资产默认不是当前项目的生效最高规则。
5. 方法论可以吸收，术语和边界通常要本地化重写。
6. 结论至少要落到“隔离保留 / 值得改写 / 不建议引入”。

## Review Dimensions

默认重点检查 7 个维度：

- 项目适配性：是否贴合当前 Odoo 物流项目
- 技术栈匹配：是否绑定 Go / xfx / WPS / Docmini / 私有平台
- 规则冲突：是否和 `AGENTS.md`、`docs/ai/`、本地 skills 打架
- 边界风险：是否重写了当前主线、主对象或模块边界
- 执行风险：是否鼓励越权、跳过确认、绕过审批或静默操作
- 收益密度：是方法论高价值，还是只是换一套话术
- 接入形态：适合进 `.agents/skills/`、`docs/ai/`，还是只留 `_upstream/`

## Workflow

### 1. Lock the target asset

先明确本轮审查对象：

- 是单个 `SKILL.md`
- 单条 rule
- 一篇治理文档
- 还是一整组外部资产

### 2. Compare with current local baseline

至少对照：

- `AGENTS.md`
- `docs/ai/prompt_engineering/AI外部资产接入与治理说明.md`
- `docs/context/odoo_logistics_context.md`
- `docs/architecture/ARCHITECTURE.md`
- 当前 `.agents/skills/`

### 3. Identify mismatch and hidden cost

重点回答：

- 它默认服务的项目是什么
- 它默认使用什么技术栈和流程
- 它要求的工具、平台、权限或上下文，我们这里有没有
- 如果直接并入，会最先冲突的是什么

### 4. Make an integration recommendation

默认分成三类：

- 隔离保留：可继续放在 `_upstream/` 参考
- 值得改写：保留方法论，改写成本地版
- 不建议引入：与项目收益不成比例，或冲突太大

### 5. Recommend the landing place

如果值得接入，还要继续说明：

- 更适合变成本地 skill
- 更适合变成 `docs/ai` 规则文档
- 更适合变成 review 清单
- 还是只保留审查记录

## Suggested Output Template

默认按下面顺序输出：

1. Target Asset
2. Key Findings
3. Conflict Surface
4. Integration Recommendation
5. Suggested Landing Place
6. Short Summary

## Checklist

- 是否说明了审查对象
- 是否对照了当前项目本地规则
- 是否指出了技术栈或私有平台错配
- 是否指出了会把项目边界带偏的点
- 是否给出“隔离保留 / 值得改写 / 不建议引入”
- 是否说明了推荐落点

## Output Expectation

使用这个 skill 时，最终结果至少要让团队快速知道：

- 这个外部资产现在该不该进来
- 如果能进，应该怎么进
- 如果不能进，主要是哪里不合适
- 后续是不是值得做成本地化版本
