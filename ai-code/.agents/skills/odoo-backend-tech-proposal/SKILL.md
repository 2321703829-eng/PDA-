# odoo-backend-tech-proposal

## Purpose

把“后端技术方案”写成适配当前 Odoo 物流项目的本地化版本。

这个 skill 的目标不是产出泛泛而谈的长文，而是帮助我们在真正动代码前，先把方案锁定到可实现、可升级、可验证的粒度，重点覆盖：

- Odoo 原生能力对比
- 自定义 addon 边界
- Outcome / Behavior / Boundary
- 模型、状态、接口、页面、导入导出影响
- 升级与验证路径

## Use When

- 需要写后端技术方案、详细设计、模块设计
- 需要新增或调整 custom addon 责任边界
- 需要设计模型、字段、状态、接口、事件、SQL 路径
- 需要判断某项能力应该复用 Odoo、扩展 Odoo，还是自建
- 用户给的是目标或想法，但还没有稳定到可以直接实现的规格

## Trigger Phrases

出现下面这类话时，优先考虑用这个 skill：

- “给这个需求出一版后端技术方案”
- “先别写代码，先把模型 / service / controller 方案定下来”
- “帮我判断这块该复用 Odoo 还是自建”
- “把这块拆成 addon、模型、接口、任务链”
- “整理一版能直接指导开发的详细设计”

## Not For

下面这些情况，优先不要用这个 skill：

- 只是想把零散需求整理成结构化需求稿
- 只是要 review 需求质量或 PRD 质量
- 只是要检查文档和代码是否一致
- 只是要快速了解某个模块从哪里开始读

## Core Standard

默认遵守 5 条方案基线：

1. 先对比 Odoo 原生能力，再决定自定义方案。
2. 先锁定 Outcome / Behavior / Boundary，再进入实现。
3. 方案优先贴合当前主线：`wave -> batch -> waybill -> trace -> evidence -> exception`。
4. 自定义能力尽量落在 custom addons，不直接改官方核心逻辑。
5. 每个方案都要能回答“怎么验证”和“升级是否安全”。

## Workflow

### 1. Clarify the target

先用最短的话说清楚：

- 这次要解决什么业务问题
- 谁会使用
- 现在哪一步卡住
- 改完之后什么必须变成真

如果目标仍然模糊，先补 Outcome / Behavior / Boundary，不要直接写实现细节。

### 2. Compare Odoo native capability

必须先回答下面 3 个问题：

- Odoo 原生已经提供了什么
- 原生能力为什么不够
- 这次选择的是 `reuse directly`、`extend Odoo` 还是 `create custom capability`

如果没有做这一步，这个方案默认还不够成熟。

### 3. Lock OBB

至少明确：

- Outcome：最终必须成立的业务结果
- Behavior：输入、输出、流转、状态、权限、异常表现
- Boundary：归属模块、兼容性、例外情况、明确不做的范围

### 4. Design by project-specific structure

方案正文默认覆盖：

- 目标与背景
- Odoo 基线对比
- 方案选择结论
- 业务对象与主链位置
- 模块归属与职责拆分
- 数据模型 / 字段 / 状态 / 枚举
- API / route / action / import-export / 页面联动影响
- 权限与企业隔离
- 升级兼容与历史数据处理
- 验证方案
- 风险与未决事项

### 5. Keep the design implementation-ready

结论必须能直接指导后续实现，至少要说明：

- 影响哪些 addon、模型、视图、接口或前端页面
- 哪些点必须先补 spec 或设计文档
- 哪些点能分阶段落地
- 最小验证清单是什么

## Suggested Output Template

默认按下面顺序输出：

1. Objective
2. Odoo Benchmark
3. Outcome / Behavior / Boundary
4. Design Decision
5. Contract Surface
6. Affected Modules / Files
7. Verify
8. Risks / Open Questions

其中 `Contract Surface` 至少要说明：

- 主对象与主链位置
- 关键模型 / 字段 / 状态
- API / route / action
- 导入导出或任务链契约
- 权限与升级影响

## Checklist

- 是否先做了 Odoo 原生能力对比
- 是否明确选择了复用、扩展或自建
- 是否锁定了 Outcome / Behavior / Boundary
- 是否说明了模块归属与责任边界
- 是否覆盖了字段、状态、接口、导入导出或页面影响
- 是否说明了升级兼容和历史数据处理
- 是否给出了最小验证路径
- 是否指出要同步哪些 docs 和 `change_notes`

## Output Expectation

使用这个 skill 时，最终结果至少要让团队快速回答：

- 这项能力应该放在哪里做
- 为什么这么做比其他路径更合适
- 真正开始实现前，还缺哪一块规格
- 落地后怎么验证它没有跑偏
