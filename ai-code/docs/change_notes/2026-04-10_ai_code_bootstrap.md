# Change Notes

## 本轮目标

- 将 `ai-code` 从基础框架补齐到可直接指导后续开发与协作的程度

## 修改文件

- `ai-code/AGENTS.md`
- `ai-code/README.md`
- `ai-code/docs/ai/*`
- `ai-code/docs/context/*`
- `ai-code/docs/architecture/*`
- `ai-code/docs/dev/*`
- `ai-code/docs/review/*`
- `ai-code/docs/change_notes/_template.md`
- `ai-code/.agents/skills/*`
- `ai-code/templates/odoo_addon_template/*`

## 修改原因

- 原有 `ai-code` 已具备框架，但仍缺少足够可直接开工的开发蓝图、模板和实际变更沉淀

## 改动摘要

- 补齐 AI 入口约束与协作规范
- 补齐项目上下文与可实现性文档
- 新增订单 / 留痕 / 异常字段与状态草图
- 新增客户 / 门店 / 工作人员 / 仓库主数据草图
- 新增 custom_addons 拆分蓝图
- 新增人工验证清单
- 新增 Odoo addon 模板目录
- 新增首份实际 change note

## 影响范围

- 仅影响 `ai-code` 文档与模板体系
- 不影响业务代码
- 不影响 Odoo 运行逻辑

## 是否影响模型 / 视图 / 权限 / 数据兼容性

- 不影响实际模型
- 不影响实际视图
- 不影响实际权限
- 不影响数据兼容性

## 验证方法

- 检查 `ai-code` 目录树是否完整
- 检查关键文档是否存在
- 检查模板目录和技能目录是否存在

## 风险点

- 部分运行命令仍为模板，需要后续结合真实环境补成可执行版本
- 自定义 addon 名称和路径仍需在真正建模块前最终确认

## 回滚建议

- 若需回滚，仅删除本次新增的 `ai-code` 文档与模板文件即可

## 后续待办

- 结合真实 `odoo.conf` 与数据库名称补齐运行文档
- 产出 `logistics_base` / `logistics_order` 的正式 addon 设计稿
- 后续每次代码变更都补写新的 change note
