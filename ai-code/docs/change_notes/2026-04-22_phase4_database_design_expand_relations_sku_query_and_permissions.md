# 2026-04-22 phase4 database design expand relations sku query and permissions

## 本次调整

在《四期数据库底表设计稿 v1（第二次修正版）》中继续补充了以下内容：

- 更明确的数据关系图
- `logistics_product_unit` 扩充为更完整的规格/SKU层
- 页面/接口/报表查询模型清单
- 一致性规则向可执行约束推进
- 敏感字段与权限边界
- 导入/变更/回滚/排障相关日志对象补充

## 主要新增点

### 数据关系图

- 明确了：
  - `res.partner -> logistics_store_profile`
  - `product.template -> logistics_product_unit`
  - `hr.employee -> logistics_driver_profile`
  - `wave -> batch -> waybill -> customer_line -> order_line -> goods_line`
  - `batch -> driver / vehicle`

### SKU层扩展

`logistics_product_unit` 新增/扩展承接：

- 全级分类
- 多单位标准价/采购价/建议零售价
- 多单位条码
- 销售单位
- 税率
- 长宽高
- 体积/毛重单位
- 大单位数量
- 小/中单位毛重与体积
- 默认供应商
- 采购员
- 起订量
- 品牌方名称
- 是否可以压货
- 备注

### 查询模型

- 补充了：
  - 页面查询模型
  - 接口查询模型
  - 报表查询模型
- 明确首轮阅读主链继续以快照层为主

### 可执行约束

- 补充了订单键、门店节点键、编码串字段、司机来源等可执行约束建议

### 权限边界

- 补充了敏感字段分级
- 默认角色可见范围
- 导出权限建议

### 日志对象

- 在原有导入日志基础上新增建议：
  - `import_source_file`
  - `mapping_snapshot`
  - `data_fix_log`
  - `migration_log`

## 目的

让数据库底表设计稿进一步从“结构稿”升级为“可支撑实现、查询、权限和运维的后端设计底稿”。
