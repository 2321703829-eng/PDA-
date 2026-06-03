# 客户=门店 单对象收口方案

## Objective

- 以你当前确认的业务口径为准：`客户 = 门店 = 同一个业务对象`
- 结束当前“客户一套、门店一套、画像两套、入口两套”的拆分状态
- 统一首页入口、主档模型、画像入口、调度引用和页面命名

## Boundary

- 本方案只定义“客户/门店”单对象收口方向
- 本方案不直接编码
- 本方案优先面向四期首轮实际使用口径，不追求兼容旧的双对象语义
- 运单、配送节点、货物、司机、车辆主链不在本次重构范围内，只调整它们对客户对象的引用方式

## Benchmark

- Odoo 原生主档基础继续以 `res.partner` 为核心
- 不再人为在业务层拆成“客户主档”和“门店主档”两种用户必须区分的对象
- 物流定制能力以“一个主档 + 一套物流画像”方式补充，不再并列两套画像

## Current Understanding

### 当前系统为什么让人困惑

当前实现里，同一个业务对象被拆成了四层：

- `res.partner`
  - 同时挂了 `is_logistics_customer` 和 `is_logistics_store`
- `logistics.customer.profile`
  - 客户经营画像
- `logistics.store.profile`
  - 门店配送画像
- 调度链路里又继续拆成：
  - `customer_id`
  - `store_id`
  - `partner_id`

对应代码落点：

- [res_partner.py](/D:/Desktop/Odoo/custom_addons/logistics_base/models/res_partner.py:8)
- [logistics_customer_profile.py](/D:/Desktop/Odoo/custom_addons/logistics_base/models/logistics_customer_profile.py:4)
- [logistics_store_profile.py](/D:/Desktop/Odoo/custom_addons/logistics_base/models/logistics_store_profile.py:5)
- [logistics_dispatch_waybill.py](/D:/Desktop/Odoo/custom_addons/logistics_dispatch/models/logistics_dispatch_waybill.py:33)
- [logistics_dispatch_waybill_customer_line_v2.py](/D:/Desktop/Odoo/custom_addons/logistics_dispatch/models/logistics_dispatch_waybill_customer_line_v2.py:38)

这套设计的问题不是“字段多”，而是**用户必须先理解系统怎么拆，才能找到入口**。  
如果业务上已经明确“客户和门店就是同一个对象”，那这套拆法应该收口，而不是继续解释。

## Proposed Direction

### 总原则

- 一个对象：`客户`
- 一个主档：`res.partner`
- 一套画像：`物流客户画像`
- 一个首页入口：`客户`
- 一套调度引用：统一只关联一个客户主档

## 一、首页入口怎么改

### 目标状态

企业首页的“系统模块”区域补一个清晰入口：

- `客户`

说明文案建议：

- `进入客户主档、画像与配送规则维护`

### 顶部入口口径

- 保留 Odoo 原生顶层 `客户`
- 企业首页卡片也补 `客户`
- 不再新增单独的 `门店` 首页入口

### 用户体验规则

- 想看客户资料：进 `客户`
- 想看物流画像：也进 `客户`
- 想看本次运单节点：进 `配送节点明细`

也就是说：

- 首页不再要求用户先理解“客户”和“门店”有什么区别
- 首页只暴露一个业务入口：`客户`

## 二、模型哪些该合并

### 1. 主档模型收口

继续保留：

- `res.partner`

取消双对象语义：

- `is_logistics_customer`
- `is_logistics_store`

建议收口为：

- `is_logistics_partner`

如果要降低迁移成本，可先过渡一版：

- 短期保留原字段
- 业务口径上要求两者始终同步
- 页面不再暴露“客户/门店二选一”

### 2. 画像模型收口

当前两套画像：

- `logistics.customer.profile`
- `logistics.store.profile`

建议目标：

- 合并为单一画像模型：`logistics.partner.profile`

角色：

- `res.partner` 承担主档身份信息
- `logistics.partner.profile` 承担物流专有画像信息

### 3. 调度引用模型收口

当前调度链路里的双引用需要统一：

- `waybill.customer_id`
- `waybill.store_id`
- `customer_line.customer_id`
- `customer_line.store_id`
- `customer_line.partner_id`

建议目标：

- 统一收口成一个字段：
  - `partner_id`
  - 或更直白地命名成 `customer_partner_id`

原则：

- 运单层只认一个客户主档
- 配送节点层也只认一个客户主档
- 不再同时保留“客户”和“门店”双 FK

## 三、页面哪些名字要统一

### 首页与导航

- `客户`
  - 保留
- `门店`
  - 从首页入口和主导航里移除

### 主档页

