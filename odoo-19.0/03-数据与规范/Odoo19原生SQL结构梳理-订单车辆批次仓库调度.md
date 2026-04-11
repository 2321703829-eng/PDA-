# Odoo19原生SQL结构梳理：订单、车辆、批次、仓库、调度

本文档用于从“数据库 / SQL 结构视角”梳理 Odoo 19 里和你当前项目最相关的几类对象：

- 订单
- 出库单
- 批次
- 车辆
- 车次 / 调度
- 仓库
- 仓库位置 / 装车位

这份文档的目标不是把 Odoo 全部表结构列完，而是回答下面几个更实际的问题：

1. Odoo 原生到底有哪些表可以直接复用
2. 哪些表是社区模块扩展出来的
3. 订单、出库、批次、车辆、仓库之间是怎么连起来的
4. 哪些结构适合作为你后续自定义模块的依附点

---

## 1. 先给结论

如果只看你现在的业务，Odoo 里最值得重点关注的原生 / 现成模型是这几张：

```text
sale.order
stock.picking
stock.picking.batch
stock.warehouse
stock.location
fleet.vehicle
stock.delivery.trip
stock.delivery.proof
```

把它们换成 SQL 视角的表名，通常就是：

```text
sale_order
stock_picking
stock_picking_batch
stock_warehouse
stock_location
fleet_vehicle
stock_delivery_trip
stock_delivery_proof
```

最关键的主线是：

```text
sale_order
  -> stock_picking
    -> stock_picking_batch
      -> fleet_vehicle
      -> stock_warehouse / stock_location

stock_delivery_trip
  -> stock_picking
  -> stock_delivery_proof
```

但要特别注意：

- Odoo 原生有订单、出库、批次、仓库、车辆
- Odoo 也有一定程度的车次 / proof 扩展
- 但 Odoo 原生并没有你要的“运单号主对象”
- 你后续真正要补的是“运单号 + 留痕事件 + 证据对象”这一层

---

## 2. Odoo 里表名和模型名的关系

Odoo 默认是 ORM 模型驱动，不是先写 SQL 表。

通常情况下：

- 模型名 `sale.order` 对应表 `sale_order`
- 模型名 `stock.picking` 对应表 `stock_picking`
- 模型名 `fleet.vehicle` 对应表 `fleet_vehicle`

规则可以简单理解为：

```text
模型名里的点号 .
-> 替换成下划线 _
-> 得到默认表名
```

所以你后面看 Python 模型文件时，基本可以直接推断数据库表名。

---

## 3. 订单相关：`sale_order`

## 3.1 业务定位

Odoo 里的销售订单主对象是：

- 模型：`sale.order`
- 表：`sale_order`

它主要承接：

- 客户
- 下单时间
- 收货地址
- 订单状态
- 销售行明细
- 发货仓库

相关源码：

- `d:\tianshu\odoo-19.0\odoo-19.0\addons\sale\models\sale_order.py`
- `d:\tianshu\odoo-19.0\odoo-19.0\addons\sale_stock\models\sale_order.py`

## 3.2 典型字段

按 SQL 视角看，可以先把它理解成：

```sql
sale_order (
    id bigint primary key,
    name varchar,
    company_id bigint,
    partner_id bigint,
    partner_invoice_id bigint,
    partner_shipping_id bigint,
    warehouse_id bigint,
    state varchar,
    date_order timestamp,
    commitment_date timestamp,
    origin varchar,
    user_id bigint,
    team_id bigint,
    amount_total numeric,
    create_date timestamp,
    write_date timestamp
)
```

其中最值得你关注的是：

- `name`：订单编号
- `partner_id`：客户
- `partner_shipping_id`：收货地址
- `warehouse_id`：仓库
- `state`：订单状态
- `origin`：来源单据

## 3.3 和仓库 / 出库的关系

`sale_stock` 模块会给 `sale.order` 扩展两个很关键的字段：

- `warehouse_id`
- `picking_ids`

也就是说，销售订单和库存出库单之间并不是完全分离的。

从结构上可以理解为：

```text
sale_order.id
  -> stock_picking.sale_id
```

---

## 4. 出库单 / 履约单：`stock_picking`

## 4.1 业务定位

Odoo 库存执行里的核心单据是：

- 模型：`stock.picking`
- 表：`stock_picking`

它本质上是“仓库作业单 / 调拨单 / 出库单”。

