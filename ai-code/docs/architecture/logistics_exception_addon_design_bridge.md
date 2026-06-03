# logistics_exception Addon 设计稿

> 状态说明：本文档已转为历史入口说明。
>
> 原因：当前有效设计已不再以 `logistics_exception` 作为最终模块命名与边界，异常层已回调为 `logistics_trace_exception`，并建立在 `logistics_dispatch + logistics_trace_core` 之上。
>
> 当前请优先参考：
> - `ai-code/docs/architecture/logistics_trace_exception_addon_design.md`
> - `ai-code/docs/context/Odoo19物流留痕系统运单主对象与留痕主流程设计.md`
> - `ai-code/docs/architecture/ARCHITECTURE.md`

---

## 1. 当前结论

`logistics_exception_addon_design_bridge.md` 不再作为当前现行模块设计稿继续维护。

当前系统已经明确：

- 异常不再默认挂在订单上
- 异常应建立在批次 / 运单上下文与留痕事实之上
- 异常层应与 `dispatch`、`trace_core`、`evidence` 一起构成完整追溯链

因此，原本由 `logistics_exception` 承担的“订单问题追溯链模块”设计思路，已经不再适合作为当前模块边界。

---

## 2. 回调后的模块理解

当前应将旧的 `logistics_exception` 设计，整体迁移理解为：

- 历史阶段的过渡命名
- 向 `logistics_trace_exception` 过渡的旧入口

也就是说，如果后续文档或历史记录里仍提到：

- `logistics_exception`
- `logistics.exception`

阅读时都不应再直接理解为当前最终模块真相。

---

## 3. 当前替代文档

后续如果要继续设计或实现异常层，请直接参考：

1. `docs/architecture/logistics_trace_exception_addon_design.md`
2. `docs/context/Odoo19物流留痕系统运单主对象与留痕主流程设计.md`
3. `docs/architecture/ARCHITECTURE.md`
4. `docs/architecture/custom_addons_blueprint.md`

---

## 4. 本文档保留的唯一价值

本文档现在保留的价值只有两点：

1. 作为历史命名的跳转入口
2. 帮助后续阅读旧 change note 或旧评审记录时理解“为什么 `logistics_exception` 被回调为 `logistics_trace_exception`”

除此之外，本文档不再承担现行设计职责。

