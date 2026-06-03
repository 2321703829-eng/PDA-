# docs/architecture

`docs/architecture/` 是系统架构与模块设计的正式入口。

## 建议阅读顺序

1. [ARCHITECTURE.md](./ARCHITECTURE.md)
2. [custom_addons_blueprint.md](./custom_addons_blueprint.md)
3. 现行模块设计
4. 主体系与专题体系边界
5. 前端承载与代码目录补充
6. 历史桥接稿

## 现行模块设计

- [logistics_base_addon_design.md](./logistics_base_addon_design.md)
- [logistics_dispatch_addon_design.md](./logistics_dispatch_addon_design.md)
- [logistics_trace_core_addon_design.md](./logistics_trace_core_addon_design.md)
- [logistics_trace_exception_addon_design.md](./logistics_trace_exception_addon_design.md)
- [logistics_trace_evidence_addon_design.md](./logistics_trace_evidence_addon_design.md)
- [logistics_web_addon_design.md](./logistics_web_addon_design.md)

## 状态标识规则

- `现行`：当前默认应阅读、应维护、可作为正式决策入口的文档。
- `bridge`：旧命名或旧边界的桥接稿，只用于帮助重解释历史资料，不再承担现行设计职责。
- `archive`：历史留痕、旧草图、旧方案或来源资料，只保留追溯价值。
- 如需快速区分入口，可先看 [history_and_bridge_index.md](./history_and_bridge_index.md)。

## 主体系与专题体系边界

### 主体系

以下内容属于当前正式主体系，优先在 `docs/` 下维护：

- 业务总基线、主对象、主流程与 Odoo 复用判断
- 系统架构、模块边界、现行 addon 职责划分
- 升级验证、实施 runbook 和结构治理规则

### 专题体系

以下内容优先在 `专题设计/` 下的专题包中维护：

- 前端阶段化设计与页面方案
- 仓管设计的专题方案、状态规则和落地清单
- 企业隔离设计的分期方案和平台级专题研究
- 高并发优化设计的查询风险、热点 SQL 与性能优化方案

### 默认判断

- 如果会改变项目主线、模块边界或正式系统职责，先更新 `docs/context/`、`docs/architecture/` 或 `docs/dev/`。
- 如果只是某个专题的专项设计、专项方案或专项验证，先更新对应专题设计包。
- 如果专题结论已经正式上升为系统基线，再把关键结论回灌到 `docs/` 主体系。

### 当前统一专题根目录

专题设计包当前统一归并到：

- `专题设计/前端设计/`
- `专题设计/仓管设计/`
- `专题设计/企业隔离设计/`
- `专题设计/高并发优化设计/`

## 补充设计

- [前端代码目录规划.md](./前端代码目录规划.md)
- [custom_addons_blueprint.md](./custom_addons_blueprint.md)

## 来源资料

- [source_materials/README.md](./source_materials/README.md)
  系统级架构与数据库来源资料入口。

## 历史桥接稿

以下文档仍可用于追溯旧命名或旧边界，但不应再作为当前主设计入口：

- [logistics_order_addon_design_bridge.md](./logistics_order_addon_design_bridge.md)
- [logistics_trace_addon_design_bridge.md](./logistics_trace_addon_design_bridge.md)
- [logistics_exception_addon_design_bridge.md](./logistics_exception_addon_design_bridge.md)
- [logistics_order_mapping_bridge.md](./logistics_order_mapping_bridge.md)
- [logistics_trace_mapping_bridge.md](./logistics_trace_mapping_bridge.md)



