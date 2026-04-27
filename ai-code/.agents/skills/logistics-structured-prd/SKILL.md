# logistics-structured-prd

## Purpose

把零散需求、会议结论、口头描述或临时想法，整理成适合当前 Odoo 物流项目继续推进的结构化需求文档。

这个 skill 重点不是“写漂亮 PRD”，而是把需求收敛到可以继续做方案、评审、拆任务和验收的状态，避免后面实现时反复补定义。

## Use When

- 用户要“展开需求”“细化设计”“补完整规格”
- 现有描述只有目标，没有稳定的行为与边界
- 需要把需求转成可交给开发或 AI 持续执行的文档
- 一个需求会影响模型、状态、接口、页面或业务流程
- 需要为后续技术方案、代码实现或验收打基础

## Trigger Phrases

出现下面这类话时，优先考虑用这个 skill：

- “把这个需求展开成结构化文档”
- “先整理一版 PRD / 规格稿”
- “把口头想法收成可以继续推进的需求”
- “补一版完整的业务规则、流程和验收”
- “先别做技术方案，先把需求写清楚”

## Not For

下面这些情况，优先不要用这个 skill：

- 已经有稳定规格，只是想做需求质量评审
- 已经进入技术设计，重点是模型 / route / service 方案
- 只是要检查多份文档是否一致
- 只是要做模块上手概览

## Core Standard

默认遵守 5 条整理原则：

1. 先收敛业务目标，再展开实现影响。
2. 先写清主流程和异常流程，再谈字段和接口。
3. 使用当前项目术语，不引入上游仓库或其他系统的话语体系。
4. 需求文档要能支撑后续 OBB、技术方案和验证。
5. 不确定的内容要明确标成假设或待确认，不要伪装成既定事实。

## Workflow

### 1. Normalize the request

先把原始输入整理成最小需求摘要：

- 谁提出这个需求
- 目标是什么
- 涉及哪个业务主线
- 当前痛点是什么
- 成功标准是什么

### 2. Lock scope and actors

明确：

- 角色是谁
- 使用场景发生在哪个环节
- 哪些对象是主对象，哪些只是从属对象
- 哪些内容在本次范围内，哪些明确不做

默认遵守当前项目主线，不要把 `sale.order` 误当物流执行主对象。

### 3. Expand into structured sections

结构化正文默认覆盖：

- Objective
- Background / Current Problem
- Scope / Out of Scope
- Actors / Roles
- Main Flow
- Exception / Edge Cases
- Business Rules
- Data / Fields / Status / Enum
- API / Import / Export / Notification impact
- Permission / Isolation considerations
- Acceptance / Verify
- Open Questions

### 4. Prepare for downstream design

如果需求会影响方案或实现，继续补足：

- Outcome / Behavior / Boundary
- 可能影响的 addon 或页面
- 需要先更新的 spec / architecture / context 文档
- 依赖的上游数据或外部系统

### 5. Mark uncertainty explicitly

对于还没有共识的部分，要分清：

- 已确认规则
- 当前假设
- 待用户确认项
- 明确超出本次范围的内容

## Suggested Output Template

默认按下面顺序输出：

1. Objective
2. Background
3. Scope / Out of Scope
4. Actors / Main Object
5. Outcome / Behavior / Boundary
6. Main Flow / Exception Flow
7. Rules / Data / States
8. Interfaces / Page Impact
9. Acceptance / Open Questions

如果需求涉及任务链、导入导出或结果页，额外明确：

- 发起入口
- 主对象类型
- 结果回读或下载链
- 明确不做的能力

## Checklist

- 是否已经把零散输入整理成稳定目标
- 是否明确了主对象、从属对象和业务主线
- 是否覆盖主流程和异常流程
- 是否写清了规则、字段、状态或枚举
- 是否说明接口、导入导出或页面影响
- 是否标出了假设、待确认项和 out of scope
- 是否足够支撑后续技术方案或实现

## Output Expectation

使用这个 skill 时，产出应该能直接作为：

- 技术方案输入
- 任务拆解依据
- 设计评审底稿
- 验收与回归检查的上游文档
