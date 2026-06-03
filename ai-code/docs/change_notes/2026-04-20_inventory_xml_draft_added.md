# 2026-04-20 新增库存search view与Smart Button XML草稿

## 本轮目标

- 新增 `05_库存search view与Smart Button XML草稿.md`
- 将库存专题从字段与视图清单继续下沉到 XML 结构草稿层

## 修改文件

- `仓管模块设计/01_模块设计/03_库存管理/05_库存search view与Smart Button XML草稿.md`

## 修改原因

- 库存字段映射和视图落地清单已经形成，但实现前仍缺少一份专门回答“search view、tree/form 增强、Smart Button 和 act_window 怎么写”的 XML 草稿
- 若不先固定 XML 片段组织方式，后续真实回填时容易继续散落在不同命名和不同结构里

## 改动摘要

- 新增文档定位、范围边界、统一目标和章节总览
- 固定库存专题 XML 的文件拆分方式、对象对照和 XML ID 前缀
- 补齐 `stock.quant / stock.location / stock.warehouse` 三类对象的 `search view` 草稿
- 补齐三类对象的 `tree / form` 视图增强草稿
- 补齐三类对象的 `act_window` 草稿
- 补齐 Smart Button 方法命名、返回结构和上下文字段建议
- 固定 XML 文件拆分、回填顺序和重点验证项

## 影响范围

- `仓管模块设计/01_模块设计/03_库存管理/`
- 后续库存专题 XML、search view、Smart Button、action 回填将以本稿为实现前参照

## 是否影响模型 / 视图 / 权限 / 数据兼容性

- 不直接影响真实模型、视图、权限或数据兼容性
- 本次为设计文档新增，后续若按文档落地，可能影响 XML 文件拆分、视图继承方式、Smart Button 方法命名和 action 参数结构

## 验证方法

- 检查文档是否已形成完整章节闭环
- 检查三类对象是否都已具备 `search view`、`tree / form`、`action` 和 Smart Button 草稿
- 检查 XML ID、方法命名和上下文字段是否与前面的字段清单、反查稿、页面结构稿保持一致

## 风险点

- 当前 XML 片段为草稿，真实回填时仍需结合目标原生视图的真实 `inherit_id` 和 xpath 位置进一步确认
- 片段中涉及的扩展字段和对象方法仍需在真实模型与服务端方法里补齐
- 若目标页 action 或 search view 命名后续调整，本稿中的引用也需要同步回写

## 回滚建议

- 若后续决定重做库存 XML 组织方式，可删除本稿并回退到由字段清单承接的状态
- 回滚前建议先确认是否已有真实 XML 实现或模块说明基于本稿继续扩写

## 后续待办

- 视需要继续补库存扩展字段到 Python 模型文件的映射草稿
- 视需要继续补 Smart Button 对应服务端方法返回值草稿
- 若 XML 草稿评审通过，可同步回填总导航和进度总结
