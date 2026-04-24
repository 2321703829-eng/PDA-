# 2026-04-24 客户画像与货物画像导出 Controller 扩展已落地

## 本次变更

- 在 `custom_addons/logistics_web/controllers/logistics_web_export.py` 新增客户画像导出创建路由：
  - `POST /api/admin/logistics/exports/customer-profile`
- 在 `custom_addons/logistics_web/controllers/logistics_web_export.py` 新增货物画像导出创建路由：
  - `POST /api/admin/logistics/exports/product-profile`
- 创建路由首轮仍采用“创建任务 + 同步执行任务”的闭环方式，和 `from_waybill` 首轮保持一致。
- 将导出结果读取、行结果读取、错误明细、错误报告下载、主文件下载这 5 条共享链路改为按 `logistics.export.task.object_type` 动态分发到对应 service，不再固定走 `DispatchMainExportService`。

## 影响范围

- `dispatch_main`
- `customer_profile`
- `product_profile`

以上三类导出任务现在都可复用同一组结果读取与下载路由。

## 当前状态

- Python 语法检查已通过：
  - `custom_addons/logistics_web/controllers/logistics_web_export.py`
  - `custom_addons/logistics_web/controllers/__init__.py`
- 尚未执行：
  - Odoo 模块升级
  - HTTP 路由联调
  - 浏览器 smoke

## 下一步建议

- 继续做 `CPPR-EXP-F1`，先把导出结果页补上 `customer_profile / product_profile` 分支。
- 结果页分支接好后，再做客户画像页与货物画像页的入口按钮。
