# 2026-05-06 mini_trace_dedup_and_auth_local

## 本次本地代码变更

### 1. `/api/mini/logistics/traces` 去掉自动创建 evidence

文件：

- `custom_addons/logistics_web/controllers/logistics_web_mini_trace.py`

调整内容：

- `POST /api/mini/logistics/traces` 现在只创建 `logistics.trace.event`
- 不再在 `/traces` 中顺手创建 `logistics.trace.evidence`
- 返回数据中不再包含自动创建的 `evidence_id`
- 这样可避免小程序后续继续调用 `/api/mini/logistics/evidences` 时天然制造重复 evidence

### 2. mini 接口补最小 token 校验

文件：

- `custom_addons/logistics_web/controllers/logistics_web_mini_trace.py`
- `custom_addons/logistics_web/controllers/logistics_web_mini_waybill.py`

调整内容：

- 新增 `LogisticsMiniApiAuthMixin`
- 支持从以下位置读取 token：
  - Header:
    - `X-Mini-Api-Token`
    - `X-Mini-Token`
    - `X-App-Token`
  - Payload / Query:
    - `mini_api_token`
    - `miniApiToken`
    - `token`
    - `app_token`
    - `appToken`
- 服务端优先读取：
  - `ir.config_parameter['logistics_web.mini_api_token']`
  - 或环境变量 `LOGISTICS_MINI_API_TOKEN`
- 如果未配置 token，则直接返回 `401`
- 如果已配置 token 但请求不匹配，也返回 `401`
- 这意味着 mini 接口不再默认裸奔，对接前必须先补 token 配置

## 当前状态

- 两个 controller 文件已完成本地修改
- Python 编译通过
- 本地 `feat-text` 已对齐到 `origin/feat-text`
- Odoo 仓库内 `__pycache__` 已清理完成
- 还未同步到联调服务器

## 尚未完成

- 给本地/联调环境补 `logistics_web.mini_api_token` 或 `LOGISTICS_MINI_API_TOKEN`
- 把本轮 controller 变更同步到联调服务器并回归
