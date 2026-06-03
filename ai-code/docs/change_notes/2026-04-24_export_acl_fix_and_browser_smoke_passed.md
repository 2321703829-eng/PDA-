# 2026-04-24 导出 ACL 修复与浏览器 Smoke 通过

## 本次变更

- 调整 `logistics_dispatch` 导出正式模型的用户级 ACL：
  - `logistics.export.source.scope`
  - `logistics.export.task`
  - `logistics.export.task.line`
  - `logistics.export.error.line`
- 将上述“user”级 access 统一从 `group_logistics_export_user` 收口到 `base.group_user`，保证当前首轮导出入口与实际页面授权口径一致。

## 变更文件

- `custom_addons/logistics_dispatch/security/ir.model.access.csv`

## 修复背景

- 列表页“导出”按钮点击后，`POST /api/admin/logistics/exports/waybill` 返回 `403`，浏览器停留在运单列表页。
- 详情页“导出结果”按钮点击后，弹出访问错误，不允许创建 `logistics.export.source.scope`。
- 根因是导出正式底表只授权给自定义导出组，但首轮页面入口并未绑定该组判断，导致内部用户可见按钮却无法真正创建导出任务。

## 验证结果

- 已升级 `logistics_dispatch, logistics_web` 并重启单实例 Odoo。
- 已完成真实浏览器 smoke：
  - 列表页勾选两条运单后点击“导出”，成功进入导出结果页，任务号 `EXT260424-00004`。
  - 详情页点击“导出结果”，成功进入导出结果页，任务号 `EXT260424-00005`。
  - 两条链路均成功下载导出文件：
    - `TSL-EXPORT-FROM-WAYBILL-20260424-033305.xlsx`
    - `TSL-EXPORT-FROM-WAYBILL-20260424-033310.xlsx`

## Smoke 产物

- 目录：`ai-code/.smoke/export_browser_smoke_20260424_113251/`
- 摘要：`ai-code/.smoke/export_browser_smoke_20260424_113251/summary.json`
- 截图：`ai-code/.smoke/export_browser_smoke_20260424_113251/screenshots/`
