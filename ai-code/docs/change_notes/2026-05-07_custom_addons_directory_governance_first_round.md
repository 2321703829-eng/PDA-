# custom_addons 文件治理第一轮

## 本轮目标

为 `custom_addons/` 建立第一轮目录治理入口，明确现行模块、桥接目录、默认阅读顺序和各模块 README 的职责口径。

## 本轮变更

1. 重写 `custom_addons/README.md`，统一说明：
   - 当前现行模块主线
   - 历史桥接目录
   - 模块状态表
   - 默认阅读顺序
   - 目录治理规则
2. 重写以下现行模块 README：
   - `custom_addons/logistics_base/README.md`
   - `custom_addons/logistics_dispatch/README.md`
   - `custom_addons/logistics_trace_core/README.md`
   - `custom_addons/logistics_trace_evidence/README.md`
   - `custom_addons/logistics_trace_exception/README.md`
   - `custom_addons/logistics_web/README.md`
3. 重写以下桥接目录 README，明确它们不是现行可安装模块：
   - `custom_addons/logistics_order/README.md`
   - `custom_addons/logistics_trace/README.md`
   - `custom_addons/logistics_exception/README.md`

## 本轮结论

- `custom_addons/` 根入口不再把 `logistics_order / logistics_trace / logistics_exception` 误写成当前主线。
- 现行模块与桥接目录的边界已经在目录入口层明确。
- 本轮未修改业务代码、manifest、模型、控制器或视图，只做入口治理与说明同步。
