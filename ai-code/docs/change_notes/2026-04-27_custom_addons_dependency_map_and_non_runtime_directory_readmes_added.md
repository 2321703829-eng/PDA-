# 2026-04-27 custom_addons 职责依赖总表与非运行目录入口补齐

## 本轮目标

- 补 `custom_addons` 的模块职责与依赖总表
- 给 `scripts/`、`templates/` 建正式入口 README
- 不动任何运行代码或活跃模块文件

## 本轮新增

- `docs/dev/custom_addons_responsibility_and_dependency_map.md`
- `scripts/README.md`
- `templates/README.md`

## 本轮同步

- 更新 `docs/dev/README.md`
- 更新仓库根 `README.md`

## 当前口径

- `custom_addons_module_status_inventory.md` 负责回答“哪些模块是现行，哪些是历史占位”
- `custom_addons_responsibility_and_dependency_map.md` 负责回答“现行模块各自负责什么、依赖谁、先看哪里”
- `scripts/` 与 `templates/` 当前只做辅助目录，不承接运行时代码
