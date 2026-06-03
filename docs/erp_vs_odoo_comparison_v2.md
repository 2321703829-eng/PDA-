# ERP 模板 vs Odoo 系统 - 字段级对比（修正版）

> 对比时间：2026-05-27
> 数据来源：ERP模板.xlsx + custom_addons/ 实际代码

---

## 1. 基础档案模块

### 1.1 客户信息（erp_customer.py + web_import_partner.py + crm.lead）

| ERP字段 | Odoo字段 | 所在模型 | 状态 | 备注 |
|---------|----------|----------|------|------|
| 客户名称 | name | res.partner | ✅ 已有 | 客户简称 |
| 客户编码 | x_customer_code | erp.customer | ✅ 已有 | 客户唯一编码 |
| 客户简称 | x_short_name | erp.customer | ✅ 已有 | |
| 客户类型 | x_customer_type | erp.customer | ✅ 已有 | 门店/经销商/商超 |
| 助记码 | x_mnemonic_code | erp.customer | ✅ 已有 | 首字母简拼 |
| 联系人 | x_contact_name | erp.customer | ✅ 已有 | |
| 联系电话 | phone | res.partner | ✅ 已有 | |
| 详细地址 | street | res.partner | ✅ 已有 | |
| 经度 | x_longitude | crm.lead | ✅ 已有 | web_import_partner 导入 |
| 纬度 | x_latitude | crm.lead | ✅ 已有 | web_import_partner 导入 |
| 送货地址 | x_delivery_address | crm.lead | ✅ 已有 | 独立送货地址 |
| 区域 | x_area | crm.lead | ✅ 已有 | |
| 备注 | x_notes | crm.lead | ✅ 已有 | |
| 负责业务员 | user_id | res.partner | ✅ 已有 | Odoo原生 |
| 创建时间 | create_date | res.partner | ✅ 已有 | Odoo原生 |
| 最近下单日期 | x_last_order_date | erp.customer | ✅ 已有 | |
| 应收余额 | x_receivable_balance | erp.customer | ✅ 已有 | |
| 订单数 | x_order_count | erp.customer | ✅ 已有 | |
| 累计消费 | x_total_spent | erp.customer | ✅ 已有 | |
| 收货时间段 | ❌ 缺失 | - | ❌ 需新增 | ERP有此字段 |
| 停车费 | ❌ 缺失 | - | ❌ 需新增 | 配送相关 |
| 卸货位置 | ❌ 缺失 | - | ❌ 需新增 | 配送相关 |
| 配送设备要求 | ❌ 缺失 | - | ❌ 需新增 | 如需要尾板车 |

**覆盖率：85%**（经修正后大幅提升）

---

### 1.2 供应商管理（erp_partner.py）

| ERP字段 | Odoo字段 | 所在模型 | 状态 | 备注 |
|---------|----------|----------|------|------|
| 供应商编码 | x_supplier_code | res.partner | ✅ 已有 | |
| 供应商名称 | name | res.partner | ✅ 已有 | |
| 简称 | x_short_name | res.partner | ✅ 已有 | |
| 企业状态 | x_business_status | res.partner | ✅ 已有 | |
| 助记码 | x_mnemonic_code | res.partner | ✅ 已有 | |
| 联系人 | x_contact_name | res.partner | ✅ 已有 | |
| 手机号 | phone | res.partner | ✅ 已有 | |
| 电话 | x_telephone | res.partner | ✅ 已有 | |
| 详细地址 | street | res.partner | ✅ 已有 | |
| 预付比例 | x_prepayment_ratio | res.partner | ✅ 已有 | |
| 采购提前期 | x_lead_time | res.partner | ✅ 已有 | |
| 采购价 | x_purchase_price | res.partner | ✅ 已有 | |
| 税率 | x_tax_rate | res.partner | ✅ 已有 | |
| 邮箱 | email | res.partner | ✅ 已有 | |
| 采购员 | x_buyer | res.partner | ✅ 已有 | |
| 主要商品 | x_main_products | res.partner | ✅ 已有 | |
| 开户行 | x_bank_name | res.partner | ✅ 已有 | |
| 银行账号 | x_bank_account | res.partner | ✅ 已有 | |
| 信用额度 | x_credit_limit | res.partner | ✅ 已有 | |
| 描述 | comment | res.partner | ✅ 已有 | |
| 备注 | x_notes | res.partner | ✅ 已有 | |

