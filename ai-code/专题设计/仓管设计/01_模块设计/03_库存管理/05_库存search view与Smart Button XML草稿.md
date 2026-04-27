# 库存search view与Smart Button XML草稿 v0.1

## 版本信息

- 文档名称：库存search view与Smart Button XML草稿
- 当前版本：`v0.1`
- 当前阶段：可评审初稿版
- 所属专题：仓管模块 / 模块设计 / 库存管理
- 当前用途：
  - 将库存专题中的字段映射和视图落地清单继续下沉为 XML 结构草稿
  - 为 `search view`、`act_window`、列表 / 表单增强和 Smart Button 落地提供实现前参考
  - 为后续真实 XML 回填时的文件拆分、命名和片段组织提供统一起点

## 目录索引

- `1. 文档定位`
- `2. 范围与边界`
- `3. 当前统一目标`
- `4. 文件与对象总览`
- `5. stock.quant XML草稿`
- `6. stock.location XML草稿`
- `7. stock.warehouse XML草稿`
- `8. Smart Button 方法与动作约定`
- `9. 文件拆分与命名建议`
- `10. 实施顺序与验证点`
- `11. 当前建议联读专题`

## 章节总览

这份稿子当前主要解决 4 个问题：

1. `stock.quant / stock.location / stock.warehouse` 的 `search view` 大致该怎么写
2. 列表页 / 表单页增强片段应该优先补哪些字段和入口
3. Smart Button 和 `act_window` 的 XML 该如何跟前面的字段清单、反查稿保持一致
4. 后续真实回填 XML 时，文件名、XML ID、视图继承节奏应如何收口

建议阅读顺序：

1. 先看 `1` 到 `4`，明确这份稿的职责和文件组织方式
2. 再看 `5` 到 `7`，按对象查看 XML 草稿
3. 最后看 `8` 到 `11`，明确方法约定、文件拆分和实施顺序

## 1. 文档定位

本文件重点回答“库存相关 XML 片段大致怎么落”，不直接替代真实代码实现。

它的作用是：

- 把 `04_库存页面字段映射与视图落地清单草稿.md` 继续下沉到 XML 结构层
- 提前固定 `search view`、`tree / form` 增强和 Smart Button 的组织方式
- 降低后续实现时“命名对了但 XML 结构散了”的风险

当前更推荐把这份稿理解成：

`库存专题中负责“XML 怎么拆、片段怎么摆、入口怎么接”的实现前草稿。`

## 2. 范围与边界

### 2.1 当前纳入范围

- `search view` 草稿
- `act_window` 草稿
- `tree / form` 视图增强片段草稿
- Smart Button 片段草稿
- XML ID 命名和文件命名建议

### 2.2 当前不纳入范围

- 真实可运行 XML 最终稿
- 真实 Python 方法实现
- 最终菜单树 XML
- 权限组与记录规则 XML
- 目标页如批次 / 运单 / 异常页的完整 XML

### 2.3 一句话边界

`本稿提供的是“实现草稿和组织方式”，不是可以直接上线的最终 XML。`

## 3. 当前统一目标

当前更推荐通过本稿先收住下面 5 件事：

1. 统一库存专题的 XML ID 前缀和文件拆分节奏
2. 统一 `search view + tree/form增强 + act_window + Smart Button` 的搭配方式
3. 让 `stock.quant` 先成为第一优先落地对象
4. 让所有入口继续遵守 `act_window + domain + context + search_default_*` 规则
5. 让真实实现时尽量以增量继承为主，而不是重写原生页面

当前更推荐的 XML 原则是：

`原生 view 轻继承，search view 先收口，Smart Button 只补最关键入口，动作参数和上下文统一复用。`

## 4. 文件与对象总览

### 4.1 当前推荐的文件拆分

当前更推荐库存专题 XML 后续按对象拆成下面 3 组文件：

- `views/inventory/inventory_quant_views.xml`
- `views/inventory/inventory_location_views.xml`
- `views/inventory/inventory_warehouse_views.xml`

如 search view 需要独立维护，也可继续拆成：

- `views/inventory/inventory_quant_search.xml`
- `views/inventory/inventory_location_search.xml`
- `views/inventory/inventory_warehouse_search.xml`

