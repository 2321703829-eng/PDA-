# 2026-04-23 页面冲突改造总验收

## 目标

对客户、门店、司机、车辆四条入口链做一次总验收，确认页面冲突改造四步执行后，系统已经从“主档 / 画像 / 运营页并列打架”收口为：

- 主档负责基础档案维护
- 画像负责物流专有补充信息
- 司机/车辆运营页负责驾驶舱与跳转

验收库：

- `odoo_logistics_phase4_v1`

## 验收范围

1. 菜单归属
2. 独立画像菜单权限收口
3. 主档 smart button 入口
4. 司机/车辆运营页 client action 链
5. 主档到画像的动作返回
6. 画像重复字段是否已回归主档

## 结论

本轮四步改造已基本通过总验收。

四条入口链当前口径如下：

- 客户：`res.partner` 主档 -> `客户经营画像`
- 门店：`res.partner` 主档 -> `门店配送画像`
- 司机：`hr.employee` 主档 -> `司机画像`；运营侧 `司机管理` -> 驾驶舱 -> 主档/画像跳转
- 车辆：`fleet.vehicle` 主档 -> `车辆画像`；运营侧 `车辆管理` -> 驾驶舱 -> 主档/画像跳转

没有发现“普通业务用户默认看到原生主档 + 画像独立菜单 + 运营页三套并列入口”的结构性回退。

## 验收结果

### 1. 菜单与权限

验证结果：

- `contacts.menu_contacts` 已恢复为顶层入口
- `hr.menu_hr_root` 已恢复为顶层入口
- `fleet.menu_root` 已恢复为顶层入口
- `logistics_web.menu_logistics_web_driver_management` 仍位于 `天枢科技物流系统/物流`
- `logistics_web.menu_logistics_web_vehicle_management` 仍位于 `天枢科技物流系统/物流`
- 四个独立画像菜单仅绑定 `物流画像配置管理员`

对应菜单：

- `logistics_base.menu_logistics_customer_profile`
- `logistics_base.menu_logistics_store_profile`
- `logistics_base.menu_logistics_driver_profile`
- `logistics_base.menu_logistics_vehicle_profile`

### 2. 客户链路

数据库动作验证通过：

- 主档记录 `partner_id=8`
- `action_open_or_create_customer_profile()` 返回 `res_model = logistics.customer.profile`
- 返回画像记录 `partner_id = 8`
- `logistics_customer_profile_count = 1`

字段一致性验证通过：

- `profile.customer_seq_no == partner.logistics_customer_code`
- `profile.registered_address == partner.address_full`

### 3. 门店链路

数据库动作验证通过：

- 主档记录 `partner_id=9`
- `action_open_or_create_store_profile()` 返回 `res_model = logistics.store.profile`
- 返回画像记录 `partner_id = 9`
- `logistics_store_profile_count = 1`

字段一致性验证通过：

- `profile.customer_name == partner.customer_name`
- `profile.address_full == partner.address_full`

### 4. 司机链路

数据库动作验证通过：

- 主档记录 `employee_id=2`
- `action_open_or_create_driver_profile()` 返回 `res_model = logistics.driver.profile`
- 返回画像记录 `employee_id = 2`
- `logistics_driver_profile_count = 1`

字段一致性验证通过：

- `profile.internal_driver_code == employee.logistics_employee_code`
- `profile.driver_phone == employee.mobile_phone/work_phone/private_phone 归并结果`

运营页 source-chain 验证通过：

- `ir.actions.client.tag = logistics_web.driver_management`
- JS registry key = `logistics_web.driver_management`
- `static template = logistics_web.DriverManagementActionV2`
- XML `t-name = logistics_web.DriverManagementActionV2`
- JS/XML 均在 `logistics_web.__manifest__.py` 中声明

### 5. 车辆链路

数据库动作验证通过：

- 主档记录 `vehicle_id=1`
- `action_open_or_create_vehicle_profile()` 返回 `res_model = logistics.vehicle.profile`
- 返回画像记录 `vehicle_id = 1`
- `logistics_vehicle_profile_count = 1`

运营页 source-chain 验证通过：

- `ir.actions.client.tag = logistics_web.vehicle_management`
- JS registry key = `logistics_web.vehicle_management`
- `static template = logistics_web.VehicleManagementActionV2`
- XML `t-name = logistics_web.VehicleManagementActionV2`
- JS/XML 均在 `logistics_web.__manifest__.py` 中声明

## 剩余风险

### 1. 浏览器级人工点击未做

本次验收完成了：

- 源码链路验证
- 模块升级验证
- 数据库动作返回验证
- 样例数据一致性验证

但还没有做浏览器里逐页点击的人工验收，所以以下内容仍属于残余风险：

- smart button 在真实表单中的显示位置和交互观感
- 司机/车辆驾驶舱按钮在浏览器中的实际点击体验
- 普通业务账号登录后的最终可见菜单树

### 2. 车辆主档显示存在历史数据/编码噪音

测试库里的车辆显示名仍带有编码噪音痕迹，不影响本次“页面去打架”结构验收，但会影响界面观感，建议后续单独清理测试数据或补统一显示名规则。

## 建议

下一步建议分两类继续：

1. 做一次浏览器人工验收：
   - Contacts -> 客户/门店主档 -> smart button
   - HR -> 司机主档 -> smart button
   - Fleet -> 车辆主档 -> smart button
   - 物流 -> 司机管理 / 车辆管理 -> 驾驶舱按钮

2. 单独做一轮测试数据整理：
   - 客户/门店中文名称
   - 车辆显示名
   - 编号与标签统一规则
