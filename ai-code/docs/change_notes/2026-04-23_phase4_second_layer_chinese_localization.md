# 2026-04-23 四期第二层中文化收口

## 背景

在首轮完成导航、菜单、动作名回调为中文后，继续将第二层中文化补齐，范围覆盖：

- 页面内部按钮、表头、提示语
- Python 报错和提示文案
- 表单字段标签、模型描述与帮助文案

目标是让 `odoo_logistics_phase4_v1` 新开发库的实际运行界面尽量保持全中文口径，避免英文和中文混杂。

## 本次改动

### 1. 活动页前端文案中文化

处理了 `logistics_web` 当前资产包中的活动页头部和导入页残留英文：

- `driver_management_templates_safe.xml`
- `vehicle_management_templates.xml`
- `dashboard_action_templates.xml`
- `boss_trace_action_templates.xml`
- `stats_center_templates.xml`
- `import_center_templates.xml`
- `import_result_templates.xml`
- `import_center_action.js`

调整点包括：

- `PHASE 3/4 ...` 页头 kicker 改为中文
- `DRIVER PROFILE` / `VEHICLE PROFILE` 改为中文
- 导入页中的 `Sheet` 改为 `工作表`
- 导入页关于 `三 Sheet` 的提示改为 `三张工作表`

### 2. Python 报错与约束提示中文化

统一了主数据、调度、导入、车辆服务中的英文约束提示和错误信息：

- `logistics_base/models/logistics_product_unit.py`
- `logistics_base/models/logistics_driver_profile.py`
- `logistics_base/models/logistics_vehicle_profile.py`
- `logistics_base/models/logistics_store_profile.py`
- `logistics_base/models/logistics_customer_profile.py`
- `logistics_base/models/res_partner.py`
- `logistics_base/models/product_template.py`
- `logistics_dispatch/models/logistics_dispatch_wave.py`
- `logistics_dispatch/models/logistics_dispatch_batch.py`
- `logistics_dispatch/models/logistics_dispatch_waybill.py`
- `logistics_dispatch/models/logistics_dispatch_waybill_order_line.py`
- `logistics_dispatch/models/logistics_dispatch_waybill_customer_line_v2.py`
- `logistics_dispatch/models/logistics_dispatch_waybill_customer_goods_line_v2.py`
- `logistics_dispatch/models/logistics_import_log.py`
- `logistics_dispatch/models/logistics_import_batch.py`
- `logistics_web/models/logistics_vehicle_service.py`

### 3. 字段标签与模型描述中文化

同步将一批仍为英文的字段 `string`、模型 `_description`、唯一约束消息收口为中文，主要集中在：

- 商品主档扩展
- 客户/门店/司机/车辆画像
- 导入日志与导入批次
- 运单订单明细

## 校验

已完成：

- Python 语法解析校验
- XML 模板解析校验
- Odoo 模块升级：
  - `logistics_base`
  - `logistics_dispatch`
  - `logistics_web`
- 目标库：`odoo_logistics_phase4_v1`

## 结果

当前新库已同步到这一轮第二层中文化版本。搜索确认主要用户可见的 `PHASE`、`DRIVER PROFILE`、`VEHICLE PROFILE`、`Sheet` 等残留已从活动页移除。
