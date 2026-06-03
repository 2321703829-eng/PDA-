# 2026-04-22 phase4 database design add driver vehicle layers for dispatch

## 本次调整

在《四期数据库底表设计稿 v1（第二次修正版）》中补充了司机与车辆面向排线模块的三层设计。

## 调整点

### 三层结构收口

- 明确司机与车辆统一按三层拆分：
  - 基本信息层
  - 当前调度状态层
  - 历史业务记录层
- 将司机/车辆“快照层”统一收口为“当前调度状态层”，避免与运单/门店业务快照层混淆

### 新增/补充对象

- `fleet.vehicle` 扩展
- `logistics_vehicle_profile`
- `logistics_driver_dispatch_state`
- `logistics_vehicle_dispatch_state`
- `logistics_driver_assignment_history`
- `logistics_vehicle_assignment_history`

### 排线模块字段口径

- 司机夜班意愿进入司机画像层
- 当前待命仓、当前司机/车辆、当前批次、当前可调度状态进入当前调度状态层
- 排线读取优先使用画像层与当前调度状态层，不直接读取运单快照层

### 历史追溯口径

- 历史层只保存历史关联键和摘要
- 不复制完整订单事实
- 需要完整订单信息时，继续从 `waybill -> customer_line -> order_line -> goods_line` 主链反查

### 配套补充

- 补充了唯一约束、默认值、合法性约束
- 补充了面向排线的索引建议
- 补充了司机/车辆当前调度状态枚举
- 补充了司机敏感字段的审计与权限边界

## 目的

让四期数据库底表设计不仅能承接导入、执行和追溯，也能直接服务后续排线模块对司机与车辆的实时筛选和状态判断。
