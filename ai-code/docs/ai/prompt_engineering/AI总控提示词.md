# AI总控提示词

## 启动顺序

1. 读取 `AGENTS.md`
2. 读取 `docs/ai/skill_router.md`
3. 按需读取 `docs/ai/prompt_engineering/*.md`
4. 读取 `docs/context/*.md`
5. 读取 `docs/architecture/ARCHITECTURE.md`
6. 读取当前相关官方 addon
7. 读取当前相关自定义 addon

## 任务分流规则

### 官方能力复用型任务

适用于：

- 客户
- 门店
- 工作人员
- 仓库
- 二期车辆

优先动作：

- 识别官方模型
- 判断继承点
- 设计补充字段
- 评估是否需要新菜单、新视图、新权限

### 自定义业务模块任务

适用于：

- 订单
- 留痕
- 异常

优先动作：

- 先出模型草图
- 再出字段草图
- 再出状态草图
- 再出关系草图
- 最后进入代码与视图层

## 输出纪律

- 每轮都保留 `Boundary` 和 `Risks`
- 任何代码建议都带 `Verify`
- 任何真实变更都要沉淀到 `docs/change_notes/`

## 项目默认判断

- 当前不是全面 ERP 改造
- 当前不是 WMS 全量建设
- 当前不是调度系统全量建设
- 当前是一期物流主链路定制开发
