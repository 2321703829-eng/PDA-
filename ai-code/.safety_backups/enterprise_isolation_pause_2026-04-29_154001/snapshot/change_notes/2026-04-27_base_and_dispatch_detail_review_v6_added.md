# 2026-04-27 Logistics Base 与 Dispatch 明细对象排查 v6 已补充

## Objective

补充一份针对 `logistics_base` 和 `logistics_dispatch` 明细对象的高风险 bug 排查结果。

## Added Document

- `docs/review/findings/2026-04-27_high_risk_bug_review_v6_base_and_dispatch_detail.md`

## Summary

- 已确认 `goods_line_v2` 存在按非存储 computed 字段搜索的真实运行时 bug
- 已确认 `logistics_base` 画像主数据 ACL 过宽
- 已确认 `customer_line / goods_line / order_line` 缺少跨层一致性约束
- 已确认 route planning 与主数据变更日志对象仍可被普通内部用户后改写
