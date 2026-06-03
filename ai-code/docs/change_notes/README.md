# docs/change_notes

`docs/change_notes/` 用于记录每次真实代码或文档变更的留痕。

## 当前目录状态

- 顶层仍保留扁平存放，兼容既有链接和检索习惯
- 截至 `2026-04-27`，顶层 Markdown 已超过 `660` 份，单靠文件列表浏览成本很高
- 从本轮开始，优先通过 `README + indexes/` 提供导航，而不是直接在顶层翻文件

## 建议入口

1. [_template.md](./_template.md)
2. [indexes/2026-04.md](./indexes/2026-04.md)
3. [indexes/2026-05.md](./indexes/2026-05.md)
4. 需要版本基线时，补读 [../versioning/README.md](../versioning/README.md)

## 当前检索规则

- 先按日期找：文件名前缀统一为 `YYYY-MM-DD_`
- 再按主题筛：常见主题前缀包括 `phase4_`、`import_`、`execution_page_`、`database_design_`、`driver_`、`frontend_`、`tag_`
- 需要追某次治理动作时，优先先看月索引，再回到具体 note

## 文件命名规则

- 例外格式：`YYYY-MM-DD_topic_summary.md`
- 同一天多次迭代时，保持日期不变，靠主题段区分
- 文件名优先写“发生了什么”，而不是写模糊状态词
- 这是设计文件总治理规范下的目录级例外；正式规则见 [../spec/design_document_governance_spec.md](../spec/design_document_governance_spec.md)

## 目录治理规则

- 顶层保留历史 note，不做本轮大规模搬迁
- 后续新增月份时，在 `indexes/` 下补对应月索引，例如 `indexes/2026-05.md`
- 如某个月份 note 数量继续膨胀，再考虑第二阶段治理：
  - 按月分目录
  - 或按月保留扁平文件，但新增更细的专题索引

## 当前可读入口

- [indexes/2026-04.md](./indexes/2026-04.md)
  - 汇总 `2026-04` 每天的 note 数量、主要主题和建议检索词
- [indexes/2026-05.md](./indexes/2026-05.md)
  - 汇总 `2026-05` 每天的 note 数量、主要主题和建议检索词

## 使用边界

- `README.md` 和 `indexes/` 负责导航，不替代原始 change note
- 具体事实、改动范围和验证结果仍以对应 note 正文为准