在你的业务里，它最接近：

- 订单出库执行对象
- 仓库发货执行对象
- 后续被批次和车次承接的对象

## 4.2 典型字段

可以先把它理解成：

```sql
stock_picking (
    id bigint primary key,
    name varchar,
    origin varchar,
    partner_id bigint,
    company_id bigint,
    picking_type_id bigint,
    state varchar,
    move_type varchar,
    scheduled_date timestamp,
    date_deadline timestamp,
    date_done timestamp,
    location_id bigint,
    location_dest_id bigint,
    user_id bigint,
    batch_id bigint,
    sale_id bigint,
    create_date timestamp,
    write_date timestamp
)
```

其中最重要的是：

- `name`：出库 / 调拨编号
- `picking_type_id`：操作类型
- `state`：执行状态
- `location_id`：源位置
- `location_dest_id`：目标位置
- `partner_id`：联系方
- `batch_id`：所属批次
- `sale_id`：所属销售订单

## 4.3 状态字段

原生 `stock_picking.state` 主要有：

- `draft`
- `waiting`
- `confirmed`
- `assigned`
- `done`
- `cancel`

这套状态更偏库存执行，不是你后面业务 UI 想直接给用户看的最终状态。

## 4.4 和订单的关系

`stock_picking` 的 `sale_id` 不是 stock 原生字段，而是 `sale_stock` 扩展进去的。

这点很重要，因为它说明：

- 订单和出库单的直接关联来自 `sale_stock`
- 如果你以后不用销售流程，也不一定非要强依赖 `sale_order`

---

## 5. 批次：`stock_picking_batch`

## 5.1 业务定位

Odoo 里和“批次 / 波次”最接近的对象是：

- 模型：`stock.picking.batch`
- 表：`stock_picking_batch`

它主要用于：

- 一组出库单统一处理
- 波次 / 批次拣货
- 批量分配和处理出库单

## 5.2 典型字段

可以先把它理解成：

```sql
stock_picking_batch (
    id bigint primary key,
    name varchar,
    description varchar,
    user_id bigint,
    company_id bigint,
    picking_type_id bigint,
    warehouse_id bigint,
    state varchar,
    scheduled_date timestamp,
    is_wave boolean,
    estimated_shipping_weight numeric,
    estimated_shipping_volume numeric,
    vehicle_id bigint,
    driver_id bigint,
    dock_id bigint,
    vehicle_category_id bigint,
    end_date timestamp,
    create_date timestamp,
    write_date timestamp
)
```

这里要注意：

- 前半部分来自 `stock_picking_batch`
- 后半部分 `vehicle_id`、`driver_id`、`dock_id` 这些来自 `stock_fleet` 扩展

## 5.3 和出库单的关系

批次和出库单的关系是：

```text
stock_picking_batch.id
  -> stock_picking.batch_id
```

也就是说：

- 一批次可以有多张出库单
- 一张出库单只能挂一个批次

## 5.4 原生批次状态

`stock_picking_batch.state` 主要有：

- `draft`
- `in_progress`
- `done`
- `cancel`

对你来说，这张表很适合承接：

- 车辆装车任务
- 多门店配送前的一组发货单组织
- 批量分拣和仓内组织

---

## 6. 车辆信息：`fleet_vehicle`

## 6.1 业务定位

Odoo 社区的车辆对象是：

- 模型：`fleet.vehicle`
- 表：`fleet_vehicle`

它是车队管理对象，不是物流调度对象。

也就是说它更偏：

- 车牌
- 司机
- 车型
- 车队维护

而不是：

- 路线任务
- 运单执行

## 6.2 典型字段

可以先理解成：

```sql
fleet_vehicle (
    id bigint primary key,
    name varchar,
    active boolean,
    company_id bigint,
    manager_id bigint,
    license_plate varchar,
    vin_sn varchar,
    driver_id bigint,
    future_driver_id bigint,
    model_id bigint,
    brand_id bigint,
    category_id bigint,
    state_id bigint,
    location varchar,
    odometer numeric,
    odometer_unit varchar,
    fuel_type varchar,
    transmission varchar,
    vehicle_type varchar,
    acquisition_date date,
    write_off_date date,
    create_date timestamp,
    write_date timestamp
)
```

## 6.3 司机关系

`fleet_vehicle.driver_id` 直接关联：

- `res_partner`

