# 2026-05-06 mini evidence 幂等与 image 去重本地落地

## 本次处理

本地代码已完成以下两项：

1. `/api/mini/logistics/evidences` 幂等
2. `/api/mini/logistics/evidences/<id>/images` 去重 / 幂等

当前仅落地在本地代码，**尚未同步到联调服务器**。

## 具体改动

### 1. `/evidences` 幂等

在 `logistics.trace.evidence` 增加字段：

- `client_request_id`

后端控制器改为优先按以下规则复用已有 evidence：

- `trace_event_id + client_request_id`

如果前端暂时没有显式传幂等键，则增加一个保守兜底：

- 同一 `trace_event`
- 同一 `remark`
- `image_count = 0`
- 且创建时间在 5 分钟窗口内

满足上述条件时，优先复用最近的一条 evidence，而不是再次新建。

### 2. `/images` 去重

在 `logistics.trace.evidence.image` 增加字段：

- `content_sha256`

上传时：

- 对上传文件内容计算 `sha256`
- 在同一 `evidence` 下查找是否已存在相同 `content_sha256`
- 若已存在，则直接复用已有图片记录
- 若不存在，才真正创建新 image

返回结果中增加：

- `deduplicated`

用于标记该图片是否是复用已有记录。

## 涉及文件

- `D:\Desktop\Odoo\custom_addons\logistics_web\controllers\logistics_web_mini_trace.py`
- `D:\Desktop\Odoo\custom_addons\logistics_trace_evidence\models\logistics_trace_evidence.py`

## 本地校验

已完成源码级编译校验：

- `logistics_web_mini_trace.py`
- `logistics_trace_evidence.py`

说明：

- `py_compile` 由于外部 `__pycache__` 写入权限会报拒绝访问
- 已改用 `compile(source, ..., 'exec')` 做源码级语法校验，结果通过

## 后续动作

要让这两项在联调服生效，后续还需要：

1. 同步代码到服务器
2. 升级相关模块：
   - `logistics_web`
   - `logistics_trace_evidence`
3. 做真实小程序链回归：
   - `/traces`
   - `/evidences`
   - `/evidences/<id>/images`

## 当前状态标记

- `/evidences` 幂等：**已完成（本地）**
- `/images` 去重 / 幂等：**已完成（本地）**
- 联调服部署：**未开始**
