# 2026-04-24 from_waybill 首轮开发任务拆分单

## 文档定位

- 本文用于把标准批量导出里的 `from_waybill` 首轮切片拆成可直接排期和执行的开发工作包。
- 本文是 [四期批量导出正式落库与接口冻结稿](../02_跨模块规范/01_接口与数据/2026-04-24_四期批量导出正式落库与接口冻结稿.md) 的实现拆分层，不重新定义接口、底表或权限。
- 本文默认开发目标是：先打通 `from_waybill -> export task -> result page -> download` 最小闭环，再复用到 `from_batch / from_customer`。

## Outcome

- 用户可从运单列表页、运单详情页发起 `from_waybill` 标准导出。
- 系统可创建正式导出任务，生成四 Sheet `xlsx`，并在结果页回读任务摘要、行结果、错误明细和下载链接。
- 该切片完成后，应成为后续 `from_batch / from_customer` 的复用底座，而不是只做一次性代码。

## Boundary

- 只做 `from_waybill`。
- 只做 `dispatch_main + standard_xlsx + dispatch_main_four_sheet`。
- 不做图片 ZIP。
- 不做导出中心历史页。
- 不做字段级脱敏导出。
- 不做取消任务、批量重试、超大任务分片。

## 当前前提

- 正式导出模型与接口口径已冻结到：
  - `export_source_scope`
  - `export_task`
  - `export_task_line`
  - `export_error_line`
- 正式结果页阅读节奏明确复用导入结果页。
- 首轮文件保存策略明确为：
  - 本地文件存储
  - 元数据挂 `export_task`
  - 错误报告动态生成

## 推荐顺序

1. `WB-EXP-M1` 模型层
2. `WB-EXP-S1` 服务层最小闭环
3. `WB-EXP-C1` Controller 路由
4. `WB-EXP-F1` 前端结果页
5. `WB-EXP-F2` 发起入口与跳转胶水
6. `WB-EXP-V1` Smoke 与验收

说明：

- `WB-EXP-C1` 可以在 `WB-EXP-S1` 接口 shape 基本稳定后并行收尾。
- `WB-EXP-F1` 可在 DTO 冻结后先做页面骨架，不必等真实导出逻辑全部完成。

## 工作包总览

| 编号 | 工作包 | 责任面 | 前置依赖 |
| --- | --- | --- | --- |
| `WB-EXP-M1` | 导出正式模型与序列 | `logistics_dispatch` | 冻结稿已定 |
| `WB-EXP-S1` | `from_waybill` 导出服务主链 | `logistics_web/services` | `WB-EXP-M1` |
| `WB-EXP-C1` | 导出控制器与下载路由 | `logistics_web/controllers` | `WB-EXP-S1` |
| `WB-EXP-F1` | 导出结果页客户端动作 | `logistics_web/static` | `WB-EXP-C1` DTO 稳定 |
| `WB-EXP-F2` | 运单页导出入口与跳转 | `logistics_web/static` + 相关视图 | `WB-EXP-C1` |
| `WB-EXP-V1` | Smoke、联调、验收回归 | 全链路 | 前四包完成 |

## 一、模型工作包

### `WB-EXP-M1` 导出正式模型与序列

### 目标

- 在 `logistics_dispatch` 里补齐导出正式模型、sequence、access 和索引迁移。
- 为后续 `from_batch / from_customer` 留出共用骨架，但当前只先服务 `from_waybill`。

### 建议文件

- `custom_addons/logistics_dispatch/models/logistics_export_log.py`
- `custom_addons/logistics_dispatch/models/selection_options.py`
- `custom_addons/logistics_dispatch/models/__init__.py`
- `custom_addons/logistics_dispatch/data/sequence_data.xml`
- `custom_addons/logistics_dispatch/security/ir.model.access.csv`
- `custom_addons/logistics_dispatch/migrations/19.0.1.1.0/post-migration.py`

### 主要任务

- 新增 4 个模型：
  - `logistics.export.source.scope`
  - `logistics.export.task`
  - `logistics.export.task.line`
  - `logistics.export.error.line`
- 在 `selection_options.py` 新增导出相关枚举：
  - `EXPORT_OBJECT_TYPE_SELECTION`
  - `EXPORT_ENTRY_TYPE_SELECTION`
  - `EXPORT_MODE_SELECTION`
  - `EXPORT_PACKAGE_STRUCTURE_SELECTION`
  - `EXPORT_TASK_STATUS_SELECTION`
  - `EXPORT_TASK_LINE_STATUS_SELECTION`
  - `EXPORT_ERROR_STAGE_SELECTION`
- 新增 sequence：
  - `logistics.export.source.scope`
  - `logistics.export.task`
- 补 access：
  - `group_logistics_export_user`
  - `group_logistics_export_manager`
- 补迁移索引：
  - `export_task`
  - `export_task_line`
  - `export_error_line`

### 完成标准

- Odoo 模型可被正常加载。
- `_sql_constraints` 与字段名和冻结稿一致。
- `ir.model.access.csv` 无缺失引用。
- 模块升级后表、索引、sequence 均可见。

