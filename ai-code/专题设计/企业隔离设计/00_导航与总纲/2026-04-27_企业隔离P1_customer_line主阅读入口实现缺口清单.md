# 2026-04-27 企业隔离 `P1` `customer_line` 主阅读入口实现缺口清单

## 状态说明

- 本文承接的是“`customer_line` 作为 `P1` 主阅读入口”的旧讨论前提。
- 2026-04-27 已确认当前业务按“一运单一门店”强约束收口后，本文不再作为当前 `P1` 的现行实现目标清单。
- 本文继续保留，作为历史讨论和未来如需恢复多门店节点阅读层时的参考材料。
- 当前现行口径请优先阅读：
  - `2026-04-27_企业隔离P1_一运单一门店口径调整说明.md`
  - `企业隔离方案可行性与分期落地调整说明.md`

## 1. 文档定位

- 本文承接 `2026-04-27_企业隔离P1_customer_line主阅读入口必要性说明.md`。
- 本文不再解释“为什么重要”，而是直接回答：
  - 要让 `customer_line` 真正成为图片、留痕、异常的主阅读入口，还缺哪些具体实现点
  - 这些实现点分别属于哪一层
  - 哪些应优先做，哪些可以作为配套补强
- 本文仍只覆盖企业隔离 `P1`，不扩展到 `P2 / P3` 平台设计。

## 2. 当前现实起点

### 2.1 已经有的部分

- `customer_line` 对象、列表页、表单页、搜索页已经存在：
  - `custom_addons/logistics_dispatch/views/logistics_dispatch_waybill_views.xml`
  - `custom_addons/logistics_dispatch/models/logistics_dispatch_waybill_customer_line_v2.py`
- `waybill` 页已有留痕、证据、异常摘要和聚合字段：
  - `trace_count`
  - `evidence_count`
  - `open_exception_count`
- `trace_event / evidence / exception` 三层正式对象已经存在：
  - `logistics.trace.event`
  - `logistics.trace.evidence`
  - `logistics.trace.exception`

### 2.2 还没完成的关键点

当前 `customer_line` 虽然“存在”，但它还没有完成主阅读入口所需要的整条实现链：

- 页面入口链
- 查询取数链
- 反读跳转链
- 图片命中补链
- 权限与导出审计链

## 3. 缺口清单总览

当前最关键的缺口建议拆成 8 项：

1. `customer_line` 页缺少 trace / evidence / exception 摘要区
2. `customer_line` 页缺少直达 trace / evidence / exception 的入口动作
3. 图片 reader 仍按 `waybill_id` 取数，未形成 `customer_line` 视角 reader
4. 留痕反读规则未正式落成 `customer_line -> trace_event` 查询桥
5. 异常反读规则未正式落成 `customer_line -> exception` 查询桥
6. 图片导入与图片包补链未形成 `customer_line` 命中闭环
7. 导出与预览权限还没有按 `customer_line` 主阅读链细化
8. 联调与验收还没有把 `customer_line` 入口作为独立通过条件

下面逐项展开。

## 4. 具体实现缺口

### 4.1 缺口一：`customer_line` 页缺少三层摘要区

#### 当前现实

`customer_line` 表单页当前主要承载：

- 客户信息
- 汇总信息
- 履约说明
- 货物明细

但没有稳定的：

- 留痕摘要区
- 证据摘要区
- 异常摘要区

#### 为什么这是缺口

如果没有摘要区，`customer_line` 页即使有对象表单，也只是“信息页”，还不是“阅读入口页”。

#### 建议补法

在 `customer_line` 表单页首屏补最小摘要区：

- 最近相关留痕类型
- 最近相关留痕时间
- 相关证据数
- 相关异常数
- 当前证据状态
- 当前异常状态

#### 建议优先级

`P1` 必补。

### 4.2 缺口二：`customer_line` 页缺少三层直达入口

#### 当前现实

当前 `waybill` 页已有较成熟入口：

- 运单侧留痕 smart button
- 运单侧证据聚合
- 运单侧异常聚合

但 `customer_line` 页还没有对应的直达动作。

#### 为什么这是缺口

没有入口，就无法让用户形成“先看门店节点，再下钻事实材料”的稳定使用路径。

#### 建议补法

在 `customer_line` 表单页补三个入口：

- 查看相关留痕
- 查看相关证据
- 查看相关异常

要求：

- 入口是阅读入口，不改变正式对象归属
- 入口打开后的 domain 必须是“与当前 `customer_line` 相关”，不是整单全量

#### 建议优先级

`P1` 必补。

### 4.3 缺口三：图片 reader 仍按 `waybill_id` 取数

#### 当前现实

当前运单页前端 evidence reader 直接按 `waybill_id` 查询 `logistics.trace.evidence`。

这意味着实现层默认仍是：

- 运单页是主 reader
- `customer_line` 只是运单内部结构

#### 为什么这是缺口

只要读取仍按运单聚合，`customer_line` 就很难真正成为图片主阅读入口。

#### 建议补法

至少补一层 `customer_line` 视角 reader：

- 方案 A：新增 `customer_line` 页 evidence reader
- 方案 B：保留 waybill reader，但新增按 `customer_line` 分组与切换

无论哪种方案，都要满足：

