# Odoo 原生模块复用源码入口索引

适用范围：

- 当前物流项目在 Odoo 19 仓库中可直接复用的原生模块
- 用于给后续前端开发、模型扩展、视图扩展、Smart Button 接入提供源码入口索引

优先基准：

- `ai-code/docs/context/Odoo19物流留痕系统运单主对象与留痕主流程设计.md`
- `ai-code/docs/dev/project_coordination/Odoo19物流留痕系统五人分工与前端改造安排.md`
- `ai-code/docs/context/odoo_logistics_feasibility.md`
- `ai-code/docs/architecture/logistics_dispatch_addon_design.md`

检查日期：

- 2026-04-13

---

## 1. 文档定位

这份文档不负责重新定义业务方案，它只回答 3 个务实问题：

1. 当前项目哪些地方适合直接复用 Odoo 原生模块
2. 这些原生模块在当前仓库里应该去哪个目录、哪个文件看
3. 现有设计文档里关于“复用原生模块”的说法，哪些是正确的，哪些需要特别留意

---

## 2. 现有相关文档检查结论

当前 `ai-code` 里已经有几份文档提到了“复用 Odoo 原生模块”，其中最有价值的有：

- `docs/context/odoo_logistics_feasibility.md`
- `docs/architecture/logistics_dispatch_addon_design.md`
- `专题设计/前端设计/一期前端相关设计/01_模块设计/06_业务单据/业务单据前端接入设计草案.md`
- `专题设计/前端设计/一期前端相关设计/01_模块设计/07_商品与基础资料/商品与基础资料模块前端设计草案.md`
- `专题设计/前端设计/一期前端相关设计/01_模块设计/04_运输与调度/运输与调度模块前端设计草案.md`

总体判断：

- 模块级判断大体正确
- 大部分模块名、模型名和目录方向是对的
- 但现有文档更多停留在“该复用哪个模块”，还没有统一收口到“具体去哪个源码文件看”

---

## 3. 这次实查发现的关键差异点

### 3.1 正确的部分

当前仓库里，下面这些原生模块和关键模型都可以直接找到：

- `contacts`
- `hr`
- `stock`
- `sale`
- `purchase`
- `mail`
- `fleet`
- `stock_picking_batch`
- `stock_fleet`
- `base` 底层模型目录

### 3.2 需要特别注意的差异

当前仓库里：

- `stock_picking_batch` 存在
- `stock_fleet` 存在
- **`stock_delivery_trip` 不存在**

所以如果后续看到文档里把 `stock_delivery_trip` 写成“当前可直接复用模块”，应理解为：

- 历史设想
- 或未来扩展方向

而不是当前仓库中的现成模块。

### 3.3 一个常见误区

如果只是看“客户 / 门店能力”，写 `contacts` 没问题。  
但如果你要找 **Python 主模型定义**，`res.partner` 的核心并不在 `addons/contacts`，而在：

- `odoo/addons/base/models/res_partner.py`

同理：

- `contacts` 更偏入口、菜单、视图
- `base/models` 才是底层对象定义入口

---

## 4. 推荐优先阅读的原生模块索引

## 4.1 客户 / 门店 / 联系人

### 适合复用的原因

- 客户、门店、联系人层级关系
- 地址与联系人信息
- 后台联系人页基础入口

### 推荐先看目录

- `addons/contacts`
- `odoo/addons/base/models`

### 关键模型文件

- `odoo/addons/base/models/res_partner.py`

### 关键视图文件

- `addons/contacts/views/contact_views.xml`

### 项目中的推荐用途

- 客户主档底座
- 门店主档底座
- 客户 / 门店 / 联系人层级关系

### 不建议硬套的地方

- 不要把 `res.partner` 直接等同于“物流执行对象”
- 不要把联系人页直接当成追溯页

---

## 4.2 工作人员 / 责任人

### 适合复用的原因

- 员工对象
- 岗位、部门、人员信息
- 可作为司机、责任人、处理人等基础关联对象

### 推荐先看目录

- `addons/hr`

### 关键模型文件

