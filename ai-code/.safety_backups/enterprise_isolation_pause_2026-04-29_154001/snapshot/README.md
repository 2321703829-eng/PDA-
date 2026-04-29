# custom_addons

`custom_addons/` 用于承接项目自定义 Odoo 模块。

当前这里不再只是规划目录，而是已经同时存在：

- 现行可加载模块
- 历史占位目录

## 当前现行模块

以下目录当前属于现行可加载模块：

- `logistics_base`
- `logistics_dispatch`
- `logistics_trace_core`
- `logistics_trace_evidence`
- `logistics_trace_exception`
- `logistics_web`

判断口径：以上目录都存在 `__manifest__.py`。

## 历史占位目录

以下目录当前主要保留历史命名或桥接意义：

- `logistics_order`
- `logistics_trace`
- `logistics_exception`

判断口径：以上目录当前只有 `README.md`，没有 `__manifest__.py`，不应作为现行运行模块理解。

## 当前默认理解方式

- 如果在查当前运行模块、依赖关系、视图、模型、控制器或前端资源，请优先看 6 个现行模块。
- 如果在阅读旧设计、旧 change note 或旧命名桥接材料，可以把 `logistics_order / logistics_trace / logistics_exception` 理解为历史术语入口。

## 整理边界

在仍有 bug 排查和修复进行时，当前建议只做低风险治理：

- 更新总索引说明
- 维护模块状态清单
- 不移动现行模块目录
- 不改 manifest
- 不改 Python / XML / JS 活跃代码
- 不删 `__pycache__`

## 相关文档

- `ai-code/docs/architecture/ARCHITECTURE.md`
- `ai-code/docs/architecture/custom_addons_blueprint.md`
- `ai-code/docs/dev/custom_addons_module_status_inventory.md`
