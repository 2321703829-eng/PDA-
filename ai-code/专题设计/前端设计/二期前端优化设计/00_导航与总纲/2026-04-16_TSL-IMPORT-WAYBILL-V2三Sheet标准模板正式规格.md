# 2026-04-16 TSL-IMPORT-WAYBILL-V2 三 Sheet 标准模板正式规格

## 文档定位

- 本文件用于把二期导入链路的下一阶段主方案正式收口为规格文档
- 本文件对应“本期优先推进”的标准模板升级方向
- 本文件中的模板结构、Sheet 关系、跨 Sheet 预校验规则，作为后续实现的正式口径

## 开发优先级说明

当前标注为：

- `本期已落地`

说明：

- 当前单表 CSV 标准模板方案已完成第一轮能力铺底
- 本期已经把标准模板升级为单一 `xlsx` 多 Sheet 结构
- 客户与货品固定需求拆分等方向，暂不属于本文件主目标

---

## 当前落地状态

截至 `2026-04-16`，本规格对应的第一轮开发已完成落地，当前生效口径如下：

- 标准模板主版本已切换为 `TSL-IMPORT-WAYBILL-V2.xlsx`
- 模板下载已支持：
  - `TSL-IMPORT-WAYBILL-V2.xlsx`
  - `TSL-IMPORT-WAYBILL-V2.zh_CN.xlsx`
- 当前标准模板固定包含 3 个业务 Sheet：
  - `运单`
  - `客户明细`
  - `货物明细`
- 当前标准导入接口已支持：
  - 模板元信息
  - 模板下载
  - 跨 Sheet 预校验
  - 正式导入
  - 导入结果查询
  - 预校验错误报告导出
- 当前运单、客户明细、货物明细页面的模板下载入口，均已统一为 V2 标准模板，不再展示旧模板按钮

当前实现说明：

- 后端已按本规格落地第一轮可用版本
- 当前执行对象仍以 `waybill` 为主对象，按 `运单 -> 客户明细 -> 货物明细` 顺序导入
- 当前错误报告导出格式仍为 `CSV`，用于承接预校验错误明细下载
- 当前 `V1 CSV` 仍保留兼容文件与历史代码，但已不再作为界面主入口

---

## Objective

把当前标准导入模板从单表 `CSV` 升级为一份多 Sheet 的 `XLSX` 标准模板：

- 文件名统一
- 三层对象分表表达
- 通过跨 Sheet 预校验完成整单导入

目标是同时解决下面 4 个问题：

1. 运单、客户明细、货物明细层次在模板中表达不清
2. 客户明细页、货物明细页共享同一张单表模板时业务语义不直观
3. 三层结构缺少更自然的表格表达方式
4. 后续跨层校验规则难以继续扩展

---

## Outcome

正式模板统一为：

- `TSL-IMPORT-WAYBILL-V2.xlsx`

模板内固定包含 3 个业务 Sheet：

1. `运单`
2. `客户明细`
3. `货物明细`

后续标准导入主路径调整为：

1. 下载 `TSL-IMPORT-WAYBILL-V2.xlsx`
2. 按 3 个 Sheet 填写数据
3. 上传模板文件
4. 执行跨 Sheet 预校验
5. 预校验通过后执行正式导入
6. 统一查看导入结果与错误报告

---

## 模板文件名

## 1. 当前正式文件名

- `TSL-IMPORT-WAYBILL-V2.xlsx`

## 2. 命名解释

- `TSL`：天枢物流
- `IMPORT`：导入模板
- `WAYBILL`：运单主对象
- `V2`：相对当前单表 `CSV` 标准模板的升级版

## 3. 版本策略

- `V1`：单表 `CSV` 方案，进入兼容过渡期
- `V2`：三 Sheet `XLSX` 正式方案
- 后续如果仅字段增量、不改结构，可在文档层使用 `V2.x`
- 如果 Sheet 结构或关联规则变化，再升 `V3`

---

## Sheet 清单

固定 3 个业务 Sheet：

1. `运单`
2. `客户明细`
3. `货物明细`

当前不强制要求说明 Sheet。

如果后续需要增强模板可用性，可追加：

- `填写说明`

但该 Sheet 不纳入导入解析范围。

---

## 3 个 Sheet 的字段清单

## 1. Sheet1：运单

