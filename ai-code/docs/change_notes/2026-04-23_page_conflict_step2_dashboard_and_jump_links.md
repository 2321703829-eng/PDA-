# 2026-04-23 页面去打架第二步：司机/车辆页收口为运营驾驶舱并补跳转

## 变更目标

按 `docs/dev/page_conflict_resolution_checklist.md` 的第二步执行，把司机管理页和车辆管理页从“并列主档维护页”收口成“运营驾驶舱 + 跳转”。

本轮目标是：

- 保留司机管理、车辆管理作为运营观察入口
- 明确页面不承担主档编辑职责
- 在详情头部补充“打开主档 / 打开画像”标准跳转

## Outcome

- 司机页在列表态和详情态都明确表达为“司机运营驾驶舱”
- 车辆页在列表态和详情态都明确表达为“车辆运营驾驶舱”
- 司机页可直接跳转到 `hr.employee` 和 `logistics.driver.profile`
- 车辆页可直接跳转到 `fleet.vehicle` 和 `logistics.vehicle.profile`

## Behavior

- 列表操作按钮由“查看画像”改为“进入驾驶舱”
- 详情头部新增：
  - 司机页：`打开员工主档`、`打开司机画像`
  - 车辆页：`打开车辆主档`、`打开车辆画像`
- 当画像记录不存在时，前端弹出 warning 提示，不直接报错

## Boundary

- 本轮不新增后端 API
- 本轮不修改司机/车辆服务的 DTO
- 本轮不处理画像独立菜单权限
- 本轮不处理主档与画像字段归属，只先收口页面定位和跳转

## 变更文件

- `custom_addons/logistics_web/static/src/js/actions/driver_management_action_v2.js`
- `custom_addons/logistics_web/static/src/js/actions/vehicle_management_action_v2.js`
- `custom_addons/logistics_web/static/src/xml/driver_management_templates_safe.xml`
- `custom_addons/logistics_web/static/src/xml/vehicle_management_templates.xml`
- `docs/dev/page_conflict_resolution_checklist.md`

## 实现说明

### 司机页

- 新增 `openDriverMasterRecord()`
- 新增 `openDriverProfileRecord()`
- 通过 `orm.searchRead("logistics.driver.profile", [["employee_id", "=", activeDriverId]], ["id"], { limit: 1 })` 查找画像记录
- 无画像时使用 `notification` 服务提示

### 车辆页

- `setup()` 中新增 `notification` 服务
- 新增 `openVehicleMasterRecord()`
- 新增 `openVehicleProfileRecord()`
- 通过 `orm.searchRead("logistics.vehicle.profile", [["vehicle_id", "=", activeVehicleId]], ["id"], { limit: 1 })` 查找画像记录
- 无画像时使用 `notification` 服务提示

### 模板文案

- 标题收口为“运营驾驶舱”
- 列表区说明收口为“先做运营判断，再跳主档/画像”
- 详情 badge 收口为“运营视图”

## 升级与验证

执行命令：

```powershell
python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_web --stop-after-init
```

验证结果：

- `driver_management_action_v2.js` 通过 `node --check`
- `vehicle_management_action_v2.js` 通过 `node --check`
- `driver_management_templates_safe.xml` 通过 XML 解析
- `vehicle_management_templates.xml` 通过 XML 解析
- `logistics_web` 模块升级成功

## 风险提示

- 这一步只是页面收口，不代表画像页权限已经收紧
- 如果当前用户无 `hr.employee` 或 `fleet.vehicle` 访问权限，跳转后仍会按 Odoo 权限规则受限
