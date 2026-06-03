# 2026-05-06 司机端小程序人工回归清单新增

## 变更类型

- 文档新增

## 新增文件

- `deliverables/2026-05-06_司机端小程序人工回归清单.md`

## 目的

将当前联调环境下司机端小程序的实际操作回归路径整理成可直接执行的步骤，覆盖：

- 批次号搜索
- 站点列表展示
- 上传留痕
- 创建证据
- 上传图片
- 图片回显
- 异常反馈

## 说明

该清单基于当前已验证通过的 mini 主链能力编写：

- `/api/mini/logistics/waybills/<no>/stops`
- `/api/mini/logistics/traces`
- `/api/mini/logistics/evidences`
- `/api/mini/logistics/evidences/<id>/images`
- `/logistics_trace/evidence-images/<key>`

