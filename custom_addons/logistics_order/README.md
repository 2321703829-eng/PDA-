# logistics_order

## 当前角色

- bridge
- 历史命名桥接目录

## 当前状态

- 当前目录没有 `__manifest__.py`
- 当前不作为可安装模块

## 角色说明

- 该目录保留的是历史命名与设计桥接价值
- 当前执行主链已经以 `logistics_dispatch` 为正式承载层
- 不应再把 `sale.order` 或 `logistics_order` 理解成当前物流执行主对象

## 参考口径

- 现行业务模块：`../logistics_dispatch/`
- 项目架构基线：`../ai-code/docs/architecture/ARCHITECTURE.md`

## 使用说明

- 只有在追溯旧设计、旧命名或历史讨论时才进入本目录。
- 如果未来确实要恢复独立订单层设计，应先更新 `ai-code/docs/architecture/` 和专题设计，而不是直接在这里补代码。
