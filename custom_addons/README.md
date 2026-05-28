# custom_addons

`custom_addons/` 是当前物流项目自定义 Odoo 模块的统一根入口。

## 当前角色

- 现行代码承载层
- 自定义物流能力模块入口

## 关键入口

- [模块职责矩阵.md](./模块职责矩阵.md)
  模块主对象、API 入口、前端承接和专题归属总表。
- [变更同步规则.md](./变更同步规则.md)
  改 `models / controllers / services / views / static / tests` 时的最小文档同步规则。
- [单测补全指南.md](../单测补全指南.md)
  BDD 验证优先开发规范、测试架构说明、覆盖率要求（40%–50%）。

## 当前有效主线

当前项目内应优先按下面这组模块理解：

1. `logistics_base`
2. `logistics_dispatch`
3. `logistics_trace_core`
4. `logistics_trace_evidence`
5. `logistics_trace_exception`
6. `logistics_web`

这组模块对应当前业务与页面主线：

- 执行主线：`wave -> batch -> waybill -> customer_line -> order_line -> goods_line`
- 留痕主线：`waybill -> trace -> evidence -> exception`
- 前端增强层：`logistics_web`

## 模块分组

### 现行模块

- [logistics_base/README.md](./logistics_base/README.md)
  主数据与基础扩展层。
- [logistics_dispatch/README.md](./logistics_dispatch/README.md)
  当前执行主链承载层。
- [logistics_trace_core/README.md](./logistics_trace_core/README.md)
  留痕主对象与事件核心层。
- [logistics_trace_evidence/README.md](./logistics_trace_evidence/README.md)
  证据与图片元数据层。
- [logistics_trace_exception/README.md](./logistics_trace_exception/README.md)
  异常与处理闭环层。
- [logistics_web/README.md](./logistics_web/README.md)
  后台前端增强与聚合读取层。

### 桥接 / 预留目录

- [logistics_order/README.md](./logistics_order/README.md)
  历史命名桥接目录，当前不是现行执行主模块。
- [logistics_trace/README.md](./logistics_trace/README.md)
  历史粗粒度命名桥接目录，当前已拆到 `trace_core / evidence / exception`。
- [logistics_exception/README.md](./logistics_exception/README.md)
  历史命名桥接目录，当前不是现行异常主模块。

## 当前目录状态

| 模块 | 当前状态 | 是否有 `__manifest__.py` | 说明 |
| --- | --- | --- | --- |
| `logistics_base` | active | 是 | 现行 |
| `logistics_dispatch` | active | 是 | 现行 |
| `logistics_trace_core` | active | 是 | 现行 |
| `logistics_trace_evidence` | active | 是 | 现行 |
| `logistics_trace_exception` | active | 是 | 现行 |
| `logistics_web` | active | 是 | 现行 |
| `logistics_order` | bridge | 否 | 目录保留，当前不作为安装模块 |
| `logistics_trace` | bridge | 否 | 目录保留，当前不作为安装模块 |
| `logistics_exception` | bridge | 否 | 目录保留，当前不作为安装模块 |

## 默认读法

1. 先读 `ai-code/docs/context/` 和 `ai-code/docs/architecture/ARCHITECTURE.md`，确认业务主线和模块边界。
2. 再从本文件确认哪些模块是现行、哪些只是桥接目录。
3. 进入具体模块时，优先按 `base -> dispatch -> trace_core -> evidence -> exception -> web` 的顺序阅读。
4. 只有在追溯历史命名或旧设计稿时，才进入 `logistics_order / logistics_trace / logistics_exception`。
5. 需要判断“代码该落哪个模块”时，优先回看 [模块职责矩阵.md](./模块职责矩阵.md)。
6. 需要判断“改完代码后还要同步哪些文档”时，回看 [变更同步规则.md](./变更同步规则.md)。

## 测试规范

- **BDD 验证优先**：每次代码提交必须包含对应的单元测试，不接受"先合代码，后补测试"
- **覆盖率要求**：有效方法覆盖率 40%–50%（不计纯字段声明、配置文件等）
- **Mock 策略**：使用 mock-based 测试，不依赖数据库连接
- **运行方式**：`pytest -v` 在项目根目录执行
- 详见 [单测补全指南.md](../单测补全指南.md)

## 目录治理规则

- 不直接修改官方 Odoo addon 来承载物流业务主能力。
- 现行模块必须同时具备：
  - `README.md`
  - `__manifest__.py`
  - `tests/` 目录（含 mock-based 单元测试）
  - 清晰的职责边界
- 仅保留桥接价值的目录，应在 `README.md` 中明确标注 `bridge`，避免误读为现行模块。
- 模块职责、依赖、主对象或接口策略发生变化时，必须同步：
  - 本目录下相关模块 `README.md`
  - `ai-code/docs/architecture/`
  - `ai-code/docs/change_notes/`
