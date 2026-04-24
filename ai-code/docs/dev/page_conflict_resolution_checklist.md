# 页面去打架改造清单

## 1. 目标

把当前物流系统里与 Odoo 原生页面互相打架的入口、模型、命名和编辑边界收口，形成下面这条稳定规则：

- 客户 / 门店主档统一归 `res.partner`
- 司机主档统一归 `hr.employee`
- 车辆主档统一归 `fleet.vehicle`
- `logistics_*_profile` 只承接物流画像补充信息，不再被当成第二套主档
- `logistics_web` 的司机管理 / 车辆管理只做运营驾驶舱，不再承担主档编辑职责
- 运单下 `customer_line` 不再用“客户明细”这种容易和客户主档混淆的名字

## 2. 边界

本清单只处理下面四类问题：

- 菜单入口冲突
- 页面定位冲突
- 权限与入口暴露冲突
- 数据编辑归属冲突

本清单不包含：

- 大规模字段迁移
- 前端视觉重做
- 历史数据修复脚本

## 3. 当前判断

当前冲突主要来自三层叠加：

- 同一个对象既扩展了原生主档，又建了独立画像模型
- 同一个对象同时暴露了原生页、画像页、物流运营页三套入口
- `ui_label_sync` 在运行时重挂了部分原生菜单，导致系统结构进一步混杂

关键落点：

- 原生主档扩展：
  - [res_partner.py](/D:/Desktop/Odoo/custom_addons/logistics_base/models/res_partner.py:7)
  - [hr_employee.py](/D:/Desktop/Odoo/custom_addons/logistics_base/models/hr_employee.py:8)
  - [fleet_vehicle.py](/D:/Desktop/Odoo/custom_addons/logistics_base/models/fleet_vehicle.py:5)
- 独立画像模型：
  - [logistics_customer_profile.py](/D:/Desktop/Odoo/custom_addons/logistics_base/models/logistics_customer_profile.py:7)
  - [logistics_store_profile.py](/D:/Desktop/Odoo/custom_addons/logistics_base/models/logistics_store_profile.py:6)
  - [logistics_driver_profile.py](/D:/Desktop/Odoo/custom_addons/logistics_base/models/logistics_driver_profile.py:6)
  - [logistics_vehicle_profile.py](/D:/Desktop/Odoo/custom_addons/logistics_base/models/logistics_vehicle_profile.py:6)
- 原生视图扩展：
  - [res_partner_views.xml](/D:/Desktop/Odoo/custom_addons/logistics_base/views/res_partner_views.xml:6)
  - [hr_employee_views.xml](/D:/Desktop/Odoo/custom_addons/logistics_base/views/hr_employee_views.xml:6)
  - [fleet_vehicle_views.xml](/D:/Desktop/Odoo/custom_addons/logistics_base/views/fleet_vehicle_views.xml:6)
- 画像独立菜单：
  - [logistics_base_profile_views.xml](/D:/Desktop/Odoo/custom_addons/logistics_base/views/logistics_base_profile_views.xml:344)
- 物流运营页入口：
  - [logistics_web_menus.xml](/D:/Desktop/Odoo/custom_addons/logistics_web/views/logistics_web_menus.xml:27)
  - [logistics_web_actions.xml](/D:/Desktop/Odoo/custom_addons/logistics_web/views/logistics_web_actions.xml:34)
- 运行时菜单改挂：
  - [ui_label_sync.py](/D:/Desktop/Odoo/custom_addons/logistics_web/models/ui_label_sync.py:39)

## 4. 改造步骤

### 第一步：先改菜单和命名

目标：

- 停止把原生 `Contacts / HR / Fleet` 根菜单强行挂进物流根下面
- 物流根下只保留业务入口和运营页入口
- “客户明细” 改成更准确的业务名称，避免和客户主档混淆

要改的文件：

- [ui_label_sync.py](/D:/Desktop/Odoo/custom_addons/logistics_web/models/ui_label_sync.py:39)
- [logistics_web_menus.xml](/D:/Desktop/Odoo/custom_addons/logistics_web/views/logistics_web_menus.xml:1)
- [logistics_dispatch_waybill_views.xml](/D:/Desktop/Odoo/custom_addons/logistics_dispatch/views/logistics_dispatch_waybill_views.xml:46)

