# Change Notes

## 本轮目标
在 `odoo` 仓库内按 4.3 分工正式落下留痕中心与证据中心的第一版模块骨架，并把建模口径从“订单中心”纠正为“批次/运单中心”。

## 修改文件
- `addons/logistics_trace_core/__init__.py`
- `addons/logistics_trace_core/__manifest__.py`
- `addons/logistics_trace_core/models/__init__.py`
- `addons/logistics_trace_core/models/logistics_trace_event.py`
- `addons/logistics_trace_core/security/ir.model.access.csv`
- `addons/logistics_trace_core/views/logistics_trace_event_views.xml`
- `addons/logistics_trace_core/views/logistics_trace_menu.xml`
- `addons/logistics_trace_evidence/__init__.py`
- `addons/logistics_trace_evidence/__manifest__.py`
- `addons/logistics_trace_evidence/models/__init__.py`
- `addons/logistics_trace_evidence/models/logistics_trace_event.py`
- `addons/logistics_trace_evidence/models/logistics_trace_evidence.py`
- `addons/logistics_trace_evidence/security/ir.model.access.csv`
- `addons/logistics_trace_evidence/views/logistics_trace_evidence_views.xml`

## 修改原因
- 仓库规范已经明确一期只聚焦留痕、证据、司机端上传、后台追溯和异常查看，不引入聊天、日历、联系人中心等通用协同能力。
- 《Odoo19物流留痕系统运单主对象与留痕主流程设计》已经明确：留痕主对象不是订单，而是运单号；同时还需要支持批次级留痕。
- 因此 4.3 的第一步必须先把“批次/运单双主体留痕 + 证据图片关系”作为正式业务对象落到 Odoo 模块里。

## 改动摘要
- 新增 `logistics_trace_core` 模块，提供 `logistics.trace.event` 留痕事件对象。
- `logistics.trace.event` 支持两类主体：`batch` 和 `waybill`。
- 事件类型先覆盖装车前、装车完成、到店、交付完成、签收、异常上报等核心节点。
- 新增 `logistics_trace_evidence` 模块，提供 `logistics.trace.evidence` 与 `logistics.trace.evidence.image`。
- 图片对象目前只保存 `image_access_key`、文件名、类型、大小、时间和预览/下载地址，不直接存图片二进制。
- 为避免模块循环依赖，证据关系由 `logistics_trace_evidence` 通过继承方式挂回 `logistics.trace.event`，不是让 `core` 直接依赖 `evidence`。

## 建模口径变化
改动前：
- 仓库里还没有 4.3 的正式 Odoo 模块实现。
- 留痕与证据层没有明确的 Odoo 业务对象承载。

改动后：
- `batch/waybill -> logistics.trace.event -> logistics.trace.evidence -> logistics.trace.evidence.image`
- 订单不再作为证据直接挂载点。

## 风险点
- 当前只完成了模块骨架、模型、基础权限和基础视图，还没有接入真实的图片服务上传调用。
- 当前 `batch_no`、`waybill_no` 先使用业务编号字段承载，后续需要和调度模块里的正式批次对象、运单对象接起来。
- 目前还没有做安装验证和数据库迁移验证，后续需要在 Odoo 环境里实际安装模块确认视图与访问权限。

## 验证方法
- 检查新增模块目录结构是否完整。
- 检查三个 Python 模型文件是否能通过基础语法解析。
- 后续在 Odoo 环境中执行模块安装，验证菜单、列表、表单和模型加载是否正常。

## 后续待办
- 接上调度侧的批次对象和运单对象，替换纯编号挂载。
- 为 `logistics_trace_evidence` 接入 `image-manager-main` 的图片服务适配层。
- 增加司机端/后台追溯会用到的查询接口和动作方法。
- 评估如何以可逆方式收起当前阶段明确不需要的 Odoo 原生功能入口。
