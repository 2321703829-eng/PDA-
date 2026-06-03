# 2026-04-27 logistics_web export permission fix report added

## Objective

补充上一轮 `logistics_web` 导出权限与 `ui_label_sync` 修复的正式报告，并追加正向 smoke 结果。

## Added

- [2026-04-27_logistics_web_export_permission_and_label_sync_fix_report.md](d:/Desktop/Odoo/ai-code/docs/review/findings/2026-04-27_logistics_web_export_permission_and_label_sync_fix_report.md)

## Included verification

- 普通内部用户负向拦截：
  - 司机路线导出 `EXPORT_PERMISSION_DENIED`
  - 客户画像导出 `EXPORT_PERMISSION_DENIED`
  - 商品画像导出 `EXPORT_PERMISSION_DENIED`
- 临时授权后的正向 smoke：
  - `driver_route_2026-04-24.xlsx`
  - 客户画像任务 `EXT260427-00028`
  - 商品画像任务 `EXT260427-00029`
- 临时加组后已回收权限

## Notes

- 本轮没有新增代码修复，只补充了验证与正式报告输出。
- smoke 中发现的 `check_access_rights / check_access_rule` 弃用告警暂未在本轮处理。
