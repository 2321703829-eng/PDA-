# 2026-04-13 项目上下文文档重写

## 本次变更

- 重写 `docs/context/odoo_logistics_context.md`
- 更新 `docs/review/过期文档处理清单_2026-04-13.md`

## 主要调整

- 不再沿用 `shipment_batch -> shipment_order -> trace_record -> trace_record_image` 旧主线
- 正式切换为 `波次 -> 批次 -> 运单 -> 留痕 -> 证据 -> 异常` 的项目级上下文口径
- 明确 `odoo_logistics_context.md` 是当前项目上下文正式入口，而不是历史草图
- 将后续优先回调目标前移到仍未重写的上下文与桥接类文档

## 说明

- 本次仅修改文档
- 未进行代码实现、编译、模块升级或服务启动
