# 2026-04-14 Logistics Web UI Localization Phase 2

## 本轮目标

- 在不修改 `ai-code/前端相关设计/` 既有文件的前提下，补一份二期前端优化设计文档，并把当前 Odoo 物流后台的核心可见界面收口为更适合中国用户的简约运营风格。

## 修改文件

- [2026-04-14_Odoo物流后台UI本土化与中文体验优化方案.md](d:/Desktop/Odoo/ai-code/二期前端优化设计/2026-04-14_Odoo物流后台UI本土化与中文体验优化方案.md)
- [logistics_web_menus.xml](d:/Desktop/Odoo/custom_addons/logistics_web/views/logistics_web_menus.xml)
- [logistics_web_actions.xml](d:/Desktop/Odoo/custom_addons/logistics_web/views/logistics_web_actions.xml)
- [logistics_web_waybill_views.xml](d:/Desktop/Odoo/custom_addons/logistics_web/views/logistics_web_waybill_views.xml)
- [logistics_dispatch_waybill_views.xml](d:/Desktop/Odoo/custom_addons/logistics_dispatch/views/logistics_dispatch_waybill_views.xml)
- [logistics_dispatch_waybill.py](d:/Desktop/Odoo/custom_addons/logistics_dispatch/models/logistics_dispatch_waybill.py)
- [logistics_dispatch_waybill_order_line.py](d:/Desktop/Odoo/custom_addons/logistics_dispatch/models/logistics_dispatch_waybill_order_line.py)
- [__manifest__.py](d:/Desktop/Odoo/custom_addons/logistics_web/__manifest__.py)
- [dashboard_action_v2.js](d:/Desktop/Odoo/custom_addons/logistics_web/static/src/js/actions/dashboard_action_v2.js)
- [boss_trace_action_v2.js](d:/Desktop/Odoo/custom_addons/logistics_web/static/src/js/actions/boss_trace_action_v2.js)
- [logistics_waybill_form_view.js](d:/Desktop/Odoo/custom_addons/logistics_web/static/src/js/views/logistics_waybill_form_view.js)
- [trace_timeline_widget.js](d:/Desktop/Odoo/custom_addons/logistics_web/static/src/js/widgets/trace_timeline_widget.js)
- [evidence_viewer_widget.js](d:/Desktop/Odoo/custom_addons/logistics_web/static/src/js/widgets/evidence_viewer_widget.js)
- [trace_evidence_field_widgets.js](d:/Desktop/Odoo/custom_addons/logistics_web/static/src/js/widgets/trace_evidence_field_widgets.js)
- [widget_templates.xml](d:/Desktop/Odoo/custom_addons/logistics_web/static/src/xml/widget_templates.xml)
- [logistics_web.scss](d:/Desktop/Odoo/custom_addons/logistics_web/static/src/scss/logistics_web.scss)
- [logistics_dispatch_waybill.py](d:/Desktop/Odoo/custom_addons/logistics_web/models/logistics_dispatch_waybill.py)

## 修改原因

- 现有后台界面仍过于接近 Odoo 默认后台，和中国物流团队常见的运营后台阅读习惯不完全匹配。
- 部分可见文案虽然已中文化，但表达偏直译，仍有中英混排、技术术语过重和动作导向不足的问题。
- 用户明确要求不要改动 `前端相关设计` 文件夹中的已有文件，因此需要把设计说明落到新的 `二期前端优化设计` 目录。
- 原有 `logistics_web` action JS 存在历史编码异常，直接继续在旧文件上补丁风险较高，因此改为新增 `*_v2.js` 并在资产清单中显式加载。

## 改动摘要

- 新增二期设计文档，明确 UI 本土化方向、中文文案规则、视觉规则和本轮收口范围。
- 将菜单与 client action 名称收口为更业务化的中文命名，如 `运营工作台`、`管理层总览`、`留痕与证据`。
- 将运单详情页、留痕时间线、证据查看区和订单明细列头中的显性英文统一替换为更自然的中文表达。
- 将工作台和管理层总览的卡片、按钮和说明文案改成“先看什么、再做什么”的业务动作语气。
- 为 `logistics_web.scss` 增加一套更贴近国内物流后台的轻量视觉变量与层级规则，弱化 Odoo 默认感，保留简约风格。
- 收口旧 field widget 路径中残留的英文 `displayName`、空态提示和动作文案，避免 Step 1 只在主渲染路径完成、旧路径仍保留英文。

## 影响范围

- `logistics_web` 的菜单、client action、增强表单渲染、widget 模板与样式。
- `logistics_dispatch` 运单详情页中的页签、标题和订单明细字段显示文案。
- 仅影响用户可见命名、提示语与视觉层级，不改变业务主链和模型关系。

## 是否影响模型 / 视图 / 权限 / 数据兼容性

- 模型：否，仅调整字段 `string` 和选择项显示标签。
- 视图：是，更新了运单页签、按钮、标题与增强区文案。
- 权限：否。
- 数据兼容性：否，不涉及表结构、数据迁移和接口协议变更。

## 验证方法

- 搜索确认显性英文是否已从目标界面移除，例如：
  - `Trace & Evidence`
  - `External Order No`
  - `Sale Order`
  - `Stock Picking`
  - `Goods Summary`
  - `Line Status`
- 检查 `custom_addons/logistics_web/static/src/js/views/logistics_waybill_form_view.js` 的结构，确认文案调整后没有残留引号或模板字符串错误。
- 升级 `logistics_dispatch` 与 `logistics_web` 后，人工确认：
  - 运单详情页页签改为 `订单明细 / 备注 / 留痕与证据`
  - 留痕时间线与证据查看区使用中文标题和中文空态
  - 工作台与管理层总览更像运营入口页而非默认技术页

## 风险点

- 视觉层级调整依赖前端资产重新编译/刷新，未升级模块或未清缓存时可能仍看到旧样式。
- `*_v2.js` 是对历史异常文件的绕行方案，后续如需彻底清理遗留文件，建议单独安排一次编码与资产整治。
- 某些状态值仍以英文技术值存储，当前只是在用户可见层做中文化；后续如继续扩展，需要保持“存储值”和“显示值”分层。

## 回滚建议

- 如需快速回退，可优先回退 `logistics_web` 资产清单和新增的 `*_v2.js`，恢复旧 action 注册方式。
- 如果只需回退视觉层，不必回退设计文档，可仅回退 [logistics_web.scss](d:/Desktop/Odoo/custom_addons/logistics_web/static/src/scss/logistics_web.scss)。

## 后续待办

- 补一份工作台与管理层总览的二期视觉稿说明，进一步细化卡片优先级、风险色使用和信息布局规则。
- 若后续继续推进整体本土化，可整理一份“物流后台中文文案词表”，统一异常、留痕、证据、签收等核心词汇。
