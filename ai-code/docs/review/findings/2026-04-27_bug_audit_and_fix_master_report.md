# 2026-04-27 Bug 排查与修复总报告

## 1. 报告目的

本报告用于汇总 2026-04-27 这一轮针对 Odoo 物流项目所做的 bug 排查、修复与最小验证结果，替代此前分散在 `docs/review/findings/` 下的多份阶段性小报告。

本轮覆盖的核心目标是：

- 收口 `waybill -> trace -> evidence -> exception` 主链风险
- 收口 `wave -> batch -> waybill` 执行主链上游风险
- 收口 import/export、driver/vehicle、stats、dashboard 等外围高风险接口
- 收口主数据与 profile 查询/权限/同步一致性问题

## 2. 覆盖范围

### 已做系统排查并落修复的活跃模块

- `logistics_web`
- `logistics_dispatch`
- `logistics_trace_core`
- `logistics_trace_evidence`
- `logistics_trace_exception`
- `logistics_base`

### 已确认但未作为活跃模块深审的桥接目录

- `logistics_order`
- `logistics_trace`
- `logistics_exception`

结论：这 3 个当前主要是桥接/历史目录，不承载当前主链运行逻辑。

## 3. 排查与修复汇总

### 3.1 导出链

#### 发现的问题

- 下载接口信任数据库里的绝对路径，存在任意服务器文件读取风险
- 导出任务模型权限过宽，普通用户可能看到或篡改不属于自己的任务元数据
- 同步执行路径缺少兜底，异常时任务可能永久卡在 `running`
- 顶层错误码没有按冻结稿落地
- 普通内部用户在 `from_waybill` 导出中会撞到 `hr.employee.public` 字段权限问题

#### 已完成修复

- `output_storage_path` 改为相对路径，下载时强制校验必须落在导出根目录内
- 导出任务 ACL 与 record rule 收紧为 owner / manager 边界
- 同步执行链补齐异常兜底，异常任务自动回写为 `failed`
- 顶层错误码统一收口为 `4001 / 4003 / 4004 / 4090 / 5000`
- `from_waybill` 导出改为优先使用批次快照读取司机信息，必要时最小 `sudo` 回退

#### 验证结果

- 本人下载成功
- 非本人下载返回 `4003`
- 未完成任务下载返回 `4090`
- 非法路径记录下载返回 `4003`
- 普通内部用户 `from_waybill` 导出成功

### 3.2 导入链与非导出接口

#### 发现的问题

- 导入任务与明细模型曾对 `base.group_user` 开全权限
- 导入源文件读取同样信任数据库里的绝对路径
- 统计接口对坏参数缺少统一兜底
- `driver / vehicle` 顶层错误码契约不一致
- 导入接口自身顶层错误码未与导出链对齐

#### 已完成修复

- 收紧 `source_file / task / task_line / error_line` ACL，并补 owner read 规则
- 导入源文件改为相对 key + 固定根目录校验
- `stats` 将非法日期、非法 `limit` 等统一收口为 `4001`
- `driver / vehicle` 的 `ValidationError / ValueError / TypeError` 统一映射到 `4001`
- 导入接口顶层错误码与导出链统一为 `4001 / 4003 / 4004 / 4090 / 5000`
- 跨用户按 `task_no` 读导入任务时显式返回 `4003 / IMPORT_PERMISSION_DENIED`

#### 验证结果

- 导入任务 owner 可见，non-owner 不可见
- owner 可读任务行，non-owner 被拒绝
- 非法源文件路径被拦截
- 非法 Base64 预校验返回 `4001`
- 失效确认令牌返回 `4090`
- 不存在的导入任务结果返回 `4004`

### 3.3 trace evidence / exception / dashboard

#### 发现的问题

- `evidence / exception / process_log` 曾对普通内部用户开全量 CRUD
- 异常状态流转和处理日志缺少后端护栏，处理历史可被伪造
- `logistics_trace_evidence` 对 `logistics_trace_exception` 扩展字段存在隐藏依赖
- dashboard “今日异常”统计存在本地时区与 UTC 口径错位风险
- dashboard controller 对意外异常缺少统一 JSON 兜底

#### 已完成修复

