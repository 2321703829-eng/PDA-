# 2026-05-12 物流主线与销采存票模块边界方案

## 本轮变更

- 在 `ai-code/专题设计/ODOO原生模块设计/01_模块设计/` 新增主文档：
  - `2026-05-12_物流主线_vs_销售采购库存发票主线_模块边界方案.md`
- 更新：
  - `ai-code/专题设计/ODOO原生模块设计/01_模块设计/README.md`
  - `ai-code/专题设计/ODOO原生模块设计/主文档清单.md`

## 方案核心结论

- `wave -> batch -> waybill -> customer_line -> order_line -> goods_line` 是当前系统的物流执行主线
- `waybill / customer_line context -> trace_event -> evidence -> exception` 是当前系统的物流追溯主线
- 销售、采购、库存、发票应作为业务来源、仓储底座和结算底座，不替代物流主对象
- 官方 `sale / purchase / stock / account` 主要走 `extend Odoo`
- 物流执行与追溯对象主要走 `create custom capability`

## 文档同步情况

- 已同步：专题模块设计目录入口
- 已同步：专题主文档清单
- 已同步：`docs/change_notes/`
- 未同步：`docs/context/`、`docs/architecture/`
  - 原因：本轮方案与当前项目基线一致，属于专题设计深化，不改变项目级正式基线
