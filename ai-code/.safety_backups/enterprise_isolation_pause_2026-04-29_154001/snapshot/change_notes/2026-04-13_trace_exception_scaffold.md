# 2026-04-13 Trace Exception Scaffold

## 本次变更

- 新建 `custom_addons/logistics_trace_exception` 真实模块骨架
- 新增 `logistics.trace.exception` 与 `logistics.trace.exception.process.log`
- 为运单与留痕事件补充异常关系与异常统计
- 将时间线中的 `View Exception` 动作接到真实异常列表

## 当前结果

- 异常层已经不再只是设计稿
- 现在已经具备：
  - 异常列表入口
  - 异常详情页
  - 基础状态流转
  - 处理记录
  - 运单与留痕的异常下钻

## 当前边界

- 还未做安装 / 升级验证
- 异常详情页中“关键证据区”还未做增强展示
- 工作台与老板页还未开始读取真实异常聚合

## 下一步建议

- 将工作台异常卡片改为读取 `logistics.trace.exception`
- 或继续把异常详情页接入真实证据阅读区