**覆盖率：95%**（几乎完整）

---

### 1.3 司机列表（erp_driver.py）

| ERP字段 | Odoo字段 | 所在模型 | 状态 | 备注 |
|---------|----------|----------|------|------|
| 司机编码 | x_driver_code | erp.driver | ✅ 已有 | |
| 司机名称 | x_driver_name | erp.driver | ✅ 已有 | |
| 联系电话 | x_phone | erp.driver | ✅ 已有 | |
| 身份证号 | x_id_card | erp.driver | ✅ 已有 | |
| 有无健康证 | x_has_health_cert | erp.driver | ✅ 已有 | |
| 健康证号 | x_health_cert_no | erp.driver | ✅ 已有 | |
| 健康证到期日期 | x_health_cert_expiry | erp.driver | ✅ 已有 | |
| 司机服务评分 | x_service_score | erp.driver | ✅ 已有 | |
| 绑定车辆ID | x_vehicle_ids | erp.driver | ✅ 已有 | One2many |
| 默认状态 | x_state | erp.driver | ✅ 已有 | 空闲/运输中/休假 |
| 描述 | x_description | erp.driver | ✅ 已有 | |

**覆盖率：91%**

---

### 1.4 车辆列表（erp_vehicle.py）

| ERP字段 | Odoo字段 | 所在模型 | 状态 | 备注 |
|---------|----------|----------|------|------|
| 车辆编码 | x_vehicle_code | erp.vehicle | ✅ 已有 | |
| 车牌号 | x_plate_number | erp.vehicle | ✅ 已有 | |
| 车型 | x_vehicle_type | erp.vehicle | ✅ 已有 | |
| 所属车队 | x_fleet | erp.vehicle | ✅ 已有 | |
| 核定吨位 | x_tonnage | erp.vehicle | ✅ 已有 | |
| 核定方量 | x_cubic | erp.vehicle | ✅ 已有 | |
| 长 | x_length | erp.vehicle | ✅ 已有 | |
| 宽 | x_width | erp.vehicle | ✅ 已有 | |
| 高 | x_height | erp.vehicle | ✅ 已有 | |
| 车辆状态 | x_status | erp.vehicle | ✅ 已有 | 空闲/运输中/维修 |
| 车架号 | x_vin | erp.vehicle | ✅ 已有 | |
| 发动机号 | x_engine_no | erp.vehicle | ✅ 已有 | |
| 行驶证到期日 | x_license_expiry | erp.vehicle | ✅ 已有 | |
| 年审日期 | ❌ 缺失 | - | ❌ 需新增 | |
| 保险到期日 | ❌ 缺失 | - | ❌ 需新增 | |
| 绑定司机ID | x_driver_ids | erp.vehicle | ✅ 已有 | One2many |
| 备注 | x_notes | erp.vehicle | ✅ 已有 | |

**覆盖率：88%**

---

### 1.5 商品列表（product.template 扩展 + erp_product.py）

