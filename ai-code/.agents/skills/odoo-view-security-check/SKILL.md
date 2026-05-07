# odoo-view-security-check

## 目的

检查视图、菜单和权限是否完整。

## 使用场景

- 新增 tree / form / search
- 新增菜单与 action
- 新增或调整权限

## 检查步骤

1. 检查模型是否已定义
2. 检查 `ir.model.access.csv` 是否存在并引用正确模型
3. 检查 tree / form / search 是否都已准备
4. 检查菜单与 action 是否可达
5. 检查角色是否符合一期业务分工
6. 检查验证清单是否需要同步更新

## 检查项

- 视图是否已纳入 manifest
- 菜单和 action 是否可达
- `ir.model.access.csv` 是否齐全
- 是否存在明显越权或缺权
- 列表、表单、搜索是否能支撑业务录入和查询
