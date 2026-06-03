# 2026-04-22 phase4 database design adjust delivery access fields

## 本次调整

根据最新业务字段截图，调整了“配送可达性/入场要求”字段设计。

## 调整点

### 保持在 `delivery_access_flags` 中汇总的布尔字段

- `小巷子` -> `alley`
- `连停` -> `continuous_stop`
- `手推车` -> `handcart`
- `托盘置换` -> `pallet_exchange`
- `保温箱置换` -> `cooler_box_exchange`
- `是否送货上门` -> `door_delivery`
- `是否无电梯` -> `no_elevator`

### 改为单独结构化字段

- `上楼层数`
  - `logistics_store_profile.upstairs_floor_count`
  - `customer_line.upstairs_floor_count_snapshot`
- `地库限高`
  - `logistics_store_profile.basement_height_limit_text`
  - `customer_line.basement_height_limit_text_snapshot`

## 调整原因

- `上楼层数` 不是简单布尔值，更适合数值字段
- `地库限高` 存在单位和现场表达差异，首轮更适合文本字段
- 其余字段仍适合沿用“导入多列布尔、数据库单字段编码汇总”的策略
