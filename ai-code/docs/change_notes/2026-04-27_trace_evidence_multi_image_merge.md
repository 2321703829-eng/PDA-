# 2026-04-27 Trace Evidence 多图并入与图片批量导出

## 本次变更

- 将 `feat-image-4a` 中的图片子表与本地存储服务并入 `custom_addons/logistics_trace_evidence`
- 给现行 `logistics.trace.evidence` 增加 `image_ids / image_count / image_items_json`
- 保留旧字段 `image_access_key / preview_url / full_url` 作为首图兼容层
- 给 `logistics_web` 的证据查看链补多图返回与多缩略图展示
- 新增图片批量导出对象类型 `evidence_image_bundle`
- 将图片批量导出接入现有导出任务链与导出结果页
- 顺手清理 Odoo 19 技术债：
  - 将图片子表唯一约束改为 `models.Constraint`
  - 将导出链权限校验改为 `check_access()`

## 影响范围

- `custom_addons/logistics_trace_evidence`
- `custom_addons/logistics_web`
- `custom_addons/logistics_dispatch`
- `ai-code/docs/architecture/logistics_trace_evidence_image_merge_design.md`

## 兼容策略

- 老数据仍可通过 `image_access_key / preview_url / full_url` 正常预览
- 新数据优先走 `image_ids`，旧字段自动同步为首图
- `logistics_web` 前端优先读 `image_items_json`，无子图时自动回退老字段

## 预期收益

- 一条 evidence 可正式承载多张图片
- 运单侧 evidence viewer 支持真正的多缩略图切换
- 图片可按运单批量打包导出，并复用现有导出任务权限与结果查看链

## 验证补充

- `logistics_trace_evidence, logistics_dispatch, logistics_web` 升级通过
- 多图 smoke 记录可正常生成 `image_items_json`
- 图片批量导出任务成功生成 ZIP 包
- 导出链不再触发 `check_access_rights / check_access_rule` 弃用告警
