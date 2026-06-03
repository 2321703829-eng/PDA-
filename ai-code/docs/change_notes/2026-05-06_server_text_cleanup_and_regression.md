## 2026-05-06 服务器文本清理与页面回归

### 本地已完成
- 修复 `logistics_dispatch_menus.xml` 的物流主菜单中文显示。
- 重写 `logistics_web/models/ui_label_sync.py`，统一菜单同步口径，并在升级时自动停用历史残留的独立“五期五表导入”菜单：
  - `logistics_web.menu_logistics_web_import_center_phase5`
  - `logistics_web.menu_logistics_web_import_center_phase5_root`
- 修复 `logistics_trace_exception_views.xml` 的异常页中文显示，包括列表、表单、搜索和帮助文案。
- 修复 `logistics_trace_exception/__manifest__.py` 与 `logistics_web/__manifest__.py` 的中文摘要。
- 修复 `import_center_action.js` 与 `import_center_templates.xml` 的导入中心乱码文案。
- 修复 `dashboard_action_v2.js` 的工作台乱码文案、状态映射、动作标题与错误提示。

### 本地校验
- `import_center_action.js` 语法检查通过。
- `dashboard_action_v2.js` 语法检查通过。
- `import_center_templates.xml` XML 解析通过。
- `logistics_dispatch_menus.xml` XML 解析通过。
- `logistics_trace_exception_views.xml` XML 解析通过。
- `ui_label_sync.py`、相关 `__manifest__.py` 编译通过。

### 待服务器侧执行
- 同步本轮修复后的菜单、异常页、导入中心和工作台文件到联调服务器。
- 升级：
  - `logistics_dispatch`
  - `logistics_trace_exception`
  - `logistics_web`
- 清理 `/web/assets/%` 旧资产。
- 重启 Odoo 服务。

### 本轮重点回归项
- 顶部菜单不再出现独立“五期五表导入”入口。
- 导入中心中文文案恢复正常。
- 异常页中文文案恢复正常。
- 物流工作台中文文案恢复正常。
