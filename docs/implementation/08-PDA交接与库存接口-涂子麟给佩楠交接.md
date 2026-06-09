# PDA 交接接口 / 库存查询接口交接文档

交接人：涂子麟  
接收人：佩楠  
日期：2026-06-09  
分支：`feat_2606_pda_design`

## 一、开发范围

本次只改了 PDA 服务端模块：

```text
custom_addons/wms_pda_api/
```

没有改 `wms_task_core`、`tms_dispatch_core` 主流程。

新增/修改文件：

```text
custom_addons/wms_pda_api/controllers/handover.py
custom_addons/wms_pda_api/controllers/inventory.py
custom_addons/wms_pda_api/controllers/__init__.py
```

`__init__.py` 已注册：

```python
from . import handover
from . import inventory
```

## 二、统一调用要求

所有接口继续沿用现有 PDA API 规范：

```http
Authorization: Bearer <token>
```

统一返回格式：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

有语音提示时返回：

```json
{
  "tts": "操作成功"
}
```

所有业务查询都限制在当前 token 绑定仓库。

## 三、交接接口

文件：

```text
custom_addons/wms_pda_api/controllers/handover.py
```

### 1. 查询待交接单

```http
GET /api/pda/wms/v1/handover/orders?offset=0&limit=20
```

默认只查当前仓库下：

```text
waiting_handover
handover_ing
```

也支持传指定状态：

```http
GET /api/pda/wms/v1/handover/orders?state=waiting_handover
```

返回核心字段包括：

```text
交接单号、状态、仓库、出库任务号、门店/客户、复核任务号、拣货任务号、
关联运单、关联排线批次、司机档案、车辆档案、总重量、总体积、备注
```

### 2. 查看交接单详情

```http
GET /api/pda/wms/v1/handover/orders/<order_id>
```

打开详情时会调用：

```python
request.env["wms.task.lock"].sudo().acquire(...)
```

返回里带：

```json
{
  "locked_by": "锁定人"
}
```

### 3. 确认交接

```http
POST /api/pda/wms/v1/handover/orders/<order_id>/confirm
```

逻辑：

- 如果状态是 `waiting_handover`，调用 `handover.action_start_handover()`
- 如果已是 `handover_ing`，保持当前状态并返回成功
- 如果已完成或状态不允许，会返回状态冲突错误

成功语音：

```text
开始交接
```

### 4. 完成交接

```http
POST /api/pda/wms/v1/handover/orders/<order_id>/complete
```

逻辑：

- 调用 `handover.action_mark_done()`
- 完成后释放任务锁：

```python
request.env["wms.task.lock"].sudo().release(...)
```

成功语音：

```text
交接完成
```

### 5. 衔接排线批次

```http
POST /api/pda/wms/v1/handover/orders/<order_id>/prepare-route-batch
```

当前主流程模型 `wms.handover.order` 暂时没有：

```python
action_prepare_route_batch()
```

所以这里没有 mock 数据，按任务要求返回明确错误：

```text
当前交接单暂未接入排线批次生成动作。
```

后续如果主流程补上 `action_prepare_route_batch()`，这个接口会直接调用该动作。

## 四、库存查询接口

文件：

```text
custom_addons/wms_pda_api/controllers/inventory.py
```

库存查询使用：

```text
wms.inventory.ledger
```

原因：该模型已经按仓库、库位、商品聚合了：

```text
现存数量 quantity_on_hand
预留数量 reserved_quantity
可用数量 available_quantity
```

### 1. 商品扫码查库存

```http
GET /api/pda/wms/v1/inventory/product?barcode=6901209257452
GET /api/pda/wms/v1/inventory/product?default_code=SP001
```

兼容旧契约路径：

```http
GET /api/pda/wms/v1/inventory/by-product?barcode=6901209257452
```

逻辑：

- 用 `barcode` 或 `default_code` 查 `product.product`
- 只返回当前 token 仓库下该商品库存
- 返回商品汇总和库位明细

### 2. 库位扫码查库存

```http
GET /api/pda/wms/v1/inventory/location?location_barcode=LOC-A0102
```

兼容旧契约路径：

```http
GET /api/pda/wms/v1/inventory/by-location?barcode=LOC-A0102
```

逻辑：

- 用 `location_barcode` 或 `barcode` 查 `stock.location`
- 库位必须属于当前 token 仓库范围
- 返回该库位下所有商品库存

### 3. 仓库库存列表/搜索

```http
POST /api/pda/wms/v1/inventory/search
Content-Type: application/json

{
  "keyword": "牛奶",
  "offset": 0,
  "limit": 20
}
```

支持关键词字段：

```text
商品名称、商品编码、商品条码、库位名称、库位条码
```

支持分页：

```text
offset / limit
```

返回字段包括：

```text
product_id
product_name
default_code
barcode
location_id
location_name
location_barcode
quantity_on_hand
reserved_quantity
available_quantity
uom
warehouse_id
warehouse_name
```

## 五、联调注意点

1. PDA 前端调这些接口前，必须先登录并切仓，保证 token 上有 `warehouse_id`。
2. 交接详情、确认、完成都会使用任务锁；如果另一个人已锁定，会返回现有锁模型的错误提示。
3. 库存接口没有写库存，只读 `wms.inventory.ledger`。
4. `prepare-route-batch` 当前会报“暂未接入”，这是符合任务要求的已知状态，不是接口报错。
5. 如果后续要让交接完成后直接生成派车单，可优先看现有 `action_create_dispatch_order()`，但本次没有在 PDA 接口里自动调用，避免改动主流程。

## 六、已执行检查

```bash
python -B -c "import ast, pathlib; base=pathlib.Path('custom_addons/wms_pda_api'); [ast.parse(p.read_text(encoding='utf-8')) for p in base.rglob('*.py')]; print('python ast ok')"
```

结果：

```text
python ast ok
```

```bash
python -B -c "import pathlib, xml.etree.ElementTree as ET; base=pathlib.Path('custom_addons/wms_pda_api'); [ET.parse(p) for p in base.rglob('*.xml')]; print('xml ok')"
```

结果：

```text
xml ok
```

## 七、建议佩楠联调顺序

1. 用 PDA 登录接口拿 token。
2. 切到有交接单和库存数据的仓库。
3. 先调库存商品查询，确认 `wms.inventory.ledger` 有数据。
4. 再调库存库位查询，确认库位仓库范围校验正常。
5. 调交接列表，确认只出现当前仓库待交接/交接中的单。
6. 打开交接详情，确认锁定字段和关联任务字段正常。
7. 调确认交接，把 `waiting_handover` 推到 `handover_ing`。
8. 调完成交接，把交接单推到 `handover_done`，并确认锁释放。
