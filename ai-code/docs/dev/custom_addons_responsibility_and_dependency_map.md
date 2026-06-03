# custom_addons 模块职责与依赖总表

## 1. 目的

本表用于帮助在不打开代码细节的前提下，快速理解 `custom_addons/` 当前现行模块各自负责什么、依赖谁、排查时先看哪里。

## 2. 现行模块总览

| 模块 | 主要职责 | 直接依赖 | 高频入口目录 |
| --- | --- | --- | --- |
| `logistics_base` | 主数据基础扩展：客户、员工、车辆、仓库、基础画像 | `contacts` `hr` `product` `stock` `fleet` | `models/` `views/` `security/` |
| `logistics_dispatch` | 调度执行主线：wave、batch、waybill、执行基础对象 | `logistics_base` `mail` `fleet` `sale` | `models/` `views/` `data/` `migrations/` |
| `logistics_trace_core` | 留痕事件核心层，承接批次级和运单级 trace event | `mail` `logistics_dispatch` | `models/` `views/` |
| `logistics_trace_evidence` | 证据层，承接 evidence 与 evidence image 元数据 | `logistics_trace_core` | `models/` `views/` |
| `logistics_trace_exception` | 异常层，承接异常对象、状态流转和处理记录 | `mail` `hr` `logistics_trace_core` `logistics_trace_evidence` | `models/` `views/` `security/` |
| `logistics_web` | 物流后台前端承载层，动作、页面、导入导出、统计和前端资源 | `web` `base_import` `logistics_dispatch` `logistics_trace_core` `logistics_trace_evidence` `logistics_trace_exception` | `controllers/` `models/` `services/` `views/` `static/src/` `data/` |

## 3. 默认阅读顺序

如果只是快速定位当前代码主线，建议按这个顺序理解：

1. `logistics_base`
2. `logistics_dispatch`
3. `logistics_trace_core`
4. `logistics_trace_evidence`
5. `logistics_trace_exception`
6. `logistics_web`

## 4. 排查入口建议

### 如果问题偏模型 / 状态 / 数据落库

优先看：

- `logistics_dispatch/models/`
- `logistics_trace_core/models/`
- `logistics_trace_evidence/models/`
- `logistics_trace_exception/models/`

### 如果问题偏菜单 / 表单 / tree / search / action

优先看：

- `logistics_dispatch/views/`
- `logistics_trace_core/views/`
- `logistics_trace_evidence/views/`
- `logistics_trace_exception/views/`
- `logistics_web/views/`

### 如果问题偏前端动作 / client action / OWL / 模板 / 样式

优先看：

- `logistics_web/static/src/js/actions/`
- `logistics_web/static/src/js/components/`
- `logistics_web/static/src/js/views/`
- `logistics_web/static/src/js/widgets/`
- `logistics_web/static/src/xml/`
- `logistics_web/static/src/scss/`

### 如果问题偏导入导出 / 服务层 / 控制器

优先看：

- `logistics_web/services/`
- `logistics_web/controllers/`
- `logistics_dispatch/models/`
- `logistics_dispatch/data/`

## 5. 历史占位目录提醒

以下目录当前不属于现行可加载模块：

- `logistics_order`
- `logistics_trace`
- `logistics_exception`

它们当前主要用于历史命名桥接，不应用作当前排查入口。

## 6. 当前口径

- 现行模块状态，以 [custom_addons_module_status_inventory.md](./custom_addons_module_status_inventory.md) 为准。
- 如果要看系统正式模块边界，以 `docs/architecture/` 正文为准。
- 如果要动结构，建议等当前 bug 排查阶段结束后再做。
