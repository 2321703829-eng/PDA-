# doc_sync

## 1. 目的

防止代码、文档、目录说明和验证规则长期漂移，确保项目上下文、模块边界、架构入口和升级校验口径持续有效。

## 2. 触发场景

- 改模型
- 改目录结构
- 改 `addons_path` 或运行方式
- 改项目边界
- 改 AI 协作规则
- 准备打 `baseline / milestone / release` tag

## 3. 每次都要检查的问题

- `AGENTS.md` 是否过期
- `docs/ai/` 是否过期
- `docs/context/` 是否过期
- `docs/architecture/ARCHITECTURE.md` 是否过期
- `docs/spec/` 是否过期
- `docs/topic_design/` 是否过期
- `docs/dev/upgrade_and_verify.md` 是否过期
- `docs/versioning/version_tag_governance.md` 是否过期
- `docs/review/checklists/document_directory_governance.md` 是否过期
- `docs/archive/` 是否过期
- `docs/change_notes/` 是否已补写

## 4. 同步规则

### 改模型后

检查：

- 业务定义是否变化
- 模块关系是否变化
- 可实现性判断是否变化
- 是否影响正式规范或专题设计主文档

### 改目录结构或运行方式后

检查：

- `ARCHITECTURE.md`
- `docs/README.md`
- `docs/spec/`
- `docs/topic_design/`
- `upgrade_and_verify.md`
- `document_directory_governance.md`

### 改项目边界后

检查：

- `AGENTS.md`
- `docs/ai/`
- `docs/context/`
- `docs/architecture/`
- `docs/spec/`
- `docs/topic_design/`

### 改 API、状态流转、页面结构、对象命名后

检查：

- 当前主规范是否变化
- 相关专题方案是否变化
- `change_notes` 是否已经同步说明

### 准备打 tag 前

检查：

- 当前是否已明确属于 `baseline / milestone / release` 哪一层
- 当前正式入口文档是否同步
- 当前 change note 是否已补

## 5. 输出要求

- 标出受影响文档
- 说明是否必须同步更新
- 若暂不更新，说明原因
- 在 `change_notes` 中记录本轮同步更新了哪些文档
- 明确本轮主文档是否发生切换

## 6. 文档漂移排查清单

- 一期、二期或当前阶段边界是否一致
- 模块命名是否一致
- addon 依赖关系是否一致
- 自定义 addon 规划是否一致
- 验证步骤是否仍适用
- 当前目录现实和文档快照是否一致
- 当前有效、桥接、历史、草稿角色是否区分清楚
- 同主题是否只保留一个主文档
- 新增文档命名是否符合 `YYYY-MM-DD_主题_文档类型_状态.md`
- 如果是 `change_notes`，是否仍符合其例外命名规则 `YYYY-MM-DD_topic_summary.md`

## 7. 仓库规则同步补充

当仓库级工作规则发生变化时，同轮检查以下内容：

- `AGENTS.md`
- `docs/ai/`
- 仓库内 `.codex` skill 指引（如果存在）
- `docs/change_notes/`

如果本轮只更新了 `AGENTS.md`，需要在 `change_notes` 中写明为什么其他文档暂时不需要同步修改。

## 8. 关联规范

- [version_tag_governance.md](/d:/Desktop/Odoo/ai-code/docs/versioning/version_tag_governance.md:1)
- [document_directory_governance.md](/d:/Desktop/Odoo/ai-code/docs/review/checklists/document_directory_governance.md:1)
- [design_document_governance_spec.md](/d:/Desktop/Odoo/ai-code/docs/spec/design_document_governance_spec.md:1)
