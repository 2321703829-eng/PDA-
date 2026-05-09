## 2026-05-09 最新 feat-text 合流到 19109 回归记录

### 背景

- 远端 `origin/feat-text` 最新提交为：
  - `290f8dc40e69`
  - `fix: sync enterprise template evidence export controls`
- 基于最新远端代码，新建联调工作区：
  - `D:\Desktop\ai-code\_tmp_integration_feat_text_20260509`
- 在该工作区额外保留企业隔离必要修复：
  - `custom_addons/logistics_web/controllers/__init__.py`
  - `custom_addons/logistics_web/controllers/tenant_db_param_guard.py`
  - `custom_addons/logistics_web/views/logistics_web_templates.xml`

### 部署内容

- 同步到 `19109` 环境容器：
  - `enterprise-multidb-odoo19`
- 同步并升级的模块涉及：
  - `logistics_web`
  - `logistics_trace_evidence`
  - `logistics_dispatch`
- 升级租户库：
  - `tenant_hq`
  - `tenant_kebi`
  - `tenant_template`

### 企业隔离回归结果

- 错误 `db` 参数收口仍然成立：
  - `hq.odoo.test + db=tenant_kebi` 最终会回到 `tenant_hq`
  - `kebi.odoo.test + db=tenant_hq` 最终会回到 `tenant_kebi`
  - `template.odoo.test + db=tenant_hq` 最终会回到 `tenant_template`
- 带租户 Host 访问数据库入口时：
  - `http://hq.odoo.test:19109/web/database/selector` -> `404`
- 说明：
  - 以租户 Host 为前提的企业隔离主链仍成立
  - `tenant_db_param_guard` 未被这次最新 `feat-text` 改动打回

### 证据导出回归结果

- 已确认最新 `feat-text` 中与证据导出相关的代码已部署：
  - `selection_options.py`
  - `logistics_trace_evidence_summary.py`
  - `evidence_image_export_service.py`
  - `list_import_button.js/xml`
  - `form_back_button_patch.js`
- 以 `tenant_hq` 当前测试数据做服务层验证时：
  - 未找到一条能够成功通过 `_collect_evidence_summary_image_package` 的 `logistics.trace.evidence.summary`
  - 原因不是代码异常，而是当前候选 summary 记录没有可读图片内容

### 当前判断

- 企业隔离：通过本轮关键回归
- 证据汇总页图片导出：代码已更新到最新 `feat-text`，但当前 `tenant_hq` 测试数据不足以完成最终“成功打包导出”验证

### 后续建议

- 若要完成证据导出的最终闭环验证，需要先准备一条：
  - `logistics.trace.evidence.summary` 记录
  - 且其关联 evidence 下存在当前环境可读的真实图片内容
- 在准备好样例数据后，再补一轮：
  - summary 侧图片导出
  - 前端按钮触发
  - 输出 zip 内容核对
