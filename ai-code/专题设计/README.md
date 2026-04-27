# 专题设计

`专题设计/` 是当前仓库内所有专题设计包的统一根入口。

## 当前专题包

- [前端设计](./前端设计/README.md)
- [仓管设计](./仓管设计/README.md)
- [企业隔离设计](./企业隔离设计/README.md)
- [高并发优化设计](./高并发优化设计/README.md)

## 与 `docs/` 的关系

- `docs/` 负责项目主体系：业务基线、模块边界、升级验证和治理规则。
- `专题设计/` 负责专题体系：专题方案、专题规范、专题落地清单和专题导航。

## 状态标识规则

- `现行`：专题包根 `README.md`、阶段总纲、现行专题方案与规范。
- `bridge`：专题内用于连接旧叫法、旧目录或旧实现阶段的桥接稿。
- `archive`：`来源资料与历史草图`、`待归档`、旧版方案和历史截图材料。

## 默认读法

1. 先从 [docs/README.md](../docs/README.md) 确认主体系边界。
2. 再进入对应专题包的 `README.md`。
3. 如果专题结论已经上升为正式系统基线，再回看 [docs/architecture/README.md](../docs/architecture/README.md) 和 [docs/dev/README.md](../docs/dev/README.md)。

## 兼容与退场

- 历史根目录 `前端设计/`、`仓管模块设计/`、`企业分离功能文件夹/`、`高并发承载能力优化设计/` 已完成移除。
- 这些旧根目录名只保留在迁移说明、历史留痕和执行记录中，不再作为真实目录存在。
- 退场规则见 [../docs/dev/topic_design_legacy_root_retirement_plan.md](../docs/dev/topic_design_legacy_root_retirement_plan.md)。
- 历史路径如何理解，见 [../docs/dev/topic_design_repo_wide_trace_notice.md](../docs/dev/topic_design_repo_wide_trace_notice.md)。
