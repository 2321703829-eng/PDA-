# 2026-04-21 三期统一回扫第四段第一轮

## 本轮目标

继续推进三期页面统一回扫第四段，先收一轮共享响应式与状态层规则，重点解决：

- hero 在窄屏下的换行和右侧说明块挤压
- 摘要卡在中屏下的列数切换
- 筛选区在窄屏下的换列与按钮拉伸
- 双列分析区在中屏和小屏下的改单列顺序
- 状态面板在小屏下的按钮宽度、说明文案行距和占位层级
- 导入页长文件名、长标签和入口提示条的折行问题

## 本轮改动

### 1. 共享状态面板与 hero 断点

文件：
- `custom_addons/logistics_web/static/src/scss/logistics_web.scss`

调整：
- 统一 `state panel / placeholder panel` 的段落行距和按钮最小宽度
- 在小屏下让状态面板动作按钮改为整行宽度
- 在 `900px` 以下让 hero 的右侧说明区、状态标签区统一拉满宽度
- 补齐 hero 右侧 meta 在中屏下的对齐规则

### 2. 统计图表

文件：
- `custom_addons/logistics_web/static/src/scss/stats_center.scss`

调整：
- `1180px` 下：
  - 摘要卡从 4 列收成 2 列
  - 三列分析区收成 2 列
  - 双列区改成单列
  - 筛选区改成 2 列，动作区独占一整行
- `900px` 下：
  - 摘要卡、三列区、筛选区统一改单列
  - 刷新/重置按钮改成整列堆叠
  - 紧凑趋势卡、信号卡改成 1 列
- `640px` 下：
  - 柱状图时间桶强制改单列，避免极窄屏下被压扁

### 3. 物流工作台

文件：
- `custom_addons/logistics_web/static/src/scss/dashboard.scss`

调整：
- `1180px` 下摘要卡和常用入口统一改为 2 列
- `760px` 下摘要卡和入口卡统一改为 1 列
- 工作台卡片在小屏下继续压低内边距和最小高度

### 4. 司机管理

文件：
- `custom_addons/logistics_web/static/src/scss/driver_management.scss`

调整：
- 小屏下列表页工具条按钮统一全宽
- 画像页头部动作按钮统一改为竖排并拉满宽度
- 继续保证表格壳保持横向滚动而不是强行压扁列宽

### 5. 导入中心 / 导入结果页

文件：
- `custom_addons/logistics_web/static/src/scss/import_pages.scss`

调整：
- 模板卡、当前文件信息、结果信息行都补了长文本换行
- 入口提示条在窄屏下改成竖向堆叠
- 提示条内的 tag 区在小屏下独占一整行
- 上传动作栏和结果动作栏继续保持小屏纵向堆叠

### 6. 管理看板

文件：
- `custom_addons/logistics_web/static/src/scss/boss_trace.scss`

调整：
- `1180px` 下：
  - 风险概览摘要卡改成 2 列
  - 入口分组和信号区改成 2 列
- `760px` 下：
  - 摘要卡、入口分组、信号区统一改单列
  - 入口卡和重点卡中的按钮改成整行宽度

## 验证

- `python ai-code/scripts/check_odoo_frontend_assets.py custom_addons/logistics_web`

结果：
- `Errors: 0`
- `Warnings: 0`

## 当前结论

三期统一回扫第四段已经完成第一轮样式层收口，当前已经具备：

- 共享 hero 在中小屏下更稳定的折行规则
- 摘要卡、筛选区、双列分析区在主要业务页中的统一列数切换
- 状态面板在小屏下更统一的按钮和说明文案结构
- 导入页、工作台、管理看板、司机页在窄屏下更一致的卡片密度

仍建议继续推进：

- 统一回扫第四段第二轮：按真实页面截图逐页确认表格溢出、极窄屏下卡片顺序和状态文案口径
- 统一状态文案的最后一轮微调