这意味着 Odoo 默认把司机当作“联系人 / 合作伙伴”对象来管理，不是单独一张司机表。

对你来说，这个点既有好处，也有限制：

- 好处是现成能复用
- 限制是司机字段会比较泛，不是纯物流司机模型

---

## 7. 仓库：`stock_warehouse`

## 7.1 业务定位

Odoo 里的仓库主对象是：

- 模型：`stock.warehouse`
- 表：`stock_warehouse`

这张表本身不是“货位表”，而是“仓库主数据表”。

它定义的是：

- 仓库名称
- 仓库短编码
- 仓库地址
- 仓库的主库存位置
- 收货 / 发货流程配置

## 7.2 典型字段

可以先理解成：

```sql
stock_warehouse (
    id bigint primary key,
    name varchar,
    active boolean,
    company_id bigint,
    partner_id bigint,
    code varchar,
    view_location_id bigint,
    lot_stock_id bigint,
    wh_input_stock_loc_id bigint,
    wh_qc_stock_loc_id bigint,
    wh_output_stock_loc_id bigint,
    wh_pack_stock_loc_id bigint,
    pick_type_id bigint,
    pack_type_id bigint,
    out_type_id bigint,
    in_type_id bigint,
    int_type_id bigint,
    delivery_steps varchar,
    reception_steps varchar,
    sequence integer,
    create_date timestamp,
    write_date timestamp
)
```

## 7.3 你说的“仓库号”最接近哪个字段

如果你说的是“仓库编号 / 仓库代号”，Odoo 里最接近的是：

- `stock_warehouse.code`

它是仓库短编码，长度很短，通常用于标识仓库。

如果你说的是“仓库里的具体地库 / 装车位 / 库位号”，那就不是 `stock_warehouse` 了，而是：

- `stock.location`

也就是说：

- 仓库主编号看 `stock_warehouse.code`
- 仓内具体位置看 `stock_location`

---

## 8. 仓库位置 / 地库 / 装车位：`stock_location`

Odoo 里更细的仓内位置都落在：

- 模型：`stock.location`
- 表：`stock_location`

虽然你这次没单独问它，但你业务里“指定地库位置装车”其实强依赖这张表。

对你来说，最关键的是：

- `stock_warehouse.view_location_id`：仓库视图根位置
- `stock_warehouse.lot_stock_id`：主库存位置
- `stock_fleet` 里新增的 `dock_id`：实际装车位 / dock，指向 `stock_location`

所以如果你后面想落“地库号 / 装车位号”，最适合的承载对象其实是：

- `stock_location`

而不是再自己发明一张新的“仓位表”。

## 8.1 对你当前业务最重要的建议

结合你现在的真实调度和装车场景：

- 一波货对应一个批次
- 一辆车到仓后需要快速知道往哪个地库 / 装车位走
- 仓管需要先把这波货集中到指定位置，再组织装车

那么最合适的设计是：

- 批次直接关联一个地库位置
- 地库位置使用 `stock_location` 承载
- 司机、仓管、后台都围绕 `batch.dock_id` 来看装车位置

也就是说，在你的系统里更适合把这条链固定下来：

```text
stock_picking_batch
  -> dock_id
    -> stock_location
```

这样有几个现实好处：

- 调度完成后，可以直接给每个批次指定装车地库
- 司机到仓后不用再靠人工口头确认位置
- 仓管可以按批次把货提前归集到指定地库
- 后台可以按“批次 -> 地库 -> 车辆”统一查看当前装车组织情况

如果后面要继续扩展，你完全可以在自定义模块里继续给批次补：

- `dock_code`
- `dock_name`
- `dock_map_hint`
- `dock_arrive_note`

但底层主关联仍然建议挂在 `stock_location` 上，而不是另起一张平行表。

---

## 9. 调度 / 配送车次：`stock_delivery_trip`

## 9.1 业务定位

你当前源码里已经有一个和配送车次很接近的对象：

- 模型：`stock.delivery.trip`
- 表：`stock_delivery_trip`

它不是 Odoo 最核心的原生库存对象，但在你这套代码基线上已经是现成可用的配送车次模型。

## 9.2 典型字段

可以理解成：

```sql
stock_delivery_trip (
    id bigint primary key,
    name varchar,
    company_id bigint,
    vehicle_id bigint,
    driver_name varchar,
    state varchar,
    departure_time timestamp,
    delivered_time timestamp,
    note text,
    create_date timestamp,
    write_date timestamp
)
```

