# 2026-05-07 小程序原始单表导入设计稿

## Objective

补一份正式专题设计稿，定义“小程序原始单表导入模式”的系统化落地方案，替代继续依赖线下脚本和 Excel `VLOOKUP` 的长期路径。

## Outcome

本轮文档完成后，仓库内已经新增一份可直接指导后续实现拆分的正式设计说明，明确了：

1. 小程序端可以作为导入入口
2. `发车单号` 直接作为 `batch_no`
3. 匹配失败时允许预校验，但不允许正式 confirm 导入
4. 服务端负责 merged cells 解析、标准化、去重、客户匹配和正式落库
5. 文档已覆盖 `Outcome / Behavior / Boundary / 接口草案 / 预校验规则 / 数据模型建议 / 页面交互草图`

## Files

- [2026-05-07_小程序原始单表导入模式设计.md](D:\Desktop\ai-code\专题设计\小程序导入设计\2026-05-07_小程序原始单表导入模式设计.md)

## Summary

### 1. 新增专题设计目录

- 新建 `ai-code/专题设计/小程序导入设计/`
- 作为本次原始导入专题的正式沉淀目录

### 2. 新增正式设计稿

设计稿明确了：

- 小程序端只做上传入口、预校验触发、结果回显、确认导入
- 不把复杂解析和匹配逻辑下沉到小程序本地
- 新导入模式建议以独立 object type `mini_program_raw_sheet` 落地
- 建议复用现有导入任务模型，并新增 staging 承接原始解析行与停靠点候选结果
- confirm 阶段默认写入 route planning draft，而不是直接模拟线下模板中转

### 3. 收口了关键业务规则

- `发车单号 = batch_no`
- 去重键建议为 `batch_no + 标准化门店名 + 标准化地址`
- `matched_exact` 才允许正式 confirm
- `matched_name_only / matched_ambiguous / unmatched` 均不可正式 confirm

## Verify

本轮为文档设计稿落地，已完成：

1. 对照当前项目 AGENTS 约定补齐设计文档
2. 结合现有 `mini` 接口、`route-planning` 导入、`phase5-workbook` 导入口径收口设计
3. 对照真实样例文件确认原始表、模板 V1、客户底表三层关系

## Next Suggestion

建议下一步直接进入实现前规格冻结：

1. 明确客户信息底表的正式系统来源
2. 决定是否本轮就新增 staging 模型
3. 输出一份后端实施任务拆分
4. 再进入 `Understand -> Spec -> Plan -> Implement`
