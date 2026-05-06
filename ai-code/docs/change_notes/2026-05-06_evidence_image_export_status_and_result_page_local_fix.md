# 2026-05-06 本地证据图片导出状态与结果页口径修正

## 背景

针对证据图片批量导出，本地代码存在以下问题：

- 有图片缺失时，任务整体仍可能显示为 `success`
- 结果页没有展示图片级统计，业务难以判断“命中图片 / 已导出图片 / 未导出图片”
- `manifest.json` 的 `entry_type` 固定写成 `from_waybill`
- 从证据列表发起导出后，结果页返回入口仍指向运单列表

## 本次本地修正

### 后端

文件：

- `D:\Desktop\Odoo\custom_addons\logistics_web\services\evidence_image_export_service.py`

调整：

- 当任务行存在图片级 `skipped_image_count + failed_image_count` 时，即使行级成功，也将任务总状态从 `success` 收口为 `partial_failed`
- 任务摘要文案补充图片级统计：
  - `data-missing`
  - `system-failed`
- `manifest.json` 改为写入任务真实 `entry_type`
- 任务结果 payload 和任务行 payload 增加图片级指标：
  - `matched_image_count`
  - `skipped_image_count`
  - `failed_image_count`

### 前端

文件：

- `D:\Desktop\Odoo\custom_addons\logistics_web\static\src\js\actions\export_result_action.js`

调整：

- 证据图片导出结果页补充图片级摘要卡片：
  - `命中图片`
  - `导出运单`
  - `导出证据`
  - `导出图片`
  - `未导出-数据缺失`
  - `未导出-系统异常`
- 行级 / 摘要业务文案统一为业务口径：
  - `已导出`
  - `未导出-系统异常`
  - `未导出-数据缺失`
- 从证据列表发起的 `evidence_image_bundle` 导出结果页，返回入口改为：
  - `logistics_trace_evidence.action_logistics_trace_evidence`

## 校验

- `export_result_action.js` 已通过 `node --check`
- 关键文案块已用源码级检查确认无残留 `????`
- `evidence_image_export_service.py` 逻辑改动已保留在本地，暂未推送到服务器

## 当前状态

本次修正仅在本地完成，后续待本地进一步确认稳定后，再同步到联调服务器。