## 9.3 它和出库单的关系

`stock.delivery.trip` 和 `stock.picking` 的关系不是一对多字段，而是多对多关系：

```text
stock_delivery_trip
  <-> stock_delivery_trip_picking_rel
  <-> stock_picking
```

关系中间表是：

- `stock_delivery_trip_picking_rel`

字段大致是：

```sql
stock_delivery_trip_picking_rel (
    trip_id bigint,
    picking_id bigint
)
```

这说明它更像“车次承接一组配送出库单”。

---

## 10. 交付证明：`stock_delivery_proof`

## 10.1 业务定位

当前源码里还有一张 proof 表：

- 模型：`stock.delivery.proof`
- 表：`stock_delivery_proof`

它表达的是：

- 某次车次下的证明图片
- 可以是车次级，也可以是订单级

## 10.2 典型字段

可以理解成：

```sql
stock_delivery_proof (
    id bigint primary key,
    trip_id bigint,
    company_id bigint,
    scope varchar,
    picking_id bigint,
    image bytea_or_attachment_ref,
    note varchar,
    taken_at timestamp,
    create_date timestamp,
    write_date timestamp
)
```

这里最关键的是：

- `trip_id`：属于哪个车次
- `scope`：是车次级 proof 还是订单级 proof
- `picking_id`：指向哪张出库单

但对你的新系统来说，这张表并不够用。

因为你真正需要的是：

- 运单号级留痕
- 运单级证据

而不是仅仅车次级 / 出库单级 proof。

所以这张表更适合参考，不适合直接作为最终核心表。

---

## 11. `stock_fleet` 模块给调度补了什么

你的代码基线里，`stock_fleet` 很关键，因为它把库存批次和车队对象连起来了。

它主要做了 3 件事：

## 11.1 给批次补车辆和司机

扩展 `stock.picking.batch`：

- `vehicle_id`
- `vehicle_category_id`
- `driver_id`
- `dock_id`

这意味着 Odoo 已经可以做到：

- 一个批次选一辆车
- 批次带司机
- 批次带装车位
- 批次装车位可以直接落到仓库位置对象 `stock_location`

## 11.2 给操作类型补 dispatch 开关

扩展 `stock.picking.type`：

- `dispatch_management`
- `dock_ids`

这表示某些仓库操作类型会启用调度管理视图。

## 11.3 把仓库输出位置和 dock 逻辑串起来

扩展 `stock.warehouse`：

- 当仓库流程是发货相关步骤时，自动给出可用 dock

这说明：

- Odoo 现有代码已经有“装车位 / dock”概念
- 你不需要从零设计仓库装车位结构
- 你现在更适合直接复用这套 `dock_id -> stock_location` 机制，再在业务层补中文地库编号和装车指引

---

## 12. SQL 视角下最重要的关系图

把你最关心的几张表放一起，可以先理解成：

```text
sale_order
  1 -> n stock_picking

stock_picking
  n -> 1 stock_picking_batch
  n -> 1 stock_warehouse   (间接通过 picking_type / warehouse)
  n -> 1 sale_order        (由 sale_stock 扩展)

stock_picking_batch
  n -> 1 fleet_vehicle     (由 stock_fleet 扩展)
  n -> 1 res_partner       (driver_id，由 stock_fleet 扩展)
  n -> 1 stock_location    (dock_id，由 stock_fleet 扩展)

stock_delivery_trip
  n <-> n stock_picking    (通过中间表 stock_delivery_trip_picking_rel)

stock_delivery_proof
  n -> 1 stock_delivery_trip
  n -> 1 stock_picking

stock_warehouse
  1 -> n stock_location
```

---

## 13. 对你后续开发最有价值的复用建议

如果从你现在的物流留痕系统目标出发，我建议这样复用：

## 13.1 直接复用

建议直接复用：

- `stock_warehouse`
- `stock_location`
- `fleet_vehicle`
- `stock_picking`
- `stock_picking_batch`

原因是这些对象已经很成熟，没必要重造。

## 13.2 可以参考但不要直接当核心

建议参考但不要直接作为你最终核心：

- `stock_delivery_trip`
- `stock_delivery_proof`

原因是它们已经开始接近你的业务，但还不够“运单号中心化”。

## 13.3 必须自己补

