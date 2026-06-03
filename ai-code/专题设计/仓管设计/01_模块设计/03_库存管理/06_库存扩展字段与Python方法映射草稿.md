# 库存扩展字段与Python方法映射草稿 v0.1

## 版本信息

- 文档名称：库存扩展字段与Python方法映射草稿
- 当前版本：`v0.1`
- 当前阶段：可评审初稿版
- 所属专题：仓管模块 / 模块设计 / 库存管理
- 当前用途：
  - 将库存专题中的页面字段、搜索视图、Smart Button 继续下沉为 Python 字段与方法映射清单
  - 为 `stock.quant / stock.location / stock.warehouse` 的扩展字段、计算字段和按钮方法提供模型层参考
  - 为后续 `models/*.py` 实现、字段归属和方法拆分提供统一起点

## 目录索引

- `1. 文档定位`
- `2. 范围与边界`
- `3. 当前统一目标`
- `4. 模块归属与文件建议`
- `5. stock.quant 字段与方法映射`
- `6. stock.location 字段与方法映射`
- `7. stock.warehouse 字段与方法映射`
- `8. Smart Button 返回动作方法约定`
- `9. 计算字段、搜索字段与依赖建议`
- `10. 实施顺序与验证点`
- `11. 当前建议联读专题`

## 章节总览

这份稿子当前主要解决 4 个问题：

1. XML 草稿里已经引用的库存扩展字段，后续应该落到哪个模型文件
2. Smart Button 对应的 Python 方法应该挂在哪个模型上，职责怎么分
3. 计算字段、衍生字段、搜索字段在模型层应如何分层
4. `logistics_wms_base` 和 `logistics_wms_inventory` 之间，哪些对象更适合归在哪个模块

建议阅读顺序：

1. 先看 `1` 到 `4`，明确这份稿的职责和模块归属基线
2. 再看 `5` 到 `7`，按对象查看字段与方法映射
3. 最后看 `8` 到 `11`，明确动作返回、依赖建议和实施顺序

## 1. 文档定位

本文件重点回答“库存专题需要补哪些 Python 字段和方法”，不直接替代真实代码实现。

它的作用是：

- 把 `05_库存search view与Smart Button XML草稿.md` 再往服务端层推进一层
- 把 XML 中已经出现的字段和按钮名，对应到建议的模型文件和方法职责
- 降低后续实现时“XML 写好了，但模型字段和方法无处安放”的返工

当前更推荐把这份稿理解成：

`库存专题中负责“字段挂在哪、方法写在哪、模块怎么分”的模型层实现前草稿。`

## 2. 范围与边界

### 2.1 当前纳入范围

- `stock.quant` 的扩展字段、计算字段、按钮方法建议
- `stock.location` 的扩展字段、计算字段、按钮方法建议
- `stock.warehouse` 的扩展字段、计算字段、按钮方法建议
- Smart Button 返回动作方法的统一命名与职责建议
- 建议模块归属和建议模型文件归属

### 2.2 当前不纳入范围

- 真实 Python 代码实现
- 真实 SQL 索引与性能优化细节
- 完整权限校验实现
- 目标页如批次、运单、异常页的服务端方法实现细节

### 2.3 一句话边界

`本稿先解决“字段和方法放哪、做什么”，不直接解决“最终代码怎么写到生产级”。`

## 3. 当前统一目标

当前更推荐通过本稿先收住下面 6 件事：

1. 固定库存专题新增字段与方法的模型层归属
2. 固定衍生字段、摘要字段和动作方法的命名方向
3. 固定 `stock.quant` 为第一优先扩展对象
4. 避免把页面摘要逻辑散落到多个无边界的 helper 文件里
5. 让 XML 草稿、字段清单和模型方法命名保持一致
6. 让后续实现时可以按对象逐个回填，而不是边写 XML 边猜模型层设计

当前更推荐的模型层原则是：

`主数据扩展放 base，库存专题视图与动作增强放 inventory，能 related 就不重复造真相，能 compute 就不额外存副本。`

## 4. 模块归属与文件建议

### 4.1 当前推荐的模块归属