### 4.2 当前推荐的 XML ID 前缀

当前更推荐统一采用：

- `view_logistics_wms_inventory_*`
- `action_logistics_wms_inventory_*`

### 4.3 当前推荐的对象对照表

| 对象 | tree | form | search | action |
|---|---|---|---|---|
| `stock.quant` | `view_logistics_wms_inventory_quant_tree` | `view_logistics_wms_inventory_quant_form` | `view_logistics_wms_inventory_quant_search` | `action_logistics_wms_inventory_quant` |
| `stock.location` | `view_logistics_wms_inventory_location_tree` | `view_logistics_wms_inventory_location_form` | `view_logistics_wms_inventory_location_search` | `action_logistics_wms_inventory_location` |
| `stock.warehouse` | `view_logistics_wms_inventory_warehouse_tree` | `view_logistics_wms_inventory_warehouse_form` | `view_logistics_wms_inventory_warehouse_search` | `action_logistics_wms_inventory_warehouse` |

## 5. stock.quant XML草稿

### 5.1 search view 草稿

```xml
<record id="view_logistics_wms_inventory_quant_search" model="ir.ui.view">
    <field name="name">logistics.wms.inventory.quant.search</field>
    <field name="model">stock.quant</field>
    <field name="inherit_id" ref="stock.view_stock_quant_search"/>
    <field name="arch" type="xml">
        <xpath expr="//search" position="inside">
            <field name="product_id" string="商品"/>
            <field name="lot_id" string="批次"/>
            <field name="location_id" string="货位"/>

            <filter name="filter_has_stock"
                    string="有库存"
                    domain="[('quantity', '>', 0)]"/>
            <filter name="filter_available_positive"
                    string="可用量>0"
                    domain="[('available_quantity', '>', 0)]"/>
            <filter name="filter_has_reserved"
                    string="存在占用"
                    domain="[('reserved_quantity', '>', 0)]"/>
            <filter name="filter_has_frozen"
                    string="存在冻结"
                    domain="[('frozen_quantity', '>', 0)]"/>
            <filter name="filter_has_open_exception"
                    string="异常关注"
                    domain="[('has_open_exception', '=', True)]"/>

            <group expand="0" string="分组">
                <filter name="group_by_warehouse"
                        string="按仓库"
                        context="{'group_by': 'warehouse_id'}"/>
                <filter name="group_by_location"
                        string="按货位"
                        context="{'group_by': 'location_id'}"/>
                <filter name="group_by_product"
                        string="按商品"
                        context="{'group_by': 'product_id'}"/>
                <filter name="group_by_lot"
                        string="按批次"
                        context="{'group_by': 'lot_id'}"/>
            </group>
        </xpath>
    </field>
</record>
```

### 5.2 tree 视图增强草稿

```xml
<record id="view_logistics_wms_inventory_quant_tree" model="ir.ui.view">
    <field name="name">logistics.wms.inventory.quant.tree</field>
    <field name="model">stock.quant</field>
    <field name="inherit_id" ref="stock.view_stock_quant_tree"/>
    <field name="arch" type="xml">
        <xpath expr="//tree" position="inside">
            <field name="warehouse_id" optional="show"/>
            <field name="owner_id" optional="show"/>
            <field name="available_quantity" optional="show"/>
            <field name="reserved_quantity" optional="show"/>
            <field name="frozen_quantity" optional="show"/>
            <field name="latest_lot_display" optional="show"/>
            <field name="latest_waybill_display" optional="show"/>
            <field name="latest_trace_time" optional="show"/>
            <field name="has_open_exception" widget="boolean_toggle" optional="show"/>
        </xpath>
    </field>
</record>
```

### 5.3 form 视图增强草稿

