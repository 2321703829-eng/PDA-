# 2026-04-24 运单标准导出补中心页入口

## Objective

- 补一条“运单标准导出”的统一入口，避免当前只有运单列表页按钮可见。

## Changed Code

- 更新 [import_center_action.js](</d:/Desktop/Odoo/custom_addons/logistics_web/static/src/js/actions/import_center_action.js>)
- 更新 [import_center_templates.xml](</d:/Desktop/Odoo/custom_addons/logistics_web/static/src/xml/import_center_templates.xml>)
- 更新 [四期批量导出模块设计方案](</d:/Desktop/Odoo/ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-24_四期批量导出模块设计方案.md>)

## Summary

- 导入中心新增 `运单标准导出` 区块。
- 该区块作为统一入口存在，不在中心页内直接做运单勾选。
- 用户从这里进入运单列表后，继续使用现有列表页 `导出` 按钮发起标准导出。

## Verify

- `import_center_action.js` 已通过 `node --check`
- `import_center_templates.xml` 已通过 XML 解析

## Boundary

- 本轮不新增独立“标准导出中心”
- 本轮不改动现有运单标准导出后端链路，只补入口可发现性
