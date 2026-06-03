# 2026-04-24 排线专用导入最小可用链路首轮实现

## 本次变更

- 新增排线导入对象类型 `route_planning`，复用现有 `logistics.import.task` 审计链。
- 在 `logistics_dispatch` 中新增轻量承接模型：
  - `logistics.route.planning.batch`
  - `logistics.route.planning.stop.line`
- 在 `logistics_web` 中新增独立服务 `RoutePlanningImportService`，实现：
  - 单表模板下载
  - 按表头识别的单表解析
  - 字段顺序无关解析
  - 允许额外工作表存在
  - 最小预校验
  - 非阻断式人工复查提醒
  - 正式写入排线草稿
- 在导入中心新增“排线用数据导入”入口，支持：
  - 模板下载
  - 文件上传
  - 预校验
  - 人工复查提醒展示
  - 正式写入结果展示

## 本轮边界

- 不修改正式四 Sheet 主链导入的对象边界。
- 排线导入首轮只落排线草稿，不直接强绑 `waybill -> customer_line -> order_line -> goods_line` 正式建档。
- 排线导入结果首轮主要在导入中心页内回显，不额外扩展独立结果页能力。

## 影响文件

- `custom_addons/logistics_dispatch/models/selection_options.py`
- `custom_addons/logistics_dispatch/models/logistics_route_planning_draft.py`
- `custom_addons/logistics_dispatch/models/__init__.py`
- `custom_addons/logistics_dispatch/security/ir.model.access.csv`
- `custom_addons/logistics_web/services/route_planning_import_service.py`
- `custom_addons/logistics_web/services/__init__.py`
- `custom_addons/logistics_web/controllers/logistics_web_import_v3.py`
- `custom_addons/logistics_web/static/src/js/actions/import_center_action.js`
- `custom_addons/logistics_web/static/src/xml/import_center_templates.xml`
