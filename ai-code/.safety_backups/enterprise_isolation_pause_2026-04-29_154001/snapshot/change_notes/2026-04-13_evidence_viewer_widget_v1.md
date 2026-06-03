# 2026-04-13 Evidence Viewer Widget V1

## 本次变更

- 将 `custom_addons/logistics_web/static/src/js/widgets/evidence_viewer_widget.js` 从占位组件升级为第一版可展示组件
- 更新 `custom_addons/logistics_web/static/src/xml/widget_templates.xml`，补充证据查看头部、主显示区、信息侧栏与缩略图区
- 更新 `custom_addons/logistics_web/static/src/scss/logistics_web.scss`，补充证据查看组件样式

## 当前结果

- `EvidenceViewerWidget` 已支持以 `items` 传入证据数据
- 若上层暂未接入真实数据，可回退使用组件内默认示例数据
- 组件已支持：
  - 缩略图切换当前证据
  - 上一张 / 下一张切换
  - 查看所属留痕回调
  - 打开大图回调
  - 加载态与空态

## 当前边界

- 仍未接入真实图片 URL 与大图预览逻辑
- 仍未挂接到运单详情页或异常详情页实际渲染链路
- 当前主显示区使用的是视觉占位块，不是实际图片资源

## 下一步建议

- 将 `TraceTimelineWidget` 与 `EvidenceViewerWidget` 一起挂入运单详情页增强区域
- 后续补真实 controller 数据后，再把证据图片与留痕联动接上
