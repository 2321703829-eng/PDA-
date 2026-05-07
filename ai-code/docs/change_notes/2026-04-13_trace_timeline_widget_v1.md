# 2026-04-13 Trace Timeline Widget V1

## 本次变更

- 将 `custom_addons/logistics_web/static/src/js/widgets/trace_timeline_widget.js` 从占位组件升级为第一版可展示组件
- 为时间线组件补充筛选、空态、加载态与默认假数据
- 更新 `custom_addons/logistics_web/static/src/xml/widget_templates.xml`，增加时间线头部、筛选按钮、卡片列表与动作区
- 更新 `custom_addons/logistics_web/static/src/scss/logistics_web.scss`，补充时间线区域样式

## 当前结果

- `TraceTimelineWidget` 已支持以 `items` 传入时间线数据
- 若上层暂未接入真实数据，可回退使用组件内默认示例数据
- 组件已支持：
  - 仅看含图留痕
  - 仅看异常留痕
  - 点击整条留痕
  - 点击证据动作
  - 点击异常动作

## 当前边界

- 仍未接入真实 `logistics_trace_core` 数据模型
- 仍未挂接到运单详情页实际渲染链路
- 动作目前只暴露回调接口，等待后续接入真实跳转或打开逻辑

## 下一步建议

- 继续完成 `EvidenceViewerWidget` 第一版
- 将 `TraceTimelineWidget` 挂入运单详情页增强区域