- 收紧 `evidence / exception / process_log` ACL 和 record rule
- `process_log` 改为只允许系统生成，手工 `create / write / unlink` 被阻止
- 异常状态机加入后端状态约束、`close_summary` 强校验和 `sudo()` 审计日志写入
- `is_exception_related` 改为直接基于 `trace_event_id.event_type == "exception_report"` 计算
- dashboard 服务改为按时区安全窗口计算“今日”
- dashboard controller 增加 `5000 / ANALYSIS_INTERNAL_ERROR` 兜底

#### 验证结果

- owner 仅可见自己的 exception / evidence / process_log
- non-owner 不可见
- manager 可推进异常到 `processing`
- `open -> closed` 的越级关闭被拦截
- 缺少 `close_summary` 不能关单
- dashboard summary / boss trace summary 正常
- 强制异常时 dashboard 返回标准 `5000`

### 3.4 trace core 与 dispatch 上游主链

#### 发现的问题

- `logistics.trace.event` 曾对 `base.group_user` 开全量 CRUD
- `waybill / batch` 绑定约束不完整，存在对象错挂风险
- trace 聚合会把无效/草稿事件也算进统计
- `partial` 状态声明存在但此前不可达
- 普通内部用户曾可直接修改 `wave / batch / waybill`
- `waybill.warehouse_id` 与 `batch_id` 缺少一致性护栏
- trace 完成态不会回推 dispatch 执行态，`finished_waybill_count` 可能失真

#### 已完成修复

- 收紧 `trace event` ACL：内部用户只读/可新建，manager 可写，不允许删除
- trace 菜单只对 manager 暴露，运单调试区禁掉原始 trace 直接开表单入口
- 补齐 `waybill / batch` 一致性约束，禁止错误写穿
- trace 聚合只统计 `submitted`
- `arrive_trace_status / signoff_trace_status` 的 `partial` 变为真正可达
- `evidence_count` 同步只统计有效 trace
- 收紧 `wave / batch / waybill` ACL，普通内部用户改为只读
- `batch` 自动继承 `wave.warehouse_id`，`waybill` 自动继承 `batch.warehouse_id`
- 增加 trace -> dispatch 执行态的“只前推、不回退、不覆盖 cancelled”规则

#### 验证结果

- 普通内部用户修改 `wave / batch / waybill` 被 `AccessError` 拦截
- 错误 `waybill + batch` / `batch trace + waybill` 组合被后端拦截
- `invalid` 不再污染 `trace_count / latest_trace_type / evidence_count`
- 创建有效 `signoff` trace 后，`waybill.state = done`
- `batch.finished_waybill_count` 自动闭环

### 3.5 driver / vehicle / stats 回归

#### 检查目标

确认 `done` 状态闭环引入后，司机、车辆、统计中心对签收/完成状态的解释没有偏差。

#### 验证结果

- `driver` 月运单数与签收率按 `done` 增量
- `vehicle` 月运单数与签收率按 `done` 增量
- `stats` 总览与趋势中的 `signed_rate / waybill_count` 口径同步一致

结论：这一层没有发现新的 `P1 / P2` 级回归问题。

### 3.6 logistics_base 与 dispatch 明细对象

#### 发现的问题

- `goods_line_v2` 曾按非存储字段反查 `customer_line`，是实锤运行时 bug
- `logistics_base` 画像主数据曾对普通内部用户全量开放 CRUD
- `customer_line / goods_line / order_line` 缺少跨层一致性约束
- route planning 草稿与主数据变更日志对象权限过宽
- route planning stop line 缺少批次内唯一性保护

#### 已完成修复

- `goods_line_v2` 改为先解析客户，再用可搜索的 `partner_id + waybill` 定位 `customer_line`
- 收紧 `logistics_base` 的 customer/store/product unit/driver/vehicle profile ACL
- 收紧 route planning / master data change log ACL
- 为 `order_line` 和 `goods_line` 补齐跨层一致性约束
- 收紧 `customer_line / goods_line / order_line` ACL
- 为 route planning stop line 增加 `(batch_id, stop_seq)` 和 `(batch_id, waybill_no)` 唯一性约束

#### 验证结果

