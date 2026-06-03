# 二期 controller/service/model 具体文件创建建议

适用范围：
- 用于把二期接口文档落成“可以直接在仓库里建哪些文件”的实现建议
- 当前只覆盖后台 `admin` 场景

当前状态：
- 前一份《二期 service_controller_model 方法分层建议》回答的是职责边界
- 本文档进一步收口到“建议新建哪些文件、哪些文件只扩展现有实现”

关联文档：
- `二期接口与现有 custom_addons 文件落位映射表.md`
- `二期 service_controller_model 方法分层建议.md`
- `二期接口实现检查清单.md`

---

## 1. 总体建议

建议采用“`logistics_web` 做接口出口，`logistics_dispatch` 做主业务模型承接，`trace_*` 做领域聚合 helper”的最小侵入方案。

这样做有 3 个好处：

1. 与当前仓库已有 `logistics_web/controllers/logistics_web_dashboard.py` 风格一致
2. 不需要把首页、统计、导入流程硬塞进 `logistics_dispatch` 的大模型文件
3. 不会打散 `exception / evidence / trace` 的现有领域边界

---

## 2. 建议新增文件清单

## 2.1 `logistics_web` 建议新增

```text
custom_addons/logistics_web/
  __init__.py                          # 需补 import services
  controllers/
    __init__.py                        # 需补 import
    logistics_web_home.py              # 新增
    logistics_web_stats.py             # 新增
    logistics_web_import.py            # 新增
  services/                            # 新增目录
    __init__.py                        # 新增
    home_service.py                    # 新增
    stats_service.py                   # 新增
    import_service.py                  # 新增
```

### 文件职责

| 文件 | 建议职责 | 建议方法 |
| --- | --- | --- |
| `controllers/logistics_web_home.py` | 首页接口路由 | `get_home_overview`、`get_home_recent_activities`、`get_home_guide` |
| `controllers/logistics_web_stats.py` | 统计图表接口路由 | `get_stats_overview`、`get_stats_trend`、`get_stats_ranking` |
| `controllers/logistics_web_import.py` | 模板下载、预校验、正式导入、结果页接口路由 | `download_waybill_template`、`precheck_waybill_import`、`confirm_waybill_import`、`get_waybill_import_result` |
| `services/home_service.py` | 首页聚合编排 | `build_home_overview_summary`、`build_home_recent_activities`、`build_home_guide_by_role` |
| `services/stats_service.py` | 统计口径编排 | `build_stats_overview`、`build_stats_trend`、`build_stats_ranking` |
| `services/import_service.py` | 导入流程编排 | `get_waybill_template_meta`、`precheck_waybill_standard_import`、`confirm_waybill_standard_import`、`build_waybill_import_result` |

### 推荐说明

- 不建议继续把首页、统计、导入都堆进 `controllers/logistics_web_dashboard.py`
- 当前 `logistics_web` 还没有 `services/` 目录，二期可以正式引入
- 如果新建 `services/`，`custom_addons/logistics_web/__init__.py` 需要从
  - `from . import controllers`
  - `from . import models`
  - 调整为再补一行 `from . import services`

## 2.2 `logistics_dispatch` 建议新增

```text
custom_addons/logistics_dispatch/
  models/
    __init__.py                                           # 需补 import
    logistics_dispatch_waybill_api.py                     # 新增
    logistics_dispatch_waybill_customer_line_api.py       # 新增
    logistics_dispatch_waybill_customer_goods_line_api.py # 新增
    logistics_import_batch.py                             # 新增
```

### 文件职责

| 文件 | 建议职责 | 建议方法 |
| --- | --- | --- |
| `models/logistics_dispatch_waybill_api.py` | 运单详情 V2、首页执行聚合、统计查询 helper | `get_waybill_detail_v2`、`_get_home_todo_counts`、`_query_stats_overview`、`_query_stats_trend`、`_query_stats_ranking` |
| `models/logistics_dispatch_waybill_customer_line_api.py` | 客户明细读取接口 | `get_lines_by_waybill`、`_validate_customer_line_rows` |
| `models/logistics_dispatch_waybill_customer_goods_line_api.py` | 货物明细读取接口 | `get_goods_lines_by_waybill`、`_validate_goods_line_rows` |
| `models/logistics_import_batch.py` | 导入批次、预校验 token、结果页摘要持久化 | `create_precheck_batch`、`confirm_import_batch`、`build_import_result_dto` |

