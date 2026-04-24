# 2026-04-24 from_customer 与 from_product 首轮开发任务拆分单新增

## This round

- 新增客户画像导出与货物画像导出的首轮开发任务拆分单。
- 将正式冻结补丁稿进一步推进到可直接排期的工作包粒度。

## Added files

- [from_customer / from_product 首轮开发任务拆分单](</d:/Desktop/Odoo/ai-code/前端设计/四期前端优化设计/02_验收与联调/2026-04-24_from_customer_from_product首轮开发任务拆分单.md>)

## Key decisions

- 本轮开发拆成 8 个工作包：
  - `CPPR-EXP-M1`
  - `CP-EXP-S1`
  - `PP-EXP-S1`
  - `CPPR-EXP-C1`
  - `CPPR-EXP-F1`
  - `CP-EXP-F2`
  - `PP-EXP-F2`
  - `CPPR-EXP-V1`
- 模型层先补：
  - 新枚举值
  - `package_metrics_json`
  - `line_metrics_json`
- 服务层按对象边界拆成两条独立主链：
  - 客户画像导出服务
  - 货物画像导出服务
- 结果页继续复用现有 `export_result_action`，但按 `object_type` 增加摘要和行结果分支。
- 入口按钮继续复用运单当前模式：
  - 列表页 JS 发起
  - 详情页 object 按钮跳转结果页

## Next

- 直接按拆分单开始做 `CPPR-EXP-M1`