```xml
<record id="view_logistics_wms_inventory_quant_form" model="ir.ui.view">
    <field name="name">logistics.wms.inventory.quant.form</field>
    <field name="model">stock.quant</field>
    <field name="inherit_id" ref="stock.view_stock_quant_form"/>
    <field name="arch" type="xml">
        <xpath expr="//form/sheet" position="inside">
            <div class="oe_button_box" name="button_box">
                <button name="action_open_related_lots"
                        type="object"
                        class="oe_stat_button"
                        icon="fa-tags"
                        string="相关批次"/>
                <button name="action_open_related_waybills"
                        type="object"
                        class="oe_stat_button"
                        icon="fa-truck"
                        string="相关运单"/>
                <button name="action_open_related_documents"
                        type="object"
                        class="oe_stat_button"
                        icon="fa-list"
                        string="相关主单"/>
                <button name="action_open_related_trace"
                        type="object"
                        class="oe_stat_button"
                        icon="fa-search"
                        string="查看追溯"/>
                <button name="action_open_related_exceptions"
                        type="object"
                        class="oe_stat_button"
                        icon="fa-warning"
                        string="查看异常"/>
            </div>

            <group string="数量摘要">
                <field name="quantity" readonly="1"/>
                <field name="available_quantity" readonly="1"/>
                <field name="reserved_quantity" readonly="1"/>
                <field name="frozen_quantity" readonly="1"/>
            </group>

            <group string="追溯摘要">
                <field name="latest_lot_display" readonly="1"/>
                <field name="latest_waybill_display" readonly="1"/>
                <field name="latest_trace_time" readonly="1"/>
                <field name="has_open_exception" readonly="1"/>
            </group>
        </xpath>
    </field>
</record>
```

### 5.4 action 草稿

```xml
<record id="action_logistics_wms_inventory_quant" model="ir.actions.act_window">
    <field name="name">库存查询</field>
    <field name="res_model">stock.quant</field>
    <field name="view_mode">list,form</field>
    <field name="search_view_id" ref="view_logistics_wms_inventory_quant_search"/>
    <field name="context">{'search_default_filter_has_stock': 1}</field>
</record>
```

## 6. stock.location XML草稿

### 6.1 search view 草稿

```xml
<record id="view_logistics_wms_inventory_location_search" model="ir.ui.view">
    <field name="name">logistics.wms.inventory.location.search</field>
    <field name="model">stock.location</field>
    <field name="inherit_id" ref="stock.view_location_search"/>
    <field name="arch" type="xml">
        <xpath expr="//search" position="inside">
            <field name="name" string="货位"/>
            <field name="warehouse_id" string="仓库"/>

            <filter name="filter_location_has_stock"
                    string="有库存"
                    domain="[('current_quant_count', '>', 0)]"/>
            <filter name="filter_location_has_exception"
                    string="存在异常"
                    domain="[('exception_waybill_count', '>', 0)]"/>
            <filter name="filter_location_recent_trace"
                    string="最近有留痕"
                    domain="[('latest_trace_time', '!=', False)]"/>

            <group expand="0" string="分组">
                <filter name="group_location_by_warehouse"
                        string="按仓库"
                        context="{'group_by': 'warehouse_id'}"/>
                <filter name="group_location_by_usage"
                        string="按货位类型"
                        context="{'group_by': 'usage'}"/>
            </group>
        </xpath>
    </field>
</record>
```

### 6.2 tree / form 增强草稿

```xml
<record id="view_logistics_wms_inventory_location_tree" model="ir.ui.view">
    <field name="name">logistics.wms.inventory.location.tree</field>
    <field name="model">stock.location</field>
    <field name="inherit_id" ref="stock.view_location_tree2"/>
    <field name="arch" type="xml">
        <xpath expr="//tree" position="inside">
            <field name="warehouse_id" optional="show"/>
            <field name="current_batch_count" optional="show"/>
            <field name="current_waybill_count" optional="show"/>
            <field name="exception_waybill_count" optional="show"/>
            <field name="latest_trace_time" optional="show"/>
        </xpath>
    </field>
</record>

<record id="view_logistics_wms_inventory_location_form" model="ir.ui.view">
    <field name="name">logistics.wms.inventory.location.form</field>
    <field name="model">stock.location</field>
    <field name="inherit_id" ref="stock.view_location_form"/>
    <field name="arch" type="xml">
        <xpath expr="//form/sheet" position="inside">
            <div class="oe_button_box" name="button_box">
                <button name="action_open_related_lots"
                        type="object"
                        class="oe_stat_button"
                        icon="fa-tags"
                        string="相关批次"/>
                <button name="action_open_related_waybills"
                        type="object"
                        class="oe_stat_button"
                        icon="fa-truck"
                        string="相关运单"/>
                <button name="action_open_related_documents"
                        type="object"
                        class="oe_stat_button"
                        icon="fa-list"
                        string="相关主单"/>
            </div>

            <group string="位置摘要">
                <field name="warehouse_id" readonly="1"/>
                <field name="usage" readonly="1"/>
                <field name="current_batch_count" readonly="1"/>
                <field name="current_waybill_count" readonly="1"/>
                <field name="exception_waybill_count" readonly="1"/>
                <field name="latest_trace_time" readonly="1"/>
            </group>
        </xpath>
    </field>
</record>
```

