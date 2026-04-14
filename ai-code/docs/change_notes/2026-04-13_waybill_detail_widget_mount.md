# 2026-04-13 Waybill Detail Widget Mount

## 本次变更

- 为 `logistics.dispatch.waybill` 表单页增加 `js_class="logistics_waybill_form"`
- 在运单详情页中新增 `Trace & Evidence` 页签
- 通过 `custom_addons/logistics_web/static/src/js/views/logistics_waybill_form_view.js` 将 `TraceTimelineWidget` 与 `EvidenceViewerWidget` 挂入运单详情页
- 更新 `logistics_web` 资产与视图声明，确保自定义 form view 能被后台加载

## 当前结果

- 运单详情页已经具备真实的增强区承载结构
- 时间线与证据组件会基于当前运单记录数据生成第一版展示内容
- 异常跳转已接到“带异常的运单列表”这个现有入口
- 其余尚未落地的 trace / evidence 深层跳转当前以提示信息承接

## 当前边界

- 仍未安装验证 `js_class` 与 widget 实际渲染效果
- 仍未接入 `logistics_trace_core` 与真实证据 URL
- 当前展示内容仍以运单现有聚合字段和占位数据为基础

## 下一步建议

- 开始落 `logistics_trace_core` 的真实数据骨架
- 或继续把 Boss Trace Overview 推进成第一版页面
