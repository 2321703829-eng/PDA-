# 2026-04-18 执行页组件命名与文件映射专题补充 manifest asset 片段示例

## 本次变更

补充 `仓管模块设计/01_模块设计/02_执行页组件命名与文件映射草稿.md`：

- 新增 `11. manifest asset 片段示例`
- 将原 `v0.1 收口与后续补充方向` 顺延为 `12`
- 同步更新目录索引、章节总览与阅读主线说明

## 本次补充的重点

### 1. manifest asset 的统一组织原则

固定了以下方向：

- 执行页资源统一收在 `logistics_wms_web`
- 公共资源先于动作页资源加载
- 四类执行页统一进入同一个 backend bundle
- 不把执行页资源分散塞进多个业务模块的前端 bundle

### 2. 提供了可直接参照的片段草稿

本次新增了 `web.assets_backend` 的示例片段，覆盖：

- `execution/common/`
- `execution/receive/`
- `execution/putaway/`
- `execution/pick/`
- `execution/check/`

并明确了 JS / XML / SCSS 的推荐组织顺序。

### 3. 固定了一期不建议做法

明确不建议：

- 在业务模块 manifest 中重复声明执行页资源
- 使用很多不受控的通配符
- 动作页资源排在公共资源前面
- JS / XML / SCSS 完全无序混排

## 当前意义

这次补充后，这份专题稿已经从：

- 入口对象命名
- 组件与模板命名
- 文件与目录映射
- service / hook 命名

继续推进到了：

- `__manifest__.py` 的 asset 组织方式

后续真正落 `logistics_wms_web` 执行页前端时，已经可以直接拿这份文档作为前端目录与 asset 配置的基线参照。
