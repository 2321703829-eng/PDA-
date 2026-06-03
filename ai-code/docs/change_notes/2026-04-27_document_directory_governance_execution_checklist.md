# 2026-04-27 文档目录治理执行清单

## Objective

- 仅收口 `docs/` 内当前阅读入口、目录命名口径和重复入口问题
- 不改业务设计结论，不改模块边界，不改历史 change note 正文

## Boundary

- 本轮只处理 `docs/context/`、`docs/architecture/`、`docs/review/`、`docs/change_notes/`
- 不批量改历史 `docs/change_notes/` 中的旧路径记录
- 不改 `前端设计/` 正文内容，只修 `docs/` 对它的引用入口

## Current Understanding

- 当前最影响阅读效率的不是业务文档缺失，而是入口文档仍引用旧路径 `前端相关设计/`
- `docs/review/` 顶层存在与 `checklists/`、`findings/` 的同名双副本，容易形成双维护
- review 治理文档中已经形成正式子目录结构，适合把顶层旧文件收口为兼容跳转页

## Executed This Round

1. 修正当前核心入口文档里的前端设计路径引用。
2. 将 `docs/review/` 顶层同名旧文件收口为 redirect 入口。
3. 明确 `checklists/` 与 `findings/` 才是 `docs/review/` 的正式维护位置。
4. 在治理类 checklist 中补充“旧路径到当前路径”的统一映射说明。

## File Checklist

### A. 核心入口文档

- [odoo_logistics_context.md](/D:/Desktop/Odoo/ai-code/docs/context/odoo_logistics_context.md:1)
  - 统一 `前端相关设计/` 为 `前端设计/一期前端相关设计/`
- [ARCHITECTURE.md](/D:/Desktop/Odoo/ai-code/docs/architecture/ARCHITECTURE.md:1)
  - 更新架构入口引用到当前真实前端目录
- [logistics_web_addon_design.md](/D:/Desktop/Odoo/ai-code/docs/architecture/logistics_web_addon_design.md:1)
  - 更新关联前端资料入口到当前真实目录
- [logistics_trace_evidence_addon_design.md](/D:/Desktop/Odoo/ai-code/docs/architecture/logistics_trace_evidence_addon_design.md:1)
  - 更新证据层所依赖的前端文档入口
- [Odoo原生模块复用源码入口索引.md](/D:/Desktop/Odoo/ai-code/docs/context/Odoo原生模块复用源码入口索引.md:1)
  - 更新引用的一期前端模块设计路径

### B. review 路由与命名

- [docs/review/README.md](/D:/Desktop/Odoo/ai-code/docs/review/README.md:1)
  - 明确 `README` 只做路由
  - 明确 `checklists/`、`findings/`、`examples/` 是正式维护目录
- 顶层 redirect 入口：
  - [document_directory_governance.md](/D:/Desktop/Odoo/ai-code/docs/review/document_directory_governance.md:1)
  - [doc_sync.md](/D:/Desktop/Odoo/ai-code/docs/review/doc_sync.md:1)
  - [当前可默认跳过的文件清单.md](/D:/Desktop/Odoo/ai-code/docs/review/当前可默认跳过的文件清单.md:1)
  - [文档回调清单_v1_运单主对象调整.md](/D:/Desktop/Odoo/ai-code/docs/review/文档回调清单_v1_运单主对象调整.md:1)
  - [过期文档处理清单_2026-04-13.md](/D:/Desktop/Odoo/ai-code/docs/review/过期文档处理清单_2026-04-13.md:1)
  - [agent_kit_upstream_screening_round1.md](/D:/Desktop/Odoo/ai-code/docs/review/agent_kit_upstream_screening_round1.md:1)
  - [local_skill_calibration_round1_from_waybill_export.md](/D:/Desktop/Odoo/ai-code/docs/review/local_skill_calibration_round1_from_waybill_export.md:1)
  - [page_conflict_final_acceptance_2026-04-23.md](/D:/Desktop/Odoo/ai-code/docs/review/page_conflict_final_acceptance_2026-04-23.md:1)

### C. canonical checklist 同步

- [document_directory_governance.md](/D:/Desktop/Odoo/ai-code/docs/review/checklists/document_directory_governance.md:1)
  - 明确当前前端设计正式入口的阶段目录口径
- [doc_sync.md](/D:/Desktop/Odoo/ai-code/docs/review/checklists/doc_sync.md:1)
  - 链接改为指向 canonical checklist 路径
- [过期文档处理清单_2026-04-13.md](/D:/Desktop/Odoo/ai-code/docs/review/checklists/过期文档处理清单_2026-04-13.md:1)
  - 增加旧路径到当前阶段目录的映射说明
- [当前可默认跳过的文件清单.md](/D:/Desktop/Odoo/ai-code/docs/review/checklists/当前可默认跳过的文件清单.md:1)
  - 增加旧路径映射说明，并把最关键的目录示例改到当前真实路径

## Naming Rules Applied

- 当前前端设计默认主入口统一使用 `前端设计/一期前端相关设计/`
- 二期及以后专题统一按阶段目录命名理解，不再笼统写成 `前端相关设计/`
- `docs/review/` 顶层旧文件保留原文件名，但角色统一改成 `Redirect`

## Verify

- 核心入口文档已不再把现行入口写成不存在的 `ai-code/前端相关设计/...`
- `docs/review/README.md` 已能说明 canonical 维护位置
- `docs/review/` 顶层同名旧文件已不再承载双份正文

## Risks

- 历史 `docs/change_notes/` 仍会保留大量旧路径字符串，这是有意保留的历史记录，不在本轮清理范围
- `前端设计/` 目录内部仍有不少旧自引用，后续如果要继续治理，应单独开一轮“前端设计目录内部路径收口”

## Next Suggestion

1. 下一轮单独治理 `前端设计/` 内部的历史路径自引用。
2. 评估是否将 `docs/change_notes/` 按月份或阶段拆层，降低当前单目录检索成本。
