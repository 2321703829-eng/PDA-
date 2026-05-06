# 2026-05-06 mini 证据幂等与图片去重部署回归

## 背景

本地已完成两项 mini 上传链增强：

- `/api/mini/logistics/evidences` 幂等复用
- `/api/mini/logistics/evidences/<id>/images` 去重 / 幂等

本次将这批改动推送到 GitHub `feat-text` 分支，并同步到联调服做真实回归。

## GitHub

- 分支：`feat-text`
- 提交：`f9499da03f74`
- 提交信息：`feat(logistics): sync mini trace hardening and integration updates`

## 联调服部署

联调环境：

- 主机：`192.168.0.17`
- 容器：`odoo-lite-test-v19-web`
- 数据库：`odoo_logistics_webtest_v19`
- Addons 目录：`/opt/odoo-lite-test-v19/extra-addons`

部署动作：

1. 将 `feat-text` 工作树中的以下 addons 递归同步到联调服：
   - `logistics_dispatch`
   - `logistics_trace_evidence`
   - `logistics_trace_exception`
   - `logistics_web`
2. 在容器内升级模块：
   - `logistics_dispatch`
   - `logistics_trace_evidence`
   - `logistics_trace_exception`
   - `logistics_web`
3. 清理旧 `/web/assets/%`
4. 重启 `odoo-lite-test-v19-web`

## 真实回归

### mini 主链

- `POST /api/mini/logistics/traces`：`200`
- `POST /api/mini/logistics/evidences`：`200`
- `POST /api/mini/logistics/evidences/<id>/images`：`200`
- 图片预览：`200`

### `/evidences` 幂等

回归样本：

- `trace_event_id = 98`
- `request_id = codex-idemp-d2ef97d25612`

两次调用 `/api/mini/logistics/evidences` 返回：

- 第一次：`evidence_id = 180`
- 第二次：`evidence_id = 180`

结论：

- 同一 `trace_event_id + request_id` 已实现幂等复用

### `/images` 去重 / 幂等

回归样本：

- `evidence_id = 180`
- 同一张 1x1 PNG 连续上传两次

两次调用 `/api/mini/logistics/evidences/180/images` 返回：

- 第一次：`image_id = 213`，`deduplicated = false`
- 第二次：`image_id = 213`，`deduplicated = true`

结论：

- 同一 `evidence` 下的相同图片已实现去重复用

### 图片回显

- `image_access_key = img_8c741d770ae8aa96c3ecbec99d8b532e`
- 预览地址：
  - `http://8.166.131.218:7084/logistics_trace/evidence-images/img_8c741d770ae8aa96c3ecbec99d8b532e`
- 响应：
  - `200`
  - `Content-Type = image/png`

## 结论

本次推送与联调服部署后，mini 相关主链当前确认可用：

- `/traces` 只创建 `trace_event`
- `/evidences` 支持幂等复用
- `/images` 支持图片去重
- 图片预览链继续可用

