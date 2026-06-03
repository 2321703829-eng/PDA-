# docs/context

`docs/context/` 用于承载项目背景、业务基线、Odoo 复用判断和历史上下文。

## 建议阅读顺序

1. [Odoo19物流留痕系统运单主对象与留痕主流程设计.md](./Odoo19物流留痕系统运单主对象与留痕主流程设计.md)
2. [odoo_logistics_context.md](./odoo_logistics_context.md)
3. [odoo_logistics_feasibility.md](./odoo_logistics_feasibility.md)
4. [Odoo原生模块复用源码入口索引.md](./Odoo原生模块复用源码入口索引.md)
5. [odoo_logistics_execution_trace_context.md](./odoo_logistics_execution_trace_context.md)

## 补充与历史草稿

以下文件更适合在需要追溯旧方案时再看：

- [odoo_logistics_order_trace_exception_draft.md](./odoo_logistics_order_trace_exception_draft.md)
- [odoo_logistics_master_data_draft.md](./odoo_logistics_master_data_draft.md)

## 状态标识规则

- `现行`：默认阅读入口，包括 `odoo_logistics_context.md`、`odoo_logistics_feasibility.md`、`Odoo原生模块复用源码入口索引.md`。
- `bridge`：现行上下文与正式 addon 设计之间的桥接层，当前主要是 `odoo_logistics_execution_trace_context.md`。
- `draft`：待确认草图或旧方案入口，不默认作为当前开发决策基线。

## 默认判断

- 想确认当前业务基线：先读 `odoo_logistics_context.md`
- 想判断应复用 Odoo 还是自建：再读 `odoo_logistics_feasibility.md`
- 想落到具体 Odoo 源码入口：再读 `Odoo原生模块复用源码入口索引.md`
- 想补执行链与追溯链上下文：再读 `odoo_logistics_execution_trace_context.md`

## 当前口径

- 执行与数据主链：`wave -> batch -> waybill -> customer_line -> order_line -> goods_line`
- 页面主阅读链：`waybill -> customer_line -> order_line`
- 图片阅读链：`waybill -> customer_line -> 图片预览 / 留痕 / 证据`
- `waybill` 仍是当前追溯主对象
- `customer_line` 是当前门店侧主阅读入口
- 正式证据对象仍围绕 `trace_event`
- `sale.order` 不是物流执行主单
- 历史 `draft` 文件默认不作为现行决策入口，除非正文明确声明仍有效

## 辅助目录

- [meeting_notes/](./meeting_notes/)
  项目级会议纪要与阶段沟通材料。
- [source_materials/](./source_materials/)
  项目级原始设计来源稿。
- [compliance/](./compliance/)
  商用合规检查资料。