- `客户主档`
  - 作为统一入口名称
- `门店主档`
  - 不再作为独立用户概念出现

### 画像页

当前：

- `客户经营画像`
- `门店配送画像`

建议统一为：

- `物流客户画像`

如果确实需要在画像内区分不同信息块，放在页内分组，而不是做成两张画像：

- `经营信息`
- `配送信息`
- `收货规则`

### 节点页

- `配送节点明细`
  - 可以保留

原因：

- 这是执行页面，不是主档页面
- “配送节点”描述的是运单内节点，不等于主档对象名称

但页面内部字段命名应统一：

- `客户号`
- `客户名称`
- `联系人`
- `联系电话`
- `地址`

不再混用：

- `客户号 / 门店号`
- `客户 / 门店`
- `客户名称 / 门店名称`

## 四、哪些字段保留、哪些字段删掉

## 4.1 主档 `res.partner` 建议保留

### 识别字段

- `name`
- `internal_customer_code`
- `external_customer_code`
- `logistics_internal_reference`

### 联系字段

- `contact_name`
- `contact_phone`

### 地址字段

- `address_full`
- `partner_longitude`
- `partner_latitude`
- 结构化地址字段
  - 建议统一保留一个 JSON 字段，例如 `address_region_json`

### 基础经营字段

- `customer_status`
- `organization_name`
- `channel_name`
- `department_name`
- `salesperson_name`

### 基础物流字段

- `logistics_delivery_time_window`
- `logistics_unload_requirement`
- `logistics_need_sign_receipt`
- `logistics_service_note`

## 4.2 统一画像建议保留

### 来自“客户经营画像”的字段

- `customer_level`
- `allow_cash_on_delivery`
- `internal_counterparty_flag`
- `invoice_type`

### 来自“门店配送画像”的字段

- `delivery_window_text`
- `receive_start_time`
- `receive_end_time`
- `receive_time_slots_text`
- `no_receive_time_slots_text`
- `delivery_week_flags`
- `default_signoff_requirement`
- `delivery_access_flags`
- `illegal_parking_flag`
- `free_parking_minutes`
- `parking_fee_per_hour`
- `parking_location_text`
- `parking_mode_text`
- `unload_entrance_text`
- `unload_location_text`
- `upstairs_floor_count`
- `basement_height_limit_text`
- `route_preference`
- `warehouse_preference`

## 4.3 建议删除或淘汰的双对象字段

### 主档层

- `is_logistics_customer`
- `is_logistics_store`
- `logistics_customer_code`
- `logistics_store_code`
- `logistics_customer_status`
- `logistics_store_status`
- `logistics_customer_profile_count`
- `logistics_store_profile_count`

### 动作与入口层

- `action_open_or_create_customer_profile`
- `action_open_or_create_store_profile`
- `客户经营画像`
- `门店配送画像`

### 调度链路层

- `customer_id` 与 `store_id` 并存模式
- `customer_no` 与 `store_no` 并存模式
- `customer_name` 与 `store_name` 并存模式

## 五、页面收口后的推荐结构

### 1. 客户页

统一只保留一张主档页，页签建议：

- `基础信息`
- `物流信息`
- `物流客户画像`
- `联系人`
- `备注`

### 2. 物流画像页

统一只保留一张画像页，分组建议：

- `经营信息`
- `配送规则`
- `到店与停车`
- `收货时间`
- `签收与卸货`

### 3. 配送节点页

继续保留为执行页，但引用单一对象：

- 只显示一个客户主档
- 只保留一个客户编号口径
- 页面内展示本次运单的快照信息

## 六、推荐迁移策略

### 第一阶段：先统一用户口径

- 首页补 `客户` 入口
- 页面名称先统一
- 不再向用户暴露“客户/门店”两套概念

### 第二阶段：统一页面入口

- 主档页只保留一个画像入口
- 配送节点页增加“打开物流客户画像”
- 删除双画像菜单

### 第三阶段：统一数据结构

- 合并画像表
- 收口主档标记字段
- 收口调度链路双 FK

## Risks

- 当前代码里双对象引用较多，直接硬删会影响导入、查询、搜索域和旧视图
- 如果不做过渡层，短期改动面会集中在：
  - `logistics_base`
  - `logistics_dispatch`
  - `logistics_web`
- 若历史文档仍继续使用“客户/门店双对象”表述，会在后续联调里反复打架

## Next Suggestion

先按下面顺序推进，风险最小：

1. 首页补 `客户` 入口
2. 主档和画像文案统一成单对象口径
3. 配送节点页从“客户/门店双字段”收成单字段口径
4. 最后再动数据库模型与画像表合并
