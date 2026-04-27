# 2026-04-11-007 Align Naming, State Machine, and Real Storage

## 背景
在重新通读 `odoo-reconstruct-main` 里的规范文档后，确认 `feat-image-4a` 之前有几类偏差：

- 模型字段命名没有完全按统一规范收口
- 状态机和值域与设计文档不一致
- 仍残留“外接 image-manager-main 才能跑”的表述
- 测试里还保留了 mock 写法，不适合后续真实可行性验证

## 本次改动

### 1. 留痕模型按统一命名纠偏
- `subject_type -> biz_type`
- `event_type -> trace_type`
- `source -> trace_source`
- `note -> remark`

同时把留痕状态机改成：

- `new`
- `done`
- `void`

### 2. 证据模型按统一命名纠偏
- `trace_event_id -> trace_id`
- `subject_type -> biz_type`
- `description -> remark`

同时把证据状态机改成：

- `new`
- `ok`
- `bad`
- `del`

并把 `evidence_type` 收口为：

- `image`
- `sign`
- `file`
- `video`
- `other`

### 3. 视图和搜索统一改字段引用
同步修正了 tree / form / search 视图中对旧字段名的引用，避免后续模块安装时出现字段不存在的问题。

### 4. 图片存储口径改为服务器侧真实存储
当前图片存储继续坚持：

- 不走 Odoo 默认附件图片存储方式
- 二进制真实写入服务器存储目录
- Odoo 只维护业务关系和元数据

并把 `storage_provider` 收口成当前实现可用的 `local`。

### 5. 增加真实预览 / 下载入口
补充了 Odoo 控制器：

- `/logistics_trace/evidence-images/<image_access_key>`

现在预览和下载不再只是元数据字段，而是有实际路由返回文件内容。

### 6. 测试移除 mock 依赖
把原来依赖 mock 的两组测试改成基于临时目录的真实文件写入 / 读取校验，更贴近后续你们上服务器前的真实可行性验证。

## 当前结果
本轮改动后，`feat-image-4a` 更接近下面这个目标：

- 在 Odoo 内实现图片证据能力
- 对外保持标准 addon 结构
- 对内按你们统一规范命名
- 对部署环境只要求数据库和服务器存储目录

## 仍待继续的点
- `services/image_service_client.py` 文件名还偏历史命名，后续可再收口
- 旧说明文档还需要继续合并整理
- 最终还需要在你们自己的 Odoo 环境和数据库里做一次真实安装验收
