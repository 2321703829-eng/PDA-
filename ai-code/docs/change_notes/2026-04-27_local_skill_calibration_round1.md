# Change Notes

## 本轮目标

- 用仓库里的真实业务切片试跑已本地化的需求 / 方案 / 一致性 / 概览类 skill
- 根据真实试跑结果，收紧触发语和输出模板，减少相邻 skill 的职责重叠

## 修改文件

- 更新 `.agents/skills/odoo-backend-tech-proposal/SKILL.md`
- 更新 `.agents/skills/logistics-structured-prd/SKILL.md`
- 更新 `.agents/skills/cross-doc-consistency-check/SKILL.md`
- 更新 `.agents/skills/structured-requirement-review/SKILL.md`
- 更新 `.agents/skills/odoo-module-overview/SKILL.md`
- 新增 `docs/review/local_skill_calibration_round1_from_waybill_export.md`
- 新增 `docs/change_notes/2026-04-27_local_skill_calibration_round1.md`

## 修改原因

- 前两批本地 skill 已落地，但触发语还偏宽，容易在真实任务中互相打架
- 用户明确要求“跑一遍，再把触发语和输出模板收紧一轮”
- `from_waybill` 导出链路具备较完整的需求、设计、任务拆分、落地代码与 smoke 证据，适合作为校准样本

## 改动摘要

- 为 5 个 skill 补了更明确的“典型触发语”
- 为 5 个 skill 补了“不要用于什么场景”
- 收紧了输出模板，突出各自最关键的结论结构
- 新增一份校准记录，说明试跑样本、发现的问题和本轮收口动作

## 影响范围

- 影响当前项目的本地 AI skill 资产与使用约定
- 不影响业务代码、模块行为、接口返回、权限、数据结构或升级兼容性

## 是否影响模型 / 视图 / 权限 / 数据兼容性

- 不影响

## 验证方法

- 检查 5 个 skill 是否都新增了更明确的触发语与误触发约束
- 检查输出模板是否比前一版更窄、更少重叠
- 检查校准记录是否明确说明了本轮真实样本和调整原因

## 风险点

- 当前仍是项目内模板层校准，不代表外部运行时一定自动按同样方式触发
- 后续如果再引入更多细分 skill，仍可能需要新一轮职责收口

## 回滚建议

- 若后续判断本轮收口方向不适合，可恢复以下文件的前一版内容：
  - `.agents/skills/odoo-backend-tech-proposal/SKILL.md`
  - `.agents/skills/logistics-structured-prd/SKILL.md`
  - `.agents/skills/cross-doc-consistency-check/SKILL.md`
  - `.agents/skills/structured-requirement-review/SKILL.md`
  - `.agents/skills/odoo-module-overview/SKILL.md`
- 或删除：
  - `docs/review/local_skill_calibration_round1_from_waybill_export.md`
  - `docs/change_notes/2026-04-27_local_skill_calibration_round1.md`

## 后续待办

- 用下一条真实任务继续验证触发边界，尤其是 `structured-requirement-review` 与 `cross-doc-consistency-check`
- 如果后续要纳入自动 discover，再补 frontmatter 或统一 skill 元数据策略
