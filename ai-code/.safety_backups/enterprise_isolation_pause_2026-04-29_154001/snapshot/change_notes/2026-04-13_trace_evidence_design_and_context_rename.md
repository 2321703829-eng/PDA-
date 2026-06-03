# 2026-04-13 trace_evidence 正式设计稿与 context 命名升级

## 本次变更

本次同时完成了 3 类文档收口：

1. 补充证据层独立正式设计稿
2. 将执行 / 追溯上下文文档从 `draft` 命名升级为现行主入口
3. 同步相关状态型文档与阅读入口

## 1. 新增正式设计稿

新增：

- `docs/architecture/logistics_trace_evidence_addon_design.md`

当前定位：

- 证据层独立正式设计稿
- 明确证据对象、留痕事件挂接关系、图片服务边界、页面建议、聚合字段来源与约束

## 2. draft 命名升级

新增主入口：

- `docs/context/odoo_logistics_execution_trace_context.md`

处理方式：

- 将执行主线与追溯主线的中间上下文内容提升到新文件
- 原 `docs/context/odoo_logistics_order_trace_exception_draft.md` 保留为兼容旧引用的历史别名入口
- 当前不再将旧 `draft` 文件作为主入口维护

说明：

- `docs/context/odoo_logistics_master_data_draft.md` 本次未做命名升级
- 原因是该文档仍然只承载方向性弱假设，当前 `draft` 命名仍有保留必要

## 3. 同步更新的状态型文档

已同步：

- `docs/context/odoo_logistics_context.md`
- `docs/review/过期文档处理清单_2026-04-13.md`
- `docs/review/当前可默认跳过的文件清单.md`
- `docs/architecture/logistics_trace_mapping.md`
- `docs/architecture/logistics_web_addon_design.md`

同步内容包括：

- 将 `logistics_trace_evidence` 纳入现行有效入口
- 将 `odoo_logistics_execution_trace_context.md` 纳入阅读口径
- 将 `odoo_logistics_master_data_draft.md` 明确归入“待确认草图”
- 将 `logistics_web` 中“未来 evidence”表述收平

## 变更目的

- 让证据层拥有独立正式设计入口
- 减少 `draft` 命名继续占据主入口造成的误读
- 让当前阅读顺序、跳过清单、过期清单与真实文档结构保持一致

## 验证

- 已检查 `logistics_trace_evidence_addon_design.md` 已创建
- 已检查 `odoo_logistics_execution_trace_context.md` 已创建
- 已检查旧 `draft` 文件已补充跳转说明
- 已检查过期清单、跳过清单、项目上下文入口已同步更新