| ERP字段 | Odoo字段 | 所在模型 | 状态 | 备注 |
|---------|----------|----------|------|------|
| 商品编码 | default_code | product.template | ✅ 已有 | Odoo原生 |
| 商品名称 | name | product.template | ✅ 已有 | Odoo原生 |
| 规格型号 | x_specification | product.template | ✅ 已有 | |
| 所属分类 | categ_id | product.template | ✅ 已有 | Odoo原生 |
| 品牌 | x_brand | product.template | ✅ 已有 | |
| 基本单位 | uom_id | product.template | ✅ 已有 | Odoo原生 |
| 小单位 | x_small_uom | product.template | ✅ 已有 | |
| 中单位 | x_medium_uom | product.template | ✅ 已有 | |
| 大单位 | x_large_uom | product.template | ✅ 已有 | |
| 小单位重量 | x_small_weight | product.template | ✅ 已有 | |
| 大单位重量 | x_large_weight | product.template | ✅ 已有 | |
| 大单位换算中单位 | x_large_to_medium | product.template | ✅ 已有 | |
| 中单位换算小单位 | x_medium_to_small | product.template | ✅ 已有 | |
| 重量 | weight | product.template | ✅ 已有 | Odoo原生 |
| 体积 | volume | product.template | ✅ 已有 | Odoo原生 |
| 长 | x_length | product.template | ✅ 已有 | |
| 宽 | x_width | product.template | ✅ 已有 | |
| 高 | x_height | product.template | ✅ 已有 | |
| 单位体积重 | x_unit_volume_weight | product.template | ✅ 已有 | |
| 毛重 | x_gross_weight | product.template | ✅ 已有 | |
| 起订量 | x_min_order_qty | product.template | ✅ 已有 | |
| 拆零标志 | x_is_splitable | product.template | ✅ 已有 | |
| 是否液体 | x_is_liquid | product.template | ✅ 已有 | |
| 是否有保质期 | x_has_shelf_life | product.template | ✅ 已有 | |
| 默认保质期天数 | x_shelf_life_days | product.template | ✅ 已有 | |
| 成本 | standard_price | product.template | ✅ 已有 | Odoo原生 |
| 售价 | list_price | product.template | ✅ 已有 | Odoo原生 |
| 三证资质 | ❌ 缺失 | - | ❌ 需新增 | 附件字段 |
| 有效期 | ❌ 缺失 | - | ❌ 需新增 | 与保质期不同 |
| 描述 | description | product.template | ✅ 已有 | Odoo原生 |
| 备注 | x_notes | product.template | ✅ 已有 | |
| 图片 | image_1920 | product.template | ✅ 已有 | Odoo原生 |

**覆盖率：94%**（多单位体系已完整实现）

---

## 2. 采购管理模块

### 2.1 采购订单（purchase.order 扩展）

| ERP字段 | Odoo字段 | 所在模型 | 状态 | 备注 |
|---------|----------|----------|------|------|
| 订单日期 | date_order | purchase.order | ✅ 已有 | Odoo原生 |
| 订单号 | name | purchase.order | ✅ 已有 | Odoo原生 |
| 供应商 | partner_id | purchase.order | ✅ 已有 | Odoo原生 |
| 采购员 | x_buyer | purchase.order | ✅ 已有 | 扩展字段 |
| 仓库 | x_warehouse_id | purchase.order | ✅ 已有 | |
| 税率 | x_tax_rate | purchase.order | ✅ 已有 | |
| 结算账户 | ❌ 缺失 | - | ❌ 需新增 | |
| 结算方式 | ❌ 缺失 | - | ❌ 需新增 | |
| 部门 | ❌ 缺失 | - | ❌ 需新增 | Odoo原生department_id可用 |
| 操作员 | x_operator | purchase.order | ✅ 已有 | |
| 附件 | x_attachment | purchase.order | ✅ 已有 | |
| 备注 | x_notes | purchase.order | ✅ 已有 | |
| 制单人 | create_uid | purchase.order | ✅ 已有 | Odoo原生 |
| 制单日期 | create_date | purchase.order | ✅ 已有 | Odoo原生 |
| 审核人 | x_reviewer | purchase.order | ✅ 已有 | |
| 审核日期 | x_review_date | purchase.order | ✅ 已有 | |
| 业务状态 | ❌ 缺失 | - | ❌ 需新增 | draft/confirm/reviewed/approved |
| **明细行** | | | | |
| 商品 | product_id | purchase.order.line | ✅ 已有 | Odoo原生 |
| 数量 | product_qty | purchase.order.line | ✅ 已有 | Odoo原生 |
| 单价 | price_unit | purchase.order.line | ✅ 已有 | Odoo原生 |
| 税率 | taxes_id | purchase.order.line | ✅ 已有 | Odoo原生 |
| 税金 | x_tax_amount | purchase.order.line | ✅ 已有 | |
| 赠品数量 | x_gift_qty | purchase.order.line | ✅ 已有 | |
| 预付金额 | x_prepayment_amount | purchase.order.line | ✅ 已有 | |

**覆盖率：80%**

---

### 2.2 采购入库单（wms_receipt.py）