你真正必须自己补的是：

- 运单主对象
- 运单与订单归并关系
- 批次级与运单级留痕事件
- 运单级证据对象

---

## 14. 最终结论

从 Odoo 原生 SQL 结构角度看，你后面最适合依附的主线不是：

```text
订单 -> 直接留痕
```

而更适合是：

```text
sale_order
  -> stock_picking
    -> stock_picking_batch
      -> fleet_vehicle
      -> stock_location(dock)

你自定义的：
  -> logistics_dispatch_waybill
  -> logistics_trace_event
  -> logistics_trace_evidence
```

一句话总结：

**Odoo 原生已经帮你把订单、出库、批次、车辆、仓库、装车位这些底座搭好了；你后面真正需要新增的，是“运单号主对象”和围绕运单号展开的留痕证据链。**

---

## 15. Odoo 里的图片是怎么存的

这个问题很重要，因为它会直接影响你后面做留痕图片时的存储方案判断。

## 15.1 Odoo 原生图片 / 附件主对象

Odoo 原生绝大多数图片、附件、二进制文件，核心都走：

- 模型：`ir.attachment`
- 表：`ir_attachment`

从 SQL 视角可以先把它理解成：

```sql
ir_attachment (
    id bigint primary key,
    name varchar,
    res_model varchar,
    res_id bigint,
    res_field varchar,
    type varchar,
    mimetype varchar,
    store_fname varchar,
    db_datas bytea,
    checksum varchar,
    file_size bigint,
    public boolean,
    create_date timestamp,
    write_date timestamp
)
```

其中最关键的字段是：

- `res_model` / `res_id`：附件挂在哪个业务对象上
- `res_field`：是否挂在某个二进制字段上
- `store_fname`：文件在文件存储中的物理标识
- `db_datas`：附件直接落数据库时的二进制内容
- `checksum`：文件摘要
- `mimetype`：文件类型
- `file_size`：文件大小

## 15.2 默认不是 MinIO / S3

Odoo 原生默认并不要求对象存储中间件。

从源码看，`ir.attachment` 默认读取配置项：

- `ir_attachment.location`

默认值是：

- `file`

这表示默认附件存储方式是：

- 元数据写入 `ir_attachment`
- 文件内容写入本地文件系统 filestore

也就是说，默认并不是：

- MinIO
- S3
- OSS
- FastDFS

这些都不是 Odoo 开箱即用的默认附件中间件。

## 15.3 默认文件存储方式

默认文件存储逻辑大致是：

```text
业务对象
  -> ir_attachment
    -> checksum(sha1)
    -> store_fname
    -> 本地 filestore 目录
```

Odoo 会按摘要生成文件名，并散列到 filestore 子目录下。

默认可以理解成：

```text
<data_dir>/filestore/<dbname>/<sha1 path>
```

所以它本质上是：

- 数据库存元数据
- 文件系统存文件实体

## 15.4 能不能改成对象存储

可以，但不是默认行为。

`ir.attachment` 里 `_file_read`、`_file_write`、`_file_delete` 这些方法就是预留出来给存储引擎扩展的。

所以后面如果你们留痕图片量很大，完全可以做成：

- Odoo 元数据仍保留在 `ir_attachment`
- 文件实体改写到 MinIO / S3
- 或者你自己单独设计 `logistics_trace_evidence` + 对象存储键

## 15.5 对你这个系统更务实的建议

如果从你们当前物流留痕系统来看，我建议分两阶段考虑：

第一阶段：

- 先搞清楚业务主对象和证据链
- 图片元数据不要直接塞满业务主表
- 可以先兼容 Odoo `ir_attachment` 机制

第二阶段：

- 如果日图片量、并发和归档要求明显上来
- 再把图片实体迁到 MinIO / S3
- 业务层保留自己的证据对象表，单独维护图片清单和访问键

一句话理解：

**Odoo 默认图片存储是 `ir_attachment + 本地 filestore`，不是对象存储中间件；如果你后面图片量大，建议把物流留痕图片逐步升级为“业务证据对象 + 独立对象存储”。**

如果按你们现在预估的量级：

- 一个批次约 `100` 张图片
- `6` 个月约 `3T`

那这个“第二阶段”其实不应该往后拖。更稳的做法是：

- 从一开始就按对象存储路线设计图片架构
- 不把 Odoo 默认 filestore 当作正式长期主方案
