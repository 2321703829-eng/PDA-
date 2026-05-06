# 2026-05-06 mini 非安全治理联调服部署与回归

## 范围

基于 `feat-text` 提交：

- `ba4cc1b96711`
- `fix(logistics): harden mini idempotency and legacy fallback`

将本地已完成的非安全治理同步到联调服，并做真实回归：

- `/api/mini/logistics/evidences` 强幂等
- `/api/mini/logistics/evidences/<id>/images` 强去重 / 幂等
- batch `CURRENT` 判定优化
- legacy 缺图状态收口

## 联调服部署

- 服务器：`192.168.0.17`
- 容器：`odoo-lite-test-v19-web`
- 数据库：`odoo_logistics_webtest_v19`

已同步文件：
- `custom_addons/logistics_web/controllers/logistics_web_mini_trace.py`
- `custom_addons/logistics_web/controllers/logistics_web_mini_waybill.py`
- `custom_addons/logistics_trace_evidence/models/logistics_trace_evidence.py`
- `custom_addons/logistics_trace_evidence/hooks.py`

已升级模块：
- `logistics_trace_evidence`
- `logistics_web`

已重启容器：
- `odoo-lite-test-v19-web`

## 真实回归结果

### 1. `/evidences` 重复请求只保留 1 条

回归请求：
- `POST /api/mini/logistics/traces`
- 之后两次：
  - `POST /api/mini/logistics/evidences`
  - 相同 `trace_event_id + request_id`

结果：
- `trace_event_id = 99`
- 第一次 `evidence_id = 181`
- 第二次 `evidence_id = 181`
- 验证通过：重复请求复用同一 evidence

### 2. `/images` 重复上传只保留 1 张

回归请求：
- 同一 `evidence_id = 181`
- 连续两次上传同一张 `tiny.png`

结果：
- 第一次：
  - `image_id = 214`
  - `deduplicated = false`
- 第二次：
  - `image_id = 214`
  - `deduplicated = true`

验证通过：重复上传复用同一 image

### 3. batch `CURRENT` 判定

回归请求：
- `GET /api/mini/logistics/waybills/PC202604290005/stops`

结果：
- 返回 `200`
- 当前批次共 `11` 个 `stops`
- 当前返回中：
  - `CURRENT = 0`
  - `ARRIVED = 11`

说明：
- 新逻辑已生效，但当前样本批次中的运单事实状态全部落在 `ARRIVED`
- 因此本轮无法从该样本观察到 `CURRENT` 的页面效果差异
- 需要后续补一个混合状态批次样本再做二次回归

补充回归（人工构造最小混合状态样本）：
- 目标批次：`PC202604020010`
- 目标运单：
  - `YD2026040200126` -> 通过 `POST /api/mini/logistics/traces` 写入 `leave/departed`
  - `YD2026040200127` -> 保持 `PENDING`

补充回归结果：
- 对 `YD2026040200126` 写入 `trace_event_id = 100`
- 再查询：
  - `GET /api/mini/logistics/waybills/PC202604020010/stops`
- 返回：
  - `LEAVED`：`YD2026040200126`（`stop_seq = 1`）
  - `CURRENT`：`YD2026040200127`（`stop_seq = 2`）

结论：
- `CURRENT` 不再错误落在“第一条已离开站点”
- 新逻辑会优先把后续 `PENDING` 站点选为当前站点
- `CURRENT` 判定本轮已完成有效验证

### 4. legacy 缺图记录是否伪装成可展示图片

检查结果：
- 当前联调库中 `state = 'missing'` 的 evidence：`0` 条
- 但仍存在 `8` 条：
  - 无 `image_ids`
  - 保留 legacy `image_access_key`
  - `state = available`
  - `image_count = 1`

说明：
- 这 `8` 条不是“缺图后仍装作有图”的 `missing` 记录
- 而是“legacy-only 且当前仍可读”的历史记录
- 它们没有被迁移到图片子表，但当前仍会走 legacy 回退展示

## 当前结论

本轮 4 项中：

- `/evidences` 幂等：**通过**
- `/images` 去重 / 幂等：**通过**
- batch `CURRENT` 逻辑：**代码已生效，但样本不足以验证差异**
- legacy 缺图伪装：**未发现 `missing` 伪装问题，但发现 8 条 legacy-only 可读残留记录**

## 后续建议

1. 补一组混合状态批次样本，继续验证 `CURRENT`
2. 针对这 8 条 legacy-only 记录，后续决定：
   - 是否补迁移进 `logistics.trace.evidence.image`
   - 或继续容忍 legacy 回退长期存在
