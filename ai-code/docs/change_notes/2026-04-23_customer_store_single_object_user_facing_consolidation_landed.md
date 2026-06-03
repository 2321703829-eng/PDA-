# 2026-04-23 客户=门店用户侧单对象收口落地

## 背景

前端与调度链路中长期并存 `客户` / `门店` 双口径，已经导致：

- 首页缺少统一客户入口
- 画像入口需要用户自行判断看客户还是门店
- 运单、配送节点、货物明细页面同时出现客户/门店双对象字段
- 页面理解成本高，且与当前业务口径“客户=门店”不一致

本次按“用户侧单对象”原则做第一阶段落地，优先统一入口、统一画像、统一运单阅读口径，同时保留底层兼容字段，避免开发库结构瞬时断裂。

## 本次改动

### 1. 首页补统一客户入口

- 企业首页模块卡片新增 `客户`
- 卡片不再依赖菜单猜测，直接打开统一动作 `logistics_base.action_logistics_partner_profile`

涉及文件：

- `custom_addons/logistics_web/static/src/js/actions/home_action.js`

### 2. 主档与画像收口到 `res.partner`

- `res.partner` 新增 `is_logistics_partner` 作为统一物流客户标识
- 将客户经营与门店配送层面的物流字段统一挂到 `res.partner`
- 新增统一入口动作 `action_open_or_create_logistics_profile`
- 原 `action_open_or_create_customer_profile` / `action_open_or_create_store_profile` 统一转发到新入口
- 原 `logistics.customer.profile` / `logistics.store.profile` 保留为兼容包装层，主要字段改为 `related` 到 `res.partner`

涉及文件：

- `custom_addons/logistics_base/models/res_partner.py`
- `custom_addons/logistics_base/models/logistics_customer_profile.py`
- `custom_addons/logistics_base/models/logistics_store_profile.py`
- `custom_addons/logistics_base/views/res_partner_views.xml`
- `custom_addons/logistics_base/views/logistics_base_profile_views.xml`

### 3. 旧画像数据回刷主档

- 迁移脚本新增从 `logistics_customer_profile` / `logistics_store_profile` 回刷 `res_partner` 的逻辑
- 确保开发库里已有画像配置能提升为统一客户主档字段

涉及文件：

- `custom_addons/logistics_base/migrations/19.0.1.1.0/post-migration.py`

### 4. 运单与配送节点收口为单对象阅读口径

- `waybill` 新增用户侧统一字段 `partner_id / partner_no / partner_name`
- 旧 `customer_* / store_*` 保留兼容，但写入与解析统一映射到一个 `partner`
- `customer_line` 同步采用统一 `partner_*` 主阅读字段
- 配送节点页面补齐设计稿要求的关键快照字段：
  - `internal_customer_code_snapshot`
  - `external_customer_code_snapshot`
  - `signoff_requirement_snapshot`
  - `basement_height_limit_text_snapshot`
  - `customer_ref`
- 页面命名统一为 `配送节点明细`

涉及文件：

- `custom_addons/logistics_dispatch/models/logistics_dispatch_waybill.py`
- `custom_addons/logistics_dispatch/models/logistics_dispatch_waybill_customer_line_v2.py`
- `custom_addons/logistics_dispatch/views/logistics_dispatch_waybill_views.xml`

### 5. 兼容明细页改成“显示单对象，底层保兼容”

- `运单订单明细` 继续保留旧字段结构，但用户显示只按“客户”理解
- `货物明细` 页面不再暴露门店概念
- 中途尝试过新增存储型相关字段，触发了 Odoo 重算递归；最终改为更稳的兼容做法，避免升级失败

涉及文件：

- `custom_addons/logistics_dispatch/models/logistics_dispatch_waybill_order_line.py`
- `custom_addons/logistics_dispatch/models/logistics_dispatch_waybill_customer_goods_line_v2.py`
- `custom_addons/logistics_dispatch/views/logistics_dispatch_waybill_views.xml`

## 升级结果

已执行：

```powershell
python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_base,logistics_dispatch,logistics_web --stop-after-init
```

升级完成，开发库已刷入本次改动。

## 当前结论

本次已经做到：

- 用户侧有统一 `客户` 入口
- 用户侧统一使用 `物流客户画像`
- 运单/配送节点不再要求用户区分“客户”还是“门店”
- 兼容数据链仍可继续使用旧字段名

本次刻意没有做：

- 物理删除 `logistics.customer.profile` / `logistics.store.profile`
- 物理删除 `waybill/customer_line/order_line/goods_line` 中旧 `customer_* / store_*` 字段
- 导入模板字段头的全面改名

这些属于第二阶段“彻底去兼容化”的工作。

## 核验摘录

已通过 Odoo Shell 抽查：

- 统一动作 `logistics_base.action_logistics_partner_profile` 名称为 `物流客户画像`
- 新统一菜单 `menu_logistics_partner_profile` 已启用
- 旧 `menu_logistics_customer_profile` / `menu_logistics_store_profile` 已停用
- 当前开发库中 `is_logistics_partner = True` 的记录数为 `2`
- `logistics.dispatch.waybill` 已存在 `partner_id / partner_no / partner_name` 三个统一字段

## 遗留风险

### 1. `is_logistics_partner` 与 `is_logistics_customer` 标签重复告警

本次是为了兼容旧字段保留双标记，日志中会出现标签重复提示。当前不阻塞功能，但后面做第二阶段去兼容时应清理。

### 2. 浏览器侧仍需人工点检

这次完成了模块升级和服务端落地，但还没有逐页做浏览器人工回归。

建议重点点检：

- 企业首页 `客户` 卡片是否可直接进入统一客户画像
- 客户主档 `物流客户画像` 按钮
- 配送节点页是否只剩客户口径
- 货物明细 / 原始订单明细页是否不再混出门店概念
