# 2026-04-17 导入中心菜单与二期样例验收材料统一到 V2 XLSX 口径

## 本次目标

把二期导入中心的菜单结构、样例目录、联调材料、验收材料统一到 `TSL-IMPORT-WAYBILL-V2` 三 Sheet `XLSX` 口径，避免继续混用旧的 `V1 CSV` 心智。

## 本次改动

### 1. 导入中心菜单收口

- 在 [custom_addons/logistics_dispatch/views/logistics_dispatch_menus.xml](/d:/Desktop/Odoo/custom_addons/logistics_dispatch/views/logistics_dispatch_menus.xml) 中为以下旧导入子菜单补充 `groups="base.group_no_one"`：
  - `运单导入`
  - `客户明细导入`
  - `货物明细导入`
- 在 [custom_addons/logistics_web/models/ui_label_sync.py](/d:/Desktop/Odoo/custom_addons/logistics_web/models/ui_label_sync.py) 中同步将上述三个菜单标记为 `active=False`
- 升级 `logistics_dispatch, logistics_web` 后，运行态已变为：
  - `导入中心` 保持可见
  - 三个旧导入子菜单处于 `active=False`
  - 三个旧导入子菜单同时挂到 `Technical Features` 组下，普通页面不再展示

### 2. 二期样例目录收口

- 正式样例目录 [03_模板与样例](/d:/Desktop/Odoo/ai-code/前端设计/二期前端优化设计/03_模板与样例) 只保留：
  - `2026-04-17_TSL-IMPORT-WAYBILL-V2三Sheet整单导入样例.xlsx`
  - `2026-04-17_TSL-IMPORT-WAYBILL-V2三Sheet标准模板使用说明.md`
  - `README.md`
- 旧样例文件已从正式样例目录移除：
  - `2026-04-15_运单标准导入模板_10条.csv`
  - `2026-04-15_运单标准导入模板_使用说明.md`
- 历史样例保留在 [99_待归档/历史导入样例](/d:/Desktop/Odoo/ai-code/前端设计/二期前端优化设计/99_待归档/历史导入样例)

### 3. 联调与验收材料切换到 V2

- 已更新 [2026-04-15_Odoo物流后台UI与导入导出验收清单.md](/d:/Desktop/Odoo/ai-code/前端设计/二期前端优化设计/02_验收与联调/2026-04-15_Odoo物流后台UI与导入导出验收清单.md)
  - 验收对象改为导入中心页
  - 验收文件改为 `V2 XLSX`
  - 验收项覆盖 `template / precheck / confirm / result / error-report`
- 已更新 [二期前端落地与联调说明.md](/d:/Desktop/Odoo/ai-code/前端设计/二期前端优化设计/02_验收与联调/二期前端落地与联调说明.md)
  - 导入链路描述改为“自定义导入中心 + V2 闭环”
- 已更新 [标准订单导入模板字段说明与错误反馈规范.md](/d:/Desktop/Odoo/ai-code/前端设计/二期前端优化设计/02_跨模块规范/01_接口与数据/标准订单导入模板字段说明与错误反馈规范.md)
  - 字段结构改为 `运单 / 客户明细 / 货物明细` 三 Sheet
  - 错误反馈改为带 `sheet_name`
- 已更新 [前端接口设计总文档.md](/d:/Desktop/Odoo/ai-code/前端设计/二期前端优化设计/02_跨模块规范/01_接口与数据/前端接口设计总文档.md)
  - 模板下载、预校验、确认导入、结果查询示例改为 `V2 XLSX`
- 已更新 [controller 示例响应.md](/d:/Desktop/Odoo/ai-code/前端设计/二期前端优化设计/02_跨模块规范/01_接口与数据/controller 示例响应.md)
  - 模板下载、预校验、确认导入、结果接口示例改为 `V2`

## 验证

- `python .\\odoo-bin -c .\\odoo_local.conf -d odoo_logistics_dev -u logistics_dispatch,logistics_web --stop-after-init`
- 目录检查：正式样例目录只剩 V2 `XLSX` 样例与说明
- 运行态菜单检查：
  - `logistics_dispatch.menu_logistics_dispatch_import_center` `active=True`
  - 三个旧导入子菜单 `active=False`
  - 三个旧导入子菜单 `group_count=1`，组为 `Technical Features`
- 文档检索：
  - 在 `02_跨模块规范/01_接口与数据`
  - `02_验收与联调`
  - `03_模板与样例`
  范围内，不再保留 `TSL-IMPORT-WAYBILL-V1` 和旧样例文件主引用

## 当前边界

- `00_导航与总纲` 中仍保留少量 `V1` 历史背景描述，用于说明方案演进过程，不属于当前正式验收口径
- `logistics_web_dashboard.py` 仍有 Odoo 19 `json` 路由 deprecated warning，本次未处理
