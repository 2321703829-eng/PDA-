# 2026-04-24 from_customer / from_product 首轮开发任务拆分单

## 文档定位

- 本文用于把客户画像导出和货物画像导出的首轮实现拆成可直接排期和执行的开发工作包。
- 本文承接以下冻结文档，不重新定义对象边界、底表或接口：
  - [客户画像与货物画像导出正式落库与接口冻结补丁稿](../02_跨模块规范/01_接口与数据/2026-04-24_客户画像与货物画像导出正式落库与接口冻结补丁稿.md)
  - [客户画像与货物画像导出模块设计方案](../01_专题方案/2026-04-24_客户画像与货物画像导出模块设计方案.md)
- 本文默认开发目标是：先打通
  - `from_customer -> customer_profile -> export task -> result page -> download`
  - `from_product -> product_profile -> export task -> result page -> download`
  最小闭环。

## Outcome

- 用户可从“物流客户画像”列表页、详情页发起客户画像正式导出。
- 用户可从商品主档列表页、详情页发起货物画像正式导出。
- 系统可创建正式导出任务，生成：
  - `CustomerProfile`
  - `ProductProfile / ProductUnit`
  对应 `xlsx`，并在统一导出结果页回读摘要、行结果、错误明细和下载链接。
- 该切片完成后，应成为后续 `CustomerProductRelation` 二阶段增强的复用底座。

## Boundary

- 只做：
  - `customer_profile + from_customer + customer_profile_bundle_v1`
  - `product_profile + from_product + product_profile_bundle_v1`
- 不做：
  - `customer_profile_bundle_v2`
  - `product_profile_bundle_v2`
  - `CustomerProductRelation`
  - 图片 ZIP
  - 导出中心历史页
  - 字段级脱敏导出
  - 取消任务、重试任务、超大任务分片
- 货物画像首轮不从 `goods_line` 发起，也不把 `goods_line` 当正式主对象。

## 当前前提

- `from_waybill` 已具备正式任务链、结果页和下载链路，可直接作为实现参考。
- 正式导出补丁稿已冻结：
  - 新对象类型：`customer_profile / product_profile`
  - 新入口类型：`from_product`
  - 新包结构：
    - `customer_profile_bundle_v1`
    - `product_profile_bundle_v1`
  - 新统计字段：
    - `package_metrics_json`
    - `line_metrics_json`
- 客户侧统一对象已经收口到 `res.partner`。
- 货物长期主数据当前已经具备：
  - `product.template`
  - `logistics.product.unit`

## 推荐顺序

1. `CPPR-EXP-M1` 模型扩展与枚举补丁
2. `CP-EXP-S1` `from_customer` 导出服务主链
3. `PP-EXP-S1` `from_product` 导出服务主链
4. `CPPR-EXP-C1` Controller 扩展
5. `CPPR-EXP-F1` 结果页分支与通用统计渲染
6. `CP-EXP-F2` 客户画像入口与跳转
7. `PP-EXP-F2` 货物画像入口与跳转
8. `CPPR-EXP-V1` Smoke、联调、验收回归

说明：

- `CP-EXP-S1` 和 `PP-EXP-S1` 在 `CPPR-EXP-M1` 完成后可以并行开发。
- `CPPR-EXP-F1` 可以在 Controller DTO shape 基本稳定后先做骨架，不必等两条服务都完全收尾。
- 入口按钮建议复用运单当前模式：
  - 列表页 JS 发起
  - 详情页 object 按钮跳结果页

## 工作包总览

| 编号 | 工作包 | 责任面 | 前置依赖 |
| --- | --- | --- | --- |
| `CPPR-EXP-M1` | 导出模型扩展与枚举补丁 | `logistics_dispatch` | 冻结补丁稿已定 |
| `CP-EXP-S1` | `from_customer` 导出服务主链 | `logistics_web/services` | `CPPR-EXP-M1` |
| `PP-EXP-S1` | `from_product` 导出服务主链 | `logistics_web/services` | `CPPR-EXP-M1` |
| `CPPR-EXP-C1` | Controller 与下载路由扩展 | `logistics_web/controllers` | `CP-EXP-S1` + `PP-EXP-S1` DTO 稳定 |
| `CPPR-EXP-F1` | 导出结果页对象分支 | `logistics_web/static` | `CPPR-EXP-C1` |
| `CP-EXP-F2` | 客户画像入口与跳转 | `logistics_web/static` + `logistics_base`/`logistics_web` 视图 | `CPPR-EXP-C1` |
| `PP-EXP-F2` | 货物画像入口与跳转 | `logistics_web/static` + 原生商品视图扩展 | `CPPR-EXP-C1` |
| `CPPR-EXP-V1` | Smoke、联调、验收回归 | 全链路 | 前七包完成 |

