# logistics-mermaid-diagram

## Purpose

为当前 Odoo 物流项目生成可直接放进文档的 Mermaid 图，重点服务于：

- 业务流程图
- 状态流转图
- 模块关系图
- 页面/入口关系图
- 简化版数据关系图

它不是通用互联网产品图表规范，而是面向当前物流项目的文档表达工具。

## Use When

- 用户明确要求画流程图、状态图、架构图、关系图
- 设计文档里有复杂流程，单靠文字不够清楚
- 需要把 `wave -> batch -> waybill -> trace -> evidence -> exception` 主线画清楚
- 需要表达后台页面入口、菜单跳转、对象关系、状态流转

## Core Standard

默认遵守 5 条图表规则：

1. 一张图只讲一个主题。
2. 节点名称尽量短，优先用项目现有术语。
3. 不为了“好看”引入新术语。
4. 复杂流程拆图，不在一张图里塞满所有信息。
5. 图和正文口径必须一致。

## Recommended Diagram Types

### Flow

用于：

- 业务流程
- 操作流程
- 页面跳转

优先语法：

- `flowchart TD`
- `flowchart LR`

### State

用于：

- 运单状态
- 留痕事件状态
- 异常状态

优先语法：

- `flowchart LR`

### Structure

用于：

- 模块关系
- 页面层级
- 入口关系

优先语法：

- `flowchart`
- `subgraph`

### Data

用于：

- 简化版实体关系

优先语法：

- `erDiagram`

## Workflow

### 1. Confirm the subject

先明确这张图想说明什么：

- 主业务线
- 某个模块
- 某个页面
- 某组状态
- 某个对象关系

### 2. Reuse project terminology

优先使用当前项目已稳定术语：

- wave
- batch
- waybill
- waybill order lines
- trace
- evidence
- exception

不要随手引入新的总称、别名或互联网产品黑话。

### 3. Keep the graph small

默认建议：

- 单图节点不超过 15 个
- 单图主分支不超过 4 条
- 超过就拆成两张图

### 4. Place the graph correctly

如果图服务于某份文档：

- 优先嵌入相关章节
- 图前用一两句话说明用途
- 图后补关键口径，不把所有说明塞进节点里

## Checklist

- 图里的术语是否和正文一致
- 是否误用了历史命名
- 是否把一期和二期内容混在一张图里
- 是否过度复杂，应该拆图
- 是否需要同步更新相关设计文档

## Output Expectation

使用这个 skill 时，默认交付：

- 一段可直接粘贴的 Mermaid 代码
- 一句图标题建议
- 一句该图说明什么
