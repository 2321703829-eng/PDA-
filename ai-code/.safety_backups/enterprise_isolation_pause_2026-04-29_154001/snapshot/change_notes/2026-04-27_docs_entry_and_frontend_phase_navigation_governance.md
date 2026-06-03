# 2026-04-27 docs 入口层与前端阶段导航治理

## 本次目标

- 为 `docs/` 补齐总入口和主要分区入口
- 为 `docs/change_notes/` 增加可检索导航，降低扁平目录浏览成本
- 统一 `前端设计/` 的阶段说明和层级口径，但不改物理目录名

## 本次边界

- 不改业务设计结论
- 不批量重命名历史目录
- 不搬迁现有 `change_notes` 正文文件，只新增导航和索引层

## 本次新增文件

- `docs/README.md`
- `docs/ai/README.md`
- `docs/architecture/README.md`
- `docs/context/README.md`
- `docs/dev/README.md`
- `docs/change_notes/README.md`
- `docs/change_notes/indexes/2026-04.md`
- `前端设计/README.md`
- `前端设计/四期前端优化设计/README.md`

## 本次重写或统一的入口页

- `前端设计/一期前端相关设计/README.md`
- `前端设计/二期前端优化设计/README.md`
- `前端设计/三期前端优化设计/README.md`

## 关键治理动作

### 1. docs 总入口补齐

- 明确 `context -> architecture -> 前端设计 -> dev -> change_notes -> review -> versioning` 的默认阅读顺序
- 为 `ai`、`architecture`、`context`、`dev`、`change_notes` 建立各自 `README.md`

### 2. change_notes 检索层补齐

- 保持顶层扁平文件不动，兼容历史链接
- 增加 `docs/change_notes/README.md` 作为总入口
- 增加 `docs/change_notes/indexes/2026-04.md` 作为月度导航
- 统一后续规则：新月份优先新增月索引，而不是继续只靠顶层文件列表浏览

### 3. 前端阶段口径统一

- 新增 `前端设计/README.md`
- 统一阶段映射为 `一期 / 二期 / 三期 / 四期`
- 统一层级口径为 `00 / 01 / 02 / 03 / 04 / 05 / 99`
- 对二三四期保留历史物理目录 `02_验收与联调/`，但在导航上统一解释为逻辑层级 `03`

## 为什么这样做

- 入口页缺失会让“文档都在，但不知道从哪读”成为常态
- `change_notes` 已经超过 660 份顶层文件，继续完全扁平浏览的成本过高
- `前端设计/` 的阶段和层级命名不完全统一，先统一导航口径比立即改物理目录更稳

## 验证

- `docs/` 现在具备总入口 `README.md`
- `docs/ai`、`docs/architecture`、`docs/context`、`docs/dev`、`docs/change_notes` 现在都具备入口页
- `前端设计/` 现在具备根入口页
- 四个阶段目录现在都具备 `README.md`

## 后续建议

1. 下一轮可以继续给 `仓管模块设计/`、`企业分离功能文件夹/`、`高并发承载能力优化设计/` 补同类入口
2. 如果 `change_notes` 后续继续快速增长，可进入第二阶段治理：按月分目录或按专题补细索引
