# logistics_base

## 当前角色

- active
- 主数据与基础扩展层

## 模块职责

- 承接物流项目的主数据基础扩展
- 复用并扩展 `contacts / hr / product / stock / fleet`
- 为后续执行链和留痕链提供基础对象与字段

## 关键依赖

- `contacts`
- `hr`
- `product`
- `stock`
- `fleet`

## 当前重点目录

- `models/`：主数据扩展模型
- `views/`：基础资料表单与列表视图
- `security/`：访问控制
- `migrations/`：版本迁移脚本

## 上游与下游

- 上游基线：`ai-code/docs/architecture/`
- 下游现行模块：
  - `logistics_dispatch`
  - `logistics_web`

## 使用说明

- 这是现行模块。
- 与物流基础资料相关的共性字段和基础对象优先落在本模块，不要直接塞进 `dispatch` 或 `web`。
