# 2026-04-13 logistics_order_mapping 回调为历史桥接文档

## 本次变更

- 重写 `docs/architecture/logistics_order_mapping.md`
- 更新 `docs/review/过期文档处理清单_2026-04-13.md`

## 主要调整

- 不再把 `logistics_order_mapping.md` 作为现行模型映射设计稿继续维护
- 将其回调为“历史命名桥接文档”
- 明确旧的 `logistics_order / logistics.order` 语义应桥接到当前的 `logistics_dispatch / logistics.dispatch.waybill`
- 将该文档从“部分过期”转为“历史记录 / 桥接说明”定位

## 说明

- 本次仅修改文档
- 未进行代码实现、编译、模块升级或服务启动
