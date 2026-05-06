# 证据图片批量导出重构口径

适用范围：
- `custom_addons/logistics_web`
- 证据图片批量导出
- 导出任务结果页与导出打包逻辑

优先基准：
- `docs/architecture/ARCHITECTURE.md`
- `docs/architecture/logistics_web_addon_design.md`
- `docs/architecture/logistics_export_result_display_design.md`
- `docs/architecture/trace_evidence_thumbnail_compat_design.md`

---

## 1. 文档目标

本文档用于正式定义“证据图片批量导出”的重构口径。

本次重构的核心不是继续优化旧的“按 evidence 导出”逻辑，而是明确把导出主单位从：

- `evidence`

调整为：

- `image`

也就是说，用户点击“批量导出图片”时，系统应该理解为：

**导出当前列表筛选结果里所有可导图片。**

---

## 2. Outcome

重构完成后，需要满足：

1. 用户点击图片批量导出时，结果与“当前列表里的图片”直觉一致
2. 空 evidence 不再作为导出失败主单位
3. 历史 legacy 证据不会因为对象层兼容噪音拖垮整体成功率
4. 导出结果统计围绕“图片”而不是“证据”展开
5. 导出包除图片外，还要附带一份图片索引清单

---

## 3. 当前问题

当前实现的主要问题是：

1. 导出主单位偏向 `evidence`
2. 空 evidence、legacy evidence、丢图 evidence 会大量进入导出流程
3. 用户点的是“导出图片”，结果页却主要在统计 evidence 成败
4. 历史数据中：
   - evidence 无图
   - legacy key 存在但底图丢失
   - evidence 与 image 结构混合
   会显著拉低结果页成功率

这会导致业务体验出现偏差：

- 用户以为当前列表有很多图
- 结果系统却报大量失败或跳过
- 但真正失败的并不是“图片导出能力”，而是“记录层对象与历史脏数据混在一起”

---

## 4. 重构原则

## 4.1 导出主单位改为图片

批量导出图片时，系统应以：

- `图片`

作为打包与统计主单位，而不是：

- `evidence`

### 正确理解

- 当前列表负责提供“筛选范围”
- evidence 负责提供“图片归属上下文”
- image 才是真正进入 ZIP 的文件单位

---

## 4.2 列表筛选结果仍然保留为入口

重构后并不是绕开列表，而是：

1. 先取当前列表筛选后的 evidence 集合
2. 再从这些 evidence 中收集所有可导图片
3. 最终导出“图片集合”

所以：

- 列表仍然是用户视角的选择范围
- 图片才是导出执行层的主对象

---

## 4.3 只导出可用图片

进入导出包的对象必须满足：

1. 有明确图片元数据
2. 图片文件可读取
3. 能生成可访问的文件内容

如果 evidence 本身没有图片，或者图片源文件已缺失，则：

- 不应把它当成“成功导出单位”
- 也不应让它主导任务失败

而应作为：

- `未导出图片`
- 或 `数据缺失`

进入结果统计

---

## 5. 正式导出流程

推荐正式流程：

1. 用户在 evidence 列表页发起导出
2. 系统按当前 domain / context 查出 evidence 列表
3. 对每条 evidence 收集图片项
4. 形成“可导图片集合”
5. 对每张图片逐一读取文件内容
6. 将成功读取的图片写入 ZIP
7. 生成一份图片索引文件
8. 将 ZIP 和索引文件一起输出

---

## 6. 图片收集口径

## 6.1 主读取来源

正式主来源应为：

- `logistics.trace.evidence.image`
- `evidence.image_ids`
- `evidence.image_items_json`

## 6.2 历史兼容来源

只有在历史残留 evidence 尚未迁移完成时，才允许读取：

- `evidence.image_access_key`
- `evidence.preview_url`
- `evidence.full_url`

但这类 legacy 来源只应作为：

- 历史兼容补充

而不再作为主导出结构。

## 6.3 无图 evidence 的处理

如果 evidence 没有任何可导图片：

- 不进入 ZIP
- 记为“未命中图片”
- 不要再把它算成“成功 evidence”

---

## 7. ZIP 包内容口径

ZIP 包建议至少包含两类内容：

## 7.1 图片文件

图片文件按统一规则命名，建议包含可读上下文，例如：

```text
<batch_no>/<waybill_no>/<stop_seq>_<evidence_id>_<image_seq>.jpg
```

允许根据内容类型自动使用：

- `.jpg`
- `.jpeg`
- `.png`
- `.webp`

## 7.2 索引清单

建议同时生成：

- `index.csv`
或
- `index.xlsx`

索引清单应至少包含：

- `batch_no`
- `waybill_no`
- `stop_seq`
- `evidence_id`
- `image_id`
- `image_access_key`
- `store_name`
- `contact_name`
- `captured_at`
- `export_file_path`

这样用户即使拿到一批图片，也能反查每张图属于哪个业务对象。

---

## 8. 结果统计口径

结果统计应从“按 evidence 统计”调整为“按图片统计”。

## 8.1 推荐摘要字段

1. `命中证据数`
2. `命中图片数`
3. `成功导出图片数`
4. `未导出图片-数据缺失`
5. `未导出图片-系统异常`
6. `写入 ZIP 的运单数`
7. `写入 ZIP 的证据数`

## 8.2 不再推荐作为主摘要字段

不建议再把下面这些作为主视图核心：

- 成功 evidence 数
- 跳过 evidence 数
- 失败 evidence 数

因为这会偏离“导出图片”的真实目标。

---

## 9. 结果页展示口径

结果页建议按以下方式解释导出：

### A. 已导出图片

含义：
- 图片文件已实际写入 ZIP

### B. 未导出图片-数据缺失

含义：
- 该 evidence 没有图片
- 或历史图片文件已丢失

### C. 未导出图片-系统异常

含义：
- 图片本应能导出
- 但系统在读取、打包、写盘等阶段失败

这样页面表达会比“Success / Failed / Skipped evidence”更符合业务理解。

---

## 10. Boundary

本重构口径负责：

- 图片批量导出的主对象定义
- 图片收集规则
- ZIP 内容口径
- 结果统计与页面展示口径

本重构口径不负责：

- 单张图片预览交互
- 小程序上传链
- evidence 模型本身的业务定义
- 历史坏数据的彻底清理方案

---

## 11. Verify

重构后至少验证以下场景：

1. 列表中 10 条 evidence，含 8 张图片
- 导出结果应以 `8 张图片` 为核心统计

2. evidence 有图但部分 legacy 文件丢失
- 成功导出其余可用图片
- 缺失图片计入“未导出图片-数据缺失”

3. evidence 中有空记录
- 不应把空 evidence 作为导出失败主单位

4. 导出包中图片路径可反查
- `index.csv` 或 `index.xlsx` 能正确映射到运单/证据

5. ZIP 写盘失败
- 图片收集成功但最终无文件
- 任务级应显示 `导出失败`
- 页面应提示“未生成可下载文件”

---

## 12. 推荐落地顺序

1. 先调整导出服务统计口径为“按图片”
2. 再补索引清单输出
3. 再改结果页摘要和文案
4. 最后清理 legacy evidence 的剩余兼容分支

这样可以先把业务体验拉正，再逐步收底层结构。
