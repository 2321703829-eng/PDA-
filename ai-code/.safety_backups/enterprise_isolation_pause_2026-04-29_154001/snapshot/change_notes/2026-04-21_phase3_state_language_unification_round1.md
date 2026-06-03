# 2026-04-21 三期状态语言统一第一轮

## 本轮目标

把三期主要前端页面的加载态、空态、错误态和无权限态进一步收成同一套结构，不再只停留在零散文案。

涉及页面：

- 首页
- 统计图表
- 物流工作台
- 司机管理
- 导入中心
- 导入结果页
- 管理看板

## 本轮改动

### 1. 共享状态结构继续收口

- 继续使用统一的 `o_logistics_web_state_panel`
- 让加载态、空态和错误态不再只有一行文本，而是统一进入：
  - 标题
  - 说明
  - 占位面板或反馈条

### 2. 导入中心

- 接口错误统一映射到：
  - 无权限
  - 预校验失败
  - 正式导入失败
  - 结果刷新失败
- 模板区、预校验区、结果回看区补了统一状态面板

### 3. 导入结果页

- 加载态补了状态面板
- 顶层错误态补了统一说明和返回导入中心动作

### 4. 物流工作台

- 页面级错误态补了统一状态面板
- 优先处理队列和最近动态空态补了统一结构

### 5. 管理看板

- 重点提醒和责任人关注区的空态补了统一状态面板

### 6. 统计图表

- 页面级加载态和错误态补了统一状态面板
- 保持四大分区空态仍按各自业务语义输出

### 7. 司机管理

- 列表页补齐：
  - 加载态
  - 错误态
  - 空结果态
- 画像页补齐：
  - 画像加载态
  - 画像错误态

## 验证

- `python ai-code/scripts/check_odoo_frontend_assets.py custom_addons/logistics_web`
  - `Errors: 0`
  - `Warnings: 0`
- XML 解析通过：
  - `home_action_templates.xml`
  - `stats_center_templates.xml`
  - `dashboard_action_templates.xml`
  - `boss_trace_action_templates.xml`
  - `import_center_templates.xml`
  - `import_result_templates.xml`
  - `driver_management_templates_safe.xml`
- `node --check custom_addons/logistics_web/static/src/js/actions/import_center_action.js`

## 当前结论

三期状态语言统一的第一轮已经完成到“主要页面都具备统一状态壳”的程度。

还未完全收口的部分主要是：

- 继续统一更细的状态文案口径
- 窄屏下的筛选区、双列区块、表格溢出处理
- 首页与三期页面在状态提示上的最后一轮语言对齐
