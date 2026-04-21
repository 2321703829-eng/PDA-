# 2026-04-18 三期统计图表与物流工作台验收清扫

## Objective

收口三期 `统计图表 / 物流工作台` 在最后一轮页面验收里最容易暴露的尾项，重点补齐：

- `物流工作台` 摘要卡与快捷入口的下钻口径
- `统计图表` 四大分区的空态与权限态表现
- 两页错误文案和无权限态的统一映射

## Outcome

- `物流工作台` 的 `风险批次 / 今日新增异常` 摘要卡不再落到泛列表，而是按真实对象精确下钻。
- `物流工作台` 摘要区在无卡片数据时会展示明确空态，不再留白。
- `统计图表` 的执行、风险、司机、地区四个分区补齐了分区级空态占位。
- `统计图表` 和 `物流工作台` 的无权限接口错误，会统一映射成页面可读文案。
- `统计图表` 的空态判断改为“存在非零趋势值”而不是“存在时间桶”，避免未来时间范围返回全 0 时间桶时页面仍误判为有图可画。

## Changed Files

- `custom_addons/logistics_web/models/logistics_dashboard_service.py`
- `custom_addons/logistics_web/static/src/js/actions/dashboard_action_v2.js`
- `custom_addons/logistics_web/static/src/xml/dashboard_templates.xml`
- `custom_addons/logistics_web/static/src/js/actions/stats_center_action.js`
- `custom_addons/logistics_web/static/src/xml/stats_center_templates.xml`

## Verify

- 工作台组件动作回放验证：
  - `风险批次` -> `logistics.dispatch.batch`，domain 为 `id in [1]`
  - `今日新增异常` -> `logistics.trace.exception`，domain 为 `id in []`
  - `优先处理队列` 第一项 -> `logistics.trace.exception`，domain 为 `name = EXC-MISSING-20260414065422`
  - `异常处理` 快捷入口 -> `logistics.trace.exception`，domain 为 `state in ['open', 'processing']`
- 统计图表接口验收：
  - 当前时间窗 `2026-03-20 ~ 2026-04-18` 能返回摘要、趋势、分布、排行数据
  - 未来时间窗 `2099-01-01 ~ 2099-01-31` 的分布和排行为空，趋势返回全 0 时间桶
  - 因此页面空态逻辑已进一步收口到“非零趋势值”判断

## Boundary

- 这轮只做验收收口，不新增统计指标、图表或新的工作台摘要卡。
- 这轮不改后端统计口径，只修前端下钻精度、空态判断和权限态展示。
