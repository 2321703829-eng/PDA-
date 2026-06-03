# 桥接参考

本目录用于承接原生模块专题下仍有参考价值、但不直接等同于当前物流主线正式设计的桥接稿与过渡稿。

## 当前文件

- [销售主链第一版业务设计草案.md](./销售主链第一版业务设计草案.md)
- [采购主链第一版业务设计草案.md](./采购主链第一版业务设计草案.md)
- [库存与往来第一版业务设计草案.md](./库存与往来第一版业务设计草案.md)

## 当前角色

- 这些文档更适合作为通用 ERP 承接草案
- 可用于参考 Odoo `sale`、`purchase`、`stock` 原生能力的复用点
- 不直接作为当前物流项目 `wave -> batch -> waybill -> customer_line -> order_line -> goods_line` 主线的正式设计

## 使用说明

- 阅读这些草案时，应先对照 `docs/context/odoo_logistics_context.md` 和 `docs/context/odoo_logistics_feasibility.md`
- 如后续继续保留，应补充基于 Odoo 19 与当前物流主线的修订版，再决定是否升回 `01_模块设计/`
