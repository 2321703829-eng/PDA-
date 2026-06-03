# 2026-04-27 Enterprise Isolation Overview Trimmed To Current Plan Only

## 本次变更

重写 `专题设计/企业隔离设计/00_导航与总纲/企业隔离方案可行性与分期落地调整说明.md`，去掉过多围绕旧 `.docx` 原方案展开的介绍性内容，只保留当前企业隔离专题继续推进时真正需要使用的现行方案口径。

## 调整重点

- 删除旧原方案的大段流程复述与平台化展开说明
- 删除平台库、套餐、授权、指标仓、灰度发布等 `P2 / P3` 细节性内容
- 保留并强化当前有效边界：
  - 企业之间默认数据库级隔离
  - 同企业内部多法人协同才考虑 `multi-company`
  - 当前只收口 `P0 / P1`
- 保留并强化当前有效业务基线：
  - `wave -> batch -> waybill -> customer_line -> order_line -> goods_line`
  - `waybill -> customer_line -> order_line`
  - `waybill -> customer_line -> 图片预览 / 留痕 / 证据`
  - 正式证据对象仍围绕 `trace_event`
- 保留 `P1` 四块当前设计范围：
  - `trace`
  - `evidence`
  - `exception`
  - 三层联动与租户内角色边界

## 结果

企业隔离总纲从“原方案可行性分析 + 全量平台化展开”调整为“当前现行方案总纲”，更适合直接指导后续 `P1` 设计细稿、差距盘点、开发拆分与联调顺序。
