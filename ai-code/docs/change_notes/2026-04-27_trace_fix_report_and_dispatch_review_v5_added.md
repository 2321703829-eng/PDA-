# 2026-04-27 Trace 修复报告与 Dispatch 上游排查 v5 已补充

## Objective

- 补充本轮 `logistics_trace_core` 修复的正式报告
- 继续向 `logistics_dispatch` 主链上游排查 `waybill / batch / wave` 的状态回写与统计口径风险

## Added Documents

- `docs/review/findings/2026-04-27_trace_core_acl_object_binding_and_metrics_fix_report.md`
- `docs/review/findings/2026-04-27_high_risk_bug_review_v5_dispatch_upstream.md`

## Summary

- 归档了 trace 主链本轮修复内容与最小核验结果
- 新识别出 `logistics_dispatch` 上游 3 个高风险问题：
  - 普通内部用户对 `wave / batch / waybill` 仍有全量 CRUD
  - `waybill` 缺少 `warehouse_id` 与 `batch_id` 的后端一致性护栏
  - trace 完成状态不会回推到 dispatch 执行态，导致统计口径割裂

## Verify

- 报告内容基于本轮静态审查和 shell smoke 结果整理
- 未在本次文档补充中新增业务代码修改
