# 2026-05-13 B Line Round2 Round3 Followup Actions

## Summary

- 补齐 `D06` 的库存操作入口和回查动作
- 补齐 `E05` 的司机在途节点与派车费用查看入口
- 补齐 `G01/G02` 的 BI 总览生成与下钻动作
- 补齐 `H01/H02` 的 `route batch / waybill` 反查入口

## Scope

- `custom_addons/wms_task_core`
- `custom_addons/tms_dispatch_core`
- `custom_addons/bi_ops_dashboard`

## Key Changes

- `stock.location` 新增库存操作统计、创建入口和列表入口
- `wms.inventory.operation` 新增 source/generated picking 回查动作，并在仓内退货时自动确认生成的内部调拨
- `tms.dispatch.order` 新增任务状态汇总与运费明细查看入口
- `tms.driver.task` 新增在途节点更新、签收/异常回查、最新坐标摘要和 waybill 回查
- `logistics.route.planning.batch` 新增交接单、派车单、司机任务反查入口
- BI 新增一键生成全套快照和多页下钻入口
- 清理 `waybill` 反查按钮文案乱码

## Validation

- Python AST parse: passed
- XML parse: passed
