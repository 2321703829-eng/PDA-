# 2026-04-27 High Concurrency Query Optimization Plan v1 Added

## 本次变更

- 新增高并发查询优化方案文档：
  - `docs/dev/高并发查询优化方案_v1.md`

## 文档内容

- 按 `短期止血 / 中期重构 / 长期架构` 拆解当前高并发查询风险的解决路径
- 覆盖对象：
  - `/api/admin/logistics/dashboard/summary`
  - `/api/admin/logistics/boss_trace/summary`
  - 统计中心接口
- 输出每类问题的：
  - 风险来源
  - 解决方式
  - 难度评估
  - 推荐实施顺序

## 结论摘要

- 首页和老板页问题相对容易先优化
- 统计中心是当前最值得优先优化的查询热点
- 首轮建议先做：
  - `search + len` 清理
  - Python 去重改数据库去重
  - 核心索引核查与补齐
- 中期重点：
  - 将统计中心从“全量 search + Python 聚合”改为数据库聚合模式
- 长期再根据压测结果决定是否引入：
  - 预聚合表
  - 统计快照
  - 缓存层