动作级别清单：

- 删除或停用 `ui_label_sync.py` 里对下面原生根菜单的重挂逻辑：
  - `fleet.menu_root`
  - `hr.menu_hr_root`
  - `contacts.menu_contacts`
- 保留 `logistics_dispatch.menu_logistics_dispatch_root` 作为物流系统根
- 保留物流根下的业务菜单：
  - `logistics_dispatch.menu_logistics_dispatch`
  - `logistics_web.menu_logistics_web_driver_management`
  - `logistics_web.menu_logistics_web_vehicle_management`
- 把下面名称统一改掉：
  - `logistics_dispatch.action_logistics_dispatch_waybill_customer_line`
  - `logistics_dispatch.menu_logistics_dispatch_waybill_customer_line`
  - `logistics_dispatch.action_logistics_dispatch_waybill_customer_line_import_center_direct`
  - `logistics_dispatch.menu_logistics_dispatch_import_customer_line`
- 推荐新名称：
  - `客户明细` -> `配送节点明细`
  - `客户明细导入` -> `配送节点明细导入`

验收点：

- 物流根下不再出现整个“员工”或“车队”原生应用树
- 原生 `HR / Fleet / Contacts` 仍能按各自原生入口进入
- 物流模块里的“客户明细”已不再误导为客户主数据

### 第二步：把运营页改成“驾驶舱 + 跳转”，不再和主档抢编辑权

目标：

- 司机管理、车辆管理继续保留
- 但它们变成运营看板页，而不是第二套主档维护页
- 页面里明确提供“打开原生主档 / 打开画像页”的跳转

要改的文件：

- [logistics_driver_service.py](/D:/Desktop/Odoo/custom_addons/logistics_web/models/logistics_driver_service.py:29)
- [logistics_vehicle_service.py](/D:/Desktop/Odoo/custom_addons/logistics_web/models/logistics_vehicle_service.py:19)
- [driver_management_templates_safe.xml](/D:/Desktop/Odoo/custom_addons/logistics_web/static/src/xml/driver_management_templates_safe.xml:1)
- [vehicle_management_templates.xml](/D:/Desktop/Odoo/custom_addons/logistics_web/static/src/xml/vehicle_management_templates.xml:1)
- 如需新增跳转 action，可补在 [logistics_web_actions.xml](/D:/Desktop/Odoo/custom_addons/logistics_web/views/logistics_web_actions.xml:1)

动作级别清单：

- 在司机管理页增加两个标准跳转：
  - 打开 `hr.employee` 主档
  - 打开 `logistics.driver.profile` 画像
- 在车辆管理页增加两个标准跳转：
  - 打开 `fleet.vehicle` 主档
  - 打开 `logistics.vehicle.profile` 画像
- 页面文案上明确区分：
  - 主档信息
  - 物流画像
  - 当前执行状态 / 当前批次 / 当前运单统计
- 禁止在运营页直接承担大段基础档案编辑

现有代码依据：

- 司机管理底层直接读 `hr.employee`：
  - [logistics_driver_service.py](/D:/Desktop/Odoo/custom_addons/logistics_web/models/logistics_driver_service.py:375)
- 车辆管理底层直接读 `fleet.vehicle`：
  - [logistics_vehicle_service.py](/D:/Desktop/Odoo/custom_addons/logistics_web/models/logistics_vehicle_service.py:288)

验收点：

- 用户在司机管理页能看清“这是运营页，不是员工主档页”
- 用户在车辆管理页能看清“这是运营页，不是车队主档页”
- 主档编辑统一回到原生对象页完成

### 第三步：收画像菜单权限和入口暴露

目标：

- 画像页不再作为普通业务用户的并行主入口
- 画像以 smart button 和配置入口为主
- 普通业务角色优先看到主档页和运营页

要改的文件：

