# 二期 service_controller_model 方法分层建议

适用范围：
- 二期新增或升级接口的后端实现分层
- 当前只覆盖后台 `admin` 场景

当前状态：
- 本文档用于把二期接口继续落到 controller / service / model 的职责分层
- 当前是分层建议稿，不强制绑定具体 Python 文件名

关联文档：
- `二期接口 DTO 与返回对象命名建议.md`
- `二期后端接口开发任务拆分稿.md`
- `二期接口入参校验与错误码清单.md`

---

## 1. 文档定位

这份文档用于回答实现时最容易混乱的问题：

1. 哪些逻辑放 controller
2. 哪些逻辑放 service
3. 哪些逻辑放 model / model method

目标是避免两种坏味道：

- controller 里塞满业务逻辑
- model 里直接堆首页/统计/导入流程

---

## 2. 总体分层原则

## 2.1 controller 层

负责：

- 路由暴露
- 入参解析
- 权限前置检查
- 调用 service
- 返回统一响应结构

不负责：

- 跨对象聚合计算
- 导入流程编排
- 复杂统计拼装

## 2.2 service 层

负责：

- 业务流程编排
- 跨对象聚合
- DTO 组装
- 调用多个 model / repository 方法
- 错误码转换

不负责：

- 直接处理 HTTP 细节
- 直接写视图层文案

## 2.3 model 层

负责：

- 单对象或强关联对象的数据读取
- ORM 查询
- 基础聚合
- 与对象强绑定的业务约束

不负责：

- 首页级跨模块拼装
- 统计页多维结果包装
- 标准导入流程状态机编排

---

## 3. 二期接口分层建议

## 3.1 首页域

### controller

建议方法：

- `get_home_overview`
- `get_home_recent_activities`
- `get_home_guide`

### service

建议方法：

- `build_home_overview_summary`
- `build_home_recent_activities`
- `build_home_guide_by_role`

### model

建议方法：

- `logistics.dispatch.waybill._get_home_todo_counts`
- `logistics.trace.exception._get_home_exception_counts`
- `logistics.trace.evidence._get_home_evidence_counts`

说明：

- 首页是多对象聚合，核心逻辑必须落 service

## 3.2 统计域

### controller

建议方法：

- `get_stats_overview`
- `get_stats_trend`
- `get_stats_ranking`

### service

建议方法：

- `build_stats_overview`
- `build_stats_trend`
- `build_stats_ranking`

### model

建议方法：

- `logistics.dispatch.waybill._query_stats_overview`
- `logistics.dispatch.waybill._query_stats_trend`
- `logistics.dispatch.waybill._query_stats_ranking`

说明：

- 趋势、排行等统计对象建议统一沉到专门 service，而不是分散在多个 controller

## 3.3 运单详情三层域

### controller

如果走 RPC：

- controller 不一定新增 HTTP 路由
- 可由模型暴露 RPC 方法供前端调用

### service

建议方法：

- `build_waybill_detail_v2`
- `get_waybill_customer_lines`
- `get_waybill_customer_goods_lines`

### model

建议方法：

- `logistics.dispatch.waybill.get_waybill_detail_v2`
- `logistics.dispatch.waybill.customer.line.get_lines_by_waybill`
- `logistics.dispatch.waybill.customer.goods.line.get_lines_by_waybill`

说明：

- 如果只是标准详情与子表读取，优先靠 model method + 轻量 service，不必强行再包一层重 controller

## 3.4 导入域

### controller

建议方法：

- `download_waybill_template`
- `precheck_waybill_import`
- `confirm_waybill_import`
- `get_waybill_import_result`

### service

建议方法：

- `get_waybill_template_meta`
- `precheck_waybill_standard_import`
- `confirm_waybill_standard_import`
- `build_waybill_import_result`

### model

建议方法：

- `logistics.dispatch.waybill.customer.line._validate_import_rows`
- `logistics.dispatch.waybill.customer.goods.line._validate_import_rows`
- `logistics.dispatch.waybill._apply_import_rows`
- `logistics.import.batch._create_or_update_result`

说明：

- 导入域最适合做一层专门 `ImportService`
- 预校验、正式导入、结果页不要散落到多个 model 各自实现流程控制

---

## 4. 推荐模块职责

## 4.1 controller 文件建议

建议按能力域分：

- `controllers/home_controller.py`
- `controllers/stats_controller.py`
- `controllers/import_controller.py`

## 4.2 service 文件建议

建议按业务域分：

- `services/home_service.py`
- `services/stats_service.py`
- `services/import_service.py`
- `services/waybill_detail_service.py`

## 4.3 model 文件建议

继续以对象归属为主：

- `models/logistics_dispatch_waybill.py`
- `models/logistics_dispatch_waybill_customer_line.py`
- `models/logistics_dispatch_waybill_customer_goods_line.py`
- `models/logistics_import_batch.py`

---

## 5. 当前推荐落地方式

如果当前仓库还没有完整 service 层，建议二期采用折中方式：

1. 首页 / 统计 / 导入：明确新增 service 层
2. 运单详情三层读取：模型方法为主，必要时加轻量 service
3. controller 只做路由和响应封装

这样改动量可控，也不会把二期逻辑继续堆回 controller。
