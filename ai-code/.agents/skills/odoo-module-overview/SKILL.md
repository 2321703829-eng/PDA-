# odoo-module-overview

## Purpose

为当前 Odoo 物流项目里的某个模块、能力域、页面链路或专题子系统生成“可快速上手”的本地概览文档。

这个 skill 不用来重写整仓架构总览，也不替代现有 `docs/architecture/ARCHITECTURE.md`。它更适合在需要快速理解一个局部范围时，产出一份能帮助开发、评审或 AI 协作对齐上下文的模块级概览。

## Use When

- 用户要求“快速了解某个模块”“做模块概览”“补 onboarding 文档”
- 需要梳理某个 addon、页面链路、接口域或证据链专题
- 新成员要接手某块能力，但不需要先吞下整个仓库
- 需要为后续方案、review、联调或重构补局部上下文
- 现有全局架构文档太高层，无法直接回答“从哪里开始看”

## Trigger Phrases

出现下面这类话时，优先考虑用这个 skill：

- “帮我快速了解这个模块”
- “这块代码从哪开始看”
- “整理一版模块概览 / onboarding”
- “梳理这个能力域的关键文件和边界”
- “新人接手这块先看什么”

## Not For

下面这些情况，优先不要用这个 skill：

- 目标是整个仓库的全局架构总览
- 目标是写需求稿或技术方案
- 目标是做文档一致性检查

## Core Standard

默认遵守 6 条概览基线：

1. 只做模块级或专题级概览，不重复写整仓总览。
2. 先说业务位置和职责，再说代码入口。
3. 结合当前项目主线解释模块位置，不脱离业务链单独描述代码。
4. 指到真实目录、真实文件、真实入口，但不过度展开实现细节。
5. 说明与 Odoo 原生、其他 custom addons 的边界关系。
6. 不把历史术语或过时命名误写成当前基线。

## Workflow

### 1. Lock the scope

先明确概览对象：

- 是某个 addon
- 某条业务链路
- 某类接口
- 某组页面
- 还是某个专题能力

范围太大时，先收窄，不要一次试图覆盖整个仓库。
如果一个范围横跨多个 addon，但仍围绕同一条业务链或同一类能力，可以按“专题概览”处理；否则应拆分。

### 2. Locate the module in the business baseline

先回答：

- 这个模块在 `wave -> batch -> waybill -> trace -> evidence -> exception` 哪一段
- 它解决什么问题
- 它和哪些官方模块、custom addons 有关系
- 它是主模块、支撑模块，还是桥接模块

### 3. Read the code and docs by entry points

优先查看：

- 相关 `AGENTS.md`、`docs/context/`、`docs/architecture/`
- 目标 addon 的 `__manifest__.py`
- 关键模型、视图、controller、security、data
- 与之相邻的 custom addon 或前端页面入口

如果是前端专题，也要指出 action、template、asset bundle 或页面入口。

### 4. Summarize in an onboarding shape

默认覆盖这些部分：

- 模块定位
- 责任边界
- 业务主流程中的位置
- 关键模型 / 页面 / 接口 / 入口文件
- 与上下游模块的关系
- 主要状态、规则、约束
- 建议阅读顺序
- 常见误解或历史命名提醒

### 5. Keep it actionable

产出要能回答：

- 我第一次看这块，从哪里开始
- 改这个能力通常会碰到哪些文件
- 哪些地方最容易误判边界
- 这块和 Odoo 原生各自负责什么

## Suggested Output Template

默认按下面顺序输出：

1. Scope
2. Module Position
3. Responsibility and Boundary
4. Key Files and Entry Points
5. Main Flow or Interaction Path
6. Reading Order
7. Risks / Common Misunderstandings
8. Next Read

如果概览对象不是单个 addon，而是某个切片或专题，`Scope` 里先写清楚：

- 这不是整仓总览
- 当前覆盖哪些 addon / 页面 / 接口
- 明确不覆盖哪些相邻能力

## Checklist

- 是否已经收窄到模块级或专题级，而不是整仓级
- 是否说明了业务主线中的位置
- 是否标注了真实目录或关键文件入口
- 是否说明了和 Odoo 原生、其他 custom addons 的边界
- 是否指出了历史术语或桥接命名
- 是否足够支撑快速 onboarding 或后续协作

## Output Expectation

使用这个 skill 时，结果至少要让接手的人快速理解：

- 这块能力在整个物流体系里负责什么
- 读代码和读文档应该从哪里开始
- 边界在哪里，最容易踩坑的点是什么
- 如果接下来要改它，第一批该看哪些文件
