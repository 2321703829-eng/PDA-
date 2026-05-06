# 2026-05-06 mini_api_security_design

## 本次变更

- 新增 mini API 安全设计文档：
  - `docs/architecture/mini_api_security_design.md`

## 设计内容

- 明确 mini 接口当前的安全问题
- 给出开关式 mini token 鉴权方案
- 说明司机端影响范围
- 说明推荐启用顺序与后续演进方向

## 适用范围

- `GET /api/mini/logistics/waybills/<no>/stops`
- `POST /api/mini/logistics/traces`
- `POST /api/mini/logistics/evidences`
- `POST /api/mini/logistics/evidences/<id>/images`
