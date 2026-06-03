# 示例 05：验证与回归

## Objective

- 用当前仓库里已经存在的落地代码和 smoke 记录，示范这条链在“verify”阶段应该怎样汇总结论。

## Verify Scope

- `from_waybill` 首轮正式导出
- 列表页入口
- 详情页入口
- 导出结果页
- 文件下载与错误报告下载
- ACL 回归

## Evidence

- [dispatch_main_export_service.py](/d:/Desktop/Odoo/custom_addons/logistics_web/services/dispatch_main_export_service.py:1)
- [logistics_web_export.py](/d:/Desktop/Odoo/custom_addons/logistics_web/controllers/logistics_web_export.py:1)
- [2026-04-24_dispatch_main_export_service_first_round_landed.md](/d:/Desktop/Odoo/ai-code/docs/change_notes/2026-04-24_dispatch_main_export_service_first_round_landed.md)
- [2026-04-24_dispatch_main_export_controller_first_round_landed.md](/d:/Desktop/Odoo/ai-code/docs/change_notes/2026-04-24_dispatch_main_export_controller_first_round_landed.md)
- [2026-04-24_export_result_page_and_waybill_entry_wiring_landed.md](/d:/Desktop/Odoo/ai-code/docs/change_notes/2026-04-24_export_result_page_and_waybill_entry_wiring_landed.md)
- [2026-04-24_export_acl_fix_and_browser_smoke_passed.md](/d:/Desktop/Odoo/ai-code/docs/change_notes/2026-04-24_export_acl_fix_and_browser_smoke_passed.md)

## 已做

- 静态验证：
  - Python 文件已做 `ast.parse`
  - 前端动作、模板、注册与路由引用已核对
- 运行态 smoke：
  - 已升级 `logistics_dispatch, logistics_web`
  - 列表页勾选两条运单后点击导出，成功进入导出结果页
  - 详情页点击导出结果，成功进入导出结果页
  - 两条链路都成功下载导出文件
- 权限回归：
  - ACL 已从仅导出组收口到当前页面入口实际用户口径
  - 修复了首轮 `403` 与 `logistics.export.source.scope` 无创建权限问题

## 未做

- 超大批量导出压力验证
- 异步执行模式验证
- `from_batch / from_customer` 共用结果链验证

## 当前结论

- 这条链已经达到“首轮闭环可用”状态。
- 结果页、下载链和 ACL 口径已经完成最关键回归。
- 当前结论基于真实浏览器 smoke 与静态检查，不只是文档推演。

## Risks

- 同步执行路径未来在大选择集场景下可能成为性能瓶颈
- 当前 smoke 更偏功能闭环验证，不等于性能上限验证

## Next Suggestion

1. 如果继续扩展导出体系，下一步优先验证 `from_batch / from_customer` 的共用任务链兼容性。
2. 如果数据量继续上升，优先评估把创建后执行链切到异步，同时保持 `task_no` 结果回读契约不变。
