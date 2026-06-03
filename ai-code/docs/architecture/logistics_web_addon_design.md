# logistics_web Addon Design

适用范围：
- `custom_addons/logistics_web`
- 当前 Odoo 物流项目中的前端增强层设计
- 面向后台 Web 端的页面增强、组件、client action、widget 与聚合前端能力

优先基准：
- `ai-code/docs/context/Odoo19物流留痕系统运单主对象与留痕主流程设计.md`
- `ai-code/docs/dev/project_coordination/Odoo19物流留痕系统五人分工与前端改造安排.md`
- `ai-code/docs/architecture/前端代码目录规划.md`
- `ai-code/专题设计/前端设计/一期前端相关设计/00_导航与总纲/前端总体设计总览.md`

关联文档：
- `ai-code/专题设计/前端设计/一期前端相关设计/03_落地与联调/P0页面Odoo落地实现清单.md`
- `ai-code/专题设计/前端设计/一期前端相关设计/02_跨模块规范/02_交互与组件/后台组件规范总表.md`
- `ai-code/专题设计/前端设计/一期前端相关设计/02_跨模块规范/01_接口与数据/最终接口总表.md`
- `ai-code/专题设计/前端设计/一期前端相关设计/02_跨模块规范/01_接口与数据/接口路线决策文档.md`

---

## 1. 文档目的

本文档用于正式定义 `logistics_web` 这个 addon 的职责、边界、依赖和目录结构。

这不是一个“把所有前端代码都塞进去”的模块设计，而是：

**在 Odoo addon 体系内，为前端负责人提供一个稳定的前端增强承载层。**

它要解决的问题是：

1. 前端代码在 GitHub 协作中应该主要放哪里
2. 哪些页面增强能力应该集中
3. 哪些能力仍应保留在业务模块里
4. `logistics_web` 和 `logistics_dispatch / logistics_trace_core / logistics_trace_exception` 怎么分工

---

## 2. 模块定位

`logistics_web` 的定位是：

**Odoo 物流项目的前端增强层与统一 UI 承载层。**

它不负责定义业务主对象本身，而负责把已有业务对象转化成更适合后台阅读、查询、判断和追溯的前端体验。

换句话说：

- 业务对象在哪里：业务模块负责
- 页面怎么更好地读：`logistics_web` 负责

---

## 3. 核心目标

`logistics_web` 要承接的核心目标有 4 个：

1. 统一承接非标准原生页面
2. 统一承接时间线、证据、工作台等增强区块
3. 统一承接前端通用组件与样式
4. 降低前端负责人和后端负责人在 GitHub 协作中的文件冲突概率

---

## 4. 不负责什么

`logistics_web` 明确不负责：

- 核心业务模型定义
- 核心字段定义
- 业务状态机本体
- 主数据模型扩展
- 核心 ACL 与 record rule
- 标准 `tree / form / search` 基础视图主体

这些能力仍应优先放在：

- `logistics_base`
- `logistics_dispatch`
- `logistics_trace_core`
- `logistics_trace_exception`

---

## 5. 与其他模块的边界

## 5.1 与 `logistics_dispatch`

`logistics_dispatch` 负责：

- 波次、批次、运单、运单订单明细
- 基础 `tree / form / search`
- 基础菜单、动作、按钮
- 运单详情主体中的基础业务字段

`logistics_web` 负责：

- 运单详情页中的增强阅读区
- 运单页上的统一组件样式
- 运单页中需要 widget 承接的阅读区块

## 5.2 与 `logistics_trace_core`

`logistics_trace_core` 负责：

- 留痕事件模型
- 留痕事实字段
- 留痕基础查询能力
- 留痕基础列表和表单

`logistics_web` 负责：

- 时间线增强 widget
- 时间线卡片阅读体验
- 时间线与详情页的前端衔接

## 5.3 与 `logistics_trace_exception`

`logistics_trace_exception` 负责：

- 异常对象
- 异常状态流转
- 异常基础表单与列表
- 异常处理记录

`logistics_web` 负责：

- 异常详情页中的增强阅读区
- 异常摘要组件
- 异常与证据/留痕的前端串联

## 5.4 与 `logistics_trace_evidence`

`logistics_trace_evidence` 负责：

