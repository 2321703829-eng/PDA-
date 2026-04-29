# 2026-04-15 导入中心乱码与 XML 结构修复

## Objective

修复导入中心新菜单出现中文乱码的问题，并同时清理导入相关 XML 中因为乱码带出的坏标签，避免模块升级再次整份回滚。

## Root Cause

本轮问题不是单纯的“文案翻译不对”，而是两类问题叠加：

1. 新增的导入中心子菜单和动作名称在源码中被写成了乱码文本。
2. `logistics_dispatch_waybill_views.xml` 中还混有多处被乱码破坏的属性值和标签闭合，导致升级时整份 XML 有较高概率失败并回滚。

## Changes

1. 重写 [logistics_dispatch_menus.xml](/d:/Desktop/Odoo/custom_addons/logistics_dispatch/views/logistics_dispatch_menus.xml)，统一修正：
   - `导入中心`
   - `运单导入`
   - `客户明细导入`
   - `货物明细导入`
2. 修正 [logistics_dispatch_waybill_views.xml](/d:/Desktop/Odoo/custom_addons/logistics_dispatch/views/logistics_dispatch_waybill_views.xml) 中：
   - 两个导入 client action 名称
   - 顶部摘要 placeholder
   - 多个 `group string`
   - 搜索区 filter/group 文案
   - 原始订单明细说明区的 `span` 闭合
   - 导入中心 help 区文案和 `<strong>` 标签
3. 重写 [ui_label_sync.py](/d:/Desktop/Odoo/custom_addons/logistics_web/models/ui_label_sync.py)，确保升级时数据库菜单和动作不会再被回写成乱码。

## Verify

已完成：

- `logistics_dispatch_menus.xml` XML 解析通过
- `logistics_dispatch_waybill_views.xml` XML 解析通过
- `ui_label_sync.py` Python 源码级编译通过
- 三层导入入口相关 v2 模型文件 Python 源码级编译通过

## Next

升级 `logistics_dispatch, logistics_web` 后，重点复核：

1. `物流 -> 导入中心` 下的 3 条子菜单是否全部显示为正常中文
2. 进入 `客户明细导入 / 货物明细导入` 后页面标题是否正常
3. 升级过程中是否还出现 `waybill_views.xml` 相关 XML 报错
