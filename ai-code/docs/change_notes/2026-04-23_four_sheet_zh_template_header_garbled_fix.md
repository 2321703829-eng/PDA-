# 2026-04-23 四 Sheet 中文模板表头乱码修复
## Objective

- 修复四 Sheet 中文模板中表头显示为 `??` 的问题。
- 重新产出可直接给业务查看的中文正式模板样稿。

## Root Cause

- `waybill_standard_import_service_v2.py` 中 `FIELD_LABELS` 的中文列头未被正确维护，实际写入的是占位式 `?? / ????` 文案。
- 导致 `template_locale=zh_CN` 下载出来的 Excel 虽然是中文模板分支，但列头本身已经坏掉。

## Scope

- 更新 [waybill_standard_import_service_v2.py](</d:/Desktop/Odoo/custom_addons/logistics_web/services/waybill_standard_import_service_v2.py>) 的 `FIELD_LABELS`。
- 重新导出样稿文件：
  - [2026-04-23_四 Sheet 中文正式模板样稿_修正版.xlsx](</d:/Desktop/Odoo/ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-23_四 Sheet 中文正式模板样稿_修正版.xlsx>)

## Result

- `Waybill` 表头已恢复为：
  - `仓库 / 预出库日期 / 波次号 / 批次号 / 运单号 / 组织 / 线路 / 司机 / 司机电话 / 主表备注`
- `CustomerLine` 表头已恢复为：
  - `运单号 / 门店节点编号 / 客户编号 / 客户名称 / 联系人 / 联系电话 / 组织 / 部门名称 / 业务员 / 渠道 ...`
- `OrderLine` 表头已恢复为：
  - `订单行编号 / 运单号 / 门店节点编号 / 单据号 / 销售订单号 / 来源参考号 / 第三方单据号 / 单据类型 ...`
- `GoodsLine` 表头已恢复为：
  - `订单行编号 / 货号 / 商品名称 / 规格 / 条码 / 品牌 / 类别 / 基本单位 / 单据单位 / 小单位 ...`

## Verify

- 本地导出的修正版样稿已通过脚本逐列检查。
- 本地 Odoo 已重启并验证运行态下载：
  - `template_locale=zh_CN` 返回的表头已是正常中文，不再出现 `??`。

## Boundary

- 首次修复时原始文件一度因本地程序占用，未能立即原地覆盖，因此先输出了修正版文件：
  - `2026-04-23_四 Sheet 中文正式模板样稿_修正版.xlsx`
- 在文件释放后，已将修正版内容覆盖回原始文件：
  - [2026-04-23_四 Sheet 中文正式模板样稿.xlsx](</d:/Desktop/Odoo/ai-code/前端设计/四期前端优化设计/01_专题方案/2026-04-23_四 Sheet 中文正式模板样稿.xlsx>)