### 明确不做

- 不在这一包里写 controller。
- 不在这一包里写文件生成逻辑。
- 不补导出中心菜单。

## 二、服务工作包

### `WB-EXP-S1` `from_waybill` 导出服务主链

### 目标

- 在 `logistics_web/services` 打通 `from_waybill` 的服务最小闭环：
  - 创建范围
  - 创建任务
  - 读取运单数据
  - 生成四 Sheet
  - 写盘
  - 回写任务状态
  - 查询结果

### 建议文件

- 新增 `custom_addons/logistics_web/services/dispatch_main_export_service.py`
- 更新 `custom_addons/logistics_web/services/__init__.py`

### 主要任务

#### S1-1 请求体校验与建任务

- 校验：
  - `object_type = dispatch_main`
  - `entry_type = from_waybill`
  - `export_mode = standard_xlsx`
  - `selected_ids` 非空
- 创建：
  - `export_source_scope`
  - `export_task(status=pending)`
  - 对应 `export_task_line(status=pending)`

#### S1-2 运单取数与关系展开

- 按 `selected_ids` 读取 `logistics.dispatch.waybill`
- 展开：
  - `customer_line`
  - `order_line`
  - `goods_line`
- 取数优先走主链快照字段，避免深度联表
- 每个任务行按“单运单”为粒度聚合统计

#### S1-3 Workbook 生成

- 复用现有 `openpyxl` 能力
- 生成四 Sheet：
  - `Waybill`
  - `CustomerLine`
  - `OrderLine`
  - `GoodsLine`
- 列顺序与正式导入模板一致
- 空层允许保留表头无数据

#### S1-4 文件写盘与任务回写

- 按冻结稿目录策略落盘
- 计算：
  - `output_file_name`
  - `output_storage_path`
  - `output_file_sha256`
  - `output_file_size`
- 回写：
  - `download_ready_at`
  - `expires_at`
  - `status`
  - 四层统计字段

#### S1-5 结果查询服务

- 提供：
  - 任务摘要读取
  - 行结果分页读取
  - 错误明细分页读取
  - 错误报告动态生成
  - 主文件下载前校验

### 建议对外方法

- `create_waybill_export_task`
- `run_waybill_export_task`
- `get_export_task_result`
- `get_export_task_lines`
- `get_export_task_errors`
- `build_export_task_error_report`
- `get_export_download_file`

### 完成标准

- 对单个运单可成功生成标准四 Sheet 文件。
- 对多个运单可按任务行逐条写入 `export_task_line` 结果。
- 失败对象会写入 `export_error_line`，而不是只写任务头级文本。
- 能稳定返回冻结稿里的 DTO shape。

### 明确不做

- 不支持 `from_batch` 和 `from_customer`。
- 不支持 ZIP。
- 不做异步队列化重构；首轮允许同步服务内执行，只要任务状态闭环正确。

## 三、Controller 工作包

### `WB-EXP-C1` 导出控制器与下载路由

### 目标

- 在 `logistics_web/controllers` 平行导入控制器，补齐 `from_waybill` 首轮所需路由。

### 建议文件

- 新增 `custom_addons/logistics_web/controllers/logistics_web_export_v1.py`
- 更新 `custom_addons/logistics_web/controllers/__init__.py`

### 主要任务

- 新增路由：
  - `POST /api/admin/logistics/exports/waybill`
  - `GET /api/admin/logistics/exports/tasks/<task_no>`
  - `GET /api/admin/logistics/exports/tasks/<task_no>/lines`
  - `GET /api/admin/logistics/exports/tasks/<task_no>/errors`
  - `GET /api/admin/logistics/exports/tasks/<task_no>/error-report`
  - `GET /api/admin/logistics/exports/tasks/<task_no>/download`
- 统一返回顶层响应码：
  - `0`
  - `4001`
  - `4003`
  - `4004`
  - `4090`
  - `5000`
- 下载接口按冻结稿校验：
  - 文件存在
  - 未过期
  - 用户有权限

### 控制器规则

- 保持与导入控制器同风格：
  - `_merged_payload`
  - `_json_response`
  - `_build_request_id`
- 错误报告与主文件下载分开，不混一个路由。
- Controller 不直接拼业务数据，只做：
  - 参数接收
  - 服务调用
  - 异常转义
  - HTTP 响应

### 完成标准

- 所有路由都能返回与冻结稿一致的 JSON shape 或文件流。
- 参数错误、任务不存在、无权限、过期下载均能稳定返回对应顶层码。

## 四、前端结果页工作包

### `WB-EXP-F1` 导出结果页客户端动作

### 目标

- 做一套平行于导入结果页的导出结果页，而不是直接改造成“导入导出共用一页”。

### 建议文件

- 新增 `custom_addons/logistics_web/static/src/js/actions/export_result_action.js`
- 新增 `custom_addons/logistics_web/static/src/xml/export_result_templates.xml`
- 更新 `custom_addons/logistics_web/static/src/js/actions/logistics_action_registry.js`
- 更新 `custom_addons/logistics_web/views/logistics_web_actions.xml`
- 更新 `custom_addons/logistics_web/__manifest__.py`

