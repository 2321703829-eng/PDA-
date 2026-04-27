# custom_addons 模块状态清单

## 1. 目的

本清单用于快速说明 `D:\Desktop\Odoo\custom_addons` 当前的模块现状，避免把历史占位目录误当成现行可运行模块。

## 2. 当前结论

`custom_addons/` 顶层当前共有 9 个目录：

- 6 个现行模块目录
- 3 个历史占位目录

是否为现行模块的最直接判断标准：

- 目录下是否存在 `__manifest__.py`

## 3. 现行模块

以下 6 个目录当前属于现行可加载模块：

| 模块目录 | 状态 | 说明 |
| --- | --- | --- |
| `logistics_base` | `现行` | 物流基础层 |
| `logistics_dispatch` | `现行` | 调度、批次、运单与执行主线 |
| `logistics_trace_core` | `现行` | 留痕核心层 |
| `logistics_trace_evidence` | `现行` | 证据层 |
| `logistics_trace_exception` | `现行` | 异常层 |
| `logistics_web` | `现行` | 前端与 Web 承载层 |

这些目录都存在 `__manifest__.py`，应按当前运行模块理解。

## 4. 历史占位目录

以下 3 个目录当前不应作为现行运行模块理解：

| 模块目录 | 状态 | 说明 |
| --- | --- | --- |
| `logistics_order` | `legacy-placeholder` | 仅保留历史命名占位 |
| `logistics_trace` | `legacy-placeholder` | 仅保留历史命名占位 |
| `logistics_exception` | `legacy-placeholder` | 仅保留历史命名占位 |

这些目录当前只有 `README.md`，没有 `__manifest__.py`，不属于现行 Odoo 可加载模块。

## 5. 当前治理建议

当前如果你还在进行 bug 排查与修复，建议只做以下低风险治理：

1. 维护 `custom_addons/README.md` 的总索引说明。
2. 维护本清单，明确现行模块与历史占位目录的状态。
3. 不在排查期内移动、改名或删除现行模块目录。
4. 不在排查期内删除 `__pycache__`、重排活跃代码文件路径或调整 manifest 依赖。

## 6. 后续可分阶段处理

### 第一阶段：现在可做

- 总索引更新
- 模块状态清单
- 文档化说明

### 第二阶段：建议等 bug 修完

- 清理 `__pycache__`
- 统一非运行类目录说明
- 评估旧占位目录是否继续保留

### 第三阶段：后续再做

- 真正的结构优化
- 旧占位目录退场
- 活跃模块内部结构再整理

## 7. 当前口径

- 当前真实模块主线以 `logistics_base / logistics_dispatch / logistics_trace_core / logistics_trace_evidence / logistics_trace_exception / logistics_web` 为准。
- `logistics_order / logistics_trace / logistics_exception` 主要用于历史桥接语义，不应再当成现行模块边界。
