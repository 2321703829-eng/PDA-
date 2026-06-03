# 2026-04-16 二期接口文档补齐到仓库落位级

## 本次变更

为 `前端设计/二期前端优化设计/02_跨模块规范/01_接口与数据/` 补充“可直接对照现有仓库开工”的最后一层文档：

1. `二期接口与现有 custom_addons 文件落位映射表.md`
2. `二期 controller/service/model 具体文件创建建议.md`
3. `二期接口实现检查清单.md`

同时同步更新：

- `README.md`
- `二期后端接口开发任务拆分稿.md`

## 变更目的

- 把二期接口设计从“抽象分层建议”推进到“对应当前 `custom_addons` 真实模块与文件位置”
- 明确哪些接口应落 `logistics_web`，哪些业务能力应落 `logistics_dispatch`
- 明确当前活跃加载文件与历史未加载文件的差别，避免写到无效位置
- 补一份后端实现与联调前的统一检查口径

## 关键结论

- `admin` 聚合接口继续统一由 `custom_addons/logistics_web/controllers/` 暴露
- 运单详情三层读取与导入落库逻辑继续由 `custom_addons/logistics_dispatch/models/` 承接
- `logistics_trace_core / evidence / exception` 保持领域 helper 角色，不在二期新增独立 controller
- 当前客户明细与货物明细活跃加载文件是 `_v2.py`，新增方法不能误落到未被 `__init__.py` 导入的历史文件

## 当前边界

- 本次仍然只做文档补强
- 没有修改 `custom_addons` 代码
- 没有执行模块升级或接口联调验证
