# 2026-04-27 dev 历史计划索引与历史桥接总索引补齐

## 本次目标

继续做文档治理收尾，把 `docs/dev/` 里的过期计划稿、已执行留档和草案材料与现行执行入口分开，同时补一份统一的历史与桥接总索引。

## 本次动作

1. 重写 `docs/dev/README.md`
   - 加入 `现行 / archive / draft` 状态口径
   - 将现行入口与历史计划入口拆开
2. 新增 `docs/dev/historical_plan_index.md`
   - 集中列出过期计划、已执行留档和测试草案
3. 为 `docs/dev/topic_design_physical_reorg_execution_plan.md` 补充已执行留档状态头
4. 修正 `docs/dev/next_step_plan_2026-04-10.md` 顶部参考路径
   - 让过期计划稿仍能正确指向当前现行入口
5. 新增 `docs/architecture/history_and_bridge_index.md`
   - 用 `现行 / bridge / archive / draft` 三栏统一列入口
6. 更新 `docs/architecture/README.md`
   - 挂出新的总索引入口
7. 小范围收口专题旧标题文件
   - 将 `仓管模块设计启动讨论稿.md` 统一为 `仓管设计启动讨论稿.md`
   - 同步修正同目录现行引用

## 本次不做

- 不全量改 `docs/change_notes/` 历史留痕
- 不改业务判断、模块边界或专题正文结论
- 不继续扩大到更多专题旧标题文件

## 当前结果

- `docs/dev/` 现在已形成：
  - 现行执行入口
  - 历史计划 / 已执行留档
  - draft 草案
- `docs/architecture/` 现在已有总览索引，可快速区分：
  - 当前该看什么
  - 旧命名该看什么 bridge
  - 哪些只是 archive / draft

