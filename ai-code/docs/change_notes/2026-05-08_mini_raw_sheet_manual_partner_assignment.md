## 2026-05-08 小程序原始单表当前任务内人工指定客户

### 目标

- 保持自动导入匹配规则严格不变。
- 对 `unmatched` 行提供“当前任务内人工指定客户”能力。
- 该指定只对当前导入任务生效：
  - 不回写原始 Excel
  - 不生成永久映射规则
  - 不影响其他后续导入任务

### 后端

- 文件：
  - `logistics_web/services/mini_program_raw_sheet_import_service.py`
  - `logistics_web/controllers/logistics_web_admin_import.py`
- 新增能力：
  - `assign_manual_partner(env, task_no, business_key, partner_id)`
  - admin 接口：
    - `/api/admin/logistics/imports/mini-program-raw-sheet/assign-partner`
- 行为：
  - 仅允许对 `pending` 的预校验任务执行
  - 仅允许对 `match_status = unmatched` 的行执行
  - 指定后将该行更新为：
    - `match_status = matched_manual`
    - `can_confirm_line = True`
  - 删除该行原有的 `NAME_MATCH_NOT_FOUND` 错误
  - 重新刷新任务汇总统计与预校验摘要

### 前端

- 文件：
  - `logistics_web/static/src/js/actions/import_center_action.js`
  - `logistics_web/static/src/xml/import_center_templates.xml`
- 新增行为：
  - 在“未命中客户候选”区域，每个候选后显示“选择此客户”
  - 点击后调用 admin assign 接口
  - 成功后直接刷新当前预校验结果，不需要重新上传文件

### 结果

- 自动匹配仍然严格。
- 人工复核时，如果候选客户就是正确客户，可以直接在当前任务里指定并继续推进 confirm。
