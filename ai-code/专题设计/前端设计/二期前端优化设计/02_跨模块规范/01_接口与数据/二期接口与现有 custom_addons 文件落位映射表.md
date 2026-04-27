# 二期接口与现有 custom_addons 文件落位映射表

适用范围：
- 用于把二期接口设计文档映射到当前仓库 `custom_addons/` 的真实模块与文件位置
- 当前只覆盖后台 `admin` 场景

当前状态：
- 本文档强调“对照现有仓库开工”
- 目标不是重新发明模块边界，而是在现有 `logistics_web / logistics_dispatch / logistics_trace_*` 基础上补齐二期接口

关联文档：
- `二期 controller/service/model 具体文件创建建议.md`
- `二期接口实现检查清单.md`
- `二期后端接口开发任务拆分稿.md`

---

## 1. 当前仓库可直接复用的模块基础

| 模块 | 当前已存在能力 | 说明 |
| --- | --- | --- |
| `custom_addons/logistics_web` | 已有 `controllers/logistics_web_dashboard.py`、前端 action、导入字段映射数据 | 适合承接二期新增 `admin` JSON controller |
| `custom_addons/logistics_dispatch` | 已有 `waybill / batch / wave` 主执行模型、三层导入模板、导入辅助逻辑 | 适合承接运单详情三层读取、导入校验与落库 |
| `custom_addons/logistics_trace_core` | 已有 trace 事件与 waybill 留痕扩展 | 适合提供最新留痕、留痕计数类基础聚合 |
| `custom_addons/logistics_trace_evidence` | 已有 evidence 模型与运单扩展 | 适合提供证据缺失、证据补齐类聚合 |
| `custom_addons/logistics_trace_exception` | 已有 exception 模型、process log、waybill 扩展 | 适合提供异常数量、异常列表、风险批次类聚合 |

---

## 2. 接口落位总表

| 二期接口 / 能力 | 建议主落位模块 | 当前可复用文件 | 建议新增或扩展文件 | 动作类型 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `getHomeOverviewSummary` | `logistics_web` | `controllers/logistics_web_dashboard.py` | `logistics_web/controllers/logistics_web_home.py` | 新增 controller | 首页入口仍建议放 `logistics_web`，不要继续堆进现有 dashboard 文件 |
| `getHomeRecentActivities` | `logistics_web` | `controllers/logistics_web_dashboard.py` | `logistics_web/controllers/logistics_web_home.py` | 新增 controller | 与首页概览共文件更合适，避免首页接口分散 |
| `getHomeGuideByRole` | `logistics_web` | `static/src/js/actions/home_action.js` | `logistics_web/controllers/logistics_web_home.py` | 新增 controller | 角色化引导是首页壳层能力，适合由 web 模块统一输出 |
| 首页聚合 service | `logistics_web` | 当前无 service 目录 | `logistics_web/services/home_service.py` | 新增 service | 负责跨 `dispatch / exception / evidence` 聚合，不建议写在 controller 中 |
| 首页待办与执行聚合 helper | `logistics_dispatch` | `models/logistics_dispatch_waybill.py` | `logistics_dispatch/models/logistics_dispatch_waybill_api.py` | 扩模型能力 | 适合补运单待执行、已签收、超时风险等查询方法 |
| 首页异常聚合 helper | `logistics_trace_exception` | `models/logistics_trace_exception.py` | 扩现有文件 | 扩模型能力 | 建议先扩现有异常模型，不单独新开 controller |
| 首页证据聚合 helper | `logistics_trace_evidence` | `models/logistics_trace_evidence.py` | 扩现有文件 | 扩模型能力 | 提供待补证据、证据补齐率类聚合 |
| `getStatsOverviewByDateRange` | `logistics_web` | `controllers/logistics_web_dashboard.py` | `logistics_web/controllers/logistics_web_stats.py` | 新增 controller | 二期统计图表独立成域，不建议复用 dashboard 路径名 |
| `getStatsTrendByMetric` | `logistics_web` | 无现成 stats controller | `logistics_web/controllers/logistics_web_stats.py` | 新增 controller | 与 overview、ranking 同域 |
| `getStatsRankingByDimension` | `logistics_web` | 无现成 stats controller | `logistics_web/controllers/logistics_web_stats.py` | 新增 controller | 排行接口应与统计域放在同一文件 |
| 统计聚合 service | `logistics_web` | 当前无 service 目录 | `logistics_web/services/stats_service.py` | 新增 service | 负责指标白名单、时间粒度、排行维度控制 |
| 统计查询 helper | `logistics_dispatch` | `models/logistics_dispatch_waybill.py` | `logistics_dispatch/models/logistics_dispatch_waybill_api.py` | 扩模型能力 | 运单、批次、客户、门店等统计主数据仍以 dispatch 为主 |
| `getWaybillDetailV2` | `logistics_dispatch` | `models/logistics_dispatch_waybill.py` | `logistics_dispatch/models/logistics_dispatch_waybill_api.py` | 扩模型能力 | 该接口更适合 model method / RPC 风格，不强制新增 HTTP controller |
| `getWaybillCustomerLinesByWaybill` | `logistics_dispatch` | `models/logistics_dispatch_waybill_customer_line_v2.py` | `logistics_dispatch/models/logistics_dispatch_waybill_customer_line_api.py` | 扩模型能力 | 当前活跃客户明细文件是 `_v2.py`，不要把新方法写进未加载的历史文件 |
| `getWaybillCustomerGoodsLinesByWaybill` | `logistics_dispatch` | `models/logistics_dispatch_waybill_customer_goods_line_v2.py` | `logistics_dispatch/models/logistics_dispatch_waybill_customer_goods_line_api.py` | 扩模型能力 | 当前活跃货物明细文件是 `_v2.py`，不要把新方法写进未加载的历史文件 |
| `downloadWaybillStandardTemplate` | `logistics_web + logistics_dispatch` | `logistics_dispatch/models/logistics_dispatch_import_support.py`、`logistics_dispatch/static/src/import_templates/*` | `logistics_web/controllers/logistics_web_import.py` | 新增 controller | 模板资源继续放 dispatch，HTTP 出口放 web |
| `precheckWaybillStandardImport` | `logistics_web + logistics_dispatch` | `logistics_dispatch/models/logistics_dispatch_import_support.py`、`logistics_web/data/base_import_mapping_data.xml` | `logistics_web/controllers/logistics_web_import.py`、`logistics_web/services/import_service.py` | 新增 controller/service | 预校验涉及上传、错误汇总、模板规则，建议由 web 编排、dispatch 落业务规则 |
| `confirmWaybillStandardImport` | `logistics_web + logistics_dispatch` | 当前无正式导入批次模型 | `logistics_web/controllers/logistics_web_import.py`、`logistics_web/services/import_service.py`、`logistics_dispatch/models/logistics_import_batch.py` | 新增 controller/service/model | 正式导入需要持久化批次、token、结果摘要 |
| `getWaybillImportResult` | `logistics_web + logistics_dispatch` | 当前无 import result 专用模型 | `logistics_web/controllers/logistics_web_import.py`、`logistics_dispatch/models/logistics_import_batch.py` | 新增 controller/model | 结果页查询建议基于导入批次模型读取 |

