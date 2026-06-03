# 2026-04-23 四 Sheet 中文正式模板样稿落地
## Objective

- 产出一份可直接查看的四 Sheet 中文正式模板样稿。
- 让系统下载的 `zh_CN` 四 Sheet 模板也同步使用更完整的正式示例行。

## Scope

- 更新 [waybill_standard_import_service_v2.py](</d:/Desktop/Odoo/custom_addons/logistics_web/services/waybill_standard_import_service_v2.py>) 的四 Sheet 示例行。
- 导出设计目录样稿文件：
  - [2026-04-23_四 Sheet 中文正式模板样稿.xlsx](</d:/Desktop/Odoo/ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-23_四 Sheet 中文正式模板样稿.xlsx>)

## Result

- `Waybill / CustomerLine / OrderLine / GoodsLine` 四个 Sheet 现在都带有更完整的中文示例数据，不再只是稀疏示例。
- 示例内容已经对齐当前四 Sheet 正式导入链路：
  - `Waybill`：波次、批次、运单主链
  - `CustomerLine`：客户/门店画像与配送约束
  - `OrderLine`：订单与单据状态字段
  - `GoodsLine`：数量、金额、重量、体积等货物事实字段
- 本地 Odoo 已重启，运行态下载 `template_locale=zh_CN` 时会返回这版更新后的样稿内容。

## Verify

- 样稿文件已成功生成到设计目录。
- 本地运行态下载验证通过：
  - `Waybill`：3 行 10 列
  - `CustomerLine`：4 行 51 列
  - `OrderLine`：4 行 24 列
  - `GoodsLine`：5 行 33 列

## Boundary

- 本轮保留英文 Sheet 名：
  - `Waybill`
  - `CustomerLine`
  - `OrderLine`
  - `GoodsLine`
- 中文化范围是列头与示例内容，不改变四 Sheet 解析所依赖的 Sheet 结构。
