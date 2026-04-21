# 2026-04-20 导入中心与导入结果页第一轮页面优化

## 目标

- 把导入中心与导入结果页拉进三期统一的 hero / panel-shell 视觉语言。
- 清理导入页残留的坏编码文案和重复动作注册问题。
- 让导入页从“功能可跑”提升到“可直接作为三期正式页面展示”的状态。

## 本轮完成

- 导入中心页头升级为 hero，并补了入口说明、状态 badge 和工作方向说明卡。
- 导入中心的模板下载、上传与预校验、导入结果 3 个主区块改成统一 panel-shell。
- 清理导入中心模板中的坏编码中文，统一为清晰中文文案。
- 导入中心动作文件中移除了重复的结果页动作实现，只保留 import center 自身逻辑。
- 导入结果页升级为 hero + 结果头部 + 摘要卡 + 批次信息 + 后续动作 + 失败说明结构。
- 导入结果摘要卡补了说明文案，结果页更接近“批次回看页”而不是纯数据回显页。
- 新增 `import_pages.scss`，单独承接导入页的 hero 配色、卡片、结果信息区和错误区样式。

## 影响文件

- `custom_addons/logistics_web/static/src/js/actions/import_center_action.js`
- `custom_addons/logistics_web/static/src/js/actions/import_result_action.js`
- `custom_addons/logistics_web/static/src/xml/import_center_templates.xml`
- `custom_addons/logistics_web/static/src/xml/import_result_templates.xml`
- `custom_addons/logistics_web/static/src/scss/import_pages.scss`

## 验证重点

- 导入中心页头、模板区、预校验区、结果区是否都已切进统一视觉层级。
- 导入结果页是否正常显示状态 badge、摘要卡、批次信息和后续动作。
- `logistics_web.import_result` 是否只由独立结果页动作文件注册，避免重复注册。

## 后续建议

- 下一轮可继续补导入中心的移动端压缩布局。
- 如结果页视觉确认稳定，可再同步优化 `管理看板` 或 `导入中心` 的空态与错误态插画层。
