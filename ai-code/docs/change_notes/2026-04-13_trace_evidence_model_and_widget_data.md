# 2026-04-13 Trace Evidence Model And Widget Data

## 本次变更

- 新建 `custom_addons/logistics_trace_evidence` 真实模块骨架
- 新增 `logistics.trace.evidence` 模型与基础列表 / 表单 / 搜索视图
- 为留痕事件和运单补充证据关系与证据统计
- 将 `EvidenceViewerWidget` 的数据源改为优先读取 `logistics.trace.evidence`

## 当前结果

- 证据区已经不再只依赖运单聚合占位字段
- 只要 `logistics_trace_evidence` 安装并有证据数据，运单详情页就会直接展示真实证据列表
- 证据项现在可以直接打开其所属留痕事件
- 若 `full_url` 可用，证据区可直接打开大图地址

## 当前边界

- 还未做安装 / 升级验证
- 仍未接入真实图片存储服务，因此 `preview_url / full_url` 当前只是模型承接口径
- 证据上传与批量管理动作还未开始做

## 下一步建议

- 接入真实图片服务，打通 `image_access_key -> preview_url / full_url`
- 或继续推进 `logistics_trace_exception`
