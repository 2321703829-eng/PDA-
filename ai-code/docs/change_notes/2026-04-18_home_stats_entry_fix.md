# 2026-04-18 首页“所有统计图表”入口修正

## Objective

修正首页模块卡片中 `所有统计图表` 的跳转目标，避免用户点击后进入错误页面或误以为统计入口不可用。

## Outcome

- 首页 `所有统计图表` 卡片现在会打开 `统计图表中心`。
- 卡片提示文案同步改为更贴近统计分析场景，不再描述成工作台摘要入口。
- 首页入口进一步改为直接打开 `logistics_web.stats_center` client action，不再依赖 xmlid 解析链。

## Changed Files

- `custom_addons/logistics_web/static/src/js/actions/home_action.js`

## Verify

- 首页点击 `所有统计图表`，应跳转到 `logistics_web.action_logistics_web_stats_center`
- 左侧菜单 `所有统计图表` 的现有入口不受影响

## Boundary

- 这次只修首页入口映射，不改统计图表页面本身逻辑
- 不涉及模块数据、菜单 XML 或后端接口口径变更
