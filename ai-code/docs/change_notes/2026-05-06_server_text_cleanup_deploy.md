## 2026-05-06 服务器文本清理部署

### 本轮已部署到联调服务器
- `logistics_dispatch/views/logistics_dispatch_menus.xml`
- `logistics_trace_exception/views/logistics_trace_exception_views.xml`
- `logistics_trace_exception/security/logistics_trace_exception_security.xml`
- `logistics_trace_exception/__manifest__.py`
- `logistics_web/__manifest__.py`
- `logistics_web/models/ui_label_sync.py`
- `logistics_web/static/src/js/actions/import_center_action.js`
- `logistics_web/static/src/js/actions/dashboard_action_v2.js`
- `logistics_web/static/src/xml/import_center_templates.xml`

### 服务器动作
- 上传上述文件到 `/opt/odoo-lite-test-v19/extra-addons`
- 升级模块：
  - `logistics_dispatch`
  - `logistics_trace_exception`
  - `logistics_web`
- 清理数据库中的 `/web/assets/%` 旧资产
- 重启 `odoo-lite-test-v19-web`

### 过程中发现并修复
- 联调服务器 `logistics_trace_exception` 目录缺少 `security/logistics_trace_exception_security.xml`
- 该缺失会导致 `logistics_trace_exception` 升级时报 `FileNotFoundError`
- 已补齐该文件后重新升级成功

### 已确认结果
- 顶部菜单库内只保留：
  - `物流`
  - `导入中心`
  - `异常`
- 历史独立“五期五表导入”菜单未出现在当前库查询结果中
- 导入中心源码已部署为中文清理版
- 工作台源码已部署为中文清理版
- 异常页视图已升级到中文清理版
- 后端 `web.assets_web.min.js` 已重新生成

### 额外观察
- 容器内直连 `8069` 的 Odoo 服务正常
- 公网入口存在分层差异：
  - `http://8.166.131.218:7084/web/login?db=odoo_logistics_webtest_v19` 当前返回 `502`
  - `http://8.166.131.218:7084/web?db=odoo_logistics_webtest_v19` 当前返回 `200`
- 因此“部分页面打开有问题”仍需继续排公网代理 / 登录入口链路，而不完全是 Odoo 页面源码问题