## 一、模型工作包

### `CPPR-EXP-M1` 导出模型扩展与枚举补丁

### 目标

- 在现有正式导出模型基础上，补齐客户画像和货物画像导出所需的字段、枚举、索引和迁移。
- 保证 `from_waybill` 现有模型不被破坏，同时为新对象类型提供可落地底座。

### 建议文件

- `custom_addons/logistics_dispatch/models/logistics_export_log.py`
- `custom_addons/logistics_dispatch/models/selection_options.py`
- `custom_addons/logistics_dispatch/models/__init__.py`
- `custom_addons/logistics_dispatch/migrations/19.0.1.1.0/post-migration.py`
- 如需权限补充：
  - `custom_addons/logistics_dispatch/security/ir.model.access.csv`

### 主要任务

- 在 `selection_options.py` 扩展枚举：
  - `EXPORT_OBJECT_TYPE_SELECTION`
    - `customer_profile`
    - `product_profile`
  - `EXPORT_ENTRY_TYPE_SELECTION`
    - `from_product`
  - `EXPORT_PACKAGE_STRUCTURE_SELECTION`
    - `customer_profile_bundle_v1`
    - `customer_profile_bundle_v2`
    - `product_profile_bundle_v1`
    - `product_profile_bundle_v2`
  - `EXPORT_TARGET_OBJECT_TYPE_SELECTION`
    - `partner`
    - `product`
- 在 `logistics_export_log.py` 新增字段：
  - `export_task.package_metrics_json`
  - `export_task_line.line_metrics_json`
- 为 `export_task` 和 `export_task_line` 补迁移索引：
  - `object_type + entry_type + status`
  - `target_object_type + target_res_id`
- 明确默认值和 JSON 结构：
  - 首轮默认 `{}`，由服务层保证 schema 正确

### 完成标准

- 模型可正常加载。
- 新枚举值可在 shell 中可见。
- 模块升级后字段、索引均可见。
- `from_waybill` 现有查询和页面不被新字段破坏。

### 明确不做

- 不在这一包里写服务取数逻辑。
- 不在这一包里写 Controller。
- 不在这一包里改结果页模板。

## 二、服务工作包

### `CP-EXP-S1` `from_customer` 导出服务主链

### 目标

- 在 `logistics_web/services` 打通客户画像导出的最小闭环：
  - 建任务
  - 读取 `res.partner`
  - 生成 `CustomerProfile`
  - 写盘
  - 回写任务状态
  - 查询结果

### 建议文件

- 新增 `custom_addons/logistics_web/services/customer_profile_export_service.py`
- 更新 `custom_addons/logistics_web/services/__init__.py`

### 主要任务

#### S1-1 请求校验与建任务

- 校验：
  - `object_type = customer_profile`
  - `entry_type = from_customer`
  - `package_structure = customer_profile_bundle_v1`
  - `selected_ids` 非空
- 命中对象：
  - `res.partner`
  - `is_logistics_partner = True`
- 创建：
  - `export_source_scope`
  - `export_task(status=pending)`
  - 对应 `export_task_line(status=pending)`

#### S1-2 客户画像取数

- 读取统一客户画像主对象字段：
  - 编码
  - 联系方式
  - 地址
  - 经营画像字段
  - 配送画像字段
  - 签收、卸货、停车、时间窗等字段
- 取数统一走 `res.partner`
- 不从 `logistics.customer.profile / logistics.store.profile` 直接拼主文件

#### S1-3 Workbook 生成

- 复用现有 `openpyxl` 能力
- 生成单 Sheet：
  - `CustomerProfile`
- 列顺序与冻结稿约定一致
- 单行粒度为一个 `res.partner`

#### S1-4 文件写盘与任务回写

- 回写：
  - `output_file_*`
  - `download_ready_at`
  - `expires_at`
  - `status`
  - `package_metrics_json.customer_count`
  - `line_metrics_json.customer_count`