### 6.3 action 草稿

```xml
<record id="action_logistics_wms_inventory_location" model="ir.actions.act_window">
    <field name="name">货位查询</field>
    <field name="res_model">stock.location</field>
    <field name="view_mode">list,form</field>
    <field name="search_view_id" ref="view_logistics_wms_inventory_location_search"/>
</record>
```

## 7. stock.warehouse XML草稿

### 7.1 search view 草稿

```xml
<record id="view_logistics_wms_inventory_warehouse_search" model="ir.ui.view">
    <field name="name">logistics.wms.inventory.warehouse.search</field>
    <field name="model">stock.warehouse</field>
    <field name="inherit_id" ref="stock.view_warehouse"/>
    <field name="arch" type="xml">
        <xpath expr="//search" position="inside">
            <field name="code" string="仓库编码"/>
            <field name="name" string="仓库名称"/>

            <filter name="filter_warehouse_has_exception"
                    string="存在异常"
                    domain="[('current_exception_count', '>', 0)]"/>
            <filter name="filter_warehouse_recent_activity"
                    string="近期有活动"
                    domain="[('latest_trace_time', '!=', False)]"/>

            <group expand="0" string="分组">
                <filter name="group_warehouse"
                        string="按仓库"
                        context="{'group_by': 'id'}"/>
            </group>
        </xpath>
    </field>
</record>
```

### 7.2 tree / form 增强草稿

```xml
<record id="view_logistics_wms_inventory_warehouse_tree" model="ir.ui.view">
    <field name="name">logistics.wms.inventory.warehouse.tree</field>
    <field name="model">stock.warehouse</field>
    <field name="inherit_id" ref="stock.view_warehouse"/>
    <field name="arch" type="xml">
        <xpath expr="//tree" position="inside">
            <field name="current_batch_count" optional="show"/>
            <field name="current_waybill_count" optional="show"/>
            <field name="current_exception_count" optional="show"/>
            <field name="today_operation_count" optional="show"/>
            <field name="latest_trace_time" optional="show"/>
        </xpath>
    </field>
</record>

<record id="view_logistics_wms_inventory_warehouse_form" model="ir.ui.view">
    <field name="name">logistics.wms.inventory.warehouse.form</field>
    <field name="model">stock.warehouse</field>
    <field name="inherit_id" ref="stock.view_warehouse"/>
    <field name="arch" type="xml">
        <xpath expr="//form/sheet" position="inside">
            <div class="oe_button_box" name="button_box">
                <button name="action_open_current_lots"
                        type="object"
                        class="oe_stat_button"
                        icon="fa-tags"
                        string="当前批次"/>
                <button name="action_open_current_waybills"
                        type="object"
                        class="oe_stat_button"
                        icon="fa-truck"
                        string="当前运单"/>
                <button name="action_open_current_exceptions"
                        type="object"
                        class="oe_stat_button"
                        icon="fa-warning"
                        string="当前异常"/>
                <button name="action_open_current_locations"
                        type="object"
                        class="oe_stat_button"
                        icon="fa-cubes"
                        string="当前货位"/>
            </div>

            <group string="仓级摘要">
                <field name="current_batch_count" readonly="1"/>
                <field name="current_waybill_count" readonly="1"/>
                <field name="current_exception_count" readonly="1"/>
                <field name="today_operation_count" readonly="1"/>
                <field name="latest_trace_time" readonly="1"/>
            </group>
        </xpath>
    </field>
</record>
```

