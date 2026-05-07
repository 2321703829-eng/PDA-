# logistics_exception

## 当前角色

- bridge
- 历史命名桥接目录

## 当前状态

- 当前目录没有 `__manifest__.py`
- 当前不作为可安装模块

## 角色说明

- 该目录保留的是旧阶段异常模块命名
- 当前正式异常能力已由 `logistics_trace_exception` 承接
- 异常对象当前属于留痕链下游，不再作为脱离 `trace` 上下文的独立旧模块理解

## 参考口径

- 现行异常模块：`../logistics_trace_exception/`
- 项目架构基线：`../ai-code/docs/architecture/ARCHITECTURE.md`

## 使用说明

- 本目录只用于桥接旧设计和历史讨论。
- 若未来异常边界要调整，先更新架构与专题文档，再决定是否需要新模块化动作。
