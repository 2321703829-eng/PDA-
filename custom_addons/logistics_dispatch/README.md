# logistics_dispatch

## 当前角色

- active
- 执行主链承载层

## 模块职责

- 承接 `wave -> batch -> waybill -> customer_line -> order_line -> goods_line` 主执行链
- 提供运单导入、批次、波次、客户行、订单行、货物行等核心执行对象
- 作为留痕链和前端增强层的主要业务底座

## 关键依赖

- `logistics_base`
- `mail`
- `fleet`
- `sale`

## 当前重点目录

- `models/`：执行主链模型与导入导出支持
- `views/`：波次、批次、运单和菜单视图
- `data/`：序列等初始化数据
- `static/src/import_templates/`：导入模板

## 上游与下游

- 上游模块：`logistics_base`
- 下游现行模块：
  - `logistics_trace_core`
  - `logistics_web`

## 使用说明

- 这是当前最核心的现行业务模块。
- 新的执行对象优先判断是否应扩展本模块，而不是回退到 `logistics_order` 旧命名思路。