- [logistics_base_profile_views.xml](/D:/Desktop/Odoo/custom_addons/logistics_base/views/logistics_base_profile_views.xml:344)
- [hr_employee_views.xml](/D:/Desktop/Odoo/custom_addons/logistics_base/views/hr_employee_views.xml:10)
- [fleet_vehicle_views.xml](/D:/Desktop/Odoo/custom_addons/logistics_base/views/fleet_vehicle_views.xml:10)
- 如需补权限，检查：
  - [ir.model.access.csv](/D:/Desktop/Odoo/custom_addons/logistics_base/security/ir.model.access.csv:1)
  - [security 目录](/D:/Desktop/Odoo/custom_addons/logistics_base/security)

动作级别清单：

- 对下面独立菜单增加配置型权限组，避免默认暴露给普通业务用户：
  - `menu_logistics_customer_profile`
  - `menu_logistics_store_profile`
  - `menu_logistics_driver_profile`
  - `menu_logistics_vehicle_profile`
- 保留并强化原生主档上的 smart button：
  - 员工页进入司机画像：
    - [hr_employee_views.xml](/D:/Desktop/Odoo/custom_addons/logistics_base/views/hr_employee_views.xml:10)
    - [hr_employee.py](/D:/Desktop/Odoo/custom_addons/logistics_base/models/hr_employee.py:45)
  - 车辆页进入车辆画像：
    - [fleet_vehicle_views.xml](/D:/Desktop/Odoo/custom_addons/logistics_base/views/fleet_vehicle_views.xml:10)
    - [fleet_vehicle.py](/D:/Desktop/Odoo/custom_addons/logistics_base/models/fleet_vehicle.py:24)
- 客户 / 门店暂时不新增独立运营页前，优先从 `res.partner` 承接进入画像的路径

验收点：

- 普通用户不会同时看到“原生主档入口 + 画像独立菜单 + 运营页入口”三套并行入口
- 管理员仍可从配置入口维护画像

### 第四步：收口数据所有权，把重复字段改成主档优先

目标：

- 明确哪些字段属于主档
- 明确哪些字段属于画像
- 重复字段不再允许两边都作为主编辑源

要改的文件：

- [logistics_store_profile.py](/D:/Desktop/Odoo/custom_addons/logistics_base/models/logistics_store_profile.py:20)
- [logistics_driver_profile.py](/D:/Desktop/Odoo/custom_addons/logistics_base/models/logistics_driver_profile.py:16)
- [logistics_vehicle_profile.py](/D:/Desktop/Odoo/custom_addons/logistics_base/models/logistics_vehicle_profile.py:16)
- 配套表单：
  - [logistics_base_profile_views.xml](/D:/Desktop/Odoo/custom_addons/logistics_base/views/logistics_base_profile_views.xml:44)
  - [res_partner_views.xml](/D:/Desktop/Odoo/custom_addons/logistics_base/views/res_partner_views.xml:6)
  - [hr_employee_views.xml](/D:/Desktop/Odoo/custom_addons/logistics_base/views/hr_employee_views.xml:6)
  - [fleet_vehicle_views.xml](/D:/Desktop/Odoo/custom_addons/logistics_base/views/fleet_vehicle_views.xml:6)

动作级别清单：

- 门店：
  - `res.partner` 负责主档身份、联系人、基础地址
  - `logistics.store.profile` 负责配送规则、收货窗口、停车卸货、结构化地址扩展
  - `customer_name`、`address_full` 这类重复字段改成只读展示或改为 related / compute
- 司机：
  - `hr.employee` 负责身份与基础联系方式
  - `logistics.driver.profile` 负责驾驶资格、画像、风险、物流补充信息
  - `driver_name`、`driver_phone` 改成只读冗余或 related
- 车辆：
  - `fleet.vehicle` 负责车牌、车型、车辆身份主信息
  - `logistics.vehicle.profile` 负责运力、证照、保险、物流补充信息
  - 车牌、车辆名称不在画像页重复作为主编辑字段

验收点：

- 用户不会再问“这个名字到底去哪里改”
- 主档改完，画像展示能同步反映
- 画像页只维护物流专有信息

## 5. 推荐执行顺序

建议按下面顺序落地，不要并行乱改：

1. 先做第一步：菜单和命名止血
2. 再做第二步：运营页定位收口
3. 再做第三步：权限和入口收口
4. 最后做第四步：字段所有权收口

