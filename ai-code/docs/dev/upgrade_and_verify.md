# upgrade_and_verify

## 1. 适用范围

适用于 `d:\Desktop\Odoo\custom_addons` 下当前有效的 `logistics_*` addon。

优先关注：

- `logistics_base`
- `logistics_dispatch`
- 后续的 `logistics_trace_core`
- 后续的 `logistics_trace_exception`
- 后续的 `logistics_trace_evidence`

## 2. 当前仓库真实约定

### 2.1 现状

当前仓库没有项目专用的 `odoo.conf`，只有官方样例配置：

- `d:\Desktop\Odoo\debian\odoo.conf`
- `d:\Desktop\Odoo\addons\iot_box_image\configuration\odoo.conf`

它们不作为本项目本地开发配置使用。

### 2.2 本项目统一约定

- 本地配置样例：`d:\Desktop\Odoo\odoo_local.conf.example`
- 本地真实配置：`d:\Desktop\Odoo\odoo_local.conf`
- 官方 addons：`d:\Desktop\Odoo\addons`
- 自定义 addons：`d:\Desktop\Odoo\custom_addons`
- 推荐开发数据库名：`odoo_logistics_dev`

## 3. 升级前检查

- `__manifest__.py` 依赖完整
- `models/__init__.py` 已引入
- `security/ir.model.access.csv` 已补齐
- 视图 XML 已纳入 manifest
- 菜单、动作、权限引用无明显遗漏

## 4. 本地配置示例

推荐的最小 `addons_path`：

```ini
addons_path = d:\Desktop\Odoo\addons,d:\Desktop\Odoo\custom_addons
```

如果使用 PostgreSQL 默认本地连接，可采用：

```ini
db_host = False
db_port = False
db_user = odoo
db_password = False
```

## 5. 常用命令模板

以下命令以 Windows / PowerShell、本地仓库路径 `d:\Desktop\Odoo` 为约定：

```bash
python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_dev -i logistics_base
python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_dev -i logistics_dispatch
python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_dev -u logistics_base,logistics_dispatch
python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_dev -u logistics_dispatch,logistics_trace_core
```

如果 Python 启动方式不同，可替换为本机实际命令。

## 6. 最小验证清单

- 模块可安装或升级
- 菜单可打开
- `list / form / search` 视图正常
- 关键字段可见且可编辑
- 权限无明显 `AccessError`
- chatter / 附件 / 活动功能正常

## 7. 按改动类型的验证要求

### 改模型

- 字段创建成功
- 必填项与默认值合理
- 关联关系可正常打开

### 改视图

- 菜单入口正常
- 表单与列表无字段缺失
- 搜索视图筛选可用

### 改菜单

- 动作、菜单、窗口视图关联正确

### 改权限

- 目标角色可以访问
- 非目标角色不会越权

### 改文档

- `docs/context`
- `ARCHITECTURE.md`
- `doc_sync.md`
- `change_notes`

需要检查是否同步更新。

## 8. 失败处理规则

- 先收口到可运行状态
- 再记录失败原因
- 更新 `docs/change_notes/`
- 给出下一步修复建议

## 9. 人工检查建议

- 用真实菜单路径手工打开页面
- 用至少两类角色检查权限
- 对运单、留痕、异常重点检查附件与关联跳转
