# 2026-04-13 logistics_trace_mapping 回调为历史桥接文档

## 本次变更

本次将 `docs/architecture/logistics_trace_mapping.md` 从“部分过期的映射稿”回调为“历史桥接文档”。

具体调整：

- 在文档顶部补充状态说明
- 明确当前不再以 `logistics_trace` 单模块同时承接留痕事件与证据图片
- 明确当前主结构已回调为：
  - `logistics_trace_core`
  - `logistics_trace_evidence`
  - `logistics_trace_exception`
- 明确当前应将旧命名：
  - `logistics.trace`
  - `logistics.trace.image`
  分别桥接到：
  - `logistics.trace.event`
  - `logistics.trace.evidence`
- 新增“当前桥接结论”“当前替代文档”“保留方式”三段说明
- 将文末结论改写为“旧阶段映射结论（历史保留）”

同时同步更新：

- `docs/review/过期文档处理清单_2026-04-13.md`
  - 将该文档移出“部分过期”列表
  - 将该文档纳入“历史桥接文档”
- `docs/review/当前可默认跳过的文件清单.md`
  - 将该文档纳入“历史桥接型文档”典型文件

## 变更目的

- 避免后续继续把旧的组合映射稿当成当前正式设计稿
- 保留旧命名与旧字段语义的解释入口
- 让当前实现入口稳定落到 `trace_core / evidence / exception` 分层口径

## 验证

- 已检查文档顶部状态说明
- 已检查文档中已明确当前主结构与替代文档
- 已检查过期清单中该文档不再位于“部分过期”列表
- 已检查跳过清单中已纳入历史桥接型文档
