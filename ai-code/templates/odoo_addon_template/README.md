# Odoo Addon Template

这个目录提供一个最小可用的 Odoo addon 模板样例，用于后续创建 `custom_addons/logistics_*` 模块时参考。

当前适用口径：

- 执行主线以 `logistics_dispatch` 为核心
- 留痕事实层以 `logistics_trace_core` 为核心
- 异常层以 `logistics_trace_exception` 为核心
- 基础扩展层以 `logistics_base` 为核心

也就是说，这个模板现在更适合拿来支撑：

- `logistics_base`
- `logistics_dispatch`
- `logistics_trace_core`
- `logistics_trace_exception`
- `logistics_trace_evidence`
- `logistics_trace_dashboard`

---

## 建议用法

1. 复制本模板目录
2. 修改模块目录名与技术名
3. 修改 `__manifest__.py` 里的依赖、数据文件和安装属性
4. 修改模型、视图、权限与菜单
5. 再接入真实业务逻辑

---

## 模板适用场景

### 适合直接从模板起步的模块

- 纯业务对象模块
- 轻量扩展模块
- 以 `list / form / search / action / menu` 为主的后台模块

### 不适合只靠本模板直接开工的模块

- 需要较多自定义 widget 的 Odoo Web 增强模块
- 强依赖 controller / RPC 聚合接口的展示模块
- 证据查看、时间线等需要专门前端区块的模块

这些场景可以先从模板起步，但通常还需要额外补：

- controller
- service / 聚合层
- 静态资源
- JS widget 或 client action

---

## 当前建议的模块命名口径

优先使用当前有效模块语义：

- `logistics_base`
- `logistics_dispatch`
- `logistics_trace_core`
- `logistics_trace_evidence`
- `logistics_trace_exception`
- `logistics_trace_dashboard`
- `logistics_trace_rule`

不建议再把下面这些当成新模块命名基线：

- `logistics_order`
- `logistics_trace`
- `logistics_exception`

它们现在更适合作为历史桥接命名理解。
