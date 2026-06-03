# 2026-04-15 logistics_web UI 本土化收口

## 本次目标

继续完成 [2026-04-14_Odoo物流后台UI本土化与中文体验优化方案](d:/Desktop/Odoo/ai-code/二期前端优化设计/2026-04-14_Odoo物流后台UI本土化与中文体验优化方案.md) 中尚未完全落地的部分，重点收口：

- 管理层总览命名一致性
- 运单“留痕与证据”页的阅读引导
- 留痕筛选后的反馈提示
- 证据查看的上下文摘要与原图可用性提示

## 变更范围

### 1. 管理层总览命名继续统一

文件：
- `custom_addons/logistics_web/static/src/js/actions/boss_trace_action_v2.js`
- `custom_addons/logistics_web/static/src/js/actions/dashboard_action_v2.js`

调整：
- 管理层总览继续统一使用“异常”语义，不再保留 `dispute` 风格的 key 命名
- 页面引导语改为更偏管理动作的表达
- 按钮文字统一收口为 `查看异常 / 查看运单 / 查看批次`

### 2. 运单“留痕与证据”页增加轻量引导条

文件：
- `custom_addons/logistics_web/views/logistics_web_waybill_views.xml`
- `custom_addons/logistics_web/static/src/scss/logistics_web.scss`

调整：
- 在页签顶部补充三段式引导：
  - 先看留痕顺序
  - 再看证据图片
  - 最后核对异常
- 保持原始关联数据区不变，但通过布局强调主阅读区优先

### 3. 留痕时间线增加筛选反馈

文件：
- `custom_addons/logistics_web/static/src/js/widgets/trace_timeline_widget.js`
- `custom_addons/logistics_web/static/src/xml/widget_templates.xml`
- `custom_addons/logistics_web/static/src/scss/logistics_web.scss`

调整：
- 新增总量/筛选后数量摘要
- 筛选启用时显示当前筛选标签
- 筛选后无结果时，空态提示用户取消筛选继续查看

### 4. 证据查看增加上下文摘要

文件：
- `custom_addons/logistics_web/static/src/js/widgets/evidence_viewer_widget.js`
- `custom_addons/logistics_web/static/src/xml/widget_templates.xml`
- `custom_addons/logistics_web/static/src/scss/logistics_web.scss`

调整：
- 显示当前是第几张证据、关联哪条留痕、上传时间、是否异常相关
- 当当前证据无法打开原图时，补充“仅支持预览”提示
- 保持图片主舞台为核心，不引入重型调试信息

## 验证

已完成：
- `node --check` 校验以下文件语法通过：
  - `boss_trace_action_v2.js`
  - `dashboard_action_v2.js`
  - `trace_timeline_widget.js`
  - `evidence_viewer_widget.js`
- 使用 Python XML 解析校验以下文件通过：
  - `widget_templates.xml`
  - `logistics_web_waybill_views.xml`

未完成：
- Odoo 模块升级后的真实页面人工验收仍需在浏览器中确认

## 升级后建议验收点

1. 管理层总览中不再出现“看异常 / 看运单 / 看批次”这类偏口语按钮，而是统一为“查看...”。
2. 运单“留痕与证据”页顶部出现三段式阅读引导。
3. 留痕时间线在启用筛选后，会显示“共多少条、当前筛出多少条”的提示。
4. 证据查看区会显示当前第几张、关联留痕、是否异常相关，以及是否仅支持预览。
