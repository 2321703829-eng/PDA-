## 2026-05-07 小程序原始单表预校验前端汇总取值修正

### 问题现象

- 网页导入中心执行“小程序原始单表导入”预校验后：
  - 导入任务号可以显示
  - 但总行数、去重后行数、未命中客户数等卡片为空
  - `可正式导入` 被错误显示为“否”

### 根因

- 后端 `mini-program-raw-sheet/precheck` 返回结构中，统计字段位于 `payload.data.summary`。
- 前端页面直接把 `payload.data` 写入 `miniProgramRawSheetPrecheckResult`，并按顶层字段读取：
  - `total_row_count`
  - `deduplicated_row_count`
  - `unmatched_row_count`
  - `can_confirm_import`
- 导致任务号可见，但汇总字段为空，`can_confirm_import` 也被误判。

### 处理

- 在 `logistics_web/static/src/js/actions/import_center_action.js` 中新增 `normalizeMiniProgramRawSheetPrecheckResult(data)`。
- 在小程序原始单表预校验完成后，先将：
  - `data.summary`
  - `data.result_flags`
  - `data.error_report`
  统一展开到前端状态对象，再驱动卡片展示和 confirm 按钮状态。

### 结果

- 前端可以正确显示预校验汇总卡片。
- `can_confirm_import` 会按后端真实结果展示，不再因为前端取值错误而固定成“否”。
