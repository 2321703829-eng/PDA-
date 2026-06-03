# logistics_web

## 当前角色

- active
- 后台前端增强与聚合读取层

## 模块职责

- 承接物流后台前端增强能力
- 提供控制器、前端动作、组件、样式和聚合读取服务
- 面向后台工作台、导入中心、导出结果、司机与车辆管理、统计与追溯阅读

## 关键依赖

- `web`
- `base_import`
- `logistics_dispatch`
- `logistics_trace_core`
- `logistics_trace_evidence`
- `logistics_trace_exception`

## 当前重点目录

- `controllers/`：后台与 mini 读取接口
- `models/`：聚合服务与映射对象
- `services/`：导入导出与业务聚合服务
- `static/src/`：前端动作、组件、服务、样式与模板
- `views/`：动作、菜单、模板与后台视图增强

## 上游与下游

- 上游业务模块：
  - `logistics_dispatch`
  - `logistics_trace_core`
  - `logistics_trace_evidence`
  - `logistics_trace_exception`
- 下游职责：前端读取与后台交互层

## 使用说明

- 这是现行模块。
- 与页面结构、聚合读取、前端动作相关的改动优先落在本模块，不要把前端增强逻辑塞回纯业务对象模块。
