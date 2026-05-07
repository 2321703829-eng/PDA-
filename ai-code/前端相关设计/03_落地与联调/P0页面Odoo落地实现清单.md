# P0页面Odoo落地实现清单

适用范围：
- 当前一期最先进入实现阶段的核心页面
- 面向 Odoo 19 后台 Web 实现

优先基准：
- `ai-code/Odoo19物流留痕系统运单主对象与留痕主流程设计.md`
- `ai-code/前端相关设计/00_导航与总纲/Odoo物流后台前端总体设计总览.md`
- `ai-code/前端相关设计/02_跨模块规范/04_实施规范/前端落地技术分层清单.md`

关联文档：
- `前后端接口字段级契约清单.md`
- `接口路线决策文档.md`
- `Smart Button设计清单.md`
- `后台按波次批次运单追溯页面设计.md`

---

## 1. 文档定位

这份文档回答的是：

**P0 页面到底怎么在 Odoo 里落。**

不是只说“这个页面大概长什么样”，而是明确：

- 挂在哪个模型上
- 用什么原生视图组合承接
- 哪些区块需要聚合字段
- 哪些位置需要 Smart Button
- 哪些区域必须做轻量自定义 widget

---

## 2. P0 页面范围

当前建议纳入 P0 的页面：

1. 运单追溯列表页
2. 运单详情页
3. 留痕时间线区
4. 证据查看区
5. 当前异常列表页
6. 异常详情页
7. 管理工作台

---

## 3. 页面落地总原则

### 3.1 先用 Odoo 原生壳

P0 页面优先使用：

- `ir.actions.act_window`
- `search view`
- `tree view`
- `form view`
- `smart button`
- `stat button`

### 3.2 只在必要处做轻量增强

允许做轻量自定义 widget 的位置：

- 留痕时间线阅读区
- 证据图片预览区
- 工作台聚合卡片区

### 3.3 详情页优先“表单页 + 增强区块”

不要把 P0 详情页做成完全脱离 Odoo 的自定义前端壳。  
更稳的方案是：

- 以 `form view` 为主
- 用 notebook / group / stat button 承接标准信息
- 用自定义组件承接时间线和证据区

---

## 4. 页面级落地清单

## 4.1 运单追溯列表页

页面定位：
- 第一轮查询和筛选入口

建议主模型：
- `logistics.dispatch.waybill`

推荐 Odoo 落地：
- `search view + tree view + act_window`

原生即可承接：
- 主搜索
- 常用筛选
- 列表列展示
- 分组与排序
- 点击行进入详情

需要聚合字段：
- `latest_trace_summary`
- `latest_trace_at`
- `exception_status`
- `evidence_status`
- `risk_level`

建议 tree 列：
- 运单号
- 当前状态
- 批次
- 门店
- 司机
- 最近留痕摘要
- 异常状态
- 证据状态
- 更新时间

建议 search view：
- 关键字搜索
- 批次筛选
- 波次筛选
- 状态筛选
- 异常状态筛选
- 证据状态筛选
- 司机筛选
- 门店筛选

是否需要自定义 widget：
- 否

---

## 4.2 运单详情页

页面定位：
- 主阅读页
- 当前状态、上下文、留痕、证据、异常动作的聚合页

建议主模型：
- `logistics.dispatch.waybill`

推荐 Odoo 落地：
- `form view + smart button + 自定义时间线区 + 自定义证据区`

原生即可承接：
- 基本信息区
- 批次/波次/仓库/司机等上下文字段
- stat button / smart button
- 订单明细 one2many 区
- 基础备注区

需要聚合字段：
- `trace_count`
- `evidence_count`
- `open_exception_count`
- `latest_trace_summary`
- `evidence_status`

建议 Smart Button：
- 查看留痕
- 查看证据
- 查看异常
- 查看所属批次
- 查看所属波次

建议 form 分区：
- 顶部摘要带
- 基本信息区
- 执行上下文区
- 运单下订单明细区
- 留痕时间线区
- 证据查看区
- 异常摘要与处理区

需要轻量自定义 widget：
- 时间线区
- 图片缩略图区

---

## 4.3 留痕时间线区

页面定位：
- 运单详情内嵌阅读区
- 也可独立展开为时间线页

建议主模型：
- `logistics.trace.event`

推荐 Odoo 落地：
- 详情页中用自定义 widget 读取结构化数据
- 独立页面可用 `tree + form` 作为降级方案

原生即可承接：
- 独立留痕列表
- 留痕详情表单