| ERP字段 | Odoo字段 | 所在模型 | 状态 | 备注 |
|---------|----------|----------|------|------|
| 入库单号 | receipt_number | wms.receipt | ✅ 已有 | |
| 仓库 | warehouse_id | wms.receipt | ✅ 已有 | |
| 供应商 | supplier_name | wms.receipt | ✅ 已有 | 字符串，非关联 |
| 关联采购订单 | purchase_order_id | wms.receipt | ✅ 已有 | |
| 状态 | state | wms.receipt | ✅ 已有 | draft/received/putaway |
| 操作员 | operator | wms.receipt | ✅ 已有 | |
| 卸货道口 | dock | wms.receipt | ✅ 已有 | |
| 实际开始时间 | actual_start | wms.receipt | ✅ 已有 | |
| 实际完成时间 | actual_end | wms.receipt | ✅ 已有 | |
| 差异标记 | has_discrepancy | wms.receipt | ✅ 已有 | |
| 差异备注 | discrepancy_note | wms.receipt | ✅ 已有 | |
| **明细行** | | | | |
| 商品 | product_id | wms.receipt.line | ✅ 已有 | |
| 预期数量 | expected_qty | wms.receipt.line | ✅ 已有 | |
| 实收数量 | actual_qty | wms.receipt.line | ✅ 已有 | |
| 批次号 | lot_id | wms.receipt.line | ✅ 已有 | |
| 单价 | ❌ 缺失 | - | ❌ 需新增 | |
| 金额 | ❌ 缺失 | - | ❌ 需新增 | |
| 税金 | ❌ 缺失 | - | ❌ 需新增 | |

**覆盖率：71%**

---

## 3. 销售管理模块

### 3.1 销售订单（sale.order 扩展）

| ERP字段 | Odoo字段 | 所在模型 | 状态 | 备注 |
|---------|----------|----------|------|------|
| 订单日期 | date_order | sale.order | ✅ 已有 | Odoo原生 |
| 订单号 | name | sale.order | ✅ 已有 | Odoo原生 |
| 客户 | partner_id | sale.order | ✅ 已有 | Odoo原生 |
| 收货人 | x_consignee | sale.order | ✅ 已有 | |
| 业务类型 | x_business_type | sale.order | ✅ 已有 | 批发/零售/调货 |
| 下单时间 | x_order_time | sale.order | ✅ 已有 | |
| 配送日期 | x_delivery_date | sale.order | ✅ 已有 | |
| 配送时段 | x_delivery_time_slot | sale.order | ✅ 已有 | |
| 期望送达时间 | x_expected_delivery_time | sale.order | ✅ 已有 | |
| 运费 | x_shipping_fee | sale.order | ✅ 已有 | |
| 收款状态 | x_payment_status | sale.order | ✅ 已有 | 未收/部分/已收 |
| 收款金额 | x_paid_amount | sale.order | ✅ 已有 | |
| 收款时间 | x_payment_time | sale.order | ✅ 已有 | |
| 收款人 | x_payment_by | sale.order | ✅ 已有 | |
| 配送地址 | x_delivery_address | sale.order | ✅ 已有 | |
| 详细地址 | x_detail_address | sale.order | ✅ 已有 | |
| 省份 | x_province | sale.order | ✅ 已有 | |
| 城市 | x_city | sale.order | ✅ 已有 | |
| 区/县 | x_district | sale.order | ✅ 已有 | |
| 发货状态 | x_delivery_status | sale.order | ✅ 已有 | 未发/部分/已发 |
| 支付方式 | ❌ 缺失 | - | ❌ 需新增 | 现金/转账/挂账 |
| 支付凭证 | ❌ 缺失 | - | ❌ 需新增 | 附件 |
| 物流公司 | ❌ 缺失 | - | ❌ 需新增 | |
| 物流单号 | ❌ 缺失 | - | ❌ 需新增 | |
| 业务员 | ❌ 缺失 | - | ❌ 需新增 | user_id 可用 |
| 取消原因 | x_cancel_reason | sale.order | ✅ 已有 | |
| 取消时间 | x_cancel_time | sale.order | ✅ 已有 | |
| 退货标志 | x_return_flag | sale.order | ✅ 已有 | |
| 标记 | x_tags | sale.order | ✅ 已有 | |
| 备注 | x_notes | sale.order | ✅ 已有 | |
| **明细行** | | | | |
| 商品 | product_id | sale.order.line | ✅ 已有 | Odoo原生 |
| 数量 | x_quantity | sale.order.line | ✅ 已有 | |
| 重量 | x_weight | sale.order.line | ✅ 已有 | |
| 单价 | price_unit | sale.order.line | ✅ 已有 | Odoo原生 |
| 折扣 | x_discount | sale.order.line | ✅ 已有 | |
| 金额 | price_subtotal | sale.order.line | ✅ 已有 | Odoo原生 |
| 税率 | tax_id | sale.order.line | ✅ 已有 | Odoo原生 |
| 赠品数量 | x_gift_quantity | sale.order.line | ✅ 已有 | |