- `goods_line` 按 `waybill_no + customer_no` 能正确解析目标 `customer_line`
- 普通内部用户写 profile / route planning / master data log 被拦截
- 错配的 `order_line / goods_line` 串链被 `ValidationError` 拦截
- route planning stop line 的重复批次顺序/运单被唯一约束拦截

### 3.7 主数据编码、snapshot 同步与 profile 展示

#### 发现的问题

- `res.partner` 主数据允许重复编码，但下游把这些编码当唯一键使用
- `waybill.partner_id` 的 inverse 写回链曾导致递归死循环
- `wave -> batch -> waybill -> customer_line` 的 snapshot 自动回填基本不工作
- `driver / vehicle` 页面门店统计仍按单一 `waybill.store_id`
- driver profile 的 `remark` 来自当前模型中不存在的字段
- stats center 可跳到 driver 管理页，但权限链此前不一致

#### 已完成修复

- 为 `logistics_customer_code / logistics_store_code / internal_customer_code` 增加唯一约束与归一化逻辑
- 拆掉 `waybill.partner_id` 的递归 inverse 写回链，改为统一 normalize 同步
- 系统补齐 wave/batch/waybill/customer_line/order_line 的 snapshot 自动回填
- driver / vehicle 页面改为优先读取 `customer_line_ids.partner_id` 统计门店与区域
- 新增 `logistics.driver.profile.driver_remark`，driver overview 改为返回正式字段
- `group_logistics_analysis_viewer` 显式继承 `group_logistics_driver_management_viewer`

#### 验证结果

- 重复客户编码被数据库唯一约束拦截
- `partner_id` 直建 `waybill` 成功
- 关键 snapshot 字段自动落值
- 临时双配送节点运单在 driver/vehicle recent waybills 中显示合并门店名
- `driver_overview.remark` 正常回显 `driver_remark`
- 只给 `analysis viewer` 的临时用户可成功访问 `getDriverList`

### 3.8 logistics_web 导出权限与标签同步治理

#### 发现的问题

- 司机路线 Excel 直下接口曾缺少独立导出权限护栏
- 客户/商品画像导出按钮可绕过专用导出分组
- `ui_label_sync` 升级时会触发全局菜单重排和资产重建，副作用超出模块边界

#### 已完成修复

- 导出权限统一收口到 `group_logistics_export_user / manager`
- 批次页司机路线导出按钮、客户/商品画像导出按钮补齐分组限制
- `ui_label_sync` 只同步物流自有菜单和 action，不再改其他模块，也不再强制重建资产

#### 验证结果

- 普通用户司机路线导出被拦成 `EXPORT_PERMISSION_DENIED`
- 普通用户客户/商品画像导出被拦成 `EXPORT_PERMISSION_DENIED`
- 临时赋权用户司机路线导出成功
- 临时赋权用户客户/商品画像导出成功
- 临时赋权用户商品画像导出成功

## 4. 总体验证结论

本轮已完成：

- 多次模块升级验证
- 多轮短命 `odoo-bin shell` smoke
- ACL / record rule / 错误码 / 状态机 / 数据一致性 / 路径安全 / 统计口径 / profile 展示 的针对性回归

截至本报告输出时，以上修复项均已通过最小验证，没有发现新的同级 `P1 / P2` 回归问题。

## 5. 仍未做更深层穷尽排查的区域

本轮已经覆盖所有当前活跃自定义模块的高风险主链，但以下区域尚未做更深层的穷尽式排查：

- 官方基础模块继承链：`res.partner / hr.employee / fleet.vehicle / stock.warehouse / mail / base`
- `logistics_base` 的全量表单、对象方法、边界输入回归
- `logistics_dispatch` 的复杂业务流、并发与大数据量查询场景
- `logistics_web` 的完整前端交互层和 client action 联调回归
- `waybill -> trace -> evidence -> exception` 的全链路端到端业务回归

## 6. 当前总判断

如果按“是否已做过系统级高风险排查”来看，本轮已经把当前活跃自定义模块的主风险面基本收口。

如果按“是否已经彻底穷尽所有边界情况”来看，当前还没有达到那个程度；但对现阶段最影响稳定性、权限安全、数据一致性和接口契约的风险点，已经完成了较完整的一轮审计与修复。
