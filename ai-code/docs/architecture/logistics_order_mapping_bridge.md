# logistics_order Mapping Bridge

适用范围：
- `ai-code/docs/architecture/` 下的历史命名桥接文档
- 用于解释旧的 `logistics_order` / `logistics.order` 命名，在当前体系中应如何理解

优先基准：
- `ai-code/docs/context/Odoo19物流留痕系统运单主对象与留痕主流程设计.md`
- `ai-code/docs/architecture/logistics_dispatch_addon_design.md`
- `ai-code/docs/architecture/ARCHITECTURE.md`
- `ai-code/docs/context/odoo_logistics_context.md`

---

## 1. 文档定位

这份文档不再承担现行模型映射设计稿的职责。

它现在的唯一职责是做一件事：

**把旧阶段出现过的 `logistics_order` 命名，桥接到当前已经稳定下来的 `dispatch / waybill` 语义上。**

也就是说，如果后续你在历史文档、旧草图、旧评审记录里继续看到：

- `logistics_order`
- `logistics.order`
- “订单主对象”
- “订单快照层”

都不应直接按字面理解成“订单中心设计”，而要先回到当前主线再解释。

---

## 2. 当前真正有效的主线

当前系统主线已经明确为：

```text
波次记录 -> 批次 -> 运单号 -> 运单下订单列表 -> 留痕事件 -> 证据图片/备注 -> 异常对象
```

其中：

- 波次：调度组织层对象
- 批次：执行组织层对象
- 运单：现场追溯主对象
- 运单下订单列表：业务明细层
- 留痕：事实层
- 证据：材料层
- 异常：问题与处理层

最关键的一句话是：

**运单是追溯主对象，订单只是运单下明细。**

---

## 3. 为什么会出现 `logistics_order` 旧命名

`logistics_order` 这组命名来自更早阶段的理解。

当时的设计还处在从“订单留痕系统”向“运单主对象系统”过渡的阶段，因此文档里会出现下面这些中间状态：

- 文件名仍叫 `logistics_order`
- 模型名可能还沿用 `logistics.order`
- 但正文已经开始把它解释成运单主对象的兼容命名

这类文档在当时有过渡价值，但现在不能再直接当成正式基线使用。

---

## 4. 当前应如何重解释旧命名

如果后续在历史资料里看到：

### 4.1 `logistics_order` 模块

当前应重解释为：
- 历史阶段的执行主线模块命名
- 当前已由 `logistics_dispatch` 取代

### 4.2 `logistics.order` 模型

当前应重解释为：
- 历史阶段对“运单主对象快照层”的兼容命名
- 当前更准确的正式语义应是：
  - `logistics.dispatch.waybill`

### 4.3 “订单主对象”说法

当前应重解释为：
- 旧阶段误把订单放在追溯主对象位置的表述
- 在现行设计里，这种说法已经失效

---

## 5. 当前正式替代文档

如果要继续看现行设计，请不要再以本文件为主，而应优先阅读：

1. `docs/architecture/logistics_dispatch_addon_design.md`
2. `docs/architecture/ARCHITECTURE.md`
3. `docs/context/odoo_logistics_context.md`
4. `docs/context/Odoo19物流留痕系统运单主对象与留痕主流程设计.md`

这几份文档已经把真正有效的执行主线收口到了：

- `logistics_dispatch`
- `wave / batch / waybill / waybill_order_line`

---

## 6. 本文档现在保留的价值

这份文档现在保留的价值只剩两点：

1. 帮助阅读历史文档时做命名翻译
2. 帮助解释为什么旧的 `order` 命名后来要回调到 `dispatch / waybill`

除此之外，它不再承担：

- 当前模型映射设计稿
- 当前 addon 设计入口
- 当前前后端字段基线

---

## 7. 当前结论

`logistics_order_mapping_bridge.md` 现在应被理解为：

**一份历史命名桥接文档，而不是现行设计文档。**

后续凡是进入正式设计、字段设计、页面设计、模块设计，都应直接转向：

- `logistics_dispatch`
- `logistics_trace_core`
- `logistics_trace_exception`

而不是继续围绕 `logistics_order` 展开。

