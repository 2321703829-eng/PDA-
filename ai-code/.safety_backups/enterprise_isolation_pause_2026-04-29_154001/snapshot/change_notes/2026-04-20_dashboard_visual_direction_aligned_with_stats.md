# 2026-04-20 物流工作台复制统计图表样板页视觉方向

## 本次调整

在 `统计图表` 样板页方向基本稳定后，把同一套视觉语言复制到 `物流工作台`，但保持工作台本身更偏执行调度入口的页面节奏。

## 调整文件

1. `custom_addons/logistics_web/static/src/js/actions/dashboard_action_v2.js`
2. `custom_addons/logistics_web/static/src/xml/dashboard_action_templates.xml`
3. `custom_addons/logistics_web/static/src/scss/dashboard.scss`

## 调整内容

### 1. Hero

- 工作台页头升级为与统计图表同语言的 hero
- 保留工作台自己的文案和业务定位
- 增加：
  - kicker
  - badge
  - 右侧说明卡

### 2. Panel shell

- `今日重点`
- `优先处理队列`
- `最新动态`
- `常用入口`

以上 4 块统一套入 panel shell 结构，和统计图表保持同一系统语言。

### 3. 摘要卡

- 给 4 张摘要卡补充说明文案
- 继续沿用 tone 语义
- 卡片形态与统计图表样板页对齐

### 4. 列表卡与入口卡

- 优先队列卡
- 最近动态卡
- 常用入口卡

统一补 hover、阴影、圆角和信息层级。

## 校验

- `python ai-code/scripts/check_odoo_frontend_assets.py custom_addons/logistics_web`
- `node --check custom_addons/logistics_web/static/src/js/actions/dashboard_action_v2.js`
- `dashboard_action_templates.xml` XML 解析通过

## 当前结论

`物流工作台` 已经开始和 `统计图表` 使用同一套三期样板页语言。

如果这版页面验收通过，下一步最合适继续把同一套系统铺到 `司机管理`。