作用：

- 定义运单主记录
- 作为整份导入模板的主表

建议字段清单：

| 字段编码 | 中文名称 | 必填 | 说明 |
|---|---|---:|---|
| `waybill_no` | 运单号 | 是 | 运单主键 |
| `batch_no` | 批次号 | 否 | 如填写则校验系统批次 |
| `wave_no` | 波次号 | 否 | 如填写则校验系统波次 |
| `delivery_date` | 配送日期 | 否 | `YYYY-MM-DD` |
| `warehouse_code` | 仓库编码 | 否 | 预留仓侧扩展 |
| `vehicle_no` | 车辆号 | 否 | 预留车队扩展 |
| `driver_name` | 司机姓名 | 否 | 预留司机扩展 |
| `driver_phone` | 司机电话 | 否 | 预留司机扩展 |
| `remark` | 运单备注 | 否 | 运单层备注 |

## 2. Sheet2：客户明细

作用：

- 定义某运单下的客户 / 门店层记录

建议字段清单：

| 字段编码 | 中文名称 | 必填 | 说明 |
|---|---|---:|---|
| `waybill_no` | 运单号 | 是 | 关联 `运单` Sheet |
| `customer_no` | 客户编号 | 是 | 客户主键 |
| `customer_name` | 客户名称 | 否 | 如填写则做一致性校验 |
| `store_no` | 门店编号 | 否 | 门店标识 |
| `store_name` | 门店名称 | 否 | 如填写则做一致性校验 |
| `delivery_remark` | 客户配送备注 | 否 | 客户层备注 |
| `signoff_requirement` | 签收要求 | 否 | 客户层要求 |
| `customer_ref` | 客户外部参考号 | 否 | 预留客户侧扩展 |

客户层建议业务唯一键：

- `waybill_no + customer_no + store_no`

如果 `store_no` 为空，则退化为：

- `waybill_no + customer_no`

## 3. Sheet3：货物明细

作用：

- 定义某运单下某客户 / 门店层的货物行

建议字段清单：

| 字段编码 | 中文名称 | 必填 | 说明 |
|---|---|---:|---|
| `waybill_no` | 运单号 | 是 | 关联 `运单` |
| `customer_no` | 客户编号 | 是 | 关联 `客户明细` |
| `store_no` | 门店编号 | 否 | 建议填写，便于精确挂接 |
| `goods_code` | 货物编码 | 否 | 货物标识 |
| `goods_name` | 货物名称 | 是 | 当前必填 |
| `spec` | 规格 | 否 | 规格说明 |
| `qty` | 数量 | 是 | 必须大于 `0` |
| `package_count` | 件数 | 否 | 非负整数 |
| `uom_name` | 单位 | 否 | 如 `箱 / 件` |
| `weight` | 重量 | 否 | 非负数 |
| `volume` | 体积 | 否 | 非负数 |
| `temperature_zone` | 温层 | 否 | 枚举值 |
| `package_type` | 包装类型 | 否 | 包装说明 |
| `remark` | 货物备注 | 否 | 行级备注 |

货物层建议去重口径：

- 优先：`waybill_no + customer_no + store_no + goods_code + goods_name`
- 如果 `goods_code` 为空，则参考：`waybill_no + customer_no + store_no + goods_name + spec`

---

## 三层之间的关联规则

## 1. 主从关系

- `运单` 是主表
- `客户明细` 必须挂在某个 `运单` 下
- `货物明细` 必须挂在某个 `客户明细` 下

## 2. 关联键规则

### 2.1 客户明细 -> 运单

- 使用 `waybill_no` 关联
- `客户明细` Sheet 中出现的 `waybill_no`，必须在 `运单` Sheet 中存在

### 2.2 货物明细 -> 客户明细

- 优先使用 `waybill_no + customer_no + store_no` 关联
- 如果 `store_no` 为空，则退化为 `waybill_no + customer_no`
- `货物明细` Sheet 中出现的这组键，必须能在 `客户明细` Sheet 中找到对应记录

## 3. 一致性规则

### 3.1 运单层一致性

- 同一个 `waybill_no` 在 `运单` Sheet 中只能出现一次

### 3.2 客户层一致性

- 同一个 `waybill_no + customer_no + store_no` 在 `客户明细` Sheet 中只能出现一次
- 若重复出现，视为模板错误，不做自动合并

