# 2026-04-24 from_waybill 首轮开发任务拆分单补充

## Objective

- 把标准批量导出的首个真实切片 `from_waybill` 继续推进到可直接排期的开发任务粒度。
- 让模型、controller、service、前端结果页和联调闭环有明确工作包边界。

## Added Docs

- 新增 [from_waybill 首轮开发任务拆分单](</d:/Desktop/Odoo/ai-code/前端设计/四期前端优化设计/02_验收与联调/2026-04-24_from_waybill首轮开发任务拆分单.md>)

## Summary

- 把 `from_waybill` 首轮拆成 6 个工作包：
  - `WB-EXP-M1` 模型
  - `WB-EXP-S1` 服务
  - `WB-EXP-C1` controller
  - `WB-EXP-F1` 前端结果页
  - `WB-EXP-F2` 入口与跳转胶水
  - `WB-EXP-V1` smoke 与验收
- 每个工作包都补了：
  - 目标
  - 建议文件
  - 主要任务
  - 完成标准
- 明确了 `from_waybill` 是标准批量导出的首个真实纵向切片，完成后应作为 `from_batch / from_customer` 的复用底座。

## Boundary

- 本次只补任务拆分文档，不改代码实现。
- 本次不扩到图片导出、司机侧导出、导出中心。
- 本次不改变此前已冻结的落库、接口、权限和错误码口径。

## Compatibility

- 当前仅影响文档层，不直接影响现有模型、视图、权限或数据兼容性。
- 后续编码实现时，应继续以既有“正式落库与接口冻结稿”为契约，以本次任务拆分单为执行排期参考。
