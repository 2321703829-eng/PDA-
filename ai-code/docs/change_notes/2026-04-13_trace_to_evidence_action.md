# 2026-04-13 Trace To Evidence Action

## 本次变更

- 将运单详情页时间线中的 `View Evidence` 动作从提示信息改为真实跳转
- 当前动作会直接打开 `logistics.trace.evidence` 列表，并自动按当前 `trace_event_id` 过滤

## 当前结果

- 时间线卡片现在可以继续下钻到真实证据列表
- 主阅读链从 `运单详情 -> 时间线 -> 证据列表` 又闭合了一段

## 当前边界

- 仍未做安装 / 升级验证
- 证据列表当前还是标准 Odoo list/form 入口，不是增强预览页

## 下一步建议

- 将证据列表页进一步接成增强预览页
- 或继续开始 `logistics_trace_exception`
