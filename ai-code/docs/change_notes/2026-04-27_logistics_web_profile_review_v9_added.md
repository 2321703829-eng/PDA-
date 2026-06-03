# 2026-04-27 `logistics_web` profile 编辑/查询入口排查报告已补充

## 本次变更

- 新增排查报告：
  - `docs/review/findings/2026-04-27_high_risk_bug_review_v9_logistics_web_profiles.md`

## 报告范围

- `logistics_web` 中直接面向 profile / master data 的接口与对象方法
- driver / vehicle profile 查询、入口跳转、展示口径

## 本轮结论

- 未确认到新的 `logistics_web` 主数据写入越权接口
- 已确认 3 个查询/入口层问题：
  1. driver / vehicle 页面仍按单一 `waybill.store_id` 处理门店，与多配送节点模型不一致
  2. driver profile 的 `remark` 字段接到了当前模型里不存在的字段
  3. 统计中心到 driver 管理页的跳转权限模型与实际 viewer 组不一致

## 说明

- 本次仅新增审计报告和登记说明
- 未改业务代码
- 已补最小运行验证：
  - 库内确实存在多配送节点运单
  - 当前 `hr.employee` 确实不存在 `notes/note` 字段
