# 2026-04-27 高风险 bug 排查报告 v4 已新增

## Objective

记录 `logistics_trace_core + logistics_web trace 直连入口 + logistics_dispatch trace 依赖行为` 的高风险静态排查结果。

## What Changed

- 新增审查报告：
  - `docs/review/findings/2026-04-27_high_risk_bug_review_v4_trace_core_and_direct_entries.md`

## Notes

- 本次仅新增审查文档，没有修改业务代码。
- 报告结论聚焦：
  - `logistics.trace.event` ACL 过宽
  - `waybill / batch` 绑定约束不完整
  - 运单 trace 聚合口径与状态枚举不一致
