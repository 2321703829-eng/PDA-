# 2026-04-22 phase4 database design add access contract sections

## 本次调整

在《四期数据库底表设计稿 v1（第二次修正版）》中，补充了可直接供后端接入的口径化章节。

## 新增内容

- 新增“表清单总览”
  - 明确每张表属于主表、扩展表、历史表还是日志表
- 新增“主键与外键矩阵”
  - 明确每张表的 `PK`、`UK`、`FK`、`nullable`
- 新增“按表必填字段清单”
  - 不再只依赖全局 non-null 列表
- 将导入日志表升级为正式结构
  - `import_source_file`
  - `import_task`
  - `import_task_line`
  - `import_error_line`
- 同步补充导入日志相关枚举、索引、唯一键、默认值、写入边界

## 目的

让当前设计稿不仅能表达业务设计，也能直接作为后端建表、接入、导入实现时的统一口径。
