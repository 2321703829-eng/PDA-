# 2026-04-16 运单相关视图乱码修复

## Objective

修复 `logistics_dispatch_waybill_views.xml` 中已经进入运行视图的中文乱码，覆盖运单、客户明细、货物明细和导入中心相关页面。

## Scope

- [logistics_dispatch_waybill_views.xml](/d:/Desktop/Odoo/custom_addons/logistics_dispatch/views/logistics_dispatch_waybill_views.xml)
- 运行中的 `logistics.dispatch.waybill*` 相关 `ir.ui.view`

## Changes

1. 修正运单主视图中的乱码文案：
   - 运单标题
   - 查看波次 / 查看批次
   - 客户明细 / 货物明细 / 原始订单明细
   - 留痕摘要 / 备注
   - 证据缺失 / 配送途中
2. 修正客户明细视图中的乱码文案：
   - 客户明细标题
   - 客户名称占位
   - 客户信息 / 履约说明 / 货物明细
   - 签收要求占位
3. 修正货物明细视图中的乱码文案：
   - 货物明细标题
   - 货物名称占位
   - 关联信息 / 货物信息 / 备注
   - 货物备注占位
4. 修正导入中心动作名称中的乱码文案。

## Verify

计划通过模块升级后确认：

- `运单` 表单页不再出现乱码页签和分组标题
- `客户明细` 新建页不再出现乱码标题和分组名
- `货物明细` 新建页不再出现乱码标题和分组名
- 数据库中的 `ir.ui.view` 已同步为修复后的中文文案