- 默认从 `customer_line` 进入时，先看当前节点相关图片
- 运单页只承担汇总和总览，不再独占图片主阅读职责

#### 建议优先级

`P1` 必补。

### 4.4 缺口四：留痕反读桥未正式落成

#### 当前现实

当前正式留痕对象仍围绕：

- `batch_id`
- `waybill_id`

这是正确的，但 `customer_line` 到 `trace_event` 的反读规则没有正式收口成实现约束。

#### 为什么这是缺口

如果没有反读桥，`customer_line` 的留痕入口就只能：

- 打开整单 trace
- 或靠人为理解去筛

这不算真正的门店节点阅读入口。

#### 建议补法

首轮先不改正式对象挂点，只补反读规则：

- 以 `waybill` 为基础范围
- 再按事件类型和业务映射收口到当前 `customer_line` 相关事件

首轮建议纳入门店节点摘要反读的事件：

- `arrive_store`
- `deliver_finish`
- `signoff`
- `exception_report`

#### 建议优先级

`P1` 必补。

### 4.5 缺口五：异常反读桥未正式落成

#### 当前现实

异常详情已经能反开：

- `waybill`
- `batch`
- `trace_event`
- `evidence`

但 `customer_line` 页还没有形成“查看本节点相关异常”的稳定入口和 domain。

#### 为什么这是缺口

异常如果只能从运单或异常列表进，就会继续停留在“整单视角优先”，而不是“门店节点视角优先”。

#### 建议补法

补 `customer_line -> exception` 反读入口，首轮查询逻辑建议：

- 先限当前 `waybill`
- 再按 `trace_event` 相关店侧事件筛
- 保留异常正式主挂点围绕 `waybill / batch / trace_event`

#### 建议优先级

`P1` 必补。

### 4.6 缺口六：图片命中与补链未形成 `customer_line` 闭环

#### 当前现实

目前已经有：

- `customer_line_no`
- `store_no`
- `image_package` 枚举

但还没有形成清晰落地的：

- 图片包导入服务
- 命中规则
- 补链规则
- 证据化规则

#### 为什么这是缺口

如果图片不能稳定命中 `customer_line`，那“图片围绕 `customer_line` 阅读”就只是口径，不是能力。

#### 建议补法

首轮命中规则固定为：

1. `waybill_no + customer_line_no`
2. 兜底 `waybill_no + store_no`

补链顺序固定为：

1. 先命中 `customer_line`
2. 再关联到对应 `trace_event`
3. 最后进入正式 `evidence`

并且明确：

- 不允许按门店名称、地址自由猜测命中
- 不允许直接把图片主挂到 `order_line`

#### 建议优先级

`P1` 必补。

### 4.7 缺口七：权限、导出、审计未按 `customer_line` 入口细化

#### 当前现实

当前权限还偏粗，更多停留在：

- 普通用户
- manager

且导出与预览还没有完全按门店节点入口分层。

#### 为什么这是缺口

如果入口切到 `customer_line`，但权限和导出仍只有整单级理解，就会出现：

- 门店节点可读但不可控
- 只能整单导出，不能按节点导出
- 阅读入口变了，审计口径没跟上

#### 建议补法

围绕 `customer_line` 主阅读链至少补清：

- 谁能看节点图片
- 谁能导出节点图片
- 谁能查看节点相关异常
- 谁能补传或补链
- 节点级预览、下载、导出是否记审计

#### 建议优先级

`P1` 强建议，最好与入口一起补。

### 4.8 缺口八：联调与验收还没把 `customer_line` 入口设为硬通过项

#### 当前现实

当前实施清单和验收清单已经开始强调 `customer_line`，但还需要进一步把它变成更明确的硬通过条件。

#### 为什么这是缺口

如果联调只验证：

- 模块能装
- 运单页能看
- 异常能流转

那么团队很容易在联调阶段默认“运单可读就算过”，从而把 `customer_line` 入口再次弱化。

#### 建议补法

在联调和验收中明确新增以下通过项：

- `customer_line` 页可看到相关留痕摘要
- `customer_line` 页可看到相关证据摘要
- `customer_line` 页可看到相关异常摘要
- `customer_line` 页可直达三层详情
- 运单页不再是图片唯一主阅读入口

#### 建议优先级

`P1` 必补。

## 5. 推荐实现顺序

为了避免返工，建议按下面顺序推进：

1. 先补 `customer_line` 页摘要区与直达入口
2. 再补 `customer_line -> trace_event` 反读桥
3. 再补 `customer_line` 视角 evidence reader
4. 再补 `customer_line -> exception` 反读桥
5. 再补 `image_package` 命中与补链闭环
6. 最后补节点级权限、导出、审计与验收硬条件

## 6. 当前最关键的边界提醒

- 不把 `customer_line` 升格成正式 `trace_event` 主挂点
- 不把正式 `evidence` 主挂点从 `trace_event` 改成 `customer_line`
- 不把异常主挂点从 `waybill / batch / trace_event` 改成 `customer_line`
- 不把“门店节点主阅读入口”误解成“正式对象主归属入口”

## 7. 一句话收口

`customer_line` 要真正成为企业隔离 `P1` 下的门店侧主阅读入口，不是只补一个页面按钮，而是要把摘要区、直达入口、按节点取数、反读桥、图片补链、权限导出和验收条件整条链一起补齐。