### 3.3 货物层一致性

- 同一客户层下允许存在多条货物行
- 不允许出现完全重复且没有业务意义的重复货物行

---

## 预校验规则怎么跨 Sheet 做

统一分为 4 层：

## 1. 模板结构级校验

校验内容：

- 文件必须为 `.xlsx`
- 必须存在 `运单 / 客户明细 / 货物明细` 三个 Sheet
- Sheet 名必须完全匹配
- 各 Sheet 列头必须匹配当前模板版本
- 不允许缺少核心字段

建议错误码：

- `TEMPLATE_FILE_TYPE_INVALID`
- `TEMPLATE_SHEET_MISSING`
- `TEMPLATE_HEADER_MISMATCH`
- `TEMPLATE_VERSION_INVALID`

## 2. 单 Sheet 字段级校验

### 2.1 运单 Sheet

- `waybill_no` 必填
- `delivery_date` 格式必须为 `YYYY-MM-DD`
- `batch_no` 如填写则必须存在
- `wave_no` 如填写则必须存在
- `batch_no` 与 `wave_no` 如同时填写则必须匹配

### 2.2 客户明细 Sheet

- `waybill_no` 必填
- `customer_no` 必填
- `customer_no` 必须存在
- `store_no` 如填写则必须存在
- `customer_name` 如填写需与主数据一致
- `store_name` 如填写需与主数据一致
- `store_no` 与 `customer_no` 归属必须一致

### 2.3 货物明细 Sheet

- `waybill_no` 必填
- `customer_no` 必填
- `goods_name` 必填
- `qty > 0`
- `package_count >= 0`
- `weight >= 0`
- `volume >= 0`
- `temperature_zone` 必须在允许枚举内

## 3. 跨 Sheet 关联校验

### 3.1 客户明细 -> 运单

- `客户明细` 中的 `waybill_no` 必须在 `运单` Sheet 中存在

建议错误码：

- `WAYBILL_NOT_FOUND_IN_WAYBILL_SHEET`

### 3.2 货物明细 -> 客户明细

- `货物明细` 中的 `waybill_no + customer_no + store_no` 必须能在 `客户明细` 中匹配到
- 若 `store_no` 为空，则按 `waybill_no + customer_no` 匹配

建议错误码：

- `CUSTOMER_LINE_NOT_FOUND_IN_CUSTOMER_SHEET`

### 3.3 货物明细 -> 运单

- `货物明细` 中的 `waybill_no` 也必须在 `运单` Sheet 中存在

建议错误码：

- `WAYBILL_NOT_FOUND_IN_WAYBILL_SHEET`

## 4. 跨层一致性校验

建议继续增加：

- `客户明细` 不允许引用不存在的运单
- `货物明细` 不允许脱离客户层独立存在
- 同一 `waybill_no` 下的运单层关键字段不允许冲突
- 后续若在下层 Sheet 扩展上层冗余字段，则必须与上层保持一致

---

## 正式导入执行顺序

正式导入时固定顺序为：

1. 先导入 `运单`
2. 再导入 `客户明细`
3. 最后导入 `货物明细`

统一原则：

- 预校验不通过，不允许正式导入
- 任一层失败，整批不落库
- 整批导入统一返回一个 `import_batch_no`

---

## 与当前方案的关系

当前应统一承认两个阶段：

### 1. 当前已落地阶段

- `TSL-IMPORT-WAYBILL-V1.csv`
- 单表 `CSV`
- 已完成模板下载、预校验、正式导入、结果查询、错误报告导出第一轮闭环

### 2. 当前准备升级阶段

- `TSL-IMPORT-WAYBILL-V2.xlsx`
- 三 Sheet `XLSX`
- 作为本期后续优先推进的升级目标

---

## Boundary

本文件当前不直接覆盖：

1. `V2.xlsx` 的实际代码实现
2. `xlsx` 解析库选型
3. 前端页面按钮布局细节
4. 客户与货品固定需求拆分设计

---

## Next Suggestion

按照当前优先级，后续建议按下面顺序推进：

1. 先补 `V2.xlsx` 模板文件样例
2. 再补 `xlsx` 多 Sheet 预校验接口设计
3. 再补正式导入执行与结果页适配
