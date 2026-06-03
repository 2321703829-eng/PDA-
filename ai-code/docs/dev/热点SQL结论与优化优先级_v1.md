# 热点 SQL 结论与优化优先级 v1

## 1. 目标

基于首轮真实 SQL 抓取结果，先回答 4 个问题：

1. 当前热点查询主要集中在哪几类接口
2. 风险点更偏 SQL 本身，还是 Python 侧聚合
3. 哪些问题应优先进入优化排期
4. 下一轮应该先补哪些验证动作

本稿仅覆盖首轮调查对象：

- `/api/admin/logistics/dashboard/summary`
- `/api/admin/logistics/boss_trace/summary`
- 统计中心接口

## 2. 调查边界

- 调查环境：`192.168.0.17:19069`
- Odoo：`19.0`
- 数据库：`odoo_logistics_webtest_v19`
- 调查方式：在 Odoo shell 中直调服务方法，并对 `Cursor.execute` 做一次性 SQL 捕获
- 本轮重点：先看查询形态、查询次数、聚合方式，不直接下最终并发承载结论

## 3. 总体结论

首轮结果已经足够支持一个明确判断：

- `dashboard/summary`：中风险
- `boss_trace/summary`：低到中风险
- `统计中心接口`：高风险，优先级最高

当前最值得关注的问题，不是“单条 SQL 特别慢”，而是：

1. 首页/看板存在多次 `search`、`search_count`
2. 统计中心采用“日期范围全量查询 + Python 内存聚合”模式
3. 一旦数据量放大或并发升高，统计中心比导入结果页、导出结果页更可能先成为瓶颈

## 4. 首轮抓取结果

### 4.1 Dashboard Summary

- SQL 总数：`15`
- 唯一 SQL 数：`13`
- 主要业务表：`logistics_trace_exception`
- 主要模式：
  - `state in (...)` 异常列表
  - `exception_type = evidence_missing`
  - 今日新增异常
  - 高风险批次异常
  - Priority Top5
  - Recent Top5

代码位置：

- [logistics_dashboard_service.py](/D:/Desktop/Odoo/custom_addons/logistics_web/models/logistics_dashboard_service.py:15)

结论：

- 这条接口 SQL 数量不算重
- 但存在多次 `search(...)` 后再 `len()/mapped()` 的 Python 侧聚合
- 如果异常量明显上升，这类“多次取数 + Python 汇总”会先放大 CPU 和内存压力

### 4.2 Boss Trace Summary

- SQL 总数：`6`
- 唯一 SQL 数：`6`
- 主要业务表：`logistics_trace_exception`
- 主要模式：
  - 多条 `COUNT(*)`
  - 一条高风险批次异常列表
  - 一条老板关注异常 Top6

代码位置：

- [logistics_dashboard_service.py](/D:/Desktop/Odoo/custom_addons/logistics_web/models/logistics_dashboard_service.py:105)

结论：

- 这是本轮最轻的一组接口
- 核心统计基本都落在数据库 `COUNT(*)`
- 真正的潜在风险点不是计数，而是：
  - 高风险批次这条 `search(...).mapped("batch_id.id")`
  - 随数据量增大后会把更多记录拉到 Python 侧再去重

### 4.3 统计中心接口

抓取对象：

- `overview`
- `trends`
- `distributions`
- `rankings`

代码位置：

- [logistics_stats_service.py](/D:/Desktop/Odoo/custom_addons/logistics_web/models/logistics_stats_service.py:18)

首轮结果：

- `stats_overview`：`11` 条 SQL，`9` 条唯一 SQL
- `stats_trends`：`2` 条 SQL
- `stats_distributions`：`2` 条 SQL
- `stats_rankings`：`2` 条 SQL

核心 SQL 实际只有两类：

1. 拉取时间范围内全部 `waybill`
2. 拉取时间范围内全部 `exception`

对应代码：

- [_get_stats_waybills](/D:/Desktop/Odoo/custom_addons/logistics_web/models/logistics_stats_service.py:182)
- [_get_stats_exceptions](/D:/Desktop/Odoo/custom_addons/logistics_web/models/logistics_stats_service.py:193)

然后后续趋势、分布、排行全部在 Python 里做：

- `filtered`
- bucket 切分
- region/group 分组
- rate 计算
- ranking 计算

结论：

- 统计中心当前的主要风险不是 SQL 条数多
- 而是“SQL 少，但每次请求都整批取数，再在 Python 里做统计”
- 这是典型的高并发隐患模式

## 5. 热点 SQL 风险归类

### P0：统计中心全量取数

风险表现：

- 时间范围一放大，单请求读取对象数线性增长
- 并发一上来，同一批记录会被多个请求重复拉取
- 数据库压力和 Python worker 压力会一起升高

归类：

- `Python 内存聚合过重`
- `查询模型不利于高并发统计`

优先级：`P0`

### P1：Dashboard Summary 多次 search

风险表现：

- 单次请求存在多次相似 domain 查询
- 每次都要回表拿 ID，再做 Python 统计/映射

归类：

- `ORM 查询次数偏多`
- `部分统计在 Python 侧完成`

优先级：`P1`

### P1：Boss Trace 高风险批次去重路径

风险表现：

- 高风险批次统计不是纯数据库聚合
- 先查异常记录，再 `mapped("batch_id.id")` 去重

归类：

- `Python 聚合替代数据库聚合`

优先级：`P1`

### P2：权限与元数据查询

风险表现：

- 首次调用时会出现一些 `res_groups`、`ir_model_data`、`res_users`、`res_partner` 查询
- 这部分不是业务主瓶颈

归类：

- `首次会话/权限预热成本`

优先级：`P2`

## 6. 优化优先级建议

### 第一优先级：统计中心

建议先动：

1. 把趋势、分布、排行从“全量 search + Python 计算”改成：
   - `read_group`
   - 聚合 SQL
   - 或预聚合表
2. 对常用统计口径做可复用的数据访问层，而不是每个统计方法各自遍历 recordset
3. 重点验证以下字段的索引命中：
   - `logistics_dispatch_waybill.delivery_date`
   - `logistics_dispatch_waybill.state`
   - `logistics_trace_exception.report_time`
   - `logistics_trace_exception.state`

### 第二优先级：Dashboard Summary

建议先动：

1. 把可直接数据库计数的口径改成 `search_count` 或聚合查询
2. 把“高风险批次数量”改成数据库端去重统计
3. 评估是否把首页摘要合并成更少的查询批次

### 第三优先级：Boss Trace Summary

建议先动：

1. 保持现有 `COUNT(*)` 路线
2. 只针对“高风险批次数”这条改成数据库端聚合/去重
3. 暂不把它作为第一批重构对象

## 7. 下一轮验证建议

首轮已经完成“热点识别”，第二轮建议直接进入：

1. 对统计中心两条核心 SQL 做 `EXPLAIN ANALYZE`
2. 用接近真实量级的数据，单独压：
   - 统计中心 `overview`
   - 统计中心 `trends`
   - `dashboard/summary`
3. 记录：
   - P50 / P95 / P99
   - PostgreSQL CPU
   - Odoo worker CPU
   - 返回对象数量

## 8. 当前结论

当前项目代码已经足够支撑性能调查，并且首轮方向已经比较明确：

- 首页和老板页不是“没有风险”，但优先级低于统计中心
- 统计中心是当前最明确的查询承载风险点
- 后续优化应优先针对：
  - 数据访问模式
  - 聚合位置
  - 索引命中

一句话总结：

**当前首轮 SQL 结果已经足够支持排期：先查和先优化统计中心，再回头压首页摘要和老板页摘要。**