#### S1-5 结果查询服务

- 提供：
  - 任务摘要读取
  - 行结果分页读取
  - 错误明细分页读取
  - 错误报告动态生成
  - 主文件下载前校验

### 建议对外方法

- `create_customer_profile_export_task`
- `run_customer_profile_export_task`
- `get_customer_profile_export_task_result`
- `get_customer_profile_export_task_lines`
- `get_customer_profile_export_task_errors`
- `build_customer_profile_export_error_report`
- `get_customer_profile_export_download_file`

### 完成标准

- 对单个客户画像可成功生成 `CustomerProfile` 文件。
- 对多个客户画像可按任务行逐条写入 `export_task_line`。
- 失败对象会写入 `export_error_line`。
- 能稳定返回冻结补丁稿里的 DTO shape。

### 明确不做

- 不接客户商品关系表。
- 不导出 `CustomerProductRelation`。
- 不支持“筛选条件不传 selected_ids 导全量”。

### `PP-EXP-S1` `from_product` 导出服务主链

### 目标

- 在 `logistics_web/services` 打通货物画像导出的最小闭环：
  - 建任务
  - 读取 `product.template`
  - 展开 `logistics.product.unit`
  - 生成 `ProductProfile / ProductUnit`
  - 写盘
  - 回写任务状态
  - 查询结果

### 建议文件

- 新增 `custom_addons/logistics_web/services/product_profile_export_service.py`
- 更新 `custom_addons/logistics_web/services/__init__.py`

### 主要任务

#### S1-1 请求校验与建任务

- 校验：
  - `object_type = product_profile`
  - `entry_type = from_product`
  - `package_structure = product_profile_bundle_v1`
  - `selected_ids` 非空
- 命中对象：
  - `product.template`
- 创建：
  - `export_source_scope`
  - `export_task(status=pending)`
  - 对应 `export_task_line(status=pending)`

#### S1-2 商品与规格取数

- 读取 `product.template`：
  - 内外部商品编码
  - 商品名称
  - 品牌
  - 类别
  - 标签
  - 默认条码
  - 基础单位
  - 默认重量
  - 默认体积
  - 配送要求
- 展开 `logistics.product.unit`：
  - SKU
  - 规格
  - 销售单位
  - 条码
  - 换算
  - 价格
  - 尺寸
  - 重量
  - 体积
  - 最小起订量
- 不从 `goods_line` 取主数据

#### S1-3 Workbook 生成

- 生成两张 Sheet：
  - `ProductProfile`
  - `ProductUnit`
- `ProductUnit` 通过 `product_tmpl_id` 或稳定业务键回带到主档

#### S1-4 文件写盘与任务回写

- 回写：
  - `output_file_*`
  - `download_ready_at`
  - `expires_at`
  - `status`
  - `package_metrics_json.product_count`
  - `package_metrics_json.product_unit_count`
  - `line_metrics_json.product_count`
  - `line_metrics_json.product_unit_count`

#### S1-5 结果查询服务

- 提供：
  - 任务摘要读取
  - 行结果分页读取
  - 错误明细分页读取
  - 错误报告动态生成
  - 主文件下载前校验

### 建议对外方法

- `create_product_profile_export_task`
- `run_product_profile_export_task`
- `get_product_profile_export_task_result`
- `get_product_profile_export_task_lines`
- `get_product_profile_export_task_errors`
- `build_product_profile_export_error_report`
- `get_product_profile_export_download_file`

### 完成标准

- 对单个商品主档可成功生成 `ProductProfile / ProductUnit` 文件。
- 规格为空时允许 `ProductUnit` 只有表头无数据，但任务和结果页语义必须正确。
- 失败对象会写入 `export_error_line`。

### 明确不做

- 不新增 `goods_profile` 模型。
- 不接 `CustomerProductRelation`。
- 不从执行层 `goods_line` 反推主档导出。

## 三、Controller 工作包

### `CPPR-EXP-C1` Controller 与下载路由扩展

### 目标

- 在现有导出 controller 基础上，补齐客户画像和货物画像首轮所需路由。

### 建议文件

- 更新 `custom_addons/logistics_web/controllers/logistics_web_export.py`
- 如需拆分 controller 文件，可新增：
  - `custom_addons/logistics_web/controllers/logistics_web_profile_export.py`
- 更新 `custom_addons/logistics_web/controllers/__init__.py`

