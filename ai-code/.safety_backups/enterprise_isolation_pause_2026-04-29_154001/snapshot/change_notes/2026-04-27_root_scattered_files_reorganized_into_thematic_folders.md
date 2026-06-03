# 2026-04-27 根目录散落资料归档到专题与来源目录

## 本轮目标

- 清理 `ai-code/` 根目录中不应长期停留的来源资料、分工稿、合规稿和表格样例
- 按用途把它们归入 `docs/` 或 `专题设计/` 下的专用目录
- 为新目录补 `README.md` 索引说明

## 本轮新增目录

- `docs/context/meeting_notes/`
- `docs/context/source_materials/`
- `docs/context/compliance/`
- `docs/architecture/source_materials/`
- `docs/architecture/source_materials/database/`
- `docs/dev/project_coordination/`
- `docs/dev/test_data/`
- `专题设计/前端设计/四期前端优化设计/03_模板与样例/`

## 本轮移动

- 项目会议纪要移入 `docs/context/meeting_notes/`
- 项目级原始设计稿移入 `docs/context/source_materials/`
- 合规检查资料移入 `docs/context/compliance/`
- 数据库来源资料与底表样例移入 `docs/architecture/source_materials/database/`
- 分工与协作稿移入 `docs/dev/project_coordination/`
- 测试用司机与车辆样例移入 `docs/dev/test_data/`
- 四期模板与样例表格移入 `专题设计/前端设计/四期前端优化设计/03_模板与样例/`
- 一期前端来源稿 `于睿_后台前端与追溯界面工作大纲.md` 移入 `04_来源资料与历史草图/01_原始资料/`

## 本轮同步

- 更新现行正文中对根目录旧位置的引用
- `docs/change_notes/` 历史留痕不做批量清洗
- 更新 `docs/context/README.md`、`docs/architecture/README.md`、`docs/dev/README.md`、`专题设计/前端设计/四期前端优化设计/README.md`

## 当前口径

- 根目录应尽量只保留仓库级入口，而不承载来源资料和表格样例
- 来源资料目录必须配套 `README.md`，说明文件来源、用途和现行关系
