# 2026-04-10 于睿后台工作大纲重构版

## 背景

`ai-code/odoo-reconstruct` 新补充了一套更完整的重构资料，明确了以下新口径：

- 系统本质是物流留痕取证系统
- 后台价值是查、看、追溯、判断
- 页面应围绕“当前状态层 / 留痕事实层 / 图片证据层”组织
- 当前阶段明确不优先做泛协同、聊天、日历、联系人中心
- 后台前端负责人应先收口追溯阅读层，而不是泛后台改版

## 本次变更

重写文件：
- `ai-code/于睿_后台前端与追溯界面工作大纲.md`

主要调整：
- 重新定义角色定位
- 引入三层阅读模型
- 明确订单 / 批次 / 车次 / 留痕 / 证据的页面主线
- 新增 P0 / P1 / P2 页面优先级
- 明确当前不做范围
- 细化后台信息架构建议
- 强化与 `logistics_dispatch`、`logistics_trace_core`、`logistics_trace_evidence`、`logistics_trace_exception`、`logistics_trace_dashboard` 的协作问题清单
- 明确 Odoo 视图落地载体为 `menu/action/search/tree/form/kanban`

## 结果

于睿这条线的工作大纲从“后台页面改造清单”升级为“后台追溯阅读层设计任务书”，更贴近当前真实项目边界和重构方向。