### 7.3 action 草稿

```xml
<record id="action_logistics_wms_inventory_warehouse" model="ir.actions.act_window">
    <field name="name">仓级总览</field>
    <field name="res_model">stock.warehouse</field>
    <field name="view_mode">list,form</field>
    <field name="search_view_id" ref="view_logistics_wms_inventory_warehouse_search"/>
</record>
```

## 8. Smart Button 方法与动作约定

### 8.1 当前推荐的方法命名

当前更推荐 Smart Button 对应的服务端方法统一采用：

- `action_open_related_lots`
- `action_open_related_waybills`
- `action_open_related_documents`
- `action_open_related_trace`
- `action_open_related_exceptions`

仓级入口更推荐采用：

- `action_open_current_lots`
- `action_open_current_waybills`
- `action_open_current_exceptions`
- `action_open_current_locations`

### 8.2 当前推荐的返回结构

当前更推荐这些 `type="object"` 方法最终统一返回 `ir.actions.act_window`，并尽量带上：

- `domain`
- `context`
- `search_default_*`

### 8.3 当前建议保留的上下文字段

当前更推荐沿用前面反查稿的上下文字段：

- `default_source_model`
- `default_source_id`
- `default_source_name`
- `search_default_warehouse_id`
- `search_default_location_id`
- `search_default_product_id`
- `search_default_lot_id`
- `search_default_has_open_exception`

### 8.4 当前推荐的一句话原则

`Smart Button 的关键不是把人打开新页，而是把人送到已经带好上下文的目标页。`

## 9. 文件拆分与命名建议

### 9.1 当前推荐的文件命名

当前更推荐后续 XML 文件统一放在：

```text
views/inventory/
  inventory_quant_views.xml
  inventory_location_views.xml
  inventory_warehouse_views.xml
```

如果 search view 后续持续变厚，可再拆：

```text
views/inventory/
  inventory_quant_search.xml
  inventory_location_search.xml
  inventory_warehouse_search.xml
```

### 9.2 当前推荐的回填方式

当前更推荐：

1. 先补 `search view`
2. 再补 `tree`
3. 再补 `form`
4. 最后补 Smart Button 方法与 action 上下文

### 9.3 当前不建议的做法

当前不建议：

- 先写大量 Smart Button，再补 search view
- 在一个超大 XML 文件里混放所有库存对象
- 为库存专题单独造重型 client action 替代原生查询页

## 10. 实施顺序与验证点

### 10.1 当前推荐的实施顺序

当前更推荐按下面顺序推进：

1. `stock.quant`
   - `search view`
   - `tree`
   - `form`
   - Smart Button

2. `stock.location`
   - `search view`
   - `tree`
   - `form`

3. `stock.warehouse`
   - `search view`
   - `tree`
   - `form`

### 10.2 当前需要重点验证

需要验证：

- `search view` 的筛选语义是否与口径稿一致
- `tree` 列结构是否与页面结构稿一致
- Smart Button 是否与反查稿中的顺序和命名一致
- `action` 是否能带出默认筛选和来源上下文
- 仓级页是否仍然是汇总入口，而不是深读页

### 10.3 一句话收口

`这份 XML 草稿的价值，不是让实现一次写完，而是让实现时每一步都不跑偏。`

## 11. 当前建议联读专题

- `01_模块设计/03_库存管理/01_库存现状与可用量口径规范草稿.md`
- `01_模块设计/03_库存管理/02_库存反查与追溯入口设计草稿.md`
- `01_模块设计/03_库存管理/03_库存页面结构与查询规范草稿.md`
- `01_模块设计/03_库存管理/04_库存页面字段映射与视图落地清单草稿.md`
- `01_模块设计/03_库存管理/06_库存扩展字段与Python方法映射草稿.md`
- `01_模块设计/03_库存管理/07_库存模块开发任务拆分清单草稿.md`
- `01_模块设计/03_库存管理/08_库存专题联调与验收草稿.md`
- `01_模块设计/00_四类主单统一页面结构规范草稿.md`
- `02_跨模块规范/05_页面与查询/00_搜索_筛选_表头统一规范草稿.md`
