# docs/review

## 目的

作为 `docs/review/` 的统一入口，帮助团队区分：

- 哪些是示范样例
- 哪些是检查清单或治理规则
- 哪些是审查结论、筛选结果或验收输出

## 当前入口规则

- `docs/review/README.md` 只负责路由，不承担长期正文维护
- `docs/review/checklists/` 是清单类和治理类文档的正式维护目录
- `docs/review/findings/` 是评审结论、筛选结论、验收结论的正式维护目录
- `docs/review/examples/` 是示范样例和完整链路演示的正式维护目录
- `docs/review/` 顶层与子目录重名的旧文件只保留为兼容跳转入口，不再作为双份正文维护

## 正式分层

- [examples/](d:/Desktop/Odoo/ai-code/docs/review/examples)
  - 放端到端示范、样卷、完整链路演示
- [checklists/](d:/Desktop/Odoo/ai-code/docs/review/checklists)
  - 放 review 清单、同步规则、目录治理、文档回调清单
- [findings/](d:/Desktop/Odoo/ai-code/docs/review/findings)
  - 放筛选结论、校准结论、验收总结、风险判断

## 当前归类

### examples

- [skill_chain_demo_from_waybill_export](d:/Desktop/Odoo/ai-code/docs/review/examples/skill_chain_demo_from_waybill_export)

### checklists

- [doc_sync.md](d:/Desktop/Odoo/ai-code/docs/review/checklists/doc_sync.md)
- [document_directory_governance.md](d:/Desktop/Odoo/ai-code/docs/review/checklists/document_directory_governance.md)
- [当前可默认跳过的文件清单.md](d:/Desktop/Odoo/ai-code/docs/review/checklists/当前可默认跳过的文件清单.md)
- [文档回调清单_v1_运单主对象调整.md](d:/Desktop/Odoo/ai-code/docs/review/checklists/文档回调清单_v1_运单主对象调整.md)
- [过期文档处理清单_2026-04-13.md](d:/Desktop/Odoo/ai-code/docs/review/checklists/过期文档处理清单_2026-04-13.md)

### findings

- [agent_kit_upstream_screening_round1.md](d:/Desktop/Odoo/ai-code/docs/review/findings/agent_kit_upstream_screening_round1.md)
- [local_skill_calibration_round1_from_waybill_export.md](d:/Desktop/Odoo/ai-code/docs/review/findings/local_skill_calibration_round1_from_waybill_export.md)
- [page_conflict_final_acceptance_2026-04-23.md](d:/Desktop/Odoo/ai-code/docs/review/findings/page_conflict_final_acceptance_2026-04-23.md)

## 兼容说明

- `docs/review/` 顶层旧文件暂时保留，主要为了兼容历史链接和 change note
- 顶层同名旧文件已统一收口为跳转入口，后续请直接维护子目录中的正式文件
- 从现在开始，新增或继续维护 review 文档时，优先放进对应子目录
- 如果一个文档同时像“规则”又像“结论”，优先按它的主要用途归类

## 默认判断

- 想看“怎么做”：先看 `checklists/`
- 想看“做出来长什么样”：先看 `examples/`
- 想看“这轮结论是什么”：先看 `findings/`
