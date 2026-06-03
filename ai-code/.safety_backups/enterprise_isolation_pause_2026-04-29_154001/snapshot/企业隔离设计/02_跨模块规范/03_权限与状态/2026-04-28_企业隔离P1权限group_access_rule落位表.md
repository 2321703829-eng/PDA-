# 2026-04-28 企业隔离 `P1` 权限 `group / access / rule` 落位表

## 1. 文档定位

- 本文用于把当前权限分组建议进一步压成可直接指导实现的落位表。
- 本文默认沿用当前 `P1` 轻量权限方案，不追求一次做成最终平台级矩阵。
- 本文重点回答：
  - 哪些组保留
  - 哪些组新增
  - 哪些模型应给什么 `access`
  - 哪些对象需要什么 `rule`

## 2. 前置基线

本文以前置文档为准：

- `2026-04-27_企业隔离P1租户内权限分组建议稿.md`
- `2026-04-27_现有Odoo权限体系与企业隔离P1角色矩阵复用对照表.md`
- `2026-04-27_企业隔离P1_三层联动与租户内角色矩阵细稿.md`

## 3. 当前 `P1` 最小角色口径

当前 `P1` 最小角色口径收口为：

- `group_logistics_tenant_admin`
- `group_logistics_dispatch_operator`
- `group_logistics_image_field_operator`
- `group_logistics_readonly_viewer`

能力组继续复用或新增：

- `group_logistics_dispatch_manager`
- `group_logistics_trace_event_manager`
- `group_logistics_export_user`
- `group_logistics_export_manager`
- `group_logistics_profile_manager`
- `group_logistics_image_auditor`
- `group_logistics_exception_handler`

## 4. 组落位建议

### 4.1 建议保留并继续复用

| 组名 | 当前建议定位 | 说明 |
| --- | --- | --- |
| `group_logistics_dispatch_manager` | 主链管理能力组 | 继续承接执行主链高权限 |
| `group_logistics_trace_event_manager` | 留痕管理能力组 | 继续承接留痕全量查看与维护 |
| `group_logistics_export_user` | 导出执行能力组 | 承接普通导出动作 |
| `group_logistics_export_manager` | 导出管理能力组 | 承接导出任务全量查看 |
| `group_logistics_profile_manager` | 主数据维护能力组 | 保持不动 |

### 4.2 建议新增

| 组名 | 建议类型 | 作用 |
| --- | --- | --- |
| `group_logistics_tenant_admin` | 基础角色组 | 租户库内总管理入口组 |
| `group_logistics_dispatch_operator` | 基础角色组 | 调度 / 客服日常业务组 |
| `group_logistics_image_field_operator` | 基础角色组 | 图片导入 / 现场工作人员组 |
| `group_logistics_readonly_viewer` | 基础角色组 | 只读查看组 |
| `group_logistics_image_auditor` | 能力组 | 图片补链 / 审计能力组 |
| `group_logistics_exception_handler` | 能力组 | 异常跟进 / 关闭能力组 |

## 5. `access` 落位总表

说明：

- 下表是 `P1` 首轮建议，不等于最终完整矩阵。
- `unlink` 当前一律从严，不建议首轮向普通业务角色开放。
- “读”与“写”之外的更细动作，继续由 `rule`、接口层和模型层兜底。

| 模型 | 只读查看 | 调度 / 客服 | 图片导入 / 现场 | 留痕管理 | 图片审计 | 异常处理 | 租户管理员 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `wave / batch / waybill / customer_line / order_line / goods_line` | `read` | `read` | `read` | `read` | `read` | `read` | `read/write/create` |
| `logistics.trace.event` | `read` | `read/create` | `read/create` | `read/write/create` | `read` | `read` | `read/write/create` |
| `logistics.trace.evidence` | `read` | `read` | `read` | `read` | `read/write/create` | `read` | `read/write/create` |
| `logistics.trace.exception` | `read` | `read/create` | `read` | `read` | `read` | `read/write/create` | `read/write/create` |
| `image_package` 相关导入任务 | 否 | `read` 按需 | `read/create` | `read` | `read/write/create` | `read` | `read/write/create` |
| 导出任务对象 | 否 | 否或按需 | 否 | 否 | 否 | 否 | `read/write/create` |

## 6. `rule` 落位建议

### 6.1 当前 `P1` 首轮最小规则

| 对象 | 建议规则 | 说明 |
| --- | --- | --- |
| 导入任务 | 本人可看 / 审计组可看全部 / 租户管理员可看全部 | 继续沿用“本人 vs manager”思路 |
| 导出任务 | 发起人可看本人 / 导出管理与租户管理员可看全部 | 保持现有导出任务模式 |
| 证据对象 | 默认只允许在当前租户库范围读取 | 企业间隔离仍由数据库兜底 |
| 异常对象 | 默认历史可读，写动作必须带角色与状态双校验 | 不只靠 `rule` |
| 留痕对象 | 默认当前租户内可读，创建按组放开 | 修改动作只给管理类组 |

### 6.2 不建议在 `P1` 首轮直接展开的复杂规则

- 组织树 / 区域树 / 门店树完整数据域
- 很细的仓、线路、责任人范围隔离
- 套餐到期后的自动只读规则

## 7. 页面层与模型层补充要求

### 7.1 页面层

- 控菜单显隐
- 控按钮显隐
- 控摘要区只读提示

### 7.2 接口层

- 控导出接口入口
- 控图片上传与补链重试入口
- 控异常关闭入口

### 7.3 模型层

- 兜底拦截非法状态流转
- 兜底拦截越权补链
- 兜底拦截越权修改留痕

## 8. 首轮实现优先级

### 第 0 优先级

- 收紧 `base.group_user` 对 `trace / evidence / exception` 的默认写权限
- 建立 `group_logistics_image_field_operator`
- 建立 `group_logistics_readonly_viewer`

### 第 1 优先级

- 建立 `group_logistics_image_auditor`
- 建立 `group_logistics_exception_handler`
- 把导入任务、导出任务、补链失败查看切到新口径

### 第 2 优先级

- 进一步拆细 `group_logistics_trace_manager`
- 补更细数据域规则

## 9. 一句话收口

这份落位表的核心目的不是把权限一次设计到极限，而是先把 `P1` 真正会写代码的那层落清楚：组怎么建、`access` 怎么给、`rule` 先做到哪一步。
