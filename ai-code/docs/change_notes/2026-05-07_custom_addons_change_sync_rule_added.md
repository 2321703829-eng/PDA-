# custom_addons 变更同步规则补充

## 本轮目标

为 `custom_addons/` 建立独立的变更同步规则，明确改 `models / controllers / services / views / static` 等目录时，哪些文档必须一起同步。

## 本轮变更

1. 新增 `custom_addons/变更同步规则.md`，统一说明：
   - 适用范围
   - 每次都要检查的基础文档
   - 按目录类型的同步规则
   - `change_notes` 最小输出要求
2. 更新 `custom_addons/README.md`，把“变更同步规则”加入关键入口与默认读法。

## 本轮结论

- `custom_addons/` 现在不只知道“模块怎么分”，也知道“代码改了以后文档怎么跟”。
- 后续改模块代码时，可以直接按目录类型对照同步，减少漏改 README、矩阵、架构文档和专题设计的风险。
