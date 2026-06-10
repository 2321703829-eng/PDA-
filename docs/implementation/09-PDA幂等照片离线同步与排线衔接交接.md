# PDA 幂等、照片、离线同步与排线衔接交接

## 本次补充范围

本次完成 `任务.md` 中第 4、5、6、7 项：

- PDA 写接口支持 `request_id` 幂等日志。
- 新增照片 URL 上传/绑定/查询接口。
- 新增离线动作批量同步接口。
- 补齐 `wms.handover.order.action_prepare_route_batch()`，交接完成后可生成/复用排线批次和停靠点。

## 1. request_id 幂等规则

已接入的 PDA POST 写接口：

- 收货：`confirm-line`、`complete`
- 上架：`confirm`、`complete`
- 拣货：`confirm-line`、`complete`
- 复核：`confirm-line`、`complete`
- 交接：`confirm`、`complete`、`prepare-route-batch`
- 退库：`return/create`、`return/{id}/add-line`、`return/{id}/confirm`
- 销退入库：`sale-return/tasks/{id}/confirm-line`、`complete`
- 照片：`photos/upload`、`photos/bind`
- 离线同步：`offline/sync`

请求体可选传：

```json
{
  "request_id": "PDA-20260610-0001",
  "device_id": "PDA-01"
}
```

处理规则：

- 第一次请求会写入 `wms.pda.request.log`。
- 同一个 `request_id + endpoint + method + payload` 再次提交时，直接返回第一次成功响应。
- 同一个 `request_id` 被不同 endpoint、method 或 payload 使用，返回 409。
- 失败请求记录为 `failed`，允许同 payload 再次重试。

后台菜单：

- `PDA Warehouse / PDA Request Logs`
- `PDA Warehouse / PDA Offline Sync Logs`

## 2. 照片接口

第一阶段只做 URL 绑定，不直接接对象存储二进制上传。

### POST `/api/pda/wms/v1/photos/upload`

如果只传 URL，会返回 accepted；如果同时传任务信息，会直接绑定。

```json
{
  "request_id": "PHOTO-UP-001",
  "device_id": "PDA-01",
  "photo_url": "https://oss.example.com/pda/a.jpg"
}
```

### POST `/api/pda/wms/v1/photos/bind`

```json
{
  "request_id": "PHOTO-BIND-001",
  "device_id": "PDA-01",
  "task_model": "wms.pick.task",
  "task_id": 12,
  "photo_urls": [
    "https://oss.example.com/pda/a.jpg",
    "https://oss.example.com/pda/b.jpg"
  ],
  "gps": "120.123,30.456",
  "note": "拣货完成照片"
}
```

支持绑定模型：

- `wms.receipt.task`
- `wms.putaway.task`
- `wms.outbound.task`
- `wms.pick.task`
- `wms.check.task`
- `wms.handover.order`
- `wms.inventory.operation`

### GET `/api/pda/wms/v1/photos?task_model=wms.pick.task&task_id=12`

返回该任务已绑定照片列表。

## 3. 离线同步接口

### POST `/api/pda/wms/v1/offline/sync`

每条离线动作必须有自己的 `request_id`。某一条失败不会影响整批返回。

```json
{
  "sync_id": "SYNC-PDA-01-20260610-001",
  "request_id": "SYNC-REQ-001",
  "device_id": "PDA-01",
  "requests": [
    {
      "request_id": "OFF-PICK-001",
      "method": "POST",
      "endpoint": "/api/pda/wms/v1/pick/tasks/12/confirm-line",
      "payload": {
        "line_id": 1001,
        "done_qty": 3,
        "barcode": "690000000001"
      }
    },
    {
      "request_id": "OFF-PHOTO-001",
      "method": "POST",
      "endpoint": "/api/pda/wms/v1/photos/bind",
      "payload": {
        "task_model": "wms.pick.task",
        "task_id": 12,
        "photo_url": "https://oss.example.com/pda/a.jpg"
      }
    }
  ]
}
```

返回字段：

- `sync_id`
- `state`: `done` / `partial` / `failed`
- `request_count`
- `success_count`
- `failed_count`
- `results`

### GET `/api/pda/wms/v1/offline/sync/{sync_id}`

按 `sync_id` 查询历史同步结果。

## 4. 交接单生成排线批次

接口：

`POST /api/pda/wms/v1/handover/orders/{order_id}/prepare-route-batch`

前置条件：

- 交接单状态必须是 `handover_done`。
- 交接单必须有关联出库任务和 `stock.picking`。
- 门店/客户必须有地址和经纬度：`address_full`、`partner_longitude`、`partner_latitude`。

行为：

- 优先复用出库单已关联的 `logistics.dispatch.waybill`。
- 如果没有关联运单，会生成一张 `WMS-HO-{handover_id}` 运单，并创建对应订单明细。
- 创建或复用 `logistics.route.planning.batch`，批次号为 `PDA-HO-{handover_id}-{yyyyMMdd}`。
- 按运单生成 `logistics.route.planning.stop.line`。
- 将 `route_batch_id`、重量、体积回写到交接单。

响应中会直接返回：

- `route_batch_id`
- `route_batch_name`
- `waybill_ids`
- `stop_line_ids`
- `route_batch.stop_lines`

## 5. 上线提醒

代码涉及两个模块：

- `wms_pda_api`
- `tms_dispatch_core`

部署后需要升级模块，至少更新模型表、访问权限和视图：

```bash
odoo-bin -u wms_pda_api,tms_dispatch_core
```

