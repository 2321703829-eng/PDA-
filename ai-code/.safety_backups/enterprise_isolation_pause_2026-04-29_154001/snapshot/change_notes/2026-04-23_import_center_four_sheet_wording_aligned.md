# 2026-04-23 导入中心四 Sheet 文案对齐
## Objective

- 修正导入中心页面仍显示“V3 单表标准模板”的旧口径。
- 让模板下载区与当前四 Sheet 正式模板基线保持一致。

## Scope

- 更新 [import_center_action.js](</d:/Desktop/Odoo/custom_addons/logistics_web/static/src/js/actions/import_center_action.js>) 的页面文案。

## Result

- 导入中心主文案已从“单表标准模板”改为“四 Sheet 标准模板”。
- 模板下载提示已改为：
  - 当前默认使用 `V3 四 Sheet 标准模板`
  - 旧单表与旧三张工作表口径仅保留兼容，不再是默认入口
- 各入口提示也已改为围绕：
  - `Waybill`
  - `CustomerLine`
  - `OrderLine`
  - `GoodsLine`
  四个工作表来说明填写重点。

## Verify

- `import_center_action.js` 已通过 `node --check`。
- 本地 Odoo 已重启，新的页面文案已具备运行条件。

## Boundary

- 若浏览器还显示旧文案，优先做一次强制刷新，避免命中旧前端缓存。
