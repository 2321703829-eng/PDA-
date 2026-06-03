# 2026-04-27 导入接口顶层错误码对齐

## 本次变更

- 重构 `logistics_web_import_v3.py` 的错误响应出口。
- 将导入接口顶层错误码统一收口到与导出链一致的风格：
  - `4001` bad request
  - `4003` forbidden
  - `4004` not found
  - `4090` status conflict / not ready
  - `5000` internal error
- 为导入任务读取补充显式 owner/manager 校验，使跨人读取场景返回 `4003`，不再依赖 record rule 隐身成 `404`。

## 涉及文件

- `custom_addons/logistics_web/controllers/logistics_web_import_v3.py`
- `custom_addons/logistics_web/services/waybill_standard_import_service_v2.py`

## 运行验证

### 语法检查

- `logistics_web_import_v3.py`: `ast.parse` 通过
- `waybill_standard_import_service_v2.py`: `ast.parse` 通过

### Shell smoke

在 `odoo_logistics_phase4_v1` 上通过短命 `odoo-bin shell` 验证了 4 类顶层码：

- 跨用户读取导入任务行：`4003 / IMPORT_PERMISSION_DENIED`
- 非法 Base64 预校验：`4001 / PRECHECK_PARSE_FAILED`
- 失效预校验令牌确认导入：`4090 / IMPORT_CONFIRM_STATUS_INVALID`
- 不存在的导入任务结果：`4004 / IMPORT_RESULT_NOT_FOUND`

### 模块升级

已执行：

```powershell
python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -u logistics_web --stop-after-init
```

结果：成功