原因：

- 第一步影响最大、回报最高，而且主要是菜单和动作层
- 第二步能先把用户认知稳定下来
- 第三步能减少混乱入口
- 第四步涉及模型和表单，应该最后做

## 6. 回滚记录建议

建议就在这份文档里持续记录，不另外拆散。

每次正式执行前，先补两类信息：

- 当前基线
- 本次改动后的目标状态

推荐记录格式：

1. 改动批次
   - 例如：批次 A / 批次 B
2. 数据库
   - 例如：`odoo_logistics_phase4_v1`
3. 升级模块
   - 例如：`logistics_base, logistics_dispatch, logistics_web`
4. 变更文件
   - 记录实际改过的 XML / Python / JS 文件
5. 回滚锚点
   - 记录改动前菜单父级、动作名、是否激活、关键文案
6. 回滚方式
   - 模块升级回滚
   - 文案恢复
   - 菜单父级恢复
   - 权限组恢复

### 当前基线（2026-04-23，数据库 `odoo_logistics_phase4_v1`）

下面这些状态建议作为第一轮改造前的回滚锚点保留：

- `contacts.menu_contacts`
  - `active = False`
- `hr.menu_hr_root`
  - `name = 员工`
  - `parent = 天枢科技物流系统`
- `fleet.menu_root`
  - `name = 车队`
  - `parent = 天枢科技物流系统`
- `logistics_web.menu_logistics_web_driver_management`
  - `name = 司机管理`
  - `parent = 天枢科技物流系统/物流`
- `logistics_web.menu_logistics_web_vehicle_management`
  - `name = 车辆管理`
  - `parent = 天枢科技物流系统/物流`
- `logistics_base.menu_logistics_customer_profile`
  - `parent = Contacts/Configuration`
- `logistics_base.menu_logistics_store_profile`
  - `parent = Contacts/Configuration`
- `logistics_base.menu_logistics_driver_profile`
  - `parent = 天枢科技物流系统/员工/Configuration/Employee`
- `logistics_base.menu_logistics_vehicle_profile`
  - `parent = 天枢科技物流系统/车队/Configuration`
- `logistics_dispatch.action_logistics_dispatch_waybill_customer_line`
  - `name = 客户明细`
- `logistics_dispatch.action_logistics_dispatch_waybill_customer_line_import_center_direct`
  - `name = 客户明细导入`

### 执行登记模板

后续每次真正动手时，可以直接在这里追加一段：

```md
### 批次 X 执行记录

- 执行日期：
- 执行数据库：
- 升级命令：
- 变更文件：
- 改动前回滚锚点：
- 改动后目标状态：
- 回滚命令：
- 手工回滚项：
- 验证结果：
```

### 批次 A 执行记录

- 执行日期：
  - 2026-04-23
- 执行数据库：
  - `odoo_logistics_phase4_v1`
- 升级命令：
  - `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_dispatch,logistics_web --stop-after-init`
- 变更文件：
  - `custom_addons/logistics_web/models/ui_label_sync.py`
  - `custom_addons/logistics_dispatch/views/logistics_dispatch_waybill_views.xml`
  - `custom_addons/logistics_dispatch/views/logistics_dispatch_menus.xml`
- 改动前回滚锚点：
  - `contacts.menu_contacts` 为 `active = False`
  - `hr.menu_hr_root / fleet.menu_root / stock.menu_stock_root / account.menu_finance / base.menu_administration` 被挂在物流根下
  - `logistics_dispatch.action_logistics_dispatch_waybill_customer_line` 名称为 `客户明细`
  - `logistics_dispatch.action_logistics_dispatch_waybill_customer_line_import_center_direct` 名称为 `客户明细导入`
- 改动后目标状态：
  - 恢复 `Contacts / HR / Fleet / Inventory / Invoicing / Settings` 为原生顶层菜单
  - 物流根下只保留物流业务与物流运营入口
  - `客户明细` 统一改为 `配送节点明细`
  - `客户明细导入` 统一改为 `配送节点明细导入`
- 回滚命令：
  - 回滚代码后执行：`python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_dispatch,logistics_web --stop-after-init`
