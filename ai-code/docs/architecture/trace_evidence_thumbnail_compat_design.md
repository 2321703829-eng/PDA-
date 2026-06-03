# Trace Evidence Thumbnail Design

适用范围：
- `logistics_trace_evidence` 证据列表页缩略图展示
- `logistics.trace.evidence` 与 `logistics.trace.evidence.image` 的正式读取口径
- 历史证据图片迁移后的兼容展示策略

## Objective

在证据链中期升级已经落地的前提下，明确证据缩略图的正式设计口径：

- 统一以 `evidence -> image` 结构作为主数据来源
- 保留 evidence 主表封面图字段作为历史兼容摘要
- 让后台列表页、详情页、小程序回显读取同一套图片结构

## Current Status

当前联调环境已经完成中期升级落地：

- 小程序上传链已经统一写入 `logistics.trace.evidence.image`
- 图片预览已统一支持：
  - `/logistics_trace/evidence-images/<key>`
  - `/<lang>/logistics_trace/evidence-images/<key>`
- 历史数据已经完成一轮迁移：
  - 已迁移到图片子表：`70` 条
  - 因源文件丢失未自动迁移：`8` 条

因此，legacy 字段回退不再是主方案，只是历史残留兜底。

## Outcome

改动完成后，`logistics.trace.evidence` 列表页应满足：

- 每条证据记录优先按 `image_ids` / `image_items_json` 展示缩略图
- 新上传证据稳定支持多图缩略图展示
- 已迁移的历史证据按图片子表正常展示
- 只有少量未迁移成功的历史 evidence 才走 legacy 单图回退
- 前端统一消费：
  - `image_items_json`
  - `image_count`

## Behavior

### 1. 后端统一字段

证据列表页正式依赖以下字段：

- `image_items_json`
- `image_count`

兼容摘要字段保留，但不再作为正式主读取来源：

- `image_access_key`
- `preview_url`
- `full_url`

说明：

- `image_items_json`
  - 正式来源：`logistics.trace.evidence.image`
  - 每项至少包含：
    - `imageAccessKey`
    - `previewUrl`
    - `fullUrl`
    - `downloadUrl`
    - `imageId`
    - `imageIndex`
    - `imageCountInEvidence`
- `image_count`
  - 正式图片总数
- `preview_url`
  - 仅作为历史兼容摘要字段

### 2. 列表页展示规则

- 新增一列：`证据缩略图`
- 单行最多显示前 `6` 张缩略图
- 超出数量显示 `+N`
- 无图时显示 `No images`
- 点击缩略图后直接打开对应 `previewUrl`

### 3. 正式读取优先级

后端读取顺序固定为：

1. 若 `image_ids` 存在：
   - 从图片子表生成 `image_items_json`
2. 若 `image_ids` 为空，但 evidence 仍有 legacy 摘要字段：
   - 回退生成单图 `image_items_json`
3. 若无图：
   - 返回空数组，前端显示 `No images`

这里要强调：

- `image_ids` 是正式结构
- legacy 回退只是历史残留例外
- 前端不应自行判断底层是新结构还是旧结构

### 4. 小程序与后台统一口径

后台证据列表、证据详情、小程序回显应统一使用：

- `image_access_key`
- `preview_url`
- `image_items_json`

其中：

- 新写入统一落到 `logistics.trace.evidence.image`
- evidence 主表封面图字段由子表首图同步回填
- 这样旧页面仍可读，新的缩略图和多图能力也能稳定工作

## Boundary

本次覆盖：

- 证据列表页缩略图正式展示口径
- 证据图片子表作为主读取结构
- 历史 evidence 的有限兼容回退

本次不覆盖：

- 证据详情页大改版
- 图片灯箱或批量预览器重做
- 历史丢失源文件的自动恢复
- 证据图片对象存储重构

## Implementation Notes

建议落地方式：

- 模型层：
  - `logistics.trace.evidence.image` 作为正式图片主结构
  - `logistics.trace.evidence.image_items_json` 统一输出给前端
- 兼容层：
  - `image_access_key / preview_url / full_url` 仅保留摘要职责
- 视图层：
  - `logistics_trace_evidence_views.xml` 使用 `image_items_json`
- 前端字段组件：
  - 继续使用 `logistics_evidence_thumbnails` widget
- 样式层：
  - 统一缩略图尺寸、圆角、溢出数量角标

## Verify

验证标准分两层：

### 1. 正式结构验证

- 新上传证据的单图缩略图可见
- 新上传证据的多图缩略图可见
- 点击缩略图可预览
- `/<lang>/logistics_trace/evidence-images/<key>` 可正常预览

### 2. 历史兼容验证

- 已迁移的旧 evidence 正常显示缩略图
- 剩余未迁移成功的历史 evidence 至少不炸页面
- 无图记录显示 `No images`

## Risks

- 仍有少量历史 evidence 因原图丢失无法自动迁移
- 如果后续页面仍直接读主表 `preview_url`，会继续延续旧结构思维
- 如果导出或报表仍按旧 evidence 字段取图，需要单独收口

## Next Suggestion

- 后续将依赖图片展示的页面全部统一到 `image_items_json`
- 把“历史残留回退”从设计主叙事里继续降级，最终只作为运维修复事项保留
- 对剩余 `8` 条未迁移成功的历史 evidence 单独做人工甄别清单
