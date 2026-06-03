# 2026-04-21 四期文档恢复到运单-门店节点结构

## 本次变更

- 将四期文档主结构从 `waybill -> order_line -> goods_line` 恢复为 `waybill -> customer_line -> order_line -> goods_line`
- 取消“强制 1 运单 = 1 门店”的临时前提
- 恢复 `customer_line` 作为四期核心对象

## 重点同步的内容

1. 总纲、导入专题、单表映射、页面信息架构、图片模块设计重新恢复门店节点层
2. 图片挂点从 `waybill` 恢复为 `customer_line`
3. 两层图片包结构恢复为：
   - `waybill package`
   - `store package`
4. 页级稿中恢复门店节点阅读区为核心页面
5. 数据库底表设计重新补回 `customer_line`
6. 字段级映射与全量映射表重新按四层对象拆分
