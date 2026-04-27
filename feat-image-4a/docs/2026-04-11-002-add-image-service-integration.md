# Change Notes

## 本轮目标
在 `feat-image-4a` 内把证据模块与独立 `image-manager-main` 服务接起来，形成“后台上传图片 -> 图片服务保存 -> Odoo 回填 `image_access_key`”的最小闭环。

## 修改文件
- `feat-image-4a/addons/logistics_trace_evidence/__init__.py`
- `feat-image-4a/addons/logistics_trace_evidence/__manifest__.py`
- `feat-image-4a/addons/logistics_trace_evidence/models/__init__.py`
- `feat-image-4a/addons/logistics_trace_evidence/models/logistics_trace_evidence.py`
- `feat-image-4a/addons/logistics_trace_evidence/models/res_config_settings.py`
- `feat-image-4a/addons/logistics_trace_evidence/services/__init__.py`
- `feat-image-4a/addons/logistics_trace_evidence/services/image_service_client.py`
- `feat-image-4a/addons/logistics_trace_evidence/views/logistics_trace_evidence_views.xml`
- `feat-image-4a/addons/logistics_trace_evidence/views/res_config_settings_views.xml`
- `feat-image-4a/addons/logistics_trace_evidence/wizards/__init__.py`
- `feat-image-4a/addons/logistics_trace_evidence/wizards/logistics_trace_evidence_upload_wizard.py`
- `feat-image-4a/addons/logistics_trace_evidence/wizards/logistics_trace_evidence_upload_wizard_views.xml`
- `feat-image-4a/addons/logistics_trace_evidence/security/ir.model.access.csv`
- `feat-image-4a/docs/README.md`
- `feat-image-4a/docs/协作边界说明.md`

## 修改原因
- 项目规范已经明确：图片能力继续走独立 `image-manager-main`，Odoo 不变成图片服务本身。
- 4.3 需要尽快交付一个可合并的图片挂接模块包，方便后续与调度、司机端、后台追溯等 `feat` 目录拼装。
- 在多人协作模式下，必须明确当前功能线的边界、依赖和集成方式。

## 改动摘要
- 新增图片服务配置项：
  - `Image Service Base URL`
  - `Image Service Timeout`
- 新增 `LogisticsImageServiceClient`
  - 支持调用 `POST /api/images/upload`
  - 支持调用 `GET /api/images/{image_access_key}?meta=true`
  - 支持生成预览和下载地址
- 新增后台上传向导：
  - 在证据对象上发起上传
  - 由 Odoo 调图片服务上传图片
  - 回填 `image_access_key` 与基础元数据
- 新增图片元数据同步方法：
  - 可按 `image_access_key` 回拉远端元数据
- 补充 `feat-image-4a` 目录下的协作边界说明和总装提示

## 调用链变化
改动前：
- Odoo 证据对象只能手工维护图片引用字段

改动后：
- Odoo 证据对象 -> 上传向导 -> `image-manager-main`
- `image-manager-main` 返回 `image_access_key` 与元数据
- Odoo 创建 `logistics.trace.evidence.image`

## 风险点
- 当前还没有在真实 Odoo 环境里安装验证这个向导与设置页。
- 运行时依赖 `requests` 和可访问的图片服务地址。
- 目前仍然是字符串级的批次号/运单号挂接，后续要和正式调度对象接起来。

## 验证方法
- 检查新增 Python 文件能通过基础语法解析。
- 检查模块 manifest 已包含设置页和上传向导视图。
- 后续在 Odoo 环境中安装模块后：
  - 在库存设置里配置图片服务地址
  - 打开证据对象
  - 通过上传向导上传图片
  - 确认图片引用记录成功创建

## 后续待办
- 增加图片服务失败时更细的错误提示和重试策略。
- 补充按钮让后台用户直接同步单张图片的远端元数据。
- 和调度/运单模块对齐正式外键关系。
