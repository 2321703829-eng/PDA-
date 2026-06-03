# 2026-04-23 页面去打架第三步：画像独立菜单权限与主档入口收口

## 变更目标

按 `docs/dev/page_conflict_resolution_checklist.md` 的第三步执行，把画像独立菜单从普通用户的并列主入口收口为配置入口，同时保留并补齐从主档进入画像的正向路径。

## Outcome

- 四个独立画像菜单只对“物流画像配置管理员”可见
- `res.partner` 主档新增客户画像、门店画像 smart button
- 客户/门店与司机/车辆一样，都可以从主档直接跳转到对应画像

## Behavior

- 新增权限组：`logistics_base.group_logistics_profile_manager`
- 下列菜单改为仅该组可见：
  - `menu_logistics_customer_profile`
  - `menu_logistics_store_profile`
  - `menu_logistics_driver_profile`
  - `menu_logistics_vehicle_profile`
- `res.partner` 新增：
  - `action_open_or_create_customer_profile()`
  - `action_open_or_create_store_profile()`
  - `logistics_customer_profile_count`
  - `logistics_store_profile_count`
- 当画像不存在时，主档 smart button 会自动创建首条画像记录再打开

## Boundary

- 本轮未收紧画像模型本身的访问权限
- 本轮未修改司机/车辆已有 smart button 的权限
- 本轮未处理画像字段只读/related 化，仍留待第四步

## 变更文件

- `custom_addons/logistics_base/security/logistics_base_security.xml`
- `custom_addons/logistics_base/__manifest__.py`
- `custom_addons/logistics_base/models/res_partner.py`
- `custom_addons/logistics_base/views/res_partner_views.xml`
- `custom_addons/logistics_base/views/logistics_base_profile_views.xml`
- `docs/dev/page_conflict_resolution_checklist.md`

## 实现说明

### 菜单权限

新增“物流画像配置管理员”组，并把四个独立画像菜单都挂到这个组上。这样普通业务用户不会再同时看到：

- 原生主档入口
- 画像独立菜单
- 运营页入口

### 主档入口补齐

`res.partner` 以前没有客户画像、门店画像的 smart button，这会导致菜单收口后客户/门店画像缺少正向入口。

本轮已补齐：

- 客户经营画像 smart button
- 门店配送画像 smart button

并在点击时支持：

- 存在画像：直接打开
- 不存在画像：自动创建首条画像后打开

## 升级与验证

执行命令：

```powershell
python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_base --stop-after-init
```

验证结果：

- `res_partner.py` 通过 Python 语法校验
- `logistics_base_security.xml`、`res_partner_views.xml`、`logistics_base_profile_views.xml` 通过 XML 解析
- 数据库中四个独立画像菜单均只绑定 `物流画像配置管理员`

## 风险提示

- 普通用户如果仍能打开主档 smart button，对应画像页仍会受现有模型访问权限控制
- 这一步优先解决“入口打架”，不是最终的字段归属收口
