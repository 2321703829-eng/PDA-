# spec-review-evidence-first

## Purpose

把“按证据审查”固定下来：当用户要 review、要对照设计稿、要看代码是否跑偏时，优先找行为问题、边界漂移、升级风险和漏测点，而不是先写大段总结。

这个 skill 适合当前 Odoo 物流项目的 spec-first 工作方式，但不依赖 OpenSpec 或上游私有评审体系。

## Use When

- 用户说“review”
- 需要对照 `AGENTS.md`、`docs/context/`、`ARCHITECTURE.md`、页面设计稿或模块设计稿审查代码
- 需要判断实现是否偏离 Outcome / Behavior / Boundary
- 需要找回归风险、漏测点、漏同步文档

## Review Order

先找问题，再说总结。默认按严重性排序。

优先检查 5 类问题：

1. 行为回归
2. 项目边界漂移
3. 升级与兼容风险
4. 权限与安全风险
5. 测试和文档缺口

## Workflow

### 1. Lock the expected behavior

先找本次审查对应的基线：

- `AGENTS.md`
- `docs/context/`
- `docs/architecture/ARCHITECTURE.md`
- 相关模块设计说明
- 相关前端设计说明

如果没有明确 spec，就至少锁住：

- Outcome
- Behavior
- Boundary

### 2. Read evidence first

只有在读到真实证据时才报问题。证据包括：

- 代码路径
- 视图或模板引用
- manifest 资产声明
- 权限文件
- migration 或接口字段
- 测试缺口
- 文档未同步处

不要把“可能有问题”直接报成 findings。

### 3. Judge by project-specific lenses

#### Behavior lens

- 用户可见行为是否与设计一致
- 状态流转、按钮、字段、页面入口是否跑偏

#### Boundary lens

- 是否把一期外内容提前做进来
- 是否错误复用 `sale.order` 作为物流执行主对象
- 是否绕开自定义 addon 直接改官方核心逻辑

#### Upgrade lens

- 是否引入升级失败或老数据不可读风险
- 是否动了字段、XML ID、模板、状态值而未给兼容方案

#### Security lens

- 是否有 `sudo()` 过度使用
- 是否有权限、记录规则、上传、访问 key 风险

#### Verification lens

- 是否缺关键验证
- 是否缺 `change_notes`
- 是否有需要同步但未同步的文档

## Output Format

默认按下面顺序输出：

1. Findings
2. Open Questions / Assumptions
3. Short Summary

每条 finding 尽量包含：

- 严重级别
- 文件位置
- 问题是什么
- 为什么是问题
- 建议怎么修

## Checklist

- 是否先列 findings 再给总结
- 是否每条问题都有证据
- 是否覆盖行为、边界、升级、安全、验证
- 是否检查 `docs/change_notes/`
- 是否说明剩余风险或验证缺口

## Output Expectation

这个 skill 最适合输出“可直接行动的 review 结果”，而不是泛泛而谈的好坏评价。
