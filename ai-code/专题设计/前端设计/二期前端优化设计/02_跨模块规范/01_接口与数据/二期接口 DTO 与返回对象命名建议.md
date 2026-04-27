# 二期接口 DTO 与返回对象命名建议

适用范围：
- 二期新增或升级接口的返回对象、请求对象、服务层入参与出参命名
- 当前只覆盖后台 `admin` 场景

当前状态：
- 本文档用于统一二期接口实现时的 DTO 命名
- 当前为命名建议层，不直接替代字段契约和接口示例文档

关联文档：
- `前端接口设计总文档.md`
- `前后端接口字段级契约清单.md`
- `二期后端接口开发任务拆分稿.md`

---

## 1. 文档定位

这份文档用于回答两个实现层问题：

1. 二期接口的请求对象和返回对象应该怎么命名
2. 聚合型 DTO、列表项 DTO、导入结果 DTO 应该按什么规律命名，避免后续代码越写越散

---

## 2. 总体命名原则

### 2.1 基本原则

- 类名使用 `PascalCase`
- 字段名使用 `snake_case` 或项目当前后端约定的字段输出名
- DTO 名称要体现对象层级和用途，不要只叫 `Data`、`ItemData`

### 2.2 推荐后缀

| 后缀 | 用途 | 示例 |
|---|---|---|
| `QueryDTO` | controller 接收查询参数 | `HomeOverviewQueryDTO` |
| `CommandDTO` | controller 接收动作型参数 | `WaybillImportConfirmCommandDTO` |
| `ResponseDTO` | 单接口返回主体 | `HomeOverviewResponseDTO` |
| `ItemDTO` | 列表项、子项 | `RecentActivityItemDTO` |
| `SummaryDTO` | 聚合摘要对象 | `StatsOverviewSummaryDTO` |
| `ResultDTO` | 导入/执行结果 | `WaybillImportResultDTO` |
| `ErrorDTO` | 错误行、错误项 | `ImportErrorItemDTO` |

### 2.3 不推荐命名

- `CommonDTO`
- `BaseData`
- `TempResult`
- `XXItemDataVODTO`

原因：

- 语义过弱
- 难以定位归属接口
- 难以长期维护

---

## 3. controller 请求对象命名建议

| 接口 | 推荐请求对象名 |
|---|---|
| `getHomeOverviewSummary` | `HomeOverviewQueryDTO` |
| `getHomeRecentActivities` | `HomeRecentActivitiesQueryDTO` |
| `getHomeGuideByRole` | `HomeGuideQueryDTO` |
| `getStatsOverviewByDateRange` | `StatsOverviewQueryDTO` |
| `getStatsTrendByMetric` | `StatsTrendQueryDTO` |
| `getStatsRankingByDimension` | `StatsRankingQueryDTO` |
| `getWaybillDetailV2` | `WaybillDetailV2QueryDTO` |
| `getWaybillCustomerLinesByWaybill` | `WaybillCustomerLinesQueryDTO` |
| `getWaybillCustomerGoodsLinesByWaybill` | `WaybillCustomerGoodsLinesQueryDTO` |
| `downloadWaybillStandardTemplate` | `WaybillTemplateDownloadQueryDTO` |
| `precheckWaybillStandardImport` | `WaybillImportPrecheckCommandDTO` |
| `confirmWaybillStandardImport` | `WaybillImportConfirmCommandDTO` |
| `getWaybillImportResult` | `WaybillImportResultQueryDTO` |

---

## 4. 返回对象命名建议

## 4.1 首页域

| 接口 | 推荐返回对象名 | 子对象 |
|---|---|---|
| `getHomeOverviewSummary` | `HomeOverviewResponseDTO` | `HomeOverviewSummaryDTO` |
| `getHomeRecentActivities` | `HomeRecentActivitiesResponseDTO` | `RecentActivityItemDTO` |
| `getHomeGuideByRole` | `HomeGuideResponseDTO` | `HomeGuideItemDTO` |

## 4.2 统计域

| 接口 | 推荐返回对象名 | 子对象 |
|---|---|---|
| `getStatsOverviewByDateRange` | `StatsOverviewResponseDTO` | `StatsOverviewSummaryDTO` |
| `getStatsTrendByMetric` | `StatsTrendResponseDTO` | `StatsTrendPointDTO` |
| `getStatsRankingByDimension` | `StatsRankingResponseDTO` | `StatsRankingItemDTO` |

## 4.3 运单详情域

| 接口 | 推荐返回对象名 | 子对象 |
|---|---|---|
| `getWaybillDetailV2` | `WaybillDetailV2ResponseDTO` | `WaybillDetailV2SummaryDTO` |
| `getWaybillCustomerLinesByWaybill` | `WaybillCustomerLinesResponseDTO` | `WaybillCustomerLineItemDTO` |
| `getWaybillCustomerGoodsLinesByWaybill` | `WaybillCustomerGoodsLinesResponseDTO` | `WaybillCustomerGoodsLineItemDTO` |

## 4.4 导入域

| 接口 | 推荐返回对象名 | 子对象 |
|---|---|---|
| `downloadWaybillStandardTemplate` | `WaybillTemplateDownloadResponseDTO` | `WaybillTemplateMetaDTO` |
| `precheckWaybillStandardImport` | `WaybillImportPrecheckResponseDTO` | `ImportErrorTypeSummaryDTO`、`ImportErrorItemDTO` |
| `confirmWaybillStandardImport` | `WaybillImportConfirmResponseDTO` | `WaybillImportExecutionResultDTO` |
| `getWaybillImportResult` | `WaybillImportResultResponseDTO` | `WaybillImportResultDTO` |

---

## 5. 列表与分页对象建议

### 5.1 如果项目已存在统一分页 DTO

优先复用：

- `PagedResponseDTO<T>`
- `PageResultDTO<T>`

### 5.2 如果当前要新建

建议：

- `PagedResponseDTO`
- 字段统一：
  - `items`
  - `page`
  - `page_size`
  - `total`

示例：

- `PagedResponseDTO<WaybillCustomerLineItemDTO>`
- `PagedResponseDTO<WaybillCustomerGoodsLineItemDTO>`

---

## 6. 错误对象命名建议

统一建议：

- `ApiErrorResponseDTO`
- `ImportErrorItemDTO`
- `ImportErrorTypeSummaryDTO`

说明：

- 普通接口错误走 `ApiErrorResponseDTO`
- 导入预校验中的逐行错误单独走 `ImportErrorItemDTO`

---

## 7. 当前实现建议

如果后端当前没有统一 DTO 体系，建议二期先按下面最小集合落地：

1. `HomeOverviewResponseDTO`
2. `StatsOverviewResponseDTO`
3. `StatsTrendResponseDTO`
4. `WaybillDetailV2ResponseDTO`
5. `WaybillCustomerLineItemDTO`
6. `WaybillCustomerGoodsLineItemDTO`
7. `WaybillImportPrecheckResponseDTO`
8. `WaybillImportResultResponseDTO`

这样能先覆盖二期最核心新增链路。
