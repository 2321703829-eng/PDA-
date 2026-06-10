# PDA 幂等 / 照片 / 离线同步 / 排线衔接交接文档

交接人：涂子麟  
接收人：佩楠  
日期：2026-06-10  
分支：`feat_2606_pda_design`

## 一、开发范围

本次是基于你已经开发好的 PDA 退库、销退、PC 审核流程继续补充，主要完成任务文件里的第 4、5、6、7 项：

```text
4. request_id 幂等日志
5. 照片上传 / 绑定 / 查询接口
6. 离线同步接口
7. wms.handover.order.action_prepare_route_batch()
```

涉及模块：

```text
custom_addons/wms_pda_api/
custom_addons/tms_dispatch_core/
```

主要新增文件：

```text
custom_addons/wms_pda_api/controllers/photos.py
custom_addons/wms_pda_api/controllers/offline.py
custom_addons/wms_pda_api/models/wms_pda_request_log.py
custom_addons/wms_pda_api/models/wms_pda_offline_sync.py
docs/implementation/09-PDA幂等照片离线同步与排线衔接交接.md
```

主要修改文件：

```text
custom_addons/wms_pda_api/controllers/base.py
custom_addons/wms_pda_api/controllers/receipt.py
custom_addons/wms_pda_api/controllers/putaway.py
custom_addons/wms_pda_api/controllers/pick.py
custom_addons/wms_pda_api/controllers/check.py
custom_addons/wms_pda_api/controllers/handover.py
custom_addons/wms_pda_api/controllers/warehouse_return.py
custom_addons/wms_pda_api/controllers/sale_return.py
custom_addons/wms_pda_api/controllers/inventory.py
custom_addons/wms_pda_api/views/wms_pda_views.xml
custom_addons/wms_pda_api/security/ir.model.access.csv
custom_addons/tms_dispatch_core/models/wms_handover_order.py
```

## 二、request_id 幂等逻辑

现在 PDA 端写接口可以传：

```json
{
  "request_id": "PDA-20260610-0001",
  "device_id": "PDA-01"
}
```

逻辑在：

```text
custom_addons/wms_pda_api/controllers/base.py
```

新增方法：

```python
_handle_idempotent_request(...)
_run_idempotent(...)
```

处理规则：

1. 第一次请求会写入 `wms.pda.request.log`。
2. 同一个 `request_id + endpoint + method + payload` 重复提交，会直接返回第一次成功响应。
3. 同一个 `request_id` 被不同接口或不同 payload 使用，返回 409。
4. 失败请求会标记为 `failed`，允许同 payload 再次重试。

目前已接入幂等的接口：

```text
收货 confirm-line / complete
上架 confirm / complete
拣货 confirm-line / complete
复核 confirm-line / complete
交接 confirm / complete / prepare-route-batch
退库 create / add-line / confirm
销退入库 confirm-line / complete
照片 upload / bind
离线同步 offline/sync
```

后台菜单已加：

```text
PDA Warehouse / PDA Request Logs
PDA Warehouse / PDA Offline Sync Logs
```

## 三、照片接口

第一阶段没有直接接对象存储二进制上传，只做 URL 接收和任务绑定。

文件：

```text
custom_addons/wms_pda_api/controllers/photos.py
```

### 1. 上传 / 接收照片 URL

```http
POST /api/pda/wms/v1/photos/upload
```

只传 URL 时，不绑定任务，只返回 accepted：

```json
{
  "request_id": "PHOTO-UP-001",
  "device_id": "PDA-01",
  "photo_url": "https://oss.example.com/pda/a.jpg"
}
```

如果同时传了 `task_model` 和 `task_id`，会直接绑定。

### 2. 绑定照片到任务

```http
POST /api/pda/wms/v1/photos/bind
```

示例：

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

支持绑定的模型：

```text
wms.receipt.task
wms.putaway.task
wms.outbound.task
wms.pick.task
wms.check.task
wms.handover.order
wms.inventory.operation
```

### 3. 查询任务照片

```http
GET /api/pda/wms/v1/photos?task_model=wms.pick.task&task_id=12
```

返回该任务下所有 `wms.task.photo` 记录。

## 四、离线同步接口

文件：

```text
custom_addons/wms_pda_api/controllers/offline.py
```

