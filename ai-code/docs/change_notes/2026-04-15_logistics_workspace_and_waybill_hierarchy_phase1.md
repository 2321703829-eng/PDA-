# 2026-04-15 物流工作区与运单客户/货物层次一期落地

## 本次处理

- 将 `物流` 模块内部导航从对象平铺改为更接近工作区结构：
  - 调度
  - 运单
  - 留痕
  - 证据
  - 异常
  - 导入中心
- 在 `运单` 工作区下新增：
  - 运单列表
  - 客户明细
  - 货物明细
- 为运单详情补充客户明细、货物明细的统计按钮与独立打开动作。
- 为 `logistics.dispatch.waybill.customer.line` 和 `logistics.dispatch.waybill.customer.goods.line` 新增列表、表单、搜索与动作定义。
- 在运单详情中增强客户/货物页签展示字段，使客户编号、门店编号、货物条数、数量、件数等结构更完整。
- 新增 `导入中心` 入口，先以运单列表为承接页，并通过帮助文案指向顶部导入按钮。

## 影响文件

- `custom_addons/logistics_dispatch/models/logistics_dispatch_waybill.py`
- `custom_addons/logistics_dispatch/views/logistics_dispatch_waybill_views.xml`
- `custom_addons/logistics_dispatch/views/logistics_dispatch_menus.xml`
- `custom_addons/logistics_web/models/ui_label_sync.py`

## 目的

- 让物流模块内部结构更接近“工作区”而不是“表名平铺”。
- 让运单详情中的客户/货物层次不仅能在单张运单中查看，也能通过物流模块内部独立列表进入。
- 为后续标准导入模板和三层导入写入逻辑提供稳定页面落点。