### 推荐说明

- `logistics_dispatch/models/logistics_dispatch_waybill.py` 已经承担大量字段与业务约束，二期不建议继续无限增厚
- 通过新增 `_api.py` 扩展文件并使用 `_inherit`，更适合控制二期变更范围
- 当前客户明细与货物明细的活跃模型文件分别是：
  - `logistics_dispatch_waybill_customer_line_v2.py`
  - `logistics_dispatch_waybill_customer_goods_line_v2.py`
- 新建的 `_api.py` 文件应继承对应模型名，而不是把逻辑落回未被导入的历史文件

## 2.3 `logistics_trace_*` 不建议新建 controller/service

当前二期不建议在以下模块新增 controller 或 service 目录：

- `custom_addons/logistics_trace_core`
- `custom_addons/logistics_trace_evidence`
- `custom_addons/logistics_trace_exception`

推荐做法：

- 首页和统计需要的聚合 helper，直接扩现有 `models/*.py`
- 只在现有文件已经明显过长、且 helper 逻辑独立时，再考虑新增：
  - `models/logistics_trace_exception_dashboard_support.py`
  - `models/logistics_trace_evidence_dashboard_support.py`

默认不建议一开始就拆，因为二期真正的接口出口不在这些模块。

---

## 3. 推荐创建顺序

1. 先建 `logistics_web/services/` 目录与 3 个 service 文件
2. 再建 `logistics_web/controllers/` 下 3 个新 controller
3. 再建 `logistics_dispatch/models/` 下 4 个模型扩展文件
4. 最后补各模块 `__init__.py`

这个顺序的好处是：

- 先把接口出口与编排层搭出来
- 再逐步把业务查询方法补到底层模型
- 可以减少“controller 先写死、后面又返工改 service 调用”的情况

---

## 4. 不建议的创建方式

1. 不建议把所有二期接口继续堆进 `logistics_web_dashboard.py`
   - 这样首页、统计、导入三个域会混在一个 controller 文件里

2. 不建议把首页聚合逻辑写进 `logistics_web/models/`
   - `logistics_web/models/` 当前主要承担 UI 补丁、导入映射和轻量字段扩展

3. 不建议把新读取方法写入未加载的旧文件
   - 当前 `logistics_dispatch/models/__init__.py` 没有导入历史 `customer_line.py` 与 `goods_line.py`
   - 写进去不会自动生效

4. 不建议为二期在 `trace_*` 模块再建一层 API controller
   - 当前后台接口壳层已经集中在 `logistics_web`
   - 再开一层只会增加联调成本

---

## 5. 最小可开工文件集

如果目标是“先把二期开工骨架搭起来”，最小建议文件集如下：

```text
custom_addons/logistics_web/controllers/logistics_web_home.py
custom_addons/logistics_web/controllers/logistics_web_stats.py
custom_addons/logistics_web/controllers/logistics_web_import.py
custom_addons/logistics_web/services/__init__.py
custom_addons/logistics_web/services/home_service.py
custom_addons/logistics_web/services/stats_service.py
custom_addons/logistics_web/services/import_service.py
custom_addons/logistics_dispatch/models/logistics_dispatch_waybill_api.py
custom_addons/logistics_dispatch/models/logistics_dispatch_waybill_customer_line_api.py
custom_addons/logistics_dispatch/models/logistics_dispatch_waybill_customer_goods_line_api.py
custom_addons/logistics_dispatch/models/logistics_import_batch.py
```

这 11 个文件补齐后，二期接口已经具备“有路由、有编排层、有模型承接点”的基本开发骨架。
