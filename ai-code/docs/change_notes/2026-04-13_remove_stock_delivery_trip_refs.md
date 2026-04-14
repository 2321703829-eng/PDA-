# 2026-04-13 移除现行文档中的 stock_delivery_trip 残留引用

## 背景

在当前仓库中，`stock_delivery_trip` / `stock.delivery.trip` 并不存在。

因此，现行设计文档中如果继续把它写成“可直接复用的 Odoo 原生模块”，会误导后续的前端设计、模块设计和代码实现。

## 本次调整

本次仅回调当前有效文档中的残留引用，不修改历史归档资料，也不修改专门说明“该模块不存在”的核查文档。

已调整文件：

- `ai-code/Odoo19物流留痕系统运单主对象与留痕主流程设计.md`
- `ai-code/Odoo19物流留痕系统五人分工与前端改造安排.md`
- `ai-code/于睿_后台前端与追溯界面工作大纲.md`

## 调整原则

- 把 `stock_delivery_trip` / `stock.delivery.trip` 统一回调为 `logistics_dispatch` 或“自定义调度层”表述
- 保持当前有效口径与现有仓库实际一致
- 保留历史目录 `ai-code/odoo-reconstruct/` 中的旧说法，作为历史参考
- 保留 `ai-code/docs/context/Odoo原生模块复用源码入口索引.md` 中关于“该模块不存在”的说明

## 当前结论

现行文档已经不再把 `stock_delivery_trip` 作为当前仓库可直接复用的 Odoo 原生模块。

如果后续需要“车次 / 调度”能力，应默认理解为：

- 由 `logistics_dispatch` 自定义模块承接
- 必要时复用 `stock.picking.batch`、`fleet`、`stock_fleet` 的底层能力
