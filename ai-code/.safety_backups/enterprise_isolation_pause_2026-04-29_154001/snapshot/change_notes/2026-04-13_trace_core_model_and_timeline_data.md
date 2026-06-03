# 2026-04-13 Trace Core Model And Timeline Data

## 本次变更

- 新建 `custom_addons/logistics_trace_core` 真实模块骨架
- 新增 `logistics.trace.event` 模型与基础列表 / 表单 / 搜索视图
- 为 `logistics.dispatch.waybill` 增加留痕事件关系、留痕统计字段计算与打开留痕事件动作
- 将 `logistics_web` 中运单详情页的时间线数据源改为直接读取 `logistics.trace.event`

## 当前结果

- 时间线已经不再只依赖运单聚合占位字段
- 只要 `logistics_trace_core` 安装并有事件数据，运单详情页就会直接展示真实留痕事件
- 若后端模型尚未安装或暂无数据链路，前端仍会回退到占位数据，避免页面完全断掉

## 当前边界

- 还未做安装 / 升级验证
- 还未接入证据真实模型，所以 `evidence_count` 仍是事件层占位字段
- 异常状态仍未由 `trace_exception` 正式接管

## 下一步建议

- 继续落 `logistics_trace_exception`
- 或开始把 `EvidenceViewerWidget` 对接真实证据模型与 URL