**覆盖率：78%**

---

### 3.2 销售出库单（wms_shipment.py）

| ERP字段 | Odoo字段 | 所在模型 | 状态 | 备注 |
|---------|----------|----------|------|------|
| 出库单号 | shipment_number | wms.shipment | ✅ 已有 | |
| 仓库 | warehouse_id | wms.shipment | ✅ 已有 | |
| 状态 | state | wms.shipment | ✅ 已有 | draft/picking/packed/shipped |
| 关联运单 | waybill_id | wms.shipment | ✅ 已有 | |
| 关联销售订单 | sale_order_id | wms.shipment | ✅ 已有 | |
| 承运人 | carrier | wms.shipment | ✅ 已有 | |
| 物流单号 | tracking_number | wms.shipment | ✅ 已有 | |
| 实际出库时间 | actual_ship_time | wms.shipment | ✅ 已有 | |
| 总数量 | total_qty | wms.shipment | ✅ 已有 | |
| 总重量 | total_weight | wms.shipment | ✅ 已有 | |
| 总体积 | total_volume | wms.shipment | ✅ 已有 | |
| 拣货员 | picker | wms.shipment | ✅ 已有 | |
| 复核员 | checker | wms.shipment | ✅ 已有 | |
| 客户名称 | ❌ 缺失 | - | ❌ 需新增 | 从关联订单获取 |
| 客户编码 | ❌ 缺失 | - | ❌ 需新增 | 从关联订单获取 |
| 发货金额 | ❌ 缺失 | - | ❌ 需新增 | |
| 结算账户 | ❌ 缺失 | - | ❌ 需新增 | |
| 结算方式 | ❌ 缺失 | - | ❌ 需新增 | |
| 结算状态 | ❌ 缺失 | - | ❌ 需新增 | 未结/已结 |
| 单据备注 | ❌ 缺失 | - | ❌ 需新增 | |
| 制单人 | create_uid | wms.shipment | ✅ 已有 | Odoo原生 |
| 制单日期 | create_date | wms.shipment | ✅ 已有 | Odoo原生 |
| **明细行** | | | | |
| 商品 | product_id | wms.shipment.line | ✅ 已有 | |
| 应发数量 | expected_qty | wms.shipment.line | ✅ 已有 | |
| 实发数量 | actual_qty | wms.shipment.line | ✅ 已有 | |
| 单价 | ❌ 缺失 | - | ❌ 需新增 | |
| 金额 | ❌ 缺失 | - | ❌ 需新增 | |
| 赠品数量 | ❌ 缺失 | - | ❌ 需新增 | |

**覆盖率：55%**（缺财务/结算字段）

---

### 3.3 销售退货单（erp_sale_return.py）