接口：

```http
POST /api/pda/wms/v1/offline/sync
```

设计思路：

- PDA 离线期间把每个动作记录下来。
- 联网后按批次提交。
- 每个离线动作必须有自己的 `request_id`。
- 单条失败不会影响整批返回。
- 如果重复提交同一个 `sync_id`，直接返回历史同步结果。

请求示例：

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

```text
sync_id
state: done / partial / failed
request_count
success_count
failed_count
results
```

查询历史同步结果：

```http
GET /api/pda/wms/v1/offline/sync/<sync_id>
```

目前离线同步支持的 endpoint 是 PDA 端主要写接口，包括收货、上架、拣货、复核、交接、退库、销退入库、照片绑定。

## 五、交接单生成排线批次

文件：

```text
custom_addons/tms_dispatch_core/models/wms_handover_order.py
custom_addons/wms_pda_api/controllers/handover.py
```

这次补齐了：

```python
wms.handover.order.action_prepare_route_batch()
```

PDA 接口：

```http
POST /api/pda/wms/v1/handover/orders/<order_id>/prepare-route-batch
```

前置条件：

1. 交接单状态必须是 `handover_done`。
2. 交接单必须有关联出库任务。
3. 出库任务必须有关联 `stock.picking`。
4. 门店 / 客户必须有地址和经纬度：

```text
address_full
partner_longitude
partner_latitude
```

处理逻辑：

1. 优先找出库单已经关联的 `logistics.dispatch.waybill`。
2. 如果没有关联运单，则自动生成一张 `WMS-HO-{handover_id}` 运单。
3. 创建或复用排线批次：

```text
PDA-HO-{handover_id}-{yyyyMMdd}
```

4. 按运单生成 `logistics.route.planning.stop.line`。
5. 回写交接单：

```text
route_batch_id
weight_total
volume_total
```

PDA 返回里现在会直接带：

```text
route_batch_id
route_batch_name
waybill_ids
stop_line_ids
route_batch.stop_lines
```

## 六、佩楠联调建议顺序

1. 先升级模块：

```bash
odoo-bin -u wms_pda_api,tms_dispatch_core
```

2. 用 PDA 登录接口拿 token，并切到有任务数据的仓库。

3. 先测幂等：

```text
同一个 POST 接口，带同一个 request_id 连续请求两次。
预期：第二次直接返回第一次成功结果，不重复写业务数据。
```

4. 再测照片：

```text
先 photos/upload，再 photos/bind，最后 GET photos 查询。
```

5. 再测离线同步：

```text
构造一个 requests 批次，里面放一条拣货确认和一条照片绑定。
预期：返回 done 或 partial，并能在 PDA Offline Sync Logs 查到记录。
```

6. 最后测交接排线：

```text
先把交接单做到 handover_done，再调 prepare-route-batch。
```

如果这里报地址或经纬度缺失，需要先补门店 / 客户主数据。

## 七、已执行检查

Python 语法检查：

```bash
python -B -c "import ast,pathlib; bases=[pathlib.Path('custom_addons/wms_pda_api'), pathlib.Path('custom_addons/tms_dispatch_core')]; [ast.parse(p.read_text(encoding='utf-8'), filename=str(p)) for base in bases for p in base.rglob('*.py')]; print('python ast ok')"
```

结果：

```text
python ast ok
```

XML 解析检查：

```bash
python -B -c "import pathlib,xml.etree.ElementTree as ET; bases=[pathlib.Path('custom_addons/wms_pda_api'), pathlib.Path('custom_addons/tms_dispatch_core')]; [ET.parse(p) for base in bases for p in base.rglob('*.xml')]; print('xml ok')"
```

结果：

```text
xml ok
```

diff 检查：

```bash
git diff --check
```

结果：通过。

## 八、注意事项

1. `photos/upload` 当前只接收 URL，不负责真实文件上传。
2. 离线同步只支持白名单里的 PDA POST 动作，暂不支持任意 URL 转发。
3. `prepare-route-batch` 对门店地址和经纬度有硬校验，否则无法生成排线停靠点。
4. 这次没有改 PC 审核接口逻辑，只补 PDA 端和交接到排线的衔接。
5. 当前只做了静态检查，还没有连接真实 Odoo 数据库做端到端联调。

