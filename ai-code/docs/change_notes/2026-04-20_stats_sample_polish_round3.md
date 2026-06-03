# 2026-04-20 统计图表样板页第三轮打磨

## 本次调整

继续围绕截图反馈，处理 3 个剩余问题：

1. hero 区亮区仍偏强，主标题对比度还不够稳
2. 月粒度只有双 bucket 时，趋势图区仍显得太散
3. `缺凭证率与缺凭证运单数` 的表达方式不够清楚

## 调整文件

1. `custom_addons/logistics_web/static/src/scss/00_design_system.scss`
2. `custom_addons/logistics_web/static/src/scss/stats_center.scss`
3. `custom_addons/logistics_web/static/src/xml/stats_center_templates.xml`
4. `custom_addons/logistics_web/static/src/js/actions/stats_center_action.js`

## 调整内容

### 1. Hero 区

- 继续压低右上高光
- 加深整体背景梯度
- 在 hero 上叠一层更偏左侧的暗色遮罩
- 增强标题文字对比度与阴影

### 2. 双 bucket 紧凑态

- compact 趋势图区改为更明确的固定宽度 bucket 卡布局
- 按月时只有少量 bucket，不再只是“缩小一点”，而是明确做成两张并列趋势卡

### 3. 缺凭证图表达方式

- 不再把“缺凭证率”和“缺凭证运单数”混在同一视觉轨道
- 改成每个时间桶一张 signal 卡
- 每张卡分别展示：
  - 缺凭证率
  - 缺凭证运单数
- 两个指标各自有独立数值与独立轨道

## 当前结论

这轮之后，`统计图表` 样板页的主要剩余问题已经从“结构与表达问题”进一步收敛到更细的审美打磨与跨页面复用。