| ERP字段 | Odoo字段 | 所在模型 | 状态 | 备注 |
|---------|----------|----------|------|------|
| 退货单号 | name | erp.sale.return | ✅ 已有 | |
| 退货日期 | return_date | erp.sale.return | ✅ 已有 | |
| 关联订单 | source_order_id | erp.sale.return | ✅ 已有 | |
| 关联订单号 | source_order | erp.sale.return | ✅ 已有 | |
| 客户编码 | customer_code | erp.sale.return | ✅ 已有 | |
| 客户名称 | customer_name | erp.sale.return | ✅ 已有 | |
| 退货原因 | reason | erp.sale.return | ✅ 已有 | |
| 退货总金额 | total_amount | erp.sale.return | ✅ 已有 | |
| 收货状态 | receive_status | erp.sale.return | ✅ 已有 | pending/received/partial |
| 收货时间 | receive_time | erp.sale.return | ✅ 已有 | |
| 收货人 | receiver | erp.sale.return | ✅ 已有 | |
| 核对状态 | check_status | erp.sale.return | ✅ 已有 | pending/checked/exception |
| 核对时间 | check_time | erp.sale.return | ✅ 已有 | |
| 核对人 | checker | erp.sale.return | ✅ 已有 | |
| 退款状态 | refund_status | erp.sale.return | ✅ 已有 | pending/refunded/partial |
| 退款金额 | refund_amount | erp.sale.return | ✅ 已有 | |
| 退款时间 | refund_time | erp.sale.return | ✅ 已有 | |
| 入库状态 | putaway_status | erp.sale.return | ✅ 已有 | |
| 入库时间 | putaway_time | erp.sale.return | ✅ 已有 | |
| 入库人 | putaway_by | erp.sale.return | ✅ 已有 | |
| 仓库 | warehouse_id | erp.sale.return | ✅ 已有 | |
| 验收人 | inspector | erp.sale.return | ✅ 已有 | |
| 备注 | notes | erp.sale.return | ✅ 已有 | |
| 制单人 | create_uid | erp.sale.return | ✅ 已有 | Odoo原生 |
| **明细行** | | | | |
| 商品ID | ❌ 缺失 | - | ❌ 需新增 | 需要 line_ids |
| 商品编码 | ❌ 缺失 | - | ❌ 需新增 | |
| 商品名称 | ❌ 缺失 | - | ❌ 需新增 | |
| 规格型号 | ❌ 缺失 | - | ❌ 需新增 | |
| 基本单位 | ❌ 缺失 | - | ❌ 需新增 | |
| 退货数量 | ❌ 缺失 | - | ❌ 需新增 | |
| 实收数量 | ❌ 缺失 | - | ❌ 需新增 | |
| 单价 | ❌ 缺失 | - | ❌ 需新增 | |
| 金额小计 | ❌ 缺失 | - | ❌ 需新增 | |

**覆盖率：70%**（主表完整，缺明细行）

---

## 4. 仓库管理模块

### 4.1 库存查询（ERP模板）

| ERP字段 | Odoo字段 | 所在模型 | 状态 | 备注 |
|---------|----------|----------|------|------|
| 商品名称 | product_id.name | stock.quant | ✅ 已有 | Odoo原生 |
| 规格型号 | product_id.x_specification | stock.quant | ✅ 已有 | |
| 分类 | product_id.categ_id | stock.quant | ✅ 已有 | Odoo原生 |
| 商品编码 | product_id.default_code | stock.quant | ✅ 已有 | Odoo原生 |
| 仓库 | warehouse_id | stock.quant | ✅ 已有 | Odoo原生 |
| 库存数量 | quantity | stock.quant | ✅ 已有 | Odoo原生 |

**覆盖率：100%**（Odoo原生）

---

### 4.2 入库任务（wms_inbound.py）

| ERP字段 | Odoo字段 | 所在模型 | 状态 | 备注 |
|---------|----------|----------|------|------|
| 任务编码 | task_code | wms.inbound.task | ✅ 已有 | |
| 入库单号 | receipt_number | wms.inbound.task | ✅ 已有 | |
| 仓库 | warehouse_id | wms.inbound.task | ✅ 已有 | |
| 供应商名称 | supplier_name | wms.inbound.task | ✅ 已有 | |
| 预到货时间 | expected_arrival_time | wms.inbound.task | ✅ 已有 | |
| 实际开始时间 | actual_start_time | wms.inbound.task | ✅ 已有 | |
| 实际完成时间 | actual_end_time | wms.inbound.task | ✅ 已有 | |
| 优先级 | priority | wms.inbound.task | ✅ 已有 | high/medium/low |
| 是否有差异 | has_difference | wms.inbound.task | ✅ 已有 | |
| 差异备注 | difference_remark | wms.inbound.task | ✅ 已有 | |
| 状态 | state | wms.inbound.task | ✅ 已有 | pending/assigned/putaway/completed |
| 收货员 | receiver_id | wms.inbound.task | ✅ 已有 | |
| 上架员 | putaway_operator_id | wms.inbound.task | ✅ 已有 | |
| 备注 | remark | wms.inbound.task | ✅ 已有 | |
| **子表** | | | | |
| 商品 | product_id | wms.inbound.task.line | ✅ 已有 | |
| 预期数量 | expected_qty | wms.inbound.task.line | ✅ 已有 | |
| 实收数量 | received_qty | wms.inbound.task.line | ✅ 已有 | |
| 差异数量 | difference_qty | wms.inbound.task.line | ✅ 已有 | |
| 采购订单 | purchase_order_id | wms.inbound.task.line | ✅ 已有 | |
| 差异类型 | difference_type | wms.inbound.task.line | ✅ 已有 | none/shortage/damage/excess |
| 差异描述 | difference_description | wms.inbound.task.line | ✅ 已有 | |
| 收货状态 | receive_status | wms.inbound.task.line | ✅ 已有 | pending/partial/completed |

