# logistics_trace

## 当前角色

- bridge
- 历史粗粒度命名桥接目录

## 当前状态

- 当前目录没有 `__manifest__.py`
- 当前不作为可安装模块

## 角色说明

- 该目录代表旧阶段里“trace 一个模块包所有留痕能力”的粗粒度叫法
- 当前现行结构已经拆分为：
  - `logistics_trace_core`
  - `logistics_trace_evidence`
  - `logistics_trace_exception`

## 参考口径

- 现行留痕主链：`waybill -> trace -> evidence -> exception`
- 现行模块入口：
  - `../logistics_trace_core/`
  - `../logistics_trace_evidence/`
  - `../logistics_trace_exception/`

## 使用说明

- 本目录只保留历史命名桥接价值。
- 新的留痕相关实现和文档同步，必须落到拆分后的现行模块上。