- 证据对象模型
- 图片元数据
- 证据访问口径
- 证据基础查询

`logistics_web` 负责：

- 证据 viewer widget
- 缩略图、大图、切换、定位留痕
- 证据阅读体验层

## 5.5 与未来 `logistics_trace_dashboard`

`logistics_trace_dashboard` 更偏：

- 聚合字段与聚合服务来源
- 统计口径
- dashboard 数据供给

`logistics_web` 更偏：

- 工作台前端承载
- 老板页前端承载
- 聚合卡片组件与 client action

---

## 6. 当前推荐依赖关系

## 6.1 最小依赖

建议 `logistics_web` 最小依赖：

- `base`
- `web`
- `mail`
- `logistics_dispatch`

## 6.2 随功能扩展逐步增加

当时间线和异常页正式接入时，再增加：

- `logistics_trace_core`
- `logistics_trace_exception`

当证据模块正式落地时，再增加：

- `logistics_trace_evidence`

## 6.3 依赖原则

`logistics_web` 应尽量依赖业务模块，但不反向被业务模块依赖。

也就是说，推荐方向是：

```text
logistics_dispatch
logistics_trace_core
logistics_trace_exception
    -> logistics_web
```

而不是：

```text
logistics_web -> 被业务模块强反向依赖
```

这样可以让前端增强层保持相对独立。

---

## 7. 当前推荐承接的页面

## 7.1 P0 优先承接

第一批最适合由 `logistics_web` 承接的页面与区块：

1. 管理工作台
2. 运单详情页的时间线增强区
3. 运单详情页的证据查看区
4. 异常详情页的关键证据阅读区

## 7.2 P1 继续承接

第二批适合承接：

1. 老板追溯摘要页
2. 增强版时间线页
3. 证据总览页
4. 高风险对象摘要页

## 7.3 不建议由 `logistics_web` 主承接的页面

以下页面主体不建议由 `logistics_web` 接管：

1. 运单标准列表页
2. 运单标准基础表单主体
3. 批次标准列表与表单
4. 异常标准列表页
5. 配置页中的标准字典表单

这些应继续由业务模块用原生视图承接。

---

## 8. 页面承载方式

## 8.1 主要承载方式

`logistics_web` 推荐使用下面这些承载方式：

- `client action`
- 自定义 JS widget
- XML template
- SCSS
- controller 聚合读取配套前端层

## 8.2 次要承载方式

在必要时，也可少量放置：

- 与前端增强页直接相关的菜单
- 与 client action 绑定的 `ir.actions.client`
- 辅助模板视图

## 8.3 不建议作为主体承载的方式

不建议把 `logistics_web` 作为大量标准 `tree / form / search` 的主要承载模块。

---

## 9. 推荐目录结构

```text
custom_addons/logistics_web/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── logistics_web_dashboard.py
├── data/
│   └── logistics_web_assets.xml
├── security/
│   └── ir.model.access.csv
├── static/
│   └── src/
│       ├── js/
│       │   ├── actions/
│       │   │   ├── dashboard_action.js
│       │   │   └── boss_trace_action.js
│       │   ├── components/
│       │   │   ├── page_header.js
│       │   │   ├── summary_band.js
│       │   │   ├── summary_card.js
│       │   │   └── status_tag.js
│       │   ├── services/
│       │   │   ├── logistics_rpc_service.js
│       │   │   └── logistics_controller_service.js
│       │   └── widgets/
│       │       ├── trace_timeline_widget.js
│       │       └── evidence_viewer_widget.js
│       ├── scss/
│       │   └── logistics_web.scss
│       ├── xml/
│       │   ├── dashboard_templates.xml
│       │   ├── boss_trace_templates.xml
│       │   └── widget_templates.xml
│       └── img/
└── views/
    ├── logistics_web_actions.xml
    ├── logistics_web_menus.xml
    └── logistics_web_templates.xml
```

---

## 10. 组件规划

## 10.1 推荐通用组件

建议在 `logistics_web` 中统一建设这些前端组件：

- `PageHeader`
- `PageFilterBar`
- `SummaryBand`
- `SummaryCard`
- `StatusTag`
- `TraceTimelineWidget`
- `EvidenceViewerWidget`
- `PriorityQueuePanel`
- `RecentChangeFeed`