- `addons/hr/models/hr_employee.py`

### 关键视图文件

- `addons/hr/views/hr_employee_views.xml`
- `addons/hr/views/hr_job_views.xml`
- `addons/hr/views/hr_department_views.xml`

### 项目中的推荐用途

- 司机 / 执行人员基础对象
- 异常责任人、处理人关联
- 人员维度统计或筛选

### 不建议硬套的地方

- 不要让 `hr.employee` 直接承担运单或留痕事实对象职责

---

## 4.3 仓库 / 库位 / 出入库事实

### 适合复用的原因

- 仓库、库位、出入库单据
- 调拨、出库、入库、库存结果
- 一期里很多“仓储接入”都适合直接复用

### 推荐先看目录

- `addons/stock`

### 关键模型文件

- `addons/stock/models/stock_warehouse.py`
- `addons/stock/models/stock_location.py`
- `addons/stock/models/stock_picking.py`

### 关键视图文件

- `addons/stock/views/stock_warehouse_views.xml`
- `addons/stock/views/stock_location_views.xml`
- `addons/stock/views/stock_picking_views.xml`
- `addons/stock/views/stock_quant_views.xml`

### 项目中的推荐用途

- 仓库与货位底座
- 出入库单据反查入口
- 仓储侧 Smart Button 接入

### 不建议硬套的地方

- 不要把 `stock.picking` 直接当成运单主对象
- 不要把仓储单据直接当成留痕主对象

---

## 4.4 批量作业 / Wave 能力参考

### 适合复用的原因

- 当前仓库确实存在 `stock_picking_batch`
- 它能提供批量作业、波次式组织、与 picking 的挂接参考

### 推荐先看目录

- `addons/stock_picking_batch`

### 关键模型文件

- `addons/stock_picking_batch/models/stock_picking_batch.py`
- `addons/stock_picking_batch/models/stock_picking.py`

### 关键视图文件

- `addons/stock_picking_batch/views/stock_picking_batch_views.xml`
- `addons/stock_picking_batch/views/stock_picking_wave_views.xml`
- `addons/stock_picking_batch/views/stock_picking_views.xml`

### 项目中的推荐用途

- 理解批量作业对象
- 理解 wave / batch 类组织方式
- 给自定义 `wave / batch` 设计提供结构参考

### 不建议硬套的地方

- 不要直接把 `stock.picking.batch` 当成项目里的最终“物流批次”对象
- 它更适合作为参考底座和关联对象

---

## 4.5 车辆与运输对象

### 适合复用的原因

- 车辆主档
- 车型、品牌、状态、里程等基础对象

### 推荐先看目录

- `addons/fleet`

### 关键模型文件

- `addons/fleet/models/fleet_vehicle.py`
- `addons/fleet/models/fleet_vehicle_model.py`
- `addons/fleet/models/fleet_vehicle_state.py`

### 关键视图文件

- `addons/fleet/views/fleet_vehicle_views.xml`
- `addons/fleet/views/fleet_vehicle_model_views.xml`

### 项目中的推荐用途

- 车辆基础对象
- 运单 / 批次上的车辆关联
- 二期车辆统计与筛选

### 不建议硬套的地方

- 不要把 `fleet` 直接理解为完整运输调度模块
- 当前调度主线仍应由自定义 `logistics_dispatch` 承接

---

## 4.6 业务来源单据

### 适合复用的原因

- 销售、采购、财务单据页本身已成熟
- 你们项目更需要的是“反查入口”，不是重做整页

### 推荐先看目录

- `addons/sale`
- `addons/purchase`
- `addons/account`

### 关键模型文件

- `addons/sale/models/sale_order.py`
- `addons/purchase/models/purchase_order.py`
- `addons/account/models/account_move.py`

### 关键视图文件

- `addons/sale/views/sale_order_views.xml`
- `addons/purchase/views/purchase_views.xml`
- `addons/account/views/account_views.xml`

### 项目中的推荐用途

- 业务来源单据反查
- Smart Button 入口
- 从单据进入运单 / 批次 / 异常 / 仓储对象

