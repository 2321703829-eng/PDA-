# 2026-05-09 Odoo 原生模块现状对照文件新增

## 本次变更

- 新增 `ai-code/专题设计/ODOO原生模块设计/2026-05-09_功能覆盖清单模块现状对照.md`
- 按 `功能覆盖清单.md` 第一部分的 1-29 项，逐条核查当前仓库与当前主库 `odoo_logistics_webtest_v19` 中的真实状态
- 明确区分：
  - 源码仍在仓库
  - 主库已安装
  - 菜单被隐藏
  - 模块未安装
- 补充“已隐藏模块”的现状说明，明确当前最确定的隐藏模块为 `sale`
- 补充“未启用原生模块中，哪些能力已被自定义模块部分承接”的对照说明

## 本次结论

- `stock`、`account`、`contacts`、`hr`、`fleet`、`barcodes`、`logistics_dispatch`、`logistics_trace_*` 当前仍在系统中
- `sale` 与 `sale_stock` 当前不是缺失，而是 `sale` 根菜单被隐藏
- `purchase`、`purchase_stock`、`website_sale`、`website_sale_stock`、`stock_picking_batch`、`delivery`、`stock_landed_costs`、毛利相关模块当前主库未安装
- `stock_picking_batch` 对应的执行组织主线、部分配送调度能力，已被 `logistics_dispatch` 部分承接
- 采购、电商前台、毛利、落地成本等能力当前仍未看到成熟的自定义替代

## 作用

- 为后续“基于 Odoo 原生能力做改造”的调研提供统一现状基线
- 避免把“已隐藏”和“未安装”混为一谈