### 主要任务

#### F1-1 结果页 Action 骨架

- 新增 client action：
  - `logistics_web.export_result`
- 页面参数以 `task_no` 为主

#### F1-2 摘要区

- 展示：
  - `task_no`
  - `entry_type`
  - `status`
  - `summary_message`
  - 四层导出统计
  - 下载按钮

#### F1-3 行结果区

- 读取 `/lines`
- 支持：
  - 状态筛选
  - 分页
  - `export_count_summary`

#### F1-4 错误明细区

- 读取 `/errors`
- 支持分页
- 优先展示：
  - `field_name`
  - `error_code`
  - `error_message`

#### F1-5 动作区

- 固定动作建议：
  - 刷新结果
  - 下载导出文件
  - 下载错误报告
  - 返回运单列表

### 页面策略

- 结构节奏复用导入结果页，但文案换成导出语义。
- 不在本页补“导出中心历史”入口。
- 不在本页补复杂图表。

### 完成标准

- 可通过 `task_no` 正常打开结果页。
- 可回读摘要、行结果、错误明细。
- 可触发主文件与错误报告下载。
- 加载态、空态、错误态、无权限态文案齐全。

## 五、入口胶水工作包

### `WB-EXP-F2` 运单页导出入口与跳转

### 目标

- 把 `from_waybill` 真正接到用户入口，而不是只剩 API 和结果页。

### 建议文件

- 视实现方式选择其一：
  - 新增 `custom_addons/logistics_web/static/src/xml/list_export_button.xml`
  - 或扩展现有 `list_import_button.xml` 旁路实现
- 如需新增 client action 跳转参数：
  - `custom_addons/logistics_web/views/logistics_web_actions.xml`
- 如需从运单模型暴露按钮支持信息：
  - `custom_addons/logistics_dispatch/models/logistics_dispatch_waybill.py`

### 主要任务

- 运单列表页：
  - 支持勾选后“批量导出”
- 运单详情页：
  - 支持“导出当前运单”
- 发起成功后：
  - 直接跳到 `logistics_web.export_result`
  - 带上 `task_no`

### 完成标准

- 列表页和详情页都能稳定发起 `from_waybill` 导出。
- 发起完成后跳结果页，不停留在静默后台。
- 无权限用户不显示或不可触发导出入口。

## 六、联调与验证工作包

### `WB-EXP-V1` Smoke、联调、验收

### 目标

- 为 `from_waybill` 首轮提供最小可接受验证闭环。

### Smoke 场景

#### V1-1 单运单成功导出

- 输入：
  - 1 条完整运单
  - 有 `customer_line / order_line / goods_line`
- 期望：
  - `export_task.status = success`
  - 四 Sheet 文件可下载

#### V1-2 多运单部分失败导出

- 输入：
  - 2 到 3 条运单
  - 至少 1 条人为制造“无下游数据”或关系断裂
- 期望：
  - `status = partial_failed`
  - 行结果正确区分 `success / failed / skipped`
  - 错误报告可下载

#### V1-3 过期下载校验

- 人工把 `expires_at` 调到过去时间
- 期望：
  - `/download` 返回过期错误

#### V1-4 权限校验

- 导出用户
  - 能看自己的任务
- 非授权用户
  - 不能发起导出
  - 不能下载别人的导出文件

### 验收输出

- 一份 smoke 记录
- 一份接口回包样例
- 一份结果页截图或录屏
- 一条 change note

## 七、并行建议

可并行拆法建议如下：

- 后端 A：
  - `WB-EXP-M1`
- 后端 B：
  - `WB-EXP-S1`
  - 在模型字段冻结后接入
- 前端：
  - `WB-EXP-F1`
  - 先按冻结稿 DTO 搭结果页骨架
- 前后端联调：
  - `WB-EXP-F2`
  - `WB-EXP-V1`

## 八、当前不建议拆散的部分

- `Workbook` 组装与文件写盘不要再拆成两个独立包，否则很容易来回返工。
- 结果页摘要、行结果、错误明细不要由不同人各自定义 DTO，应统一以冻结稿返回结构推进。
- `from_waybill` 入口发起和结果页跳转不要分两个阶段上线，否则用户体验会断层。

## 九、开发完成判定

满足以下条件，才算 `from_waybill` 首轮闭环完成：

1. 运单列表页和详情页都能发起导出。
2. 后端能生成正式四 Sheet `xlsx`。
3. `task_no -> result -> lines -> errors -> download` 全链路打通。
4. 成功、部分失败、过期、无权限四类场景都能稳定返回。
5. 该实现没有写死成只服务单一运单按钮的“特例代码”，而是可继续复用到 `from_batch / from_customer`。

## 十、下一步衔接

`from_waybill` 完成后，后续建议按下面顺序衔接：

1. 复用服务骨架接 `from_batch`
2. 再补 `from_customer`
3. 最后再评估是否需要导出中心历史页
