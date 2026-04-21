# 2026-04-16 导入中心前端闭环页落地

## 本次目标

把二期剩余的“导入中心前端闭环页”落地出来，不再让运单标准导入只停留在后端接口和原生 `tag=import` 入口，而是补齐一页可直接操作的前端导入中心。

## 本次变更

### 1. 新增导入中心前端动作

新增文件：

- `custom_addons/logistics_web/static/src/js/actions/import_center_action.js`
- `custom_addons/logistics_web/static/src/xml/import_center_templates.xml`

新增 client action：

- `logistics_web.import_center`

新增动作记录：

- `logistics_web.action_logistics_web_import_center`

### 2. 新导入中心页面当前能力

当前页面已支持：

- 显示当前入口来源
  - 运单导入
  - 客户明细导入
  - 货物明细导入
- 标准模板下载
  - 英文列头
  - 中文列头
- 选择 `.xlsx` 文件
- 调用 `precheck`
- 展示预校验统计
  - 导入批次号
  - 总行数
  - 失败行数
  - 是否可正式导入
- 展示前 20 条错误明细
- 下载错误报告
- 调用 `confirm`
- 展示导入结果
  - 状态
  - 新增运单数
  - 新增客户明细数
  - 新增货物明细数
- 从结果区跳转回运单列表

### 3. 入口切换

更新文件：

- `custom_addons/logistics_web/static/src/js/components/list_import_button.js`
- `custom_addons/logistics_web/static/src/js/actions/home_action.js`
- `custom_addons/logistics_dispatch/views/logistics_dispatch_waybill_views.xml`

当前入口切换结果：

- 首页快捷入口 `物流导入` 已切到新导入中心
- 运单列表页顶部 `导入` 按钮已切到新导入中心
- 菜单：
  - `导入中心`
  - `运单导入`
  - `客户明细导入`
  - `货物明细导入`
  均已改为打开新导入中心，只是携带不同的 `source_model` 参数

### 4. 范围控制

本轮只切运单主链路相关入口。

以下对象仍保持原生导入：

- 波次
- 批次
- 留痕
- 证据
- 异常

原因：

- 当前 V2 三 Sheet 标准导入只服务于 `waybill -> customer line -> goods line`
- 不适合把其他独立模型的导入入口误切到整单导入页

### 5. 页面样式补充

更新文件：

- `custom_addons/logistics_web/static/src/scss/logistics_web.scss`

新增了导入中心所需的：

- 模板下载卡片布局
- 上传区布局
- 操作按钮条
- 错误表格样式
- 小号批次号卡片样式

## 验证结果

### 1. 模块升级通过

已执行：

- `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_dev -u logistics_dispatch,logistics_web --stop-after-init`

### 2. JS 语法检查通过

已执行：

- `node --check custom_addons/logistics_web/static/src/js/actions/import_center_action.js`
- `node --check custom_addons/logistics_web/static/src/js/components/list_import_button.js`
- `node --check custom_addons/logistics_web/static/src/js/actions/home_action.js`

### 3. 动作与菜单记录检查通过

运行态已确认下面这些动作都指向：

- `tag = logistics_web.import_center`

已确认：

- `logistics_web.action_logistics_web_import_center`
- `logistics_dispatch.action_logistics_dispatch_waybill_import_center_direct`
- `logistics_dispatch.action_logistics_dispatch_waybill_customer_line_import_center_direct`
- `logistics_dispatch.action_logistics_dispatch_waybill_customer_goods_line_import_center_direct`

并且相关菜单仍正确挂接到这些动作。

## 当前边界

- 当前导入中心前端页已打通第一轮闭环，但还没有单独的独立结果详情页；结果展示仍在同一页完成
- 当前结果区只能跳回运单列表，还没有基于导入批次精确下钻到“本次导入的具体运单集合”
- 当前样例和验收文档里仍有一部分旧 `CSV` 口径，后续需要继续统一为 `V2 XLSX`

## 下一步建议

1. 继续同步 `03_模板与样例/` 下的旧 `CSV` 说明
2. 继续同步二期人工验收单到 `V2 XLSX + 导入中心前端页` 口径
3. 如需更强结果追溯，可在后续补“导入批次到运单记录”的反查关系