### 不建议硬套的地方

- `sale.order` 不是运单
- `purchase.order` 不是批次
- `account.move` 不是物流事实对象

---

## 4.7 消息 / 活动 / 附件 / 协同

### 适合复用的原因

- 留痕、异常、处理记录、附件、活动都能借力 Odoo 协同底座

### 推荐先看目录

- `addons/mail`
- `odoo/addons/base/models`

### 关键模型文件

- `addons/mail/models/mail_thread.py`
- `odoo/addons/base/models/ir_attachment.py`

### 关键视图文件

- `addons/mail/views/mail_activity_views.xml`
- `addons/mail/views/mail_message_views.xml`
- `addons/mail/views/mail_template_views.xml`

### 项目中的推荐用途

- chatter / activity 能力
- 异常处理协同
- 轻量附件能力

### 不建议硬套的地方

- 不要把 `mail.message` 当成留痕事实主模型
- 留痕事实层仍应由 `logistics_trace_core` 自定义承接

---

## 4.8 商品与产品

### 适合复用的原因

- 商品主档、分类、规格、条码等基础能力已经成熟

### 推荐先看目录

- `addons/product`

### 关键模型文件

- `addons/product/models/product_template.py`

### 关键视图文件

- `addons/sale/views/product_template_views.xml`
- `addons/purchase/views/product_views.xml`
- `addons/stock/views/product_views.xml`

### 项目中的推荐用途

- 商品主档底座
- 商品维度字段展示
- 订单明细中的产品反查

### 不建议硬套的地方

- 不要把商品页演变成物流执行页

---

## 4.9 stock_fleet：存在但当前优先级较低

### 当前状态

当前仓库中存在：

- `addons/stock_fleet`

### 关键文件

- `addons/stock_fleet/__manifest__.py`
- `addons/stock_fleet/models/stock_picking_batch.py`
- `addons/stock_fleet/models/stock_picking.py`
- `addons/stock_fleet/models/stock_warehouse.py`
- `addons/stock_fleet/views/stock_picking_batch.xml`
- `addons/stock_fleet/views/stock_picking_view.xml`

### 当前建议

- 可以作为“仓储 + 车辆”结合方式的参考
- 但不建议在一期里把它当成主设计入口
- 当前更稳的主线仍然是：自定义 `logistics_dispatch` + 参考 `stock_picking_batch` / `fleet`

---

## 5. 当前仓库里不存在、不能当现成入口的项

以下项在当前仓库中**没有找到**：

- `addons/stock_delivery_trip`

所以如果在旧文档中看到：

- `stock_delivery_trip`
- `stock.delivery.trip`

应理解为：

- 历史设想
- 或未来扩展候选

而不是当前仓库里现成可复用的模块。

---

## 6. 当前最推荐的阅读顺序

如果你后续是为了“边设计边写代码”去读 Odoo 原生源码，建议按这个顺序：

1. `odoo/addons/base/models/res_partner.py`
2. `addons/contacts/views/contact_views.xml`
3. `addons/hr/models/hr_employee.py`
4. `addons/stock/models/stock_picking.py`
5. `addons/stock/models/stock_warehouse.py`
6. `addons/stock_picking_batch/models/stock_picking_batch.py`
7. `addons/fleet/models/fleet_vehicle.py`
8. `addons/sale/models/sale_order.py`
9. `addons/purchase/models/purchase_order.py`
10. `addons/mail/models/mail_thread.py`
11. `odoo/addons/base/models/ir_attachment.py`

---

## 7. 当前结论

现在的 `ai-code` 文档里，已经有“复用 Odoo 原生模块”的方向性说明，而且整体方向是对的。

但如果你要真正进入代码实现，现阶段更需要的是：

**从“模块名级别的复用说明”，进入“源码文件级别的入口索引”。**

这份文档的作用，就是把这一层补出来，避免后面继续在：

- `contacts` 还是 `base/models`
- `stock` 还是 `stock_picking_batch`
- `fleet` 还是自定义 dispatch

这些地方反复绕圈。

