# 2026-04-27 bug 审计与修复报告合并

## 本次变更

- 将 2026-04-27 当日产生的 bug 排查、修复、回归相关小报告，合并为一份总报告：
  - `docs/review/findings/2026-04-27_bug_audit_and_fix_master_report.md`
- 删除原先分散的小报告，避免 `docs/review/findings/` 下同一轮 bug 审计资料过度碎片化。

## 删除的小报告范围

- 导出链、导入链、trace 主链、dispatch 上游、主数据、logistics_web profile、stats 回归等阶段性小报告
- 仅删除本轮 bug 审计/修复相关的小报告
- `agent_kit`、skill 校准、页面冲突等非本轮 bug 审计主题文档未删除

## 说明

- 本次操作属于文档治理，不涉及业务代码修改。
- 变更目的在于把“同一轮 bug 审计”的阅读入口收敛成单文件，便于对外汇报和后续维护。