- 手工回滚项：
  - 将 `ui_label_sync.py` 恢复为旧菜单挂载逻辑
  - 将 `配送节点明细` 系列文案恢复为 `客户明细`
- 验证结果：
  - `contacts.menu_contacts` 已恢复 `active = True`
  - `hr.menu_hr_root / fleet.menu_root / stock.menu_stock_root / account.menu_finance / base.menu_administration` 的 `parent_id = False`
  - `logistics_dispatch.menu_logistics_dispatch_waybill_customer_line` 名称已为 `配送节点明细`
  - `logistics_dispatch.action_logistics_dispatch_waybill_customer_line` 名称已为 `配送节点明细`
  - `logistics_dispatch.action_logistics_dispatch_waybill_customer_line_import_center_direct` 名称已为 `配送节点明细导入`

### 批次 B 执行记录

- 执行日期：
  - 2026-04-23
- 执行数据库：
  - `odoo_logistics_phase4_v1`
- 升级命令：
  - `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_web --stop-after-init`
- 变更文件：
  - `custom_addons/logistics_web/static/src/js/actions/driver_management_action_v2.js`
  - `custom_addons/logistics_web/static/src/js/actions/vehicle_management_action_v2.js`
  - `custom_addons/logistics_web/static/src/xml/driver_management_templates_safe.xml`
  - `custom_addons/logistics_web/static/src/xml/vehicle_management_templates.xml`
- 改动前回滚锚点：
  - 司机管理页列表标题仍为 `司机管理`，列表操作按钮为 `查看画像`
  - 车辆管理页列表标题仍为 `车辆管理`，列表操作按钮为 `查看画像`
  - 司机页详情头部只有 `返回列表 / 查看关联运单 / 查看关联异常`
  - 车辆页详情头部只有 `返回列表 / 查看关联运单 / 查看关联异常`
- 改动后目标状态：
  - 司机页收口为 `司机运营驾驶舱`，列表按钮改为 `进入驾驶舱`
  - 车辆页收口为 `车辆运营驾驶舱`，列表按钮改为 `进入驾驶舱`
  - 司机页详情头部新增 `打开员工主档 / 打开司机画像`
  - 车辆页详情头部新增 `打开车辆主档 / 打开车辆画像`
  - 司机/车辆管理页定位明确为运营页，不再表达为第二套主档编辑页
- 回滚命令：
  - 回滚代码后执行：`python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_web --stop-after-init`
- 手工回滚项：
  - 将司机页文案恢复为 `司机管理 / 司机画像 / 查看画像`
  - 将车辆页文案恢复为 `车辆管理 / 车辆画像 / 查看画像`
  - 删除详情头部新增的“打开主档 / 打开画像”跳转按钮
- 验证结果：
  - `driver_management_action_v2.js` 与 `vehicle_management_action_v2.js` 已通过 `node --check`
  - `driver_management_templates_safe.xml` 与 `vehicle_management_templates.xml` 已通过 XML 解析校验
  - `logistics_web` 模块已升级完成

### 批次 C 执行记录

- 执行日期：
  - 2026-04-23
- 执行数据库：
  - `odoo_logistics_phase4_v1`
- 升级命令：
  - `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_base --stop-after-init`
- 变更文件：
  - `custom_addons/logistics_base/security/logistics_base_security.xml`
  - `custom_addons/logistics_base/__manifest__.py`
  - `custom_addons/logistics_base/models/res_partner.py`
  - `custom_addons/logistics_base/views/res_partner_views.xml`
  - `custom_addons/logistics_base/views/logistics_base_profile_views.xml`
- 改动前回滚锚点：
  - 四个独立画像菜单默认暴露给普通内部用户
  - `res.partner` 主档没有“客户经营画像 / 门店配送画像” smart button
  - 客户/门店只能从配置菜单进入画像页
- 改动后目标状态：
  - 四个独立画像菜单只对 `物流画像配置管理员` 可见
  - `res.partner` 主档新增 `客户经营画像 / 门店配送画像` smart button
  - 客户/门店主档可直接打开或首次创建画像，不再依赖配置菜单
- 回滚命令：
  - 回滚代码后执行：`python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_base --stop-after-init`