根据当前数据库设计规范稿的方向，当前更推荐：

- `stock.warehouse` 扩展优先归在 `logistics_wms_base`
- `stock.location` 扩展优先归在 `logistics_wms_base`
- `stock.quant` 的库存专题增强优先归在 `logistics_wms_inventory`

### 4.2 当前推荐的模型文件

| 对象 | 当前建议模块 | 当前建议文件 | 当前说明 |
|---|---|---|---|
| `stock.quant` | `logistics_wms_inventory` | `models/inventory/wms_inventory_quant.py` | 库存专题的数量摘要、追溯摘要、按钮方法集中落位 |
| `stock.location` | `logistics_wms_base` | `models/masterdata/wms_location.py` | 货位主数据扩展与仓内位置摘要字段落位 |
| `stock.warehouse` | `logistics_wms_base` | `models/masterdata/wms_warehouse.py` | 仓级汇总摘要字段与仓级入口方法落位 |

### 4.3 当前推荐的拆分类别

当前更推荐字段与方法按下面三类理解：

1. 结构字段
   - `related`
   - `many2one`
   - `char`

2. 摘要字段
   - `compute`
   - `store=False` 优先

3. 动作方法
   - `action_open_*`
   - 返回 `ir.actions.act_window`

### 4.4 一句话收口

`仓库和货位继续算主数据扩展，quant 作为库存专题主结果页对象，单独承接页面摘要和反查动作最顺。`

## 5. stock.quant 字段与方法映射

### 5.1 当前推荐的模型定位

`stock.quant` 当前更推荐承接：

- 库存结果页的数量摘要字段
- 库存结果页的追溯摘要字段
- 库存结果页的 Smart Button 动作方法

### 5.2 当前建议字段映射表

| 字段名建议 | 类型建议 | 当前用途 | 当前来源建议 | 是否建议存储 |
|---|---|---|---|---|
| `warehouse_id` | `many2one` 或 `related` | 列表页仓库列、group by 仓库 | 从 `location_id` 映射仓库归属 | 建议 `store=True` 如实现稳定 |
| `owner_id` | `many2one` 或 `related` | 列表页货主列 | 结合货主归属字段映射 | 视实际底座字段而定 |
| `available_quantity` | `float` compute | 可用量 | `quantity - reserved_quantity - frozen_quantity` | 建议 `store=False` 起步 |
| `reserved_quantity` | `float` related / compute | 占用量 | 对齐原生预留口径 | 优先复用原生或轻量 compute |
| `frozen_quantity` | `float` compute | 冻结量 | 位置限制 + 异常限制 + 人工锁定规则 | 建议 `store=False` 起步 |
| `latest_lot_display` | `char` compute | 最近关联批次摘要 | 从关联批次集合取最近或主关联项 | 建议 `store=False` |
| `latest_waybill_display` | `char` compute | 最近关联运单摘要 | 从关联运单集合取最近或主关联项 | 建议 `store=False` |
| `latest_trace_time` | `datetime` compute | 留痕摘要 | 从最近留痕对象聚合 | 建议 `store=False` |
| `has_open_exception` | `boolean` compute | 异常关注标记 | 从未闭环异常集合判断 | 建议 `store=False` |
| `related_document_count` | `integer` compute | 相关主单数 | 入库 / 出库 / 盘点 / 移位集合聚合 | 建议 `store=False` |
| `related_lot_count` | `integer` compute | 相关批次数 | 关联批次集合聚合 | 建议 `store=False` |
| `related_waybill_count` | `integer` compute | 相关运单数 | 关联运单集合聚合 | 建议 `store=False` |

### 5.3 当前建议方法映射表

| 方法名建议 | 当前职责 | 当前返回建议 | 当前说明 |
|---|---|---|---|
| `action_open_related_lots` | 打开相关批次 | `act_window + domain` | 第一优先追溯入口 |
| `action_open_related_waybills` | 打开相关运单 | `act_window + domain + search_default_*` | 第二优先追溯入口 |
| `action_open_related_documents` | 打开相关主单 | `act_window + domain + context` | 第一优先业务解释入口 |
| `action_open_related_trace` | 打开追溯入口页 | `act_window + context` | 深读入口 |
| `action_open_related_exceptions` | 打开相关异常 | `act_window + context` | 异常入口 |

