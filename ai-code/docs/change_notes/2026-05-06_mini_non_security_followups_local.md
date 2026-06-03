# 2026-05-06 mini 非安全治理补充（本地）

## 本次目标

在不启用额外安全能力的前提下，继续收口 mini 上传与批次查询链中的非安全问题：

- 强化 `/api/mini/logistics/evidences` 的幂等
- 强化 `/api/mini/logistics/evidences/<id>/images` 的去重/幂等
- 优化批次 `stops` 查询中的 `CURRENT` 判定
- 收口 legacy 缺图记录对正式展示的干扰

## 本次修改

### 1. `/evidences` 幂等强化

文件：
- `custom_addons/logistics_web/controllers/logistics_web_mini_trace.py`
- `custom_addons/logistics_trace_evidence/models/logistics_trace_evidence.py`

处理：
- 新增数据库级唯一约束：`unique(trace_event_id, client_request_id)`
- controller 在创建 evidence 时增加 `savepoint + IntegrityError` 回收逻辑
- 并发重复创建时优先复用已落库 evidence

结果：
- 现有“应用层幂等”提升为“应用层 + 数据库级”双保险

### 2. `/images` 去重 / 幂等强化

文件：
- `custom_addons/logistics_web/controllers/logistics_web_mini_trace.py`
- `custom_addons/logistics_trace_evidence/models/logistics_trace_evidence.py`

处理：
- 新增数据库级唯一约束：`unique(evidence_id, content_sha256)`
- 上传图片时增加 `savepoint + IntegrityError` 回收逻辑
- 并发或重试场景下复用已有图片记录

结果：
- 现有“基于哈希的应用层去重”提升为“应用层 + 数据库级”双保险

### 3. 批次 CURRENT 判定优化

文件：
- `custom_addons/logistics_web/controllers/logistics_web_mini_waybill.py`

处理：
- `_pick_current_waybill_id()` 不再简单取“第一条未完成记录”
- 现改为按优先级选择：
  - `ARRIVED`
  - `PENDING`
  - `LEAVED`

结果：
- 当前站点判定更贴近司机现场语义

### 4. legacy 缺图状态收口

文件：
- `custom_addons/logistics_trace_evidence/models/logistics_trace_evidence.py`
- `custom_addons/logistics_trace_evidence/hooks.py`

处理：
- 新增 `_refresh_legacy_fallback_state()`
- 对仍依赖 legacy 字段、但无法读到真实图片文件的 evidence 标为 `state = missing`
- `image_count` 与 `image_items_json` 在 `state = missing` 时不再把 legacy 壳当作可展示图片
- `post_init_hook()` 在迁移 legacy 图片到子表后，额外刷新一次 fallback 状态

结果：
- 历史缺图记录不再伪装成“仍有图片可展示”的 evidence

## 校验

- `logistics_web_mini_trace.py`：源码 `compile(...)` 通过
- `logistics_web_mini_waybill.py`：源码 `compile(...)` 通过
- `logistics_trace_evidence.py`：源码 `compile(...)` 通过
- `hooks.py`：源码 `compile(...)` 通过

## 工作区整理

- 已尝试清理 `D:\Desktop\ai-code\_tmp_feat_text_push` 下的 `__pycache__`
- 但 `ai-code/.safety_backups/...` 里的部分历史缓存文件存在权限拒绝，未在本轮强删
- 不影响本次代码修改与静态校验

## 边界说明

- 本轮未启用 mini token 安全开关
- 本轮未做司机级 / 运单级细粒度权限控制
- 本轮未推送到联调服，仅为本地 worktree 改动
