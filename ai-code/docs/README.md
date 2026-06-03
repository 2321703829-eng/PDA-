# docs

`docs/` 是 `ai-code/` 的主文档体系入口，负责承接项目正式基线、架构、实施和治理说明。

## 建议阅读顺序

1. [context/README.md](./context/README.md)
2. [architecture/README.md](./architecture/README.md)
3. [spec/README.md](./spec/README.md)
4. [topic_design/README.md](./topic_design/README.md)
5. [dev/README.md](./dev/README.md)
6. [review/README.md](./review/README.md)
7. [change_notes/README.md](./change_notes/README.md)
8. [archive/README.md](./archive/README.md)
9. [versioning/README.md](./versioning/README.md)

## 当前分区

- [context/](./context/)
  业务基线、Odoo 复用判断、上下文与可行性文档。
- [architecture/](./architecture/)
  系统结构、模块边界、现行模块设计与历史桥接稿。
- [spec/](./spec/)
  正式规范层，承接治理规则、命名规则、生效规则与长期执行约束。
- [topic_design/](./topic_design/)
  专题设计在 `docs/` 主体系中的正式入口层，统一指向 `专题设计/` 正文体系。
- [dev/](./dev/)
  实施清单、升级验证、执行方案和结构治理说明。
- [review/](./review/)
  治理清单、评审结论和示例材料。
- [change_notes/](./change_notes/)
  每次真实代码或文档变更的留痕记录。
- [archive/](./archive/)
  历史归档规则入口，说明历史资料当前应如何理解与退场。
- [ai/](./ai/)
  提示词、技能路由与 AI 协作规则。

## 平行专题设计包

- [topic_design/README.md](./topic_design/README.md)
  `docs/` 侧的专题设计正式入口层。
- [专题设计/README.md](../专题设计/README.md)
  专题设计统一正文根入口。
- [前端设计](../专题设计/前端设计/README.md)
  一期到四期前端阶段化设计。
- [仓管设计](../专题设计/仓管设计/README.md)
  仓储与库内作业专题设计。
- [企业隔离设计](../专题设计/企业隔离设计/README.md)
  企业隔离、多租户边界与分期方案。
- [高并发优化设计](../专题设计/高并发优化设计/README.md)
  查询承载、热点 SQL 与性能优化方案。
- [六期后端性能优化设计](../专题设计/六期后端性能优化设计/README.md)
  六期后端性能优化、分期落地与验收收口专题。

## 兼容与退场

- 专题目录物理归并后的旧根目录退场规则，见 [dev/topic_design_legacy_root_retirement_plan.md](./dev/topic_design_legacy_root_retirement_plan.md)。
- 如果在仓库里看到 `前端设计/`、`仓管模块设计/`、`企业分离功能文件夹/`、`高并发承载能力优化设计/` 这些旧根目录名，请按 [dev/topic_design_repo_wide_trace_notice.md](./dev/topic_design_repo_wide_trace_notice.md) 理解其历史映射关系。
- 这 4 个旧根目录当前已经移除，不再作为真实目录存在。

## 当前治理基线

- 设计文件治理正式规范见 [spec/design_document_governance_spec.md](./spec/design_document_governance_spec.md)
- 目录治理检查清单见 [review/checklists/document_directory_governance.md](./review/checklists/document_directory_governance.md)
- 文档同步规则见 [review/checklists/doc_sync.md](./review/checklists/doc_sync.md)