原生不够好的地方：
- 时间线卡片样式
- 有图/异常/操作人信息的连续阅读体验

建议字段：
- 留痕类型
- 时间
- 操作人
- 摘要
- 图片数量
- 是否关联异常

---

## 4.4 证据查看区

页面定位：
- 详情页中的大图预览与证据阅读区

建议主模型：
- `logistics.trace.evidence`

推荐 Odoo 落地：
- 表单页内嵌轻量 evidence viewer widget
- 独立证据页可保留 `kanban/list` 作为备选

原生即可承接：
- 证据列表
- 附件元数据
- 备注字段

必须轻量增强的地方：
- 缩略图浏览
- 当前图片大图查看
- 左右切换
- 从证据跳回留痕

建议字段：
- 预览图
- 留痕类型
- 上传时间
- 上传人
- 备注
- 是否异常证据

---

## 4.5 当前异常列表页

页面定位：
- 问题队列页

建议主模型：
- `logistics.trace.exception`

推荐 Odoo 落地：
- `search view + tree view + act_window`

原生即可承接：
- 列表筛选
- 严重度排序
- 状态筛选
- 负责人筛选

需要聚合字段：
- `waybill_no`
- `batch_name`
- `evidence_status`
- `latest_process_note`

建议列：
- 异常编号
- 异常类型
- 严重度
- 状态
- 关联运单
- 关联批次
- 当前处理人
- 上报时间
- 最近处理摘要

是否需要自定义 widget：
- 否

---

## 4.6 异常详情页

页面定位：
- 单个异常的判责与处理阅读页

建议主模型：
- `logistics.trace.exception`

推荐 Odoo 落地：
- `form view + smart button + 内嵌留痕/证据摘要区`

原生即可承接：
- 异常基本信息
- 状态流转按钮
- 处理备注
- 负责人字段
- 关联对象跳转

需要轻量增强的地方：
- 关键证据阅读区
- 根留痕摘要阅读区

建议 Smart Button：
- 查看运单
- 查看批次
- 查看相关留痕
- 查看相关证据

---

## 4.7 管理工作台

页面定位：
- 管理员的第一屏

建议主模型：
- 不建议强绑单一业务模型

推荐 Odoo 落地：
- 自定义 dashboard action
- 以 controller 聚合接口驱动

原生可借用：
- 菜单入口
- act_window 或 client action 挂载

必须自定义的地方：
- 顶部概览卡
- 优先处理队列
- 最近变化流
- 高风险对象摘要块

说明：
- 这页更接近受控定制页面，不建议硬塞进标准 tree/form

---

## 5. P0 页面与实现方式总表

| 页面 | 主模型 | 原生视图 | 需要聚合字段 | 需要轻量 widget |
|---|---|---|---|---|
| 运单追溯列表页 | `logistics.dispatch.waybill` | `search + tree` | 是 | 否 |
| 运单详情页 | `logistics.dispatch.waybill` | `form` | 是 | 是 |
| 留痕时间线区 | `logistics.trace.event` | `tree/form` 兜底 | 是 | 是 |
| 证据查看区 | `logistics.trace.evidence` | `list/kanban` 兜底 | 是 | 是 |
| 当前异常列表页 | `logistics.trace.exception` | `search + tree` | 是 | 否 |
| 异常详情页 | `logistics.trace.exception` | `form` | 是 | 轻量需要 |
| 管理工作台 | 聚合页 | `client action` | 是 | 是 |

---

## 6. 开发顺序建议

建议按下面顺序落地：

1. 运单追溯列表页
2. 当前异常列表页
3. 运单详情页基础表单
4. 异常详情页基础表单
5. 运单详情页时间线区
6. 运单详情页证据区
7. 管理工作台

原因：
- 先把标准列表和表单走通
- 再补增强阅读区
- 最后做聚合工作台

---

## 7. 当前不建议直接做重定制的地方

以下内容不建议一开始就做重前端化：

- 全自定义单页应用式运单详情壳
- 完整大屏化驾驶舱
- 与 Odoo 原生导航完全脱离的独立前端
- 时间线和证据区过度动画化

---

## 8. 当前实现准备度判断

按现在文档储备，P0 页面已经可以开始：

- 建树视图和表单视图的字段清单
- 定义搜索视图和过滤器
- 明确 Smart Button 跳转
- 明确时间线区和证据区的 widget 边界

还需要边做边补的主要是：

- 真实模型字段最终命名
- controller 返回样例
- 轻量 widget 的组件结构


