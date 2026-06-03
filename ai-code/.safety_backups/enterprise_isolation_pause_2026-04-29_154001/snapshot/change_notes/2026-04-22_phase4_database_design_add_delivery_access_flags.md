# 2026-04-22 phase4 database design add delivery access flags

## 本次调整

- 在《四期数据库底表设计稿 v1（第二次修正版）》中补充了“配送可达性/入场要求”字段设计。
- 明确导入层与数据库层采用不同表达方式：
  - 导入模板层继续保留多个布尔字段铺开
  - 数据库存储层统一汇总为单字段编码串

## 新增口径

- 主数据层新增：
  - `logistics_store_profile.delivery_access_flags`
- 快照层新增：
  - `logistics.dispatch.waybill.customer.line.delivery_access_flags_snapshot`

## 导入建议字段

- `是否上楼`
- `是否小巷`
- `是否送货上门`
- `是否无电梯`

## 首轮编码建议

- `是否上楼` -> `stairs`
- `是否小巷` -> `alley`
- `是否送货上门` -> `door_delivery`
- `是否无电梯` -> `no_elevator`

## 目的

- 保持业务填写体验简单
- 避免数据库横向膨胀出大量布尔列
- 保留后续查询、展示和规则判断的可扩展性
