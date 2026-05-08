## 2026-05-08 小程序原始单表未命中候选提示

### 目标

- 保持小程序原始单表导入的自动匹配规则严格不变。
- 仅在人工复核场景下，为 `unmatched` 行提供前 5 个相近客户候选，帮助判断：
  - 数据库里确实没有该客户
  - 还是数据库里有相近客户，但名称存在细微差异

### 后端改动

- 文件：
  - `logistics_web/services/mini_program_raw_sheet_import_service.py`
- 处理：
  - 新增未命中候选召回逻辑
  - 召回口径基于 `res.partner` 的物流客户范围，按名称片段 `ilike` 召回
  - 结合名称标准化、关键词重合度、地址片段重合度做简单排序
  - 每条未命中记录最多返回 5 个候选

### 前端改动

- 文件：
  - `logistics_web/static/src/js/actions/import_center_action.js`
  - `logistics_web/static/src/xml/import_center_templates.xml`
- 处理：
  - 新增未命中候选列表 getter
  - 在“小程序预校验结果”区域新增“未命中客户候选”展示区
  - 每条未命中客户展示：
    - 原始客户名称
    - 原始地址
    - 最多 5 个相近候选客户

### 约束

- 该能力只用于人工复核辅助展示。
- 不会放宽当前自动导入的严格命中规则。
