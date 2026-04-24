# 2026-04-24 标准导出任务模型骨架首轮落地

## 本轮目标

- 落地 `WB-EXP-M1`，为标准批量导出的正式任务链提供 `logistics_dispatch` 侧模型、权限组、access、sequence 和迁移索引骨架。

## 修改文件

- `custom_addons/logistics_dispatch/models/logistics_export_log.py`
- `custom_addons/logistics_dispatch/models/selection_options.py`
- `custom_addons/logistics_dispatch/models/__init__.py`
- `custom_addons/logistics_dispatch/security/logistics_dispatch_security.xml`
- `custom_addons/logistics_dispatch/security/ir.model.access.csv`
- `custom_addons/logistics_dispatch/data/sequence_data.xml`
- `custom_addons/logistics_dispatch/migrations/19.0.1.1.0/post-migration.py`
- `custom_addons/logistics_dispatch/__manifest__.py`

## 修改原因

- 四期批量导出已经冻结正式落库与接口口径，但 `logistics_dispatch` 侧还没有对应的正式导出任务模型。
- 如果不先把模型、sequence、access 和索引骨架落下来，后续 controller、service、结果页都只能继续停留在文档层。

## 改动摘要

- 新增标准导出正式模型：
  - `logistics.export.source.scope`
  - `logistics.export.task`
  - `logistics.export.task.line`
  - `logistics.export.error.line`
- 在 `selection_options.py` 中补齐导出相关枚举：
  - 对象类型
  - 入口类型
  - 导出模式
  - 包结构
  - 任务状态
  - 行状态
  - 错误阶段
- 新增导出权限组：
  - `logistics_dispatch.group_logistics_export_user`
  - `logistics_dispatch.group_logistics_export_manager`
- 为导出范围和导出任务补齐 sequence：
  - `logistics.export.source.scope`
  - `logistics.export.task`
- 在迁移脚本中补齐导出任务相关索引。

## 影响范围

- `logistics_dispatch` 模块安装与升级链
- 后续标准批量导出的 controller / service / 结果页实现
- 导出任务模型权限与序列基线

## 是否影响模型 / 视图 / 权限 / 数据兼容性

- 影响模型：是，新增 4 个正式导出任务模型
- 影响视图：否，本轮未新增业务视图
- 影响权限：是，新增 2 个导出权限组与对应模型 access
- 影响数据兼容性：低，本轮为新增模型与新增索引，不改既有导入/执行主链表结构

## 验证方法

- 对新增 Python 文件执行 `py_compile`
- 回扫以下关键字是否已进入代码：
  - `logistics.export.task`
  - `group_logistics_export_user`
  - `logistics.export.task`
  - `idx_export_task_scope_type_status`

## 风险点

- 本轮只完成模型骨架，尚未接 controller / service / 前端结果页，功能仍不可直接使用。
- `selection_options.py` 本轮做了整文件重写，需重点确认既有导入与执行主链引用未受影响。

## 回滚建议

- 如需回滚，可整体回退本次新增的导出模型、权限组、sequence 和索引变更。
- 若数据库已升级到新增导出表结构，回滚前应先确认是否已有导出测试数据写入。

## 后续待办

- 继续推进 `WB-EXP-S1`：
  - 新增导出 service
  - 打通 `from_waybill` 任务创建、文件生成、结果回读和下载
