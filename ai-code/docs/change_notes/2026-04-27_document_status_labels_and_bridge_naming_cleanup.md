# 2026-04-27 文档状态标识与 bridge 命名收口

## 本次目标

在不改业务结论的前提下，统一 `现行 / bridge / archive` 状态口径，并收一批最容易误导人的旧文件名。

## 本次动作

1. 在入口层补状态规则：
   - `docs/architecture/README.md`
   - `docs/context/README.md`
   - `专题设计/README.md`
   - `专题设计/前端设计/README.md`
2. 将最容易误判为现行稿的历史桥接文档改名为 `*_bridge.md`：
   - `logistics_order_addon_design_bridge.md`
   - `logistics_trace_addon_design_bridge.md`
   - `logistics_exception_addon_design_bridge.md`
   - `logistics_order_mapping_bridge.md`
   - `logistics_trace_mapping_bridge.md`
3. 收口一份仍带旧专题名的导航文件：
   - `2026-04-27_高并发优化设计导航.md`
4. 更新现行文档中的文件名引用：
   - `docs/context/`
   - `docs/dev/`
   - `docs/review/`
   - `专题设计/`
5. 在四个旧根目录 `README.md` 中补充退场规则：
   - 只保留兼容跳转
   - 不再新增正文
   - 后续在目录治理下一阶段移除

## 本次不做

- 不全量改 `docs/change_notes/` 历史 note
- 不改业务结论、模块边界或专题正文判断
- 不继续扩大到全仓所有历史旧名文件

## 当前口径

- `现行`：当前正式入口与默认维护文档
- `bridge`：旧命名、旧边界、旧阶段到现行口径的桥接稿
- `archive`：历史草图、旧版方案、来源资料与待归档材料

## 说明

历史 `change_notes` 中继续保留迁移前路径和旧文件名，属于有意保留的历史留痕语境。

