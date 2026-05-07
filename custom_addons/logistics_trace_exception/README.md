# logistics_trace_exception

## 当前角色

- active
- 异常与处理闭环层

## 模块职责

- 承接 `evidence -> exception` 异常链
- 定义 `logistics.trace.exception` 与处理日志对象
- 提供异常列表、详情、处理流转和运单侧异常聚合

## 关键依赖

- `mail`
- `hr`
- `logistics_trace_core`
- `logistics_trace_evidence`

## 当前重点目录

- `models/`：异常对象与处理日志
- `views/`：异常列表、详情与处理视图
- `security/`：访问控制

## 上游与下游

- 上游模块：
  - `logistics_trace_core`
  - `logistics_trace_evidence`
- 下游现行模块：
  - `logistics_web`

## 使用说明

- 这是现行模块。
- 不要把 `logistics_exception` 旧目录继续当作当前异常正式模块使用。
