# 2026-05-13 system module restructure design formalized

## Summary

重构 `专题设计/ODOO原生模块设计/00_导航与总纲/2026-05-12_系统模块重组设计.md`，将其从同事草稿整理为与当前专题现行口径一致的正式版。

## Main changes

- 明确认可“取消物流一级菜单”的菜单重组方向
- 明确保留既有物流对象边界，不把 `waybill / customer_line / trace_event / evidence / exception` 整体并入 TMS
- 将 ERP 承接模块口径改回 `sale / purchase / stock / account` 分工承接
- 将系统底座口径改回 `base / users / groups / access rules`
- 将本期实施顺序改回 `ERP -> WMS -> TMS -> BI`
- 将文档定位从“历史菜单归位草稿”收口为“正式模块重组设计”

## Impact

- 当前系统模块重组文档已可纳入现行专题文档体系
- 菜单重组与对象边界、原生承接、本期顺序之间的冲突已基本消除