### 主要任务

- 新增路由：
  - `POST /api/admin/logistics/exports/customer-profile`
  - `POST /api/admin/logistics/exports/product-profile`
- 继续复用已有读取路由：
  - `GET /api/admin/logistics/exports/tasks/<task_no>`
  - `GET /api/admin/logistics/exports/tasks/<task_no>/lines`
  - `GET /api/admin/logistics/exports/tasks/<task_no>/errors`
  - `GET /api/admin/logistics/exports/tasks/<task_no>/error-report`
  - `GET /api/admin/logistics/exports/tasks/<task_no>/download`
- 控制器保持与现有导入/导出控制器同风格：
  - `_merged_payload`
  - `_json_response`
  - `_build_request_id`
- 顶层错误码继续沿用：
  - `0 / 4001 / 4003 / 4004 / 4090 / 5000`

### 完成标准

- 创建路由都能稳定返回冻结补丁稿中的 JSON shape。
- 参数错误、对象不存在、无权限、过期下载等均能返回稳定顶层码。
- 旧 `from_waybill` 路由行为不被破坏。

## 四、前端结果页工作包

### `CPPR-EXP-F1` 导出结果页对象分支

### 目标

- 在现有 `export_result_action.js` 基础上，扩出 `customer_profile` 与 `product_profile` 的结果页渲染分支，而不是再做一页新的结果页。

### 建议文件

- `custom_addons/logistics_web/static/src/js/actions/export_result_action.js`
- `custom_addons/logistics_web/static/src/xml/export_result_templates.xml`
- 如需抽公共 helper：
  - `custom_addons/logistics_web/static/src/js/actions/export_result_helpers.js`

### 主要任务

#### F1-1 摘要区分支

- 按 `object_type` 切摘要卡片：
  - `dispatch_main`
  - `customer_profile`
  - `product_profile`
- `customer_profile / product_profile` 改读：
  - `business_metrics`
  - `line_metrics`

#### F1-2 行结果区分支

- `customer_profile`
  - 展示客户画像对象名
  - 展示 `customer_count`
- `product_profile`
  - 展示商品名
  - 展示 `product_count / product_unit_count`

#### F1-3 文案与标签分支

- 不再把结果页里的文案都写死成“运单”“四 Sheet”
- 按对象类型切：
  - “客户画像导出结果”
  - “货物画像导出结果”

#### F1-4 向后兼容

- `dispatch_main` 继续读取旧的四段统计字段
- 新对象类型读取 `metrics_json`
- 避免一次性重构掉已稳定的 `from_waybill` 页面

### 完成标准

- 同一结果页 client action 能同时承载三类对象：
  - `dispatch_main`
  - `customer_profile`
  - `product_profile`
- 页面不再出现错误的“Waybill / GoodsLine”硬编码文案。

## 五、入口按钮工作包

### `CP-EXP-F2` 客户画像入口与跳转

### 目标

- 让用户可以从统一客户画像页直接发起导出，而不是回到原生列表工具栏找导出。

### 建议文件

- 更新 `custom_addons/logistics_web/static/src/js/components/list_import_button.js`
- 新增 `custom_addons/logistics_web/models/res_partner.py`
- 新增 `custom_addons/logistics_web/views/logistics_web_partner_views.xml`
- 更新 `custom_addons/logistics_web/__manifest__.py`

### 主要任务

#### F2-1 列表页按钮

- 扩展现有 `ListController` patch，不再只支持 `logistics.dispatch.waybill`
- 为 `res.partner` 增加导出按钮显示条件：
  - 当前 action 为统一客户画像列表
  - 只允许对 `is_logistics_partner = True` 的选中项发起导出
- 发起路由：
  - `POST /api/admin/logistics/exports/customer-profile`

#### F2-2 详情页按钮

- 在 `res.partner` 模型上增加 object 方法：
  - `action_open_customer_profile_export_result`
- 在统一客户画像表单页增加“导出结果”按钮

#### F2-3 跳转胶水

- 创建并执行任务后，统一跳转：
  - `tag = logistics_web.export_result`
  - `params.task_no`

### 完成标准

- 客户画像列表页支持勾选后批量导出。
- 客户画像详情页支持导出当前对象。
- 错误提示和成功跳转风格与运单导出一致。

### 明确不做

- 不给旧 `logistics.customer.profile` 和 `logistics.store.profile` 包装页单独做正式按钮。