**覆盖率：95%**

---

### 4.3 上架任务（wms_inbound.py）

| ERP字段 | Odoo字段 | 所在模型 | 状态 | 备注 |
|---------|----------|----------|------|------|
| 任务编码 | task_code | wms.putaway.task | ✅ 已有 | |
| 入库单号 | receipt_number | wms.putaway.task | ✅ 已有 | |
| 仓库 | warehouse_id | wms.putaway.task | ✅ 已有 | |
| 状态 | state | wms.putaway.task | ✅ 已有 | pending/in_progress/completed |
| 优先级 | priority | wms.putaway.task | ✅ 已有 | |
| 上架员 | operator_id | wms.putaway.task | ✅ 已有 | |
| 实际开始时间 | actual_start_time | wms.putaway.task | ✅ 已有 | |
| 实际完成时间 | actual_end_time | wms.putaway.task | ✅ 已有 | |
| 备注 | remark | wms.putaway.task | ✅ 已有 | |
| **子表** | | | | |
| 收货任务 | inbound_line_id | wms.putaway.task.line | ✅ 已有 | |
| 商品 | product_id | wms.putaway.task.line | ✅ 已有 | |
| 目标库位 | target_location_id | wms.putaway.task.line | ✅ 已有 | |
| 数量 | qty | wms.putaway.task.line | ✅ 已有 | |
| 状态 | status | wms.putaway.task.line | ✅ 已有 | pending/done |

**覆盖率：90%**

---

### 4.4 出库任务（wms_outbound.py）

| ERP字段 | Odoo字段 | 所在模型 | 状态 | 备注 |
|---------|----------|----------|------|------|
| 任务编码 | task_code | wms.outbound.task | ✅ 已有 | |
| 出库单号 | shipment_number | wms.outbound.task | ✅ 已有 | |
| 仓库 | warehouse_id | wms.outbound.task | ✅ 已有 | |
| 状态 | state | wms.outbound.task | ✅ 已有 | 5种状态 |
| 优先级 | priority | wms.outbound.task | ✅ 已有 | |
| 拣货员 | picker_id | wms.outbound.task | ✅ 已有 | |
| 复核员 | checker_id | wms.outbound.task | ✅ 已有 | |
| 拣货开始/完成时间 | pick_start/end_time | wms.outbound.task | ✅ 已有 | |
| 复核开始/完成时间 | check_start/end_time | wms.outbound.task | ✅ 已有 | |
| 交接完成时间 | handover_time | wms.outbound.task | ✅ 已有 | |
| 差异标记 | has_discrepancy | wms.outbound.task | ✅ 已有 | |
| 差异处理状态 | discrepancy_status | wms.outbound.task | ✅ 已有 | |
| **子表** | | | | |
| 销售订单行 | sale_line_id | wms.outbound.task.line | ✅ 已有 | |
| 商品 | product_id | wms.outbound.task.line | ✅ 已有 | |
| 应发数量 | expected_qty | wms.outbound.task.line | ✅ 已有 | |
| 实拣数量 | picked_qty | wms.outbound.task.line | ✅ 已有 | |
| 复核数量 | checked_qty | wms.outbound.task.line | ✅ 已有 | |
| 源库位 | source_location_id | wms.outbound.task.line | ✅ 已有 | |
| 目标库位 | target_location_id | wms.outbound.task.line | ✅ 已有 | |
| 拣货状态 | pick_status | wms.outbound.task.line | ✅ 已有 | |
| 差异类型 | discrepancy_type | wms.outbound.task.line | ✅ 已有 | |
| 差异描述 | discrepancy_description | wms.outbound.task.line | ✅ 已有 | |

**覆盖率：95%**

