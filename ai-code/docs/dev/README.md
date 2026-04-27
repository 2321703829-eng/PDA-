# docs/dev

`docs/dev/` 用于维护实施、升级验证、专题执行清单和结构治理说明。

## 状态标识规则

- `现行`：当前默认应阅读、应维护的实施、验证与治理文档。
- `archive`：已过期计划、已执行留档或只保留回溯价值的旧执行稿。
- `draft`：测试数据草案、待确认执行材料或尚未升格为正式 runbook 的辅助稿。

## 建议阅读顺序

1. [upgrade_and_verify.md](./upgrade_and_verify.md)
2. [manual_verify_checklist.md](./manual_verify_checklist.md)
3. [structural_governance_one_page_plan.md](./structural_governance_one_page_plan.md)
4. [historical_plan_index.md](./historical_plan_index.md)
5. 再按当前任务进入对应专题文档

## 现行入口

- 升级与验证
  - [upgrade_and_verify.md](./upgrade_and_verify.md)
  - [manual_verify_checklist.md](./manual_verify_checklist.md)
- 结构治理与阶段推进
  - [structural_governance_one_page_plan.md](./structural_governance_one_page_plan.md)
  - [phase4_first_round_scope_alignment_upgrade_runbook.md](./phase4_first_round_scope_alignment_upgrade_runbook.md)
  - [topic_design_legacy_root_retirement_plan.md](./topic_design_legacy_root_retirement_plan.md)
  - [topic_design_repo_wide_trace_notice.md](./topic_design_repo_wide_trace_notice.md)
  - [source_material_naming_and_archive_levels.md](./source_material_naming_and_archive_levels.md)
  - [custom_addons_module_status_inventory.md](./custom_addons_module_status_inventory.md)
  - [custom_addons_responsibility_and_dependency_map.md](./custom_addons_responsibility_and_dependency_map.md)
- 页面冲突与专项清单
  - [page_conflict_resolution_checklist.md](./page_conflict_resolution_checklist.md)
  - [delivery_node_page_gap_checklist.md](./delivery_node_page_gap_checklist.md)
- 数据、字段与导入专题
  - [customer_store_single_object_consolidation_plan.md](./customer_store_single_object_consolidation_plan.md)
  - [goods_master_customer_relation_execution_three_layer_plan.md](./goods_master_customer_relation_execution_three_layer_plan.md)
  - [logistics_customer_product_profile_schema_checklist.md](./logistics_customer_product_profile_schema_checklist.md)
  - [logistics_product_unit_plan_b_field_and_import_impact_checklist.md](./logistics_product_unit_plan_b_field_and_import_impact_checklist.md)
  - [project_coordination/README.md](./project_coordination/README.md)
  - [test_data/README.md](./test_data/README.md)
- 高并发专题
  - [高并发查询调查清单_v1.md](./高并发查询调查清单_v1.md)
  - [高并发查询优化方案_v1.md](./高并发查询优化方案_v1.md)
  - [热点SQL结论与优化优先级_v1.md](./热点SQL结论与优化优先级_v1.md)

## 历史计划与草案入口

- [historical_plan_index.md](./historical_plan_index.md)
  - 统一列出 `archive` 与 `draft` 状态的计划稿、已执行留档和测试草案。
- [next_step_plan_2026-04-10.md](./next_step_plan_2026-04-10.md)
  - 已过期计划稿。
- [topic_design_physical_reorg_execution_plan.md](./topic_design_physical_reorg_execution_plan.md)
  - 已执行留档。
- [首次页面验证测试数据草案.md](./首次页面验证测试数据草案.md)
  - 测试数据草案。

## 当前口径

- `docs/dev/README.md` 只做导航，不替代原始执行文档。
- 新的实施清单优先放入 `docs/dev/`，并在标题或文件名里体现专题边界。
- 如文档同时具备“治理规则”和“执行说明”属性，优先按主要用途归类。
- 专题目录归并后的旧根目录退场与历史路径理解，统一以 `topic_design_legacy_root_retirement_plan.md` 和 `topic_design_repo_wide_trace_notice.md` 为准。
- Office、Excel 与来源资料的命名和归档等级，统一以 `source_material_naming_and_archive_levels.md` 为准。
- `custom_addons/` 的现行模块与历史占位目录状态，统一以 `custom_addons_module_status_inventory.md` 为准。
- `custom_addons/` 的职责与依赖理解，统一以 `custom_addons_responsibility_and_dependency_map.md` 为准。

