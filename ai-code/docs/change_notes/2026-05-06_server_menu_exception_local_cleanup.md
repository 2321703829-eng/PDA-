## 2026-05-06 服务器菜单与异常页本地清理

### 本次本地修改
- 修正 `logistics_dispatch_menus.xml` 中的中文菜单名称，恢复为正常 UTF-8 中文。
- 重写 `logistics_web/models/ui_label_sync.py`：
  - 统一物流主菜单、导入中心、留痕、证据、异常等名称。
  - 在升级同步时自动将历史残留的
    - `logistics_web.menu_logistics_web_import_center_phase5`
    - `logistics_web.menu_logistics_web_import_center_phase5_root`
    设置为 `active=False`，避免“五期五表导入”单独出现在菜单栏。
- 重写 `logistics_trace_exception_views.xml`，将异常页列表、表单、搜索、帮助文案统一为中文口径。
- 修正 `logistics_trace_exception/__manifest__.py` 与 `logistics_web/__manifest__.py` 的中文摘要说明。

### 已做校验
- `logistics_dispatch_menus.xml` XML 解析通过。
- `logistics_trace_exception_views.xml` XML 解析通过。
- `import_center_action.js` 语法检查通过。

### 仍需后续处理
- `import_center_templates.xml` 与 `import_center_action.js` 仍残留部分历史乱码文案，需要下一轮继续做完整文本修复后再推服务器。
- 服务器端页面“打开异常”在本轮更像是前端资产缓存与部分历史乱码模板共同作用，后续同步代码后需要清理 `/web/assets/%` 并重启服务再验证。
