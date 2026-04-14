# logistics_trace Addon 设计稿

> 状态说明：本文档已转为历史入口说明。
>
> 原因：当前有效设计已不再以 `logistics_trace` 作为单一粗粒度模块继续推进，留痕核心能力已回调为 `logistics_trace_core`，证据能力则独立到 `logistics_trace_evidence`。
>
> 当前请优先参考：
> - `ai-code/docs/architecture/logistics_trace_core_addon_design.md`
> - `ai-code/Odoo19物流留痕系统运单主对象与留痕主流程设计.md`
> - `ai-code/docs/architecture/ARCHITECTURE.md`

---

## 1. 当前结论

`logistics_trace_addon_design.md` 不再作为当前现行模块设计稿继续维护。

当前系统已经明确：

- 留痕应区分批次级事件与运单级事件
- 证据对象应独立于留痕核心层单独建模
- 后台阅读链应建立在 `dispatch -> trace_core -> evidence -> exception` 这条结构上

因此，原本把留痕与证据都压在 `logistics_trace` 单模块里的思路，已经不再适合作为当前模块边界。

---

## 2. 回调后的模块理解

当前应将旧的 `logistics_trace` 设计，整体迁移理解为：

- 历史阶段的过渡命名
- 向 `logistics_trace_core` 与 `logistics_trace_evidence` 拆分过渡的旧入口

也就是说，如果后续文档或历史记录里仍提到：

- `logistics_trace`
- `logistics.trace`
- `logistics.trace.image`

阅读时都不应再直接理解为当前最终模块真相。

---

## 3. 当前替代文档

后续如果要继续设计或实现留痕核心层，请直接参考：

1. `docs/architecture/logistics_trace_core_addon_design.md`
2. `Odoo19物流留痕系统运单主对象与留痕主流程设计.md`
3. `docs/architecture/ARCHITECTURE.md`
4. `docs/architecture/custom_addons_blueprint.md`

---

## 4. 本文档保留的唯一价值

本文档现在保留的价值只有两点：

1. 作为历史命名的跳转入口
2. 帮助后续阅读旧 change note 或旧评审记录时理解“为什么 `logistics_trace` 被拆成 core / evidence 两层”

除此之外，本文档不再承担现行设计职责。
