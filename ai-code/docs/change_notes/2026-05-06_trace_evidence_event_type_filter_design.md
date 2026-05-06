# 2026-05-06 证据页面按留痕事件类型筛选与展示拆分设计说明

## 本次新增

- 新增证据页面筛选设计文档：
  - `docs/architecture/trace_evidence_event_type_filter_design.md`

## 核心内容

- 明确“留痕事件展示字段”和“留痕事件筛选字段”分离
- 建议引入三层字段：
  - `trace_event_type`
  - `trace_event_time`
  - `trace_event_display_name`
- 本轮正式采用拆开版方案：
  - 搜索区新增“留痕事件类型”
  - 列表拆分为“留痕事件类型 + 留痕时间”
  - 后端按 `trace_event_type` 正式过滤
- 补充历史数据兼容与后续增强路线