## 10.2 组件职责

### 页面结构组件

负责：

- 统一标题区
- 统一筛选区
- 统一摘要带

### 数据展示组件

负责：

- 状态标签
- 摘要卡
- 风险标识

### 阅读增强组件

负责：

- 时间线阅读
- 证据阅读
- 大图与上下文联动

---

## 11. 接口与数据读取策略

`logistics_web` 的数据读取应遵循当前项目已定路线：

- 主路线：`Odoo RPC`
- 补充路线：少量 `JSON controller`

## 11.1 优先 RPC 的场景

适合：

- 标准对象读取
- 基础详情页字段
- 标准搜索与列表跳转

## 11.2 允许 controller 的场景

适合：

- 工作台聚合卡片
- 老板摘要页
- 时间线增强输出
- 证据 viewer 结构化输出

## 11.3 不允许的做法

不允许在 `logistics_web` 里为了“前端方便”另起一套完全绕开 Odoo 权限模型的数据层。

---

## 12. 视图与菜单建议

## 12.1 适合在 `logistics_web` 中新增的入口

建议放在本模块：

- 管理工作台入口
- 老板追溯摘要入口
- 证据总览入口
- 增强版时间线入口

## 12.2 不建议搬过来的入口

不建议把下面这些入口从业务模块搬到 `logistics_web`：

- 运单管理
- 批次管理
- 波次管理
- 异常基础列表

这些入口仍应保留在其业务模块中。

---

## 13. Manifest 草案

建议 manifest 草案方向如下：

```python
{
    "name": "Logistics Web",
    "summary": "Frontend enhancement layer for Odoo logistics backend",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "depends": [
        "web",
        "mail",
        "logistics_dispatch",
    ],
    "data": [
        "data/logistics_web_assets.xml",
        "views/logistics_web_actions.xml",
        "views/logistics_web_menus.xml",
        "views/logistics_web_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "logistics_web/static/src/js/**/*.js",
            "logistics_web/static/src/xml/**/*.xml",
            "logistics_web/static/src/scss/**/*.scss",
        ],
    },
    "installable": True,
    "application": False,
}
```

说明：

- 初版不要一次性引入所有 trace 子模块依赖
- 先从 `logistics_dispatch + web` 启动最小前端增强承载
- 后续按实际落地阶段逐步增加依赖

---

## 14. 实施顺序建议

## 第一阶段：骨架

先做：

1. 模块骨架
2. assets
3. 基础 SCSS
4. 基础组件目录

## 第二阶段：P0 页面增强

再做：

1. 工作台 client action
2. 时间线 widget
3. 证据 viewer widget

## 第三阶段：P1 聚合页

最后再做：

1. 老板页
2. 证据总览页
3. 更复杂的 dashboard 入口

---

## 15. 当前风险点

## 15.1 风险一：前端层承接过多业务定义

如果把过多业务规则写进 `logistics_web`，会导致：

- 前端层变成伪业务层
- 与后端边界变模糊

因此应坚持：

- 规则与状态在业务模块
- 阅读与展示在前端模块

## 15.2 风险二：过早做成独立前端壳

如果 `logistics_web` 走向“完全替代 Odoo 后台”的方向，会显著增加复杂度。

因此应坚持：

- 先做增强，不做重壳

## 15.3 风险三：前端代码仍然大量散落

如果虽然有 `logistics_web`，但实际 widget、样式、action 仍散在多个模块里，就达不到协作优化目标。

因此应坚持：

- 新增的前端增强能力优先收敛到 `logistics_web`

---

## 16. 结论

`logistics_web` 不是一个新的独立前端工程，而是：

**当前 Odoo 物流项目中，服务于前端负责人、承接后台前端增强能力的统一 addon。**

它最适合承接：

- 工作台
- 老板页
- 时间线增强区
- 证据 viewer
- 通用前端组件

而标准业务页面主体仍应保留在：

- `logistics_dispatch`
- `logistics_trace_core`
- `logistics_trace_exception`

这套拆分方式最适合当前的：

- Odoo Web 宿主模式
- GitHub 协作模式
- 前端负责人单独负责页面增强工作的团队结构

