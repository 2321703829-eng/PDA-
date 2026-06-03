# 2026-04-27 Export Chain Review Fixes

## Objective

修复导出主链 code review 中确认的 4 个问题：

- 下载接口信任 `output_storage_path`，存在越权读取服务器文件的风险
- 普通内部用户可通过模型层读取他人导出任务元数据
- 同步执行链路异常时，任务可能永久卡在 `running`
- 导出接口顶层错误码未按冻结稿契约返回

## Boundary

- 本次只修复 `logistics_web` 导出链和共享导出任务权限边界
- 不改导出业务对象、导出文件结构和前端页面交互
- 不引入新的异步任务框架，只先补齐同步执行下的失败闭环

## Changes

### 1. Output file path hardening

- `dispatch_main_export_service` 新增导出文件路径解析与根目录约束
- 下载前统一校验实际解析路径必须落在导出根目录下
- 新写入的 `output_storage_path` 改为相对根目录的相对路径，避免持久化绝对路径
- `customer_profile` 和 `product_profile` 导出服务同步复用同一套存储逻辑
- `from_waybill` 导出中的司机姓名/电话改为优先使用批次快照，必要时再用 `sudo` 做最小字段回退，避免普通内部用户导出时触发 `hr.employee.public` 私有字段访问错误

### 2. Running task closure

- 三条导出执行链均补充外层异常兜底
- 若任务已进入 `running` 但后续阶段抛出未预期异常，会回写为 `failed`
- 保留原有业务异常的 `error_code / error_message` 语义

### 3. Export ACL and record rules

- 收紧 `group_logistics_export_manager` 对导出任务头与来源快照的写权限
- 新增导出任务、任务行、错误行、来源快照的 record rule
- 普通执行用户仅可读取自己发起的导出任务链
- 导出管理用户可读取全部导出任务链
- 将“本人可读”规则显式绑定到 `base.group_user`，与当前真实导出入口口径保持一致，避免规则只挂在 `group_logistics_export_user` 时仍然出现模型层越权可见

### 4. Top-level error contract

- `logistics_web_export` 补充顶层错误码映射
- 当前按冻结稿收口：
  - `4001`: 参数/输入非法
  - `4003`: 权限或非法文件访问
  - `4004`: 资源不存在
  - `4090`: 状态冲突、未就绪、已过期
  - `5000`: 其他未分类服务异常
- 补充覆盖 `EXPORT_DOWNLOAD_PERMISSION_DENIED` 等带 `PERMISSION` 片段的权限错误，避免越权读取被误归类为 `5000`
- 补充覆盖 `...STATUS_INVALID`、`...NOT_FINISHED` 一类任务状态冲突错误，保证未完成任务下载回落到 `4090`

## Verify

最小验证包含：

- 受影响 Python 文件 `ast.parse`
- 新增/修改的 XML 文件解析
- ACL CSV 变更检查
- 关键修复点文本检索

## Risks

- 本次没有引入新的导出重试机制，只先保证失败闭环正确
- 历史任务若已写入异常绝对路径，下载时会被拒绝并返回非法文件访问错误
- 运行时行为仍建议补一轮真实导出 smoke，重点覆盖：
  - 本人下载成功
  - 非本人读取受限
  - 非法状态下载返回 `4090`
  - 非法路径记录返回 `4003`
