# odoo-compatible-upgrade-guard

## Purpose

在 Odoo 物流项目中，检查一次改动是否会破坏模块升级、历史数据读取、现有接口、导入模板或前端联调口径。

这个 skill 的目标不是追求“大而全”的兼容体系，而是避免常见的升级事故：

- 模块 `-u` 后安装失败
- 老数据因为字段改动读不出来
- 旧菜单、旧 XML ID、旧 action 被改断
- 导入模板、导出字段、接口响应突然不兼容

## Use When

- 新增、删除、重命名模型字段
- 修改 `selection` 值、默认值、必填规则
- 增加或调整 migration
- 修改 import/export 模板字段
- 修改 controller / API 的请求响应结构
- 调整前端依赖的数据结构、字段命名、状态值

## Core Standard

默认遵守 4 条兼容原则：

1. 新增优先，替换次之，删除最后。
2. 可选优先，强制次之，破坏性调整最后。
3. 让旧数据可读，比让新结构“更干净”更重要。
4. 所有真实兼容性变更，都要同步验证升级路径和文档。

## Workflow

### 1. Lock the contract surface

先判断这次改动影响哪一层契约：

- Odoo model fields
- XML ID / action / menu / view name
- import / export template headers
- REST API request / response
- frontend page data contract
- SQL table / index / migration

如果影响多层，不要只检查其中一层。

### 2. Classify the change

把改动分成三类：

- 直接安全改动
  - 新增非必填字段
  - 新增带默认值的字段
  - 新增不影响旧调用方的响应字段
- 需要分阶段演进
  - 字段重命名
  - 字段类型变化
  - 状态值替换
  - 导入模板列名变更
- 高风险破坏性改动
  - 删除字段但无迁移方案
  - 改成必填但无历史数据回填
  - 修改 XML ID
  - 修改老页面仍在使用的 action / menu / tag

### 3. Apply Odoo-first compatibility checks

#### Model field changes

- 新增字段时，优先允许旧记录继续读取和保存。
- 改 `required=True` 前，先明确历史记录如何补值。
- 删字段前，先确认：
  - Python 代码不再读取
  - XML 视图不再引用
  - 导入导出不再引用
  - 报表和搜索视图不再引用

#### Selection / state changes

- 不要直接让旧状态值失效而无兜底。
- 如果替换状态值，至少保证：
  - 旧值还能被读取
  - 搜索、分组、统计不会直接报错
  - 页面文案、颜色、按钮规则同步更新

#### XML ID / menu / action changes

- 默认不要改已有 XML ID。
- 若必须调整，先确认是否存在：
  - 其他模块引用
  - 菜单跳转引用
  - 前端 client action 引用
  - 测试或初始化数据引用

#### API / frontend contract changes

- 响应字段优先“新增字段”，避免“直接改名”。
- 请求参数优先兼容旧字段一段时间，再逐步收口。
- 如果状态枚举变化，前后端和文档必须同步。

#### Import / export changes

- 默认优先兼容旧模板，而不是只保留新模板。
- 如果模板字段必须调整，要同步明确：
  - 哪些列新增
  - 哪些列废弃
  - 是否兼容旧表头
  - 是否需要错误报告说明

### 4. Verify the upgrade path

至少覆盖以下验证：

- 模块升级是否可执行
- 关键树表单搜索视图是否还能打开
- 老数据是否可读
- 新建记录是否可写
- 关键导入或关键接口是否还能跑通

## Checklist

- 是否新增了必填字段但没有回填策略
- 是否删除或重命名了字段但没有全链路替换
- 是否改变了旧状态值的读取口径
- 是否修改了 XML ID / action / menu 但没有检查引用
- 是否影响了 import/export 模板
- 是否影响了前端数据契约
- 是否需要更新 `docs/dev/upgrade_and_verify.md`
- 是否已经补 `docs/change_notes/`

## Output Expectation

使用这个 skill 时，结论至少要回答：

- 这次改动影响哪些契约层
- 哪些点是安全改动，哪些点要分阶段
- 最小验证清单是什么
- 需要同步哪些文档
