# 2026-04-18 执行页组件命名与文件映射专题补充 service / hook 命名规则

## 本次变更

补充 `仓管模块设计/01_模块设计/02_执行页组件命名与文件映射草稿.md`：

- 新增 `10. 执行页 service / hook 命名规则`
- 将原 `v0.1 收口与后续补充方向` 顺延为 `11`
- 同步更新目录索引、章节总览与阅读主线说明

## 本次补充的重点

### 1. 公共 service 命名口径

固定了一组当前推荐的公共执行 service 命名方向：

- `executionFeedbackService`
- `executionNavigationService`
- `executionDraftInputService`
- `executionScanService`

用于统一承接：

- 提示反馈
- 页内导航
- 未保存输入
- 扫码接入

### 2. 动作专用 service 命名口径

固定了一组当前推荐的动作专用 service 命名方向：

- `receiveExecutionService`
- `putawayExecutionService`
- `pickExecutionService`
- `checkExecutionService`

用于承接四类执行页各自动作语义下的专属流程封装。

### 3. hook 命名口径

固定了两层 hook 命名思路：

- 公共 hook：`useExecutionXxx`
- 动作专用 hook：`use动作语义ExecutionXxx`

并给出了示例：

- `useExecutionPendingSelection`
- `useExecutionActionState`
- `useExecutionFeedback`
- `useExecutionUnsavedGuard`
- `useExecutionScanner`

以及：

- `useReceiveExecutionFields`
- `usePutawayExecutionFields`
- `usePickExecutionFields`
- `useCheckExecutionFields`

## 当前意义

这次补充后，这份专题稿已经从：

- 入口命名
- 组件命名
- 模板命名
- 文件映射

继续推进到了：

- service 命名
- hook 命名
- 公共层与动作专用层的语义分层

后续前端真正落 `logistics_wms_web` 执行页时，命名体系已经更完整了。
