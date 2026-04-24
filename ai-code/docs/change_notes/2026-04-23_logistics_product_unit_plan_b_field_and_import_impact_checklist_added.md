# 2026-04-23 `logistics_product_unit` 方案 B 字段与导入影响清单补充

## 背景

业务确认 `logistics_product_unit` 应正式采用方案 B：

- 一条记录只表达一个销售单位
- 不再在同一行里混放小/中/大单位的跨单位字段

同时需要明确这套结构对导入模板、命中逻辑、页面展示和执行层的影响。

## 本次输出

新增文档：

- `ai-code/docs/dev/logistics_product_unit_plan_b_field_and_import_impact_checklist.md`

## 文档内容摘要

文档明确了：

1. 保留字段清单
   - 当前单位自己的条码、价格、重量、体积、换算系数等

2. 建议删除字段清单
   - `small_unit_weight`
   - `middle_unit_weight`
   - `small_unit_volume`
   - `middle_unit_volume`
   - `large_unit_qty`
   - `volume_unit_large`
   - `gross_weight_unit_large`

3. 导入改造影响
   - 模板要从“一行多单位”改成“多行多单位”
   - 命中逻辑要以 `product_tmpl_id + spec_desc + sale_unit_name` 为核心
   - 校验、错误提示、回写逻辑都要按“当前行只表达当前单位”重写

4. 工作量判断
   - 数据库层：中等偏小
   - 导入层：中等偏大
   - 页面层：中等

## 目的

把方案 B 从“原则判断”推进到“可直接实施的字段和导入清单”，为后续实际改设计稿、改导入、改页面做准备。
