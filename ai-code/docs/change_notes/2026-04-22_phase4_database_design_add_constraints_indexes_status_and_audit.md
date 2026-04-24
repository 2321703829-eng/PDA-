# 2026-04-22 phase4 database design add constraints indexes status and audit

## 本次调整

在《四期数据库底表设计稿 v1（第二次修正版）》中补充了数据库后端落地需要的 5 类内容：

- 约束设计
- 索引设计
- 状态枚举设计
- 写入边界设计
- 日志审计设计

## 主要新增内容

### 约束

- 明确了 `wave_no`、`batch_no`、`waybill_no` 的唯一建议
- 明确了 `customer_line_no` 建议采用 `(waybill_id, customer_line_no)` 唯一
- 明确了订单层和商品层的非空与合法性建议

### 索引

- 补充了高频查询字段索引
- 补充了状态字段索引
- 补充了组合索引建议
- 明确了不建议首轮直接索引的大文本字段

### 状态枚举

- 补充了 `payment_status`
- `audit_status`
- `settlement_status`
- `doc_status`
- `logistics_status`
- `logistics_role`

统一要求数据库层使用英文枚举值。

### 写入边界

- 明确了主数据优先命中、快照层不反向覆盖主数据
- 明确了主数据未命中时的快照兜底规则
- 明确了关键字段的单一事实来源

### 日志审计

- 补充了导入日志对象建议
- 补充了图片导入日志对象建议
- 补充了审计字段与敏感字段审计关注点

## 目的

让数据库底表设计稿从“结构与字段设计稿”进一步升级为“可落地的数据库后端设计底稿”。