- 手工回滚项：
  - 删除 `物流画像配置管理员` 分组或移除菜单上的 groups 约束
  - 删除 `res.partner` 上新增的两个 smart button 与对应方法
- 验证结果：
  - `res_partner.py` 已通过 Python 语法校验
  - `logistics_base_security.xml`、`res_partner_views.xml`、`logistics_base_profile_views.xml` 已通过 XML 解析校验
  - 数据库中四个独立画像菜单的 group 已收口为 `物流画像配置管理员`
  - `logistics_base` 模块已升级完成

### 批次 D 执行记录

- 执行日期：
  - 2026-04-23
- 执行数据库：
  - `odoo_logistics_phase4_v1`
- 升级命令：
  - `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_base --stop-after-init`
- 变更文件：
  - `custom_addons/logistics_base/models/logistics_customer_profile.py`
  - `custom_addons/logistics_base/models/logistics_store_profile.py`
  - `custom_addons/logistics_base/models/logistics_driver_profile.py`
  - `custom_addons/logistics_base/models/res_partner.py`
  - `custom_addons/logistics_base/models/hr_employee.py`
  - `custom_addons/logistics_base/migrations/19.0.1.1.0/post-migration.py`
- 改动前回滚锚点：
  - 客户画像中的 `customer_level / customer_status / registered_phone / registered_address / customer_seq_no` 仍是画像自有可编辑字段
  - 门店画像中的 `address_code / external_customer_code / customer_name / address_full / longitude / latitude` 仍是画像自有可编辑字段
  - 司机画像中的 `internal_driver_code / driver_name / driver_phone` 仍可在画像页独立维护
  - 主档创建画像时仍会把这些冗余字段写入画像表
- 改动后目标状态：
  - 客户/门店/司机画像中的重复字段收口回主档，画像改成 related 或主档驱动计算只读
  - 主档创建画像时不再写入这些重复字段
  - 现有开发库中的存量画像已补做一次主档字段回刷
  - 车辆画像未额外改字段，因为当前页里没有和 `fleet.vehicle` 直接重复的主编辑字段
- 回滚命令：
  - 回滚代码后执行：`python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_base --stop-after-init`
- 手工回滚项：
  - 将上述 related/计算只读字段恢复为画像自有字段
  - 恢复主档创建画像时的冗余写入逻辑
  - 如已执行存量回刷，按需要重新修正测试数据
- 验证结果：
  - `logistics_customer_profile.py`、`logistics_store_profile.py`、`logistics_driver_profile.py`、`res_partner.py`、`hr_employee.py` 已通过 Python 语法校验
  - 相关 XML 已通过解析校验
  - `logistics_base` 模块已升级完成
  - 当前测试库中客户/门店/司机画像抽样读取已和主档一致

### 批次 E 执行记录

- 执行日期：
  - 2026-04-23
- 执行数据库：
  - `odoo_logistics_phase4_v1`
- 升级命令：
  - `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_dispatch,logistics_web --stop-after-init`
- 变更文件：
  - `custom_addons/logistics_web/views/logistics_web_menus.xml`
  - `custom_addons/logistics_web/views/logistics_web_actions.xml`
  - `custom_addons/logistics_dispatch/views/logistics_dispatch_menus.xml`
  - `custom_addons/logistics_web/models/ui_label_sync.py`
  - `custom_addons/logistics_web/static/src/js/actions/home_action.js`
  - `custom_addons/logistics_web/static/src/xml/home_action_templates.xml`
  - `custom_addons/logistics_web/static/src/js/services/tianshu_title_service.js`
  - `custom_addons/logistics_web/views/logistics_web_templates.xml`
  - `custom_addons/logistics_web/controllers/webmanifest.py`
- 改动前回滚锚点：
  - 登录默认落点仍挂在 `logistics_dispatch.menu_logistics_dispatch_root`
  - 顶层根菜单文案仍是 `天枢科技物流系统`
  - 首页与“所有统计图表”仍作为物流根下的一级入口
  - 物流根菜单仍带首页 action，登录后直接进入物流系统首页
  - 首页文案仍使用“先进入企业模块，再处理今天的物流工作”
