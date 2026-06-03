# 2026-04-23 `waybill_standard_import_service_v2` 四 Sheet 正式导入实现

## 本次变更

- 将 `D:\Desktop\Odoo\custom_addons\logistics_web\services\waybill_standard_import_service_v2.py` 的默认标准模板定义切到四 Sheet：
  - `Waybill`
  - `CustomerLine`
  - `OrderLine`
  - `GoodsLine`
- 新增四 Sheet 工作簿解析入口，标准模板优先按四 Sheet 解析，旧单表和旧三 Sheet 仍保留兼容入口。
- 预校验新增四 Sheet 主链规则：
  - `Waybill` 运单唯一、波次/批次一致性、仓库命中、现有运单冲突
  - `CustomerLine` 父运单命中、运单内 `customer_line_no` 唯一
  - `OrderLine` 父门店节点命中、`order_line_no` 文件内唯一、`source_doc_no / sales_order_no` 二选一
  - `GoodsLine` 父订单行命中、`product_name / doc_qty` 校验
- 正式导入新增四 Sheet 主链落库顺序：
  - `wave`
  - `batch`
  - `waybill`
  - `customer_line`
  - `order_line`
  - `goods_line`
- 导入结果统计补充了 `created_order_line_count` 和 `written_order_line_count`。

## 影响范围

- 标准模板下载与模板元信息接口
- 导入预校验
- 正式导入执行
- 导入结果统计

## 当前边界

- 本次以“现有模型可稳定落库的字段”为主完成正式导入主链，`order_line` 已正式接入。
- 四 Sheet 模板中的部分扩展业务列已支持解析和预校验，但由于当前模型字段尚未完全覆盖，正式导入阶段未全部写入数据库。
- 旧单表与旧三 Sheet 兼容链路本次未删除，仍可作为过渡入口。

## 已完成校验

- Python `ast.parse` 通过
- 关键实现入口存在性复核通过：
  - `FORMAL_INPUT_MODE`
  - `_parse_formal_workbook`
  - `_validate_formal_rows`
  - `_execute_formal_task_import`
  - `created_order_line_count`