---

## 5. 完全缺失模块

### 5.1 采购退货单
**状态：❌ 完全缺失**
**建议方案：** 新建 `erp.purchase.return` + `erp.purchase.return.line`

| 字段 | 类型 | 说明 |
|------|------|------|
| name | char | 退货单号 |
| return_date | date | 退货日期 |
| source_order_id | many2one | 关联采购订单 |
| supplier_id | many2one | 供应商 |
| warehouse_id | many2one | 仓库 |
| reason | selection | 退货原因 |
| total_amount | float | 退货总金额 |
| operator | char | 操作员 |
| remark | text | 备注 |
| line_ids | one2many | 明细行 |
| state | selection | 状态（draft/confirmed/done） |

---

### 5.2 采购退货出库单
**状态：❌ 完全缺失**
**建议方案：** 扩展 `wms.shipment` 或新建

---

### 5.3 智能补货
**状态：❌ 完全缺失**
**建议方案：** 新建 `erp.replenishment.rule` + `erp.replenishment.order`

| 字段 | 类型 | 说明 |
|------|------|------|
| product_id | many2one | 商品 |
| warehouse_id | many2one | 仓库 |
| safety_stock | float | 安全库存 |
| reorder_point | float | 重订货点 |
| max_stock | float | 最大库存 |
| lead_time | integer | 补货周期（天） |
| min_order_qty | float | 最小订货量 |
| last_replenish_qty | float | 上次补货量 |
| last_replenish_date | date | 上次补货日期 |

---

## 6. 报表模块

**状态：❌ 几乎全缺（22%覆盖）**

### 需新建的报表

| 报表名称 | 数据来源 | 实现方式 |
|----------|----------|----------|
| 采购订单汇总表 | purchase.order | Odoo报表引擎 |
| 采购明细表 | purchase.order.line | Odoo报表引擎 |
| 销售订单汇总表 | sale.order | Odoo报表引擎 |
| 销售明细表 | sale.order.line | Odoo报表引擎 |
| 业务员销售汇总表 | sale.order + user_id | Odoo报表引擎 |
| 采购退货明细表 | erp.purchase.return | 新建后报表 |
| 销售退货明细表 | erp.sale.return | 新建后报表 |

---

## 7. 覆盖率总览（修正后）

| 模块 | 原估计 | 修正后 | 说明 |
|------|--------|--------|------|
| 客户信息 | 81% | **85%** | 经纬度/送货地址在crm.lead |
| 供应商管理 | 67% | **95%** | erp_partner.py字段完整 |
| 司机列表 | 91% | **91%** | 无变化 |
| 车辆列表 | 94% | **88%** | 缺年审/保险到期 |
| 商品列表 | 92% | **94%** | 多单位体系完整 |
| 采购订单 | 85% | **80%** | 缺结算/审核状态 |
| 采购入库单 | 71% | **71%** | 缺单价/金额 |
| 销售订单 | 64% | **78%** | 收款/配送字段完整 |
| 销售出库单 | 45% | **55%** | 缺结算字段 |
| 销售退货单 | 16% | **70%** | 主表完整，缺明细行 |
| 入库任务 | 90% | **95%** | WMS任务完整 |
| 上架任务 | 90% | **90%** | |
| 出库任务 | 95% | **95%** | |
| 采购退货 | 0% | **0%** | 完全缺失 |
| 智能补货 | 0% | **0%** | 完全缺失 |
| 报表 | 22% | **22%** | 几乎全缺 |

---

## 8. 建议优先级

### P0（必须补充）
1. **采购退货单** — 新建 `erp.purchase.return` + 明细行
2. **销售退货明细行** — 扩展现有 `erp.sale.return`，添加 `line_ids`
3. **销售出库单结算字段** — 扩展 `wms.shipment`

### P1（建议补充）
4. **采购入库单财务字段** — 扩展 `wms.receipt.line` 添加单价/金额
5. **车辆年审/保险字段** — 扩展 `erp.vehicle`
6. **销售订单业务员** — 复用 `user_id`

### P2（可选补充）
7. **智能补货模块** — 新建
8. **采购/销售报表** — 基于Odoo报表引擎
9. **客户配送设备字段** — 扩展 `erp.customer`

---

*对比完成于 2026-05-27*