### 5.4 当前建议的内部辅助方法

当前更推荐把对外动作方法背后的聚合逻辑收口到少量辅助方法，例如：

- `_get_related_lot_ids`
- `_get_related_waybill_ids`
- `_get_related_document_domain`
- `_get_latest_trace_info`
- `_get_open_exception_domain`

### 5.5 当前推荐的一句话原则

`quant 上的方法优先负责“收口目标对象范围并返回动作”，不要把复杂业务处理逻辑硬塞进按钮方法里。`

## 6. stock.location 字段与方法映射

### 6.1 当前推荐的模型定位

`stock.location` 当前更推荐承接：

- 货位页的汇总摘要字段
- 仓内位置反查入口
- 货位到批次 / 运单 / 主单的动作方法

### 6.2 当前建议字段映射表

| 字段名建议 | 类型建议 | 当前用途 | 当前来源建议 | 是否建议存储 |
|---|---|---|---|---|
| `warehouse_id` | `many2one` | 所属仓库 | 主数据扩展字段 | 建议 `store=True` |
| `current_batch_count` | `integer` compute | 当前批次数 | 货位下关联批次聚合 | 建议 `store=False` 起步 |
| `current_waybill_count` | `integer` compute | 当前运单数 | 货位下关联运单聚合 | 建议 `store=False` |
| `exception_waybill_count` | `integer` compute | 异常运单数 | 货位下异常运单聚合 | 建议 `store=False` |
| `latest_trace_time` | `datetime` compute | 最近留痕时间 | 货位关联追溯对象聚合 | 建议 `store=False` |
| `current_quant_count` | `integer` compute | 当前库存记录数 | 货位下 quant 聚合 | 建议 `store=False` |

### 6.3 当前建议方法映射表

| 方法名建议 | 当前职责 | 当前返回建议 | 当前说明 |
|---|---|---|---|
| `action_open_related_lots` | 打开当前货位关联批次 | `act_window + domain + search_default_*` | 第一优先位置反查入口 |
| `action_open_related_waybills` | 打开当前货位关联运单 | `act_window + domain + search_default_*` | 第二优先履约入口 |
| `action_open_related_documents` | 打开当前货位关联主单 | `act_window + domain + context` | 最近动作入口 |

### 6.4 当前推荐的一句话原则

`location 上更适合放位置级汇总和入口方法，不适合承接复杂库存事实运算。`

## 7. stock.warehouse 字段与方法映射

### 7.1 当前推荐的模型定位

`stock.warehouse` 当前更推荐承接：

- 仓级汇总摘要字段
- 仓级入口方法
- 仓级活动与异常概览字段

### 7.2 当前建议字段映射表

| 字段名建议 | 类型建议 | 当前用途 | 当前来源建议 | 是否建议存储 |
|---|---|---|---|---|
| `current_batch_count` | `integer` compute | 当前批次数 | 当前仓关联批次聚合 | 建议 `store=False` |
| `current_waybill_count` | `integer` compute | 当前运单数 | 当前仓关联运单聚合 | 建议 `store=False` |
| `current_exception_count` | `integer` compute | 当前异常数 | 当前仓未闭环异常聚合 | 建议 `store=False` |
| `today_operation_count` | `integer` compute | 今日作业数 | 当日仓侧作业对象聚合 | 建议 `store=False` |
| `latest_trace_time` | `datetime` compute | 最近留痕时间 | 当前仓关联留痕对象聚合 | 建议 `store=False` |
| `current_location_count` | `integer` compute | 当前货位数摘要 | 当前仓货位聚合 | 建议 `store=False` |

### 7.3 当前建议方法映射表

