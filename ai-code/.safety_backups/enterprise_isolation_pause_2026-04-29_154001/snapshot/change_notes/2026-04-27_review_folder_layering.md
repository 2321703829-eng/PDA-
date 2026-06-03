# 2026-04-27 Review Folder Layering

## Objective

- 为 `docs/review/` 建立更清晰的分层结构
- 把 review 文档按“示范 / 清单 / 结论”三类组织起来
- 在不打断历史引用的前提下，提升目录可读性和后续维护规范性

## Changed Files

- 更新 `README.md`
- 新增 `docs/review/README.md`
- 新增 `docs/review/examples/`
- 新增 `docs/review/checklists/`
- 新增 `docs/review/findings/`
- 复制现有 review 文档到对应正式分层位置

## Classification

### examples

- `skill_chain_demo_from_waybill_export/`

### checklists

- `doc_sync.md`
- `document_directory_governance.md`
- `当前可默认跳过的文件清单.md`
- `文档回调清单_v1_运单主对象调整.md`
- `过期文档处理清单_2026-04-13.md`

### findings

- `agent_kit_upstream_screening_round1.md`
- `local_skill_calibration_round1_from_waybill_export.md`
- `page_conflict_final_acceptance_2026-04-23.md`

## Current Decision

- 三个子目录作为后续正式维护位置
- `docs/review/` 顶层旧文件先保留兼容，不做硬迁移
- 后续新增 review 文档默认进入对应子目录，而不是继续散落在顶层

## Verify

- 检查 `docs/review/README.md` 是否存在
- 检查 `examples/`、`checklists/`、`findings/` 是否存在
- 检查各分类下是否已有对应文档副本
- 检查 `README.md` 是否已反映新的 review 目录结构

## Risks

- 由于保留了顶层兼容副本，短期内会出现“同名文档在两处可见”的状态
- 历史文档和 change note 仍可能继续引用顶层路径，这是兼容保留而不是错误

## Next Suggestion

- 下一轮如果确认历史引用影响可控，可以逐步把顶层旧文件改成 redirect 壳
- 后续新增 review 文档时，先从 `docs/review/README.md` 选择正确层级