### `PP-EXP-F2` 货物画像入口与跳转

### 目标

- 让用户可以从商品主档页直接发起货物画像导出。

### 建议文件

- 更新 `custom_addons/logistics_web/static/src/js/components/list_import_button.js`
- 新增 `custom_addons/logistics_web/models/product_template.py`
- 新增 `custom_addons/logistics_web/views/logistics_web_product_views.xml`
- 更新 `custom_addons/logistics_web/__manifest__.py`

### 主要任务

#### F2-1 列表页按钮

- 为 `product.template` 增加导出按钮显示条件
- 发起路由：
  - `POST /api/admin/logistics/exports/product-profile`
- 列表页文案不写“运单导出”，而写“导出”

#### F2-2 详情页按钮

- 在 `product.template` 模型上增加 object 方法：
  - `action_open_product_profile_export_result`
- 在商品主档表单页增加“导出结果”按钮

#### F2-3 入口取舍

- 首轮主入口以 `product.template` 为准
- `logistics.product.unit` 页面只作为后续可选增强，不在首轮单独发起正式导出

### 完成标准

- 商品主档列表页支持勾选后批量导出。
- 商品主档详情页支持导出当前对象。
- 跳转结果页逻辑与运单、客户画像保持一致。

## 六、Smoke 与验收工作包

### `CPPR-EXP-V1` Smoke、联调、验收回归

### 目标

- 为 `from_customer` 和 `from_product` 两条导出线提供最小可接受验证闭环。

### 建议验证文件

- `ai-code/.smoke/customer_profile_export_*/summary.json`
- `ai-code/.smoke/product_profile_export_*/summary.json`
- 如需人工 SOP，再补到：
  - `ai-code/专题设计/前端设计/四期前端优化设计/02_验收与联调/`

### 验证场景

#### V1-1 单客户画像成功导出

- 从统一客户画像详情页发起
- 成功进入结果页
- 可下载 `CustomerProfile` 文件

#### V1-2 多客户画像部分失败导出

- 列表页勾选多个对象
- 至少 1 条命中无效对象或关键字段缺失
- 任务进入 `partial_failed`
- 错误明细可读

#### V1-3 单商品成功导出

- 从商品主档详情页发起
- 成功生成 `ProductProfile / ProductUnit`

#### V1-4 多商品部分失败导出

- 列表页勾选多个商品
- 其中至少 1 条规格关系异常或数据不完整
- 任务进入 `partial_failed`

#### V1-5 权限回归

- 无对应对象读取权限的用户：
  - 不能发起导出
  - 不能下载别人的导出文件

### 完成标准

- 两条入口链路都能从页面发起、跳结果页、下载文件。
- 结果页统计与文件内容一致。
- `from_waybill` 现有 smoke 不回归失败。

## 七、排期建议

### 推荐先后

1. 先做 `CPPR-EXP-M1`
2. 再并行做 `CP-EXP-S1` 与 `PP-EXP-S1`
3. 然后做 `CPPR-EXP-C1`
4. 再做 `CPPR-EXP-F1`
5. 最后分别接 `CP-EXP-F2` 与 `PP-EXP-F2`
6. 用 `CPPR-EXP-V1` 收口

### 为什么先客户、后货物

- 客户画像主对象已经统一到 `res.partner`，边界更稳。
- 货物画像虽然首轮不复杂，但入口落在 `product.template` 原生页，前端接入点比客户页略分散。

## 八、完成定义

满足以下条件，才算本轮闭环完成：

1. 客户画像列表页和详情页都能发起正式导出。
2. 商品主档列表页和详情页都能发起正式导出。
3. 统一结果页能正确区分 `customer_profile / product_profile / dispatch_main` 三类对象。
4. 客户画像导出可下载 `CustomerProfile` 文件。
5. 货物画像导出可下载 `ProductProfile / ProductUnit` 文件。
6. 错误明细、错误报告、主文件下载都可用。
7. `from_waybill` 已上线能力不回归。

## 九、下一步建议

本拆分单确认后，推荐直接按下面顺序进入实现：

1. `CPPR-EXP-M1`
2. `CP-EXP-S1`
3. `PP-EXP-S1`

这样我们可以先把后端能力和 DTO 形状稳定下来，再平行接 Controller 和前端入口，不会在 UI 层反复返工。