| 方法名建议 | 当前职责 | 当前返回建议 | 当前说明 |
|---|---|---|---|
| `action_open_current_lots` | 打开当前仓关联批次 | `act_window + domain` | 仓级汇总入口 |
| `action_open_current_waybills` | 打开当前仓关联运单 | `act_window + domain + search_default_*` | 仓级履约入口 |
| `action_open_current_exceptions` | 打开当前仓异常 | `act_window + context` | 仓级异常入口 |
| `action_open_current_locations` | 打开当前仓货位 | `act_window + domain` | 仓级位置入口 |

### 7.4 当前推荐的一句话原则

`warehouse 上的方法只做汇总入口，不做深读，不做复杂追责。`

## 8. Smart Button 返回动作方法约定

### 8.1 当前推荐的统一返回结构

当前更推荐所有 Smart Button 方法统一返回 `ir.actions.act_window`，并尽量包含：

- `name`
- `type`
- `res_model`
- `view_mode`
- `domain`
- `context`

### 8.2 当前建议保留的上下文字段

当前更推荐沿用前面 XML 草稿与反查稿中的上下文字段：

- `default_source_model`
- `default_source_id`
- `default_source_name`
- `search_default_warehouse_id`
- `search_default_location_id`
- `search_default_product_id`
- `search_default_lot_id`
- `search_default_has_open_exception`

### 8.3 当前建议的职责边界

当前更推荐：

- 按钮方法只负责组装目标对象范围和动作上下文
- 目标页内部阅读逻辑继续由目标页负责
- 不在库存按钮方法里承接复杂业务判定或重处理逻辑

### 8.4 一句话收口

`Smart Button 方法应是“路由装配器”，而不是“业务处理器”。`

## 9. 计算字段、搜索字段与依赖建议

### 9.1 当前推荐的依赖方向

当前更推荐：

- 数量类字段依赖 quant 与预留关系
- 位置类字段依赖 location 与 warehouse 关系
- 留痕与异常摘要字段依赖追溯对象聚合

### 9.2 当前推荐的字段分层

当前更推荐把字段分成三层：

1. 原生或 related 字段
   - 如 `warehouse_id`
   - 优先稳定、可索引、可分组

2. 页面摘要字段
   - 如 `latest_waybill_display`
   - 优先 `store=False`

3. 风险与提示字段
   - 如 `has_open_exception`
   - 优先轻量布尔或整数摘要

### 9.3 当前不建议的一期做法

当前不建议：

- 为了页面展示把所有摘要字段都做成 `store=True`
- 为了 group by 需求强行存储大量高频变化的追溯摘要字段
- 在多个模型上重复维护同一份统计真相

### 9.4 一句话收口

`一期优先保证字段语义正确和页面可用，性能优化与存储策略后续再按真实数据量细化。`

## 10. 实施顺序与验证点

### 10.1 当前推荐的实施顺序

当前更推荐按下面顺序推进：

1. `stock.quant`
   - 字段定义
   - 计算字段
   - 动作方法

2. `stock.location`
   - 汇总字段
   - 入口方法

3. `stock.warehouse`
   - 汇总字段
   - 入口方法

### 10.2 当前需要重点验证

需要验证：

- XML 草稿里引用的字段在模型层是否已全部补齐
- Smart Button 对应的方法是否已存在且返回结构统一
- `store=False` 摘要字段是否足以满足当前页面读取需要
- 仓级与货位页的方法是否没有越界承担深读职责

### 10.3 一句话收口

`这份映射稿的目标不是替代代码，而是让后面的代码实现少走错路。`

## 11. 当前建议联读专题

- `01_模块设计/03_库存管理/00_库存管理专题总稿.md`
- `01_模块设计/03_库存管理/02_库存反查与追溯入口设计草稿.md`
- `01_模块设计/03_库存管理/03_库存页面结构与查询规范草稿.md`
- `01_模块设计/03_库存管理/04_库存页面字段映射与视图落地清单草稿.md`
- `01_模块设计/03_库存管理/05_库存search view与Smart Button XML草稿.md`
- `01_模块设计/03_库存管理/07_库存模块开发任务拆分清单草稿.md`
- `01_模块设计/03_库存管理/08_库存专题联调与验收草稿.md`
- `02_跨模块规范/04_接口与数据/01_数据库设计规范草稿.md`
