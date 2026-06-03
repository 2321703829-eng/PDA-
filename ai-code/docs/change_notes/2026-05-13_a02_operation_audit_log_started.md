# 2026-05-13 A02 Operation Audit Log Started

## Summary

- 新增统一操作审计模块 `core_operation_audit_log`
- 补系统后台操作日志列表页、搜索页、详情页和系统设置入口
- 把 WMS / TMS / BI 的关键动作接入统一日志

## Scope

- `custom_addons/core_operation_audit_log`
- `custom_addons/wms_task_core`
- `custom_addons/tms_dispatch_core`
- `custom_addons/bi_ops_dashboard`

## Key Changes

- 新增模型 `core.operation.audit.log`
- 新增字段：
  - `business_domain`
  - `action_code`
  - `action_result`
  - `operator_id`
  - `object_model/object_res_id/object_name`
  - `document_no`
  - `related_model/related_res_id/related_name`
  - `exception_state`
  - `payload_json`
- WMS 接入：
  - 库位发起库存操作
  - 库存操作开始 / 加载 quants / 完成 / 取消
  - `stock.picking -> receipt/outbound task`
- TMS 接入：
  - 派车
  - 发车
  - 运费行生成
  - 司机到仓 / 开始配送 / 在途更新 / 到店 / 配送中
  - 创建签收单 / 创建异常 / 签收确认
  - `handover -> dispatch order`
- BI 接入：
  - KPI 日快照
  - 全量快照生成
  - 订单 / 仓库 / 配送 / 异常 / 成本利润快照生成

## Validation

- Python AST parse: passed
- XML parse: passed

## Notes

- 这一轮先落“统一日志对象 + 关键动作写入 + 日志页入口”
- 登录日志、导入导出日志、页面内嵌日志 tab 还没有展开
