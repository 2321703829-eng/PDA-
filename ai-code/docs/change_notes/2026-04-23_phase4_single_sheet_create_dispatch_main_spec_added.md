# 2026-04-23 phase4 single sheet create dispatch main spec added

## Summary

- 新增《四期单表新建主链导入改造方案》。
- 正式收口标准导入从旧三 Sheet 补录模式升级为单表新建主链模式的目标、行为边界与实施顺序。

## Why

- 当前实现仍以三 Sheet 和“已有主数据补录”为核心，不满足业务希望通过导入直接创建新波次、新批次、新运单的目标。
- 在改代码前，需要先冻结 Outcome / Behavior / Boundary，避免实现过程中口径继续漂移。

## Scope

- 单表模板
- 新建主链导入模式
- 预校验规则重构
- 正式导入执行顺序
- 结果页承接方向

## Follow-up

- 按新专题方案改造 `logistics_web` 标准导入服务与前端承接逻辑。