- 改动后目标状态：
  - 新增独立顶层根菜单 `logistics_web.menu_tianshu_enterprise_root`
  - 登录默认先进入“企业首页”，不再直接落到物流 App
  - `logistics_dispatch.menu_logistics_dispatch_root` 收口为纯物流顶层入口
  - 首页与“所有统计图表”挂到企业总入口下
  - 首页品牌、页签标题、PWA manifest 名称统一切换为 `天枢科技企业系统`
- 回滚命令：
  - 回滚代码后执行：`python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_dispatch,logistics_web --stop-after-init`
- 手工回滚项：
  - 删除 `logistics_web.menu_tianshu_enterprise_root`
  - 将 `menu_logistics_web_home / menu_logistics_web` 父级改回 `logistics_dispatch.menu_logistics_dispatch_root`
  - 将 `logistics_dispatch.menu_logistics_dispatch_root` 恢复为首页默认 action 挂点
  - 将首页品牌与标题恢复为 `天枢科技物流系统`
- 验证结果：
  - 待本批模块升级后核验登录默认落点、顶层菜单顺序与首页文案

### 批次 F 执行记录

- 执行日期：
  - 2026-04-23
- 执行数据库：
  - `odoo_logistics_phase4_v1`
- 升级命令：
  - `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_web --stop-after-init`
- 变更文件：
  - `custom_addons/logistics_web/views/logistics_web_menus.xml`
  - `custom_addons/logistics_web/models/ui_label_sync.py`
- 改动前回滚锚点：
  - 企业首页顶层仅有 `首页 / 所有统计图表`
  - 顶部横向导航没有 `物流 / 车队 / 员工 / 库存 / 发票 / 设置` 的企业级快捷入口
- 改动后目标状态：
  - 企业首页顶层新增一排快捷总导航
  - `物流 / 车队 / 员工 / 库存 / 发票 / 设置` 作为企业级快捷菜单显示在顶部横条
  - 原生 app 根菜单仍保持独立存在，不做父子重挂
- 回滚命令：
  - 回滚代码后执行：`python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_web --stop-after-init`
- 手工回滚项：
  - 删除企业根下新增的快捷菜单
  - 保留 `首页 / 所有统计图表` 两个原有菜单
- 验证结果：
  - 待本批模块升级后核验顶部横向导航显示顺序与点击跳转

### 批次 G 执行记录

- 执行日期：
  - 2026-04-23
- 执行数据库：
  - `odoo_logistics_phase4_v1`
- 升级命令：
  - `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_dispatch,logistics_web --stop-after-init`
- 变更文件：
  - `custom_addons/logistics_web/views/logistics_web_menus.xml`
  - `custom_addons/logistics_dispatch/views/logistics_dispatch_menus.xml`
  - `custom_addons/logistics_web/models/ui_label_sync.py`
- 改动前回滚锚点：
  - 企业首页顶层挂了一排 `物流 / 车队 / 员工 / 库存 / 发票 / 设置` 的快捷跳转
  - 这些快捷跳转直接指向原生 action，导致丢失菜单上下文
  - 物流根下面仍只有一层 `物流工作区` 包裹，不利于直接看到运单、导入、异常等入口
- 改动后目标状态：
  - 企业首页顶层只保留企业自有页面：`首页 / 所有统计图表`
  - 上一批错误加上的快捷菜单在库里显式停用
  - 物流恢复成独立业务 app，并把 `物流工作台 / 调度 / 运单 / 留痕 / 证据 / 异常 / 导入中心 / 司机管理 / 车辆管理` 直接挂到物流根下
  - 收口策略明确为：有自研页的模块优先走自研页；没有完整替代页的模块继续保留原生入口
- 回滚命令：
  - 回滚代码后执行：`python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_dispatch,logistics_web --stop-after-init`
- 手工回滚项：
  - 如需恢复错误快捷导航，可重新激活 `menu_tianshu_enterprise_*_shortcut` 菜单
  - 如需恢复旧的物流包裹层级，可把调度/运单/导入等菜单父级改回 `logistics_dispatch.menu_logistics_dispatch`
- 验证结果：
  - 待本批模块升级后核验企业首页顶部菜单、物流 app 一级菜单与员工/车队原生入口

