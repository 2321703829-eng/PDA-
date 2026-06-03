# 2026-05-07 小程序原始导入关键规格冻结

## Objective

把小程序原始单表导入方案里最容易漂移的 3 个关键点正式冻结，避免后续实现阶段再次回到“脚本思路”或“弱匹配可放行”的不稳定口径。

## Outcome

本轮冻结后，专题设计内已经明确：

1. 客户信息底表的正式来源首期直接复用系统主数据
2. 首期匹配成功的唯一判定是 `客户名称 + 客户地址` 双命中
3. confirm 成功后首期只写 `logistics.route.planning.batch` 和 `logistics.route.planning.stop.line`

## Files

- [小程序原始单表导入模式设计](D:\Desktop\Odoo\ai-code\专题设计\小程序导入设计\2026-05-07_小程序原始单表导入模式设计.md)

## Summary

### 1. 客户信息底表来源冻结

- 首期直接复用系统内：
  - `res.partner`
  - 已落库的 logistics customer/store profile 扩展数据
- 首期不再引入独立“受控底表镜像”作为正式匹配源

### 2. 匹配成功判定冻结

- 只认 `客户名称 + 客户地址` 双命中
- 以下情况全部拦截 confirm：
  - 只命中名称
  - 地址弱匹配
  - 多命中
  - 无命中

### 3. confirm 落库范围冻结

- 首期只写：
  - `logistics.route.planning.batch`
  - `logistics.route.planning.stop.line`
- 首期不直接扩写完整：
  - `waybill`
  - `order`
  - `goods`

## Verify

本轮为设计规格冻结，已完成：

1. 把关键决策写回专题正文
2. 把“正式来源 / 成功判定 / confirm 落点”三项口径显式写死
3. 保持与当前 route planning 承接方向一致

## Next Suggestion

下一步建议直接进入“后端实施任务拆分”：

1. service 拆分
2. controller 路由清单
3. selection option 扩展
4. staging model 取舍
5. 测试样例与错误码清单
