# logistics-requirement-brief

## Purpose

把一句话需求、会议结论、口头想法或临时任务，先收成一版轻量、可继续推进的需求摘要。

这个 skill 位于正式结构化需求和技术方案之前。它不是完整 PRD，也不是详细设计，而是帮团队先把方向、范围、主对象和关键问题锁定下来，避免一开始就在模糊前提下直接写方案或改代码。

## Use When

- 用户只给了一个想法，还没到完整需求文档粒度
- 需要先整理“这次到底要解决什么”
- 需要为后续 `logistics-structured-prd` 或技术方案做上游收口
- 需求还在探索期，但已经需要形成一份可讨论、可回看的摘要
- 需要快速明确主对象、主线、边界和待确认项

## Trigger Phrases

出现下面这类话时，优先考虑用这个 skill：

- “先帮我整理一下这个需求”
- “写个需求摘要 / brief”
- “把这个想法先收成一页”
- “先别展开 PRD，先锁目标和范围”
- “我现在思路比较散，帮我归纳一下”

## Not For

下面这些情况，优先不要用这个 skill：

- 已经需要完整的结构化需求或 PRD
- 已经进入模型、接口、service 层方案设计
- 重点是评审需求质量而不是先整理需求
- 重点是做多文档一致性检查

## Core Standard

默认遵守 6 条摘要基线：

1. 先收敛目标，再展开细节。
2. 先锁主对象和主线，再谈页面或字段。
3. 明确范围内与范围外，不假装什么都已确定。
4. 使用当前项目术语，不引入外部流程术语。
5. 不把技术实现细节提前伪装成业务需求。
6. 结果应能直接作为下游结构化需求或方案输入。

## Workflow

### 1. Normalize the input

先用最短的话归纳：

- 谁提出这个需求
- 想解决什么问题
- 当前痛点是什么
- 成功后什么会变得不同

### 2. Lock the project position

明确它位于哪条主线：

- `wave -> batch -> waybill -> waybill order lines`
- `waybill -> trace -> evidence -> exception`

如果主对象不清楚，要先指出，不要跳过。

### 3. Write the minimum brief structure

默认覆盖：

- Objective
- Current Problem
- Main Object / Related Objects
- Scope / Out of Scope
- Main Flow Sketch
- Key Rules or Constraints
- Open Questions

### 4. Prepare for downstream work

如果这个摘要后面要继续推进，补一句：

- 下一步更适合进入结构化需求
- 下一步更适合进入技术方案
- 还是先需要业务确认

## Suggested Output Template

默认按下面顺序输出：

1. Objective
2. Current Problem
3. Main Object / Main Line
4. Scope / Out of Scope
5. Main Flow Sketch
6. Key Constraints
7. Open Questions
8. Suggested Next Step

## Checklist

- 是否收敛了目标
- 是否写清了主对象和业务主线
- 是否说明了范围内与范围外
- 是否避免提前写成实现方案
- 是否保留了待确认项
- 是否足够支撑进入下一步

## Output Expectation

使用这个 skill 时，结果至少要让团队快速知道：

- 这次要解决的到底是什么
- 主要围绕哪个对象和哪条主线
- 当前边界在哪里
- 接下来应该继续写 PRD、写方案，还是先回业务确认
