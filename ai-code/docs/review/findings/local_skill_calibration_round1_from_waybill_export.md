# 本地 Skill 校准 Round 1

## 目标

- 用仓库里真实存在的 `from_waybill` 导出链路，试跑第二批与第三批本地化 skill
- 根据真实材料里出现的歧义点、边界点和输出痛点，收紧触发语与输出模板

## 试跑样本

本轮统一使用 `from_waybill` 首轮正式导出切片作为样本。

主要证据来源：

- [odoo_logistics_context.md](/d:/Desktop/Odoo/ai-code/docs/context/odoo_logistics_context.md)
- [ARCHITECTURE.md](/d:/Desktop/Odoo/ai-code/docs/architecture/ARCHITECTURE.md)
- [2026-04-24_四期批量导出模块设计方案.md](</d:/Desktop/Odoo/ai-code/专题设计/前端设计/四期前端优化设计/01_专题方案/2026-04-24_四期批量导出模块设计方案.md>)
- [2026-04-24_from_waybill首轮开发任务拆分单.md](</d:/Desktop/Odoo/ai-code/专题设计/前端设计/四期前端优化设计/02_验收与联调/2026-04-24_from_waybill首轮开发任务拆分单.md>)
- [dispatch_main_export_service.py](/d:/Desktop/Odoo/custom_addons/logistics_web/services/dispatch_main_export_service.py:1)
- [logistics_web_export.py](/d:/Desktop/Odoo/custom_addons/logistics_web/controllers/logistics_web_export.py:1)
- [2026-04-24_export_result_page_and_waybill_entry_wiring_landed.md](/d:/Desktop/Odoo/ai-code/docs/change_notes/2026-04-24_export_result_page_and_waybill_entry_wiring_landed.md)
- [2026-04-24_export_acl_fix_and_browser_smoke_passed.md](/d:/Desktop/Odoo/ai-code/docs/change_notes/2026-04-24_export_acl_fix_and_browser_smoke_passed.md)

## 试跑结论

### 1. `logistics-structured-prd`

试跑后发现最容易漏掉的不是“流程本身”，而是导出链里的正式契约面：

- 发起入口
- 主对象类型
- 入口类型
- 包结构
- 结果页回读链
- 明确不做的能力

因此本轮把输出模板收紧成更偏“可继续推进”的结构，并补了典型触发语与误触发排除场景。

### 2. `structured-requirement-review`

试跑后发现，如果只写“review 需求”，很容易和一致性检查、技术方案评审打架。真正高频的问题是：

- 这份规格能不能开始开发
- 哪些定义还不稳定
- 哪些验收写得太虚

因此本轮把触发语收口到“需求质量评审”，并要求 findings 尽量包含严重级别、位置、影响和建议改写方式。

### 3. `odoo-backend-tech-proposal`

试跑 `from_waybill` 导出时，最关键的不是空泛的“后端方案”，而是：

- Odoo 原生导出为什么不够
- 为什么选择复用导入任务链风格而不直接复用 `import_task`
- 契约面到底冻结了什么

因此本轮把输出模板里的 `Benchmark` 收紧成 `Odoo Benchmark`，并新增 `Contract Surface`，要求显式写出模型、路由、任务链、权限与升级影响。

### 4. `cross-doc-consistency-check`

试跑后最有价值的检查维度，不是泛泛的“术语是否一致”，而是这条链的正式合同面是否前后一致：

- `object_type`
- `entry_type`
- `package_structure`
- 路由集合
- 返回壳
- 状态枚举
- 结果页跳转链

因此本轮为这个 skill 增加了更明确的触发语、误触发排除条件，以及 `Conflict Surface` 输出段。

### 5. `odoo-module-overview`

试跑后发现，最容易跑偏的点是：明明只想看 `logistics_web` 里的导出切片，结果写成第二份整仓架构说明。

因此本轮明确：

- 它只做模块级或专题级概览
- 可以覆盖一个切片，但不能偷偷扩成全仓总览
- 输出先写 `Scope`，再写边界和入口

## 本轮收紧动作

- 给 5 个 skill 都补了更具体的“典型触发语”
- 给 5 个 skill 都补了“不要用于什么场景”
- 将输出模板改得更窄，减少和相邻 skill 的职责重叠
- 对 `from_waybill` 这类任务链场景，额外强调主对象、入口类型、包结构、结果链这些正式契约点

## 当前建议

- 写需求时优先用 `logistics-structured-prd`
- 审需求质量时优先用 `structured-requirement-review`
- 做模型 / 路由 / service 方案时优先用 `odoo-backend-tech-proposal`
- 回看 spec、实现和 change notes 时优先用 `cross-doc-consistency-check`
- 给新人或新任务补局部上下文时优先用 `odoo-module-overview`

## 残余风险

- 这轮仍属于“文档与真实材料对照校准”，不是自动化触发层的最终验证
- 本地 skill 目前还没有纳入系统级自动 discover 列表，当前更多是作为项目内约定与可复用模板使用