---

## 3. 当前仓库中的关键参照文件

这些文件不是二期新增接口的最终落位，但它们决定了本次设计不能脱离现状：

- `custom_addons/logistics_web/controllers/logistics_web_dashboard.py`
  - 当前唯一已存在的 `admin` JSON controller
  - 二期新增首页 / 统计 / 导入接口应沿用它的 controller 风格
- `custom_addons/logistics_web/__init__.py`
  - 当前只导入 `controllers` 与 `models`
  - 如果新增 `services/`，模块根 `__init__.py` 需要同步导入
- `custom_addons/logistics_dispatch/models/__init__.py`
  - 当前已加载 `logistics_dispatch_waybill.py`
  - 当前已加载 `logistics_dispatch_waybill_customer_line_v2.py`
  - 当前已加载 `logistics_dispatch_waybill_customer_goods_line_v2.py`
  - 当前未加载历史 `logistics_dispatch_waybill_customer_line.py` 与 `logistics_dispatch_waybill_customer_goods_line.py`
- `custom_addons/logistics_dispatch/models/logistics_dispatch_import_support.py`
  - 已经具备模板路径与部分导入辅助逻辑
  - 二期应在此基础上升级，不应另起一套模板资源体系
- `custom_addons/logistics_web/data/base_import_mapping_data.xml`
  - 已经存在导入表头映射基础数据
  - 二期预校验与模板说明要与此保持一致

---

## 4. 推荐落位原则

1. `admin` HTTP / JSON 路由优先放 `logistics_web/controllers/`
   - 因为仓库当前已有 `logistics_web_dashboard.py` 作为后台聚合接口出口
   - 二期首页、统计、导入结果页都属于后台壳层能力

2. 业务查询与导入落库优先放 `logistics_dispatch/models/`
   - waybill、customer line、goods line 都是 dispatch 主执行对象
   - 三层详情与标准导入不应拆到 `logistics_web/models/`

3. trace / evidence / exception 继续只做领域 helper
   - 不建议在二期新开 `trace_*` controller
   - 保持它们作为聚合数据提供者更稳妥

4. 不要把二期新方法写进未加载的历史文件
   - 当前客户明细与货物明细实际加载的是 `_v2.py`
   - 如果新方法写在未被 `__init__.py` 导入的旧文件，代码不会生效

---

## 5. 本文档边界

- 本文档只回答“接口应落在哪个现有模块与文件附近”
- 具体新建文件清单，继续看 `二期 controller/service/model 具体文件创建建议.md`
- 实现完成后的自检口径，继续看 `二期接口实现检查清单.md`
