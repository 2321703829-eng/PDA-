# odoo-addon-scaffold

## 目的

根据项目规范生成标准 Odoo addon 骨架。

## 使用场景

- 新建 `logistics_*` addon
- 初始化标准目录
- 生成基础 manifest、init、models、views、security 结构

## 执行步骤

1. 先确认 addon 名称与职责边界
2. 确认它依赖哪些官方模块
3. 建立最小目录：
   - `__manifest__.py`
   - `__init__.py`
   - `models/`
   - `views/`
   - `security/`
4. 若需要 chatter，则默认考虑 `mail.thread` / `mail.activity.mixin`
5. 把视图和权限文件纳入 manifest
6. 生成后回到 `upgrade_and_verify.md` 执行最小验证

## 检查项

- 命名是否符合项目约定
- 依赖是否写清
- 是否误把官方模型复制成新模型
- 是否需要菜单、动作、权限文件