### 批次 H 执行记录

- 执行日期：
  - 2026-04-23
- 执行数据库：
  - `odoo_logistics_phase4_v1`
- 升级命令：
  - `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_web --stop-after-init`
- 变更文件：
  - `custom_addons/logistics_web/static/src/js/actions/home_action.js`
- 改动前回滚锚点：
  - 企业首页模块卡片仍使用 `doAction(actionXmlid)` 直接跳原生 action
  - 点击 `员工 / 车队 / 库存 / 发票 / 设置` 时容易丢失 Odoo 菜单上下文
  - 用户可能进入错误视图或直接落到新建页
- 改动后目标状态：
  - 企业首页模块卡片优先通过 `menuService.selectMenu(menu)` 进入对应模块
  - 自研页与原生页都尽量沿用各自菜单上下文进入，不再裸跳 action
  - 企业首页卡片和实际应用入口保持一致
- 回滚命令：
  - 回滚代码后执行：`python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_web --stop-after-init`
- 手工回滚项：
  - 将首页模块卡片恢复为按 `actionXmlid` 直接跳转
- 验证结果：
  - 待本批模块升级后核验首页 `物流 / 车队 / 员工 / 库存 / 发票 / 设置` 卡片点击路径

### 批次 I 执行记录

- 执行日期：
  - 2026-04-23
- 执行数据库：
  - `odoo_logistics_phase4_v1`
- 升级命令：
  - `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_dispatch,logistics_web --stop-after-init`
- 变更文件：
  - `custom_addons/logistics_web/static/src/js/actions/dashboard_action_v2.js`
  - `custom_addons/logistics_web/static/src/xml/dashboard_action_templates.xml`
  - `custom_addons/logistics_web/static/src/scss/dashboard.scss`
  - `custom_addons/logistics_dispatch/views/logistics_dispatch_menus.xml`
  - `custom_addons/logistics_web/models/ui_label_sync.py`
- 改动前回滚锚点：
  - 物流工作台没有明确返回企业首页入口
  - 物流工作台 client action 未使用标准 `Layout` 外壳
  - 用户在物流 app 中只能靠切换顶层 app 返回首页，不够直观
- 改动后目标状态：
  - 物流顶栏新增 `企业首页` 入口
  - 物流工作台页头新增 `返回企业首页` 按钮和 `查看统计图表` 按钮
  - 物流工作台切回标准 `Layout` 容器，恢复正常滚动与页面框架
- 回滚命令：
  - 回滚代码后执行：`python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_dispatch,logistics_web --stop-after-init`
- 手工回滚项：
  - 删除物流根下新增的 `企业首页` 菜单
  - 删除物流工作台页头新增按钮
  - 将工作台模板恢复为无 `Layout` 包裹的旧版本
- 验证结果：
  - 待本批模块升级后核验物流页可滚动、顶栏可回首页、页头按钮可用

## 7. 升级与验证

执行改造后，至少要做下面几项：

1. 升级模块：
   - `logistics_base`
   - `logistics_dispatch`
   - `logistics_web`
2. 校验菜单树：
   - 物流根
   - Contacts
   - HR
   - Fleet
3. 校验这几条打开链路：
   - 司机管理 -> 员工主档 / 司机画像
   - 车辆管理 -> 车辆主档 / 车辆画像
   - 门店主档 -> 门店画像
4. 校验字段编辑归属：
   - 名称
   - 联系方式
   - 地址
   - 驾驶员手机号
   - 车辆车牌
5. 校验改名后的“配送节点明细”入口不会再和客户主档混淆

## 8. 风险提醒

- `ui_label_sync.py` 会在运行时覆盖菜单树，改菜单时必须把这里一起改，不然源代码和库里最终菜单会不一致
- 画像字段如果直接从可编辑改成 related / readonly，要同步检查现有表单写入逻辑
- 如果前端模板里写死了旧名称 “客户明细”，前端和后端文案需要一起改

## 9. 建议的下一步

按这个清单真正动手时，建议拆成两个提交批次：

- 批次 A：第一步 + 第二步
- 批次 B：第三步 + 第四步

这样更容易验证，也更容易回滚。
