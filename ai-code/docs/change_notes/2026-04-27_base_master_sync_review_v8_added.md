# 2026-04-27 `logistics_base` 主数据写入与同步链高风险排查报告已补充

## 本次变更

- 新增排查报告：
  - `docs/review/findings/2026-04-27_high_risk_bug_review_v8_base_master_sync.md`

## 报告范围

- `logistics_base`
- `logistics_web` 中直接面向 profile / master data 的对象方法
- `logistics_dispatch` 中引用这些主数据快照的关键字段同步点

## 本轮确认的问题

1. `res.partner` 主数据编码允许重复，但 `dispatch` 解析链假定唯一，形成运行时冲突
2. `logistics.dispatch.waybill.partner_id` 的 inverse 写回链存在递归写死
3. `wave -> batch -> waybill -> customer_line` 的主数据 snapshot 自动回填基本未真正生效

## 说明

- 本次仅新增审计报告与登记说明
- 未改业务代码
- 报告中的第 1、2、3 条均已补最小运行验证，不是纯静态猜测
