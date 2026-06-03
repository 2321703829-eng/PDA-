# 2026-04-18 权限与角色规范补充 res.groups 映射草稿

## 本次变更

补充 `仓管模块设计/01_模块设计/08_设置与规则/00_权限与角色规范草稿.md`：

- 新增 `10. 与 res.groups 的实际落地映射草稿`
- 将原 `v0.1 收口与后续补充方向` 顺延为 `11`
- 同步更新目录索引、章节总览与阅读主线说明

## 本次补充的重点

### 1. 固定了业务角色到 group 的映射方向

本次把前面已经确认的 5 类业务角色，统一映射成以下一组 `logistics_wms` 方向的 group XML ID：

- `logistics_wms.group_wms_operator`
- `logistics_wms.group_wms_supervisor`
- `logistics_wms.group_wms_exception_handler`
- `logistics_wms.group_wms_admin`
- `logistics_wms.group_wms_readonly`

### 2. 固定了组设计原则

本次明确了：

- 先按角色职责建组
- 不按单个页面零碎建组
- 菜单、页面、动作仍需在 group 之上继续细化
- 管理员组作为兜底组，但不替代其他业务组的定义

### 3. 固定了五类组的职责边界

本次进一步明确了：

- 操作员组偏高频执行
- 主管组偏管理与关键动作
- 异常处理组偏异常闭环
- 管理员组偏全局维护与兜底
- 只读组偏查看与追溯

## 当前意义

这次补充后，这份权限专题已经从：

- 菜单、页面、动作三层权限矩阵

继续推进到了：

- 业务角色与 Odoo `res.groups` 的实际映射草稿

后续如果继续细化菜单权限、按钮显隐、记录规则或 `security/*.xml`，已经有一层更稳定的 group 基线可依附。
