# cross-doc-consistency-check

## Purpose

对当前项目里的多份文档，或“文档 + 代码 + 变更说明”进行一致性检查，优先找出会让团队理解分裂、实现跑偏或验收出错的冲突点。

这个 skill 不是做笼统的“文档润色”，而是帮助我们锁定哪一份内容才是当前基线，以及哪些地方需要同步修正。

## Use When

- 刚更新了 spec、architecture、context 或设计说明
- 一个需求跨多份文档，担心术语、状态、边界不一致
- 代码已经改了，需要回看文档有没有漏同步
- 用户要求做一致性检查、doc sync review 或交付前收口
- 需要判断哪份文档是权威来源，哪份只是历史描述

## Trigger Phrases

出现下面这类话时，优先考虑用这个 skill：

- “做一轮文档一致性检查”
- “看看 spec、实现和 change note 有没有打架”
- “帮我做 doc sync review”
- “这几份文档到底该以哪份为准”
- “哪些文档还要回调”

## Not For

下面这些情况，优先不要用这个 skill：

- 只是评审需求文档本身写得好不好
- 只是写一版后端方案
- 只是做某个模块的 onboarding 概览

## Core Standard

默认遵守 5 条检查原则：

1. 先找权威基线，再比对其他材料。
2. 先报冲突和风险，再给概括总结。
3. 只报有证据的问题，不报模糊猜测。
4. 项目术语、对象主线、状态规则优先保持一致。
5. 一致性检查要落到“谁改什么”与“还缺什么验证”。

## Workflow

### 1. Lock the source of truth

先明确本轮检查的权威来源，通常优先顺序是：

- `AGENTS.md`
- `docs/context/`
- `docs/architecture/ARCHITECTURE.md`
- 相关设计文档或模块说明
- 代码实现
- `docs/change_notes/`

如果存在历史术语或桥接命名，要明确说明它们不是当前有效基线。

### 2. Compare the critical dimensions

默认重点检查 8 个维度：

- 术语与对象命名
- 主流程与业务链路
- Outcome / Behavior / Boundary
- 模块归属与责任边界
- 字段 / 状态 / 枚举 / 规则
- API / 导入导出 / 页面结构
- 升级兼容与验证路径
- 文档同步与 change note 完整性

如果任务涉及接口、任务链或结果页，额外强制比对：

- 主对象类型
- 入口类型
- 包结构或结果结构
- 路由与返回壳
- 状态枚举与跳转链

### 3. Classify the findings

把发现分成三类：

- 直接冲突：两个来源给出互相矛盾的定义
- 漏同步：实现或设计变了，但相关文档没更新
- 表达漂移：没有硬冲突，但术语或边界容易让人误解

### 4. Recommend the sync action

每个问题至少说明：

- 冲突发生在哪些文件
- 当前应该以哪份内容为准
- 需要改文档、改代码，还是补 change note
- 是否还需要补验证或补 spec

## Suggested Output Template

默认按下面顺序输出：

1. Findings
2. Authoritative Baseline
3. Conflict Surface
4. Sync Actions
5. Open Questions / Assumptions
6. Short Summary

每条 finding 尽量包含：

- 冲突类型
- 文件位置
- 当前应以哪份为准
- 最小同步动作

## Checklist

- 是否先说明了哪份内容是当前基线
- 是否覆盖术语、主线、边界、状态、接口、验证这几类关键维度
- 是否区分了冲突、漏同步和表达漂移
- 是否给出明确同步动作，而不只是指出问题
- 是否检查了 `docs/change_notes/` 是否需要补充
- 是否说明了剩余风险或待确认项

## Output Expectation

使用这个 skill 时，结果至少要能回答：

- 现在到底该以哪份内容为准
- 哪些地方已经不一致
- 最小同步动作是什么
- 如果现在不修，会在哪个环节最容易出问题
