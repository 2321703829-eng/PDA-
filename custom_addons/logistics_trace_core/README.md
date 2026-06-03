# logistics_trace_core

## 当前角色

- active
- 留痕核心事件层

## 模块职责

- 承接 `waybill -> trace` 主留痕链中的核心事件对象
- 定义 `logistics.trace.event`
- 提供运单侧留痕聚合与时间线建模基础

## 关键依赖

- `mail`
- `logistics_dispatch`

## 当前重点目录

- `models/`：留痕事件与运单聚合扩展
- `views/`：事件视图
- `security/`：访问控制

## 上游与下游

- 上游模块：`logistics_dispatch`
- 下游现行模块：
  - `logistics_trace_evidence`
  - `logistics_trace_exception`
  - `logistics_web`

## 使用说明

- 这是现行模块。
- 不要再把 `logistics_trace` 旧目录理解成当前正式留痕主模块。
