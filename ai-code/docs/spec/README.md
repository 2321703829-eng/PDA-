# docs/spec

`docs/spec/` 是项目正式规范层入口。

这里存放的不是背景说明，也不是单轮任务记录，而是当前需要被持续遵守的正式规则。

## 适合放什么

- 文档治理规范
- 命名规范
- 状态标识规范
- 生效规则
- 跨目录协同规则
- 需要长期复用的结构性规则

## 不适合放什么

- 单次评审结论
- 一次性联调清单
- 历史来源材料
- 草图与临时想法

## 当前入口

1. [design_document_governance_spec.md](./design_document_governance_spec.md)
2. [directory_index_readme_template.md](./directory_index_readme_template.md)

## 与其他目录的关系

- `context/` 负责解释项目当前业务基线与理解口径
- `architecture/` 负责系统架构和模块边界
- `spec/` 负责把需要长期执行的规则写成正式规范
- `topic_design/` 负责专题设计总入口与专题体系导航
- `review/` 负责检查、评审、验收与治理清单
- `change_notes/` 负责记录每轮真实变更
