# 2026-04-27 导入链与非导出接口高风险问题修复

## 本次修复范围

- `custom_addons/logistics_dispatch/security/ir.model.access.csv`
- `custom_addons/logistics_dispatch/security/logistics_dispatch_security.xml`
- `custom_addons/logistics_web/services/waybill_standard_import_service_v2.py`
- `custom_addons/logistics_web/controllers/logistics_web_stats.py`
- `custom_addons/logistics_web/controllers/logistics_web_driver.py`
- `custom_addons/logistics_web/controllers/logistics_web_vehicle.py`

## 修复内容

### 1. 导入任务与明细权限收口

- 将 `logistics.import.source.file / task / task.line / error.line` 对 `base.group_user` 的 ACL 从全权限收紧为只读。
- 新增 `group_logistics_import_manager`，用于查看全部导入任务、源文件和错误结果。
- 为 `source.file / task / task.line / error.line` 补充 owner read record rule。
- 将 `logistics.import.batch` 对普通内部用户的模型级访问关闭，仅保留导入管理组只读。

### 2. 导入源文件路径加固

- 导入源文件持久化从绝对路径改为相对存储 key。
- 新增固定导入根目录解析逻辑。
- 读取源文件前会校验解析后的路径必须位于导入根目录下，阻断任意服务器文件读取。

### 3. `stats` bad-request 兜底

- `logistics_web_stats.py` 新增 `ValidationError / ValueError / TypeError` 兜底。
- 非法日期、非法 `limit` 等坏参数现在统一返回顶层 `4001`，错误码为 `ANALYSIS_BAD_REQUEST`。

### 4. `driver / vehicle` 顶层错误码统一

- `logistics_web_driver.py` 和 `logistics_web_vehicle.py` 对 `ValidationError / ValueError / TypeError` 统一返回顶层 `4001`。
- 错误码分别收口为：
  - `DRIVER_BAD_REQUEST`
  - `VEHICLE_BAD_REQUEST`

## 升级与验证

### 模块升级

- 数据库：`odoo_logistics_phase4_v1`
- 执行：

```powershell
python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_dispatch,logistics_web --stop-after-init
```

- 结果：升级成功

### 最小 smoke

使用短命 `odoo-bin shell` 脚本完成以下验证：

- 导入任务 owner 模型可见：`1`
- 非 owner 模型不可见：`0`
- owner 可读取任务行：通过
- 非 owner 读取任务行：被 `ValidationError` 拦截
- 非法源文件路径 `C:\Windows\win.ini`：被 `ValidationError` 拦截
- `stats rankings` 非法 `limit`：顶层 `4001`，错误码 `ANALYSIS_BAD_REQUEST`
- `driver profile` 非法对象：顶层 `4001`，错误码 `DRIVER_BAD_REQUEST`
- `vehicle profile` 非法对象：顶层 `4001`，错误码 `VEHICLE_BAD_REQUEST`

## 备注

- 本轮没有启动常驻 Odoo HTTP 服务。
- 本轮验证采用一次性 `odoo-bin shell` 短命进程，无残留后台进程。
