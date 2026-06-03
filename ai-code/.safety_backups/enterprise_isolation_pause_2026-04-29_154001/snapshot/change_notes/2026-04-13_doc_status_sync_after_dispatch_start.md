# 2026-04-13 文档状态同步与过期判断回扫

## 变更背景

在 `logistics_dispatch` 真实模块骨架开始落地后，`ai-code` 中一批“状态型文档”出现了与当前现实不完全一致的问题。

问题主要集中在：

- 仍把项目描述成“只有设计，没有实现起点”
- 仍把 `custom_addons` 现状写成只有旧占位目录
- 仍把部分模板或计划文档停留在旧阶段判断

## 本次更新范围

- `docs/review/过期文档处理清单_2026-04-13.md`
- `templates/odoo_addon_template/README.md`
- `docs/context/odoo_logistics_context.md`
- `docs/context/odoo_logistics_feasibility.md`
- `docs/architecture/ARCHITECTURE.md`
- `docs/architecture/custom_addons_blueprint.md`
- `docs/dev/upgrade_and_verify.md`
- `前端相关设计/00_导航与总纲/缺失和优化总览.md`
- `前端相关设计/00_导航与总纲/前端设计新工作计划安排.md`

## 本次更新结果

### 1. 过期清单重新收口

- 不再把已经回调完成的核心上下文文档误判为过期
- 将当前重点改为“状态同步”，而不是“继续大面积重写核心文档”

### 2. 当前仓库现状说明更新

- 明确 `custom_addons/logistics_dispatch` 已是当前真实实现起点之一
- 保留 `logistics_order / logistics_trace / logistics_exception` 为历史过渡目录的说明

### 3. 前端总纲判断更新

- 不再把前端资料描述成“只能做设计准备”
- 明确当前已经进入“设计可用 + 开发可启动 + 代码已起步”的状态

### 4. 模板与升级说明更新

- 模板 README 改为以 `logistics_dispatch / logistics_trace_core / logistics_trace_exception` 为现行命名口径
- 升级命令示例改到当前有效模块

## 当前结论

截至本次同步后：

- `ai-code` 中的大部分核心文档已与当前状态基本一致
- 仍需继续留意的，不再是“大方向过期”，而是后续实现推进后的状态漂移
