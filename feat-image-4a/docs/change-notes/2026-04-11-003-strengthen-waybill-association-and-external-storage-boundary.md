# Change Notes

## 本轮目标
进一步强化 `feat-image-4a` 的两条核心边界：

- 图片上传默认关联运单号，而不是订单号
- 图片二进制继续存储在服务器侧独立图片服务，不采用 Odoo 自带附件存储方式

## 修改文件
- `feat-image-4a/addons/logistics_trace_core/models/logistics_trace_event.py`
- `feat-image-4a/addons/logistics_trace_core/views/logistics_trace_event_views.xml`
- `feat-image-4a/addons/logistics_trace_evidence/models/logistics_trace_evidence.py`
- `feat-image-4a/addons/logistics_trace_evidence/views/logistics_trace_evidence_views.xml`
- `feat-image-4a/addons/logistics_trace_evidence/tests/test_logistics_trace_evidence.py`
- `feat-image-4a/docs/协作边界说明.md`
- `feat-image-4a/docs/接入与验收说明.md`

## 修改原因
- 最新要求已经明确：`image-manager-main` 是高水平参照标准，当前目标不是偏离它，而是把它的核心能力整合进 Odoo。
- 同时也已经明确：门店交付类图片的业务主对象是运单号，不是订单号。
- 为避免后续团队总装时再把图片能力误接回 Odoo 附件体系，本轮需要把“运单关联 + 外部存储”两个边界再显式强化一次。

## 改动摘要
- 证据对象新增显式关联字段：
  - `subject_type`
  - `batch_no`
  - `waybill_no`
- 图片引用对象新增显式关联字段：
  - `subject_type`
  - `batch_no`
  - `waybill_no`
- 证据列表、证据表单、图片列表里都直接展示 `waybill_no` / `batch_no`
- 测试中新增对 `waybill_no` 继承关系的断言
- 文档中明确写清：
  - 图片上传关联运单号，不关联订单号
  - 图片二进制保存在独立图片服务，不保存在 Odoo 附件体系

## 业务边界
门店交付类图片：
- 主体是 `waybill`
- 证据对象与图片对象都应能直接看到 `waybill_no`

装车前留痕类图片：
- 主体允许是 `batch`
- 证据对象与图片对象应能直接看到 `batch_no`

统一原则：
- 都不走订单号主挂载

## 风险点
- 当前仍然是编号字段挂接，后续与正式运单/批次对象接上后可能还要把 related 字段换成真正外键来源。
- 目前还没有在真实 Odoo 环境中完成安装和 UI 验证。

## 验证方法
- 创建运单级留痕事件与证据对象
- 上传图片后检查图片引用记录是否自动带出 `waybill_no`
- 检查 Odoo 中没有保存图片二进制，只保存 `image_access_key` 与元数据关系

## 后续待办
- 继续向 `image-manager-main` 的能力靠拢，补齐更细的元数据同步和错误处理
- 等调度侧正式对象落下后，将 `waybill_no` / `batch_no` 从字符串挂接升级为标准对象关系
