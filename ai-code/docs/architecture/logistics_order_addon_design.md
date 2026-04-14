# logistics_order Addon 设计稿

> 状态说明：本文档已转为历史入口说明。
>
> 原因：当前有效设计已不再以 `logistics_order / logistics.order` 作为执行主线模块，模块职责已回调为 `logistics_dispatch`。
>
> 当前请优先参考：
> - `ai-code/docs/architecture/logistics_dispatch_addon_design.md`
> - `ai-code/Odoo19物流留痕系统运单主对象与留痕主流程设计.md`
> - `ai-code/docs/architecture/ARCHITECTURE.md`

---

## 1. 当前结论

`logistics_order_addon_design.md` 不再作为当前现行模块设计稿继续维护。

当前系统已经明确：

- `订单` 不是留痕主对象
- `运单` 才是现场留痕主对象
- `波次 -> 批次 -> 运单` 才是执行主线

因此，原本由 `logistics_order` 承担的“订单 / 批次快照层模块”设计思路，已经不再适合作为当前模块边界。

---

## 2. 回调后的模块理解

当前应将旧的 `logistics_order` 设计，整体迁移理解为：

- 历史阶段的过渡命名
- 向 `logistics_dispatch` 过渡的旧入口

也就是说，如果后续文档或历史记录里仍提到：

- `logistics_order`
- `logistics.order`
- `logistics.batch`

阅读时都不应再直接理解为当前最终模块真相。

---

## 3. 当前替代文档

后续如果要继续设计或实现执行主线，请直接参考：

1. `docs/architecture/logistics_dispatch_addon_design.md`
2. `Odoo19物流留痕系统运单主对象与留痕主流程设计.md`
3. `docs/architecture/ARCHITECTURE.md`
4. `docs/architecture/custom_addons_blueprint.md`

---

## 4. 本文档保留的唯一价值

本文档现在保留的价值只有两点：

1. 作为历史命名的跳转入口
2. 帮助后续阅读旧 change note 或旧评审记录时理解“为什么 `logistics_order` 被回调掉”

除此之外，本文档不再承担现行设计职责。
