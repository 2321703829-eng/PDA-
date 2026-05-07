# doc-sync-review

## 目的

在改代码或改结构后，扫描哪些文档需要同步更新。

## 使用场景

- 改模型
- 改目录
- 改边界
- 改运行方式

## 检查步骤

1. 列出本轮改动的文件
2. 判断改动属于模型、结构、边界、运行方式中的哪一类
3. 对照 `docs/review/doc_sync.md` 确定受影响文档
4. 若需要更新文档，立即补齐
5. 生成或更新 `docs/change_notes/` 记录

## 检查项

- `AGENTS.md` 是否需要同步
- `docs/ai/` 是否需要同步
- `docs/context/` 是否需要同步
- `ARCHITECTURE.md` 是否需要同步
- `upgrade_and_verify.md` 是否需要同步
- `change_notes` 是否已补写
