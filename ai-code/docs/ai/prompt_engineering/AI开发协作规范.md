# AI开发协作规范

## 目的

定义 AI 在当前 Odoo 物流项目中的通用开发规则，确保输出稳定、可验证、可沉淀。

## 核心规则

### 先读再做

- 先读 `AGENTS.md`
- 再读 `docs/context/`
- 再读相关官方 addon
- 最后才进入方案和代码

### 最小改动优先

- 默认做局部补齐和兼容实现
- 除非明确要求，不主动发起大范围重构
- 优先继承扩展，不复制官方模型

### 开发计划先行

开始写代码前必须说明：

- 会改哪些文件
- 为什么改
- 影响范围
- 风险点
- 如何验证

### 验证优先

默认要求至少覆盖：

- 模块安装或升级可行
- 菜单可打开
- tree / form / search 视图正常
- 权限和访问规则无明显异常
- 关键业务流程能手工验证

### 每轮必须有文档沉淀

- 对话里要给出变更摘要
- 文件里要补 `docs/change_notes/`
- 如果边界、结构、运行方式变化，要同步更新相关文档

## Odoo 项目特定约束

- 当前仓库是 Odoo 19.0 单一主仓结构
- `contacts`、`hr`、`stock` 为主数据基础
- `sale` 仅作结构参考
- `mail` 为留痕和异常底层能力
- `fleet` 仅作二期预留

## 默认输出要求

每轮正式输出应尽量包含：

- Objective
- Boundary
- Current Understanding
- Development Plan
- Change Notes
- Verify
- Risks
- Next Suggestion
