# logistics_trace_evidence

## 当前角色

- active
- 证据与图片元数据层

## 模块职责

- 承接 `trace -> evidence` 证据链
- 定义 `logistics.trace.evidence`
- 提供证据对象、运单聚合、图片元数据与存储服务衔接

## 关键依赖

- `logistics_trace_core`

## 当前重点目录

- `models/`：证据对象与运单侧扩展
- `controllers/`：证据图片接口
- `services/`：图片存储服务
- `views/`：证据视图

## 上游与下游

- 上游模块：`logistics_trace_core`
- 下游现行模块：
  - `logistics_trace_exception`
  - `logistics_web`

## 使用说明

- 这是现行模块。
- 生产级图片能力应继续按“元数据 + 对象存储”方向收口，不回退为长期依赖默认附件架构。
