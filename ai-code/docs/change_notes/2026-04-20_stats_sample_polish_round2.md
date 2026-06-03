# 2026-04-20 统计图表样板页第二轮打磨

## 本次调整

根据页面截图回扫，继续打磨 `统计图表` 样板页，重点收 4 个问题：

1. hero 区可读性不够
2. 图表区纵向高度过大
3. 少数据场景留白过多
4. 分区标题有发虚或像描边的观感

## 调整文件

1. `custom_addons/logistics_web/static/src/scss/00_design_system.scss`
2. `custom_addons/logistics_web/static/src/scss/stats_center.scss`
3. `custom_addons/logistics_web/static/src/xml/stats_center_templates.xml`
4. `custom_addons/logistics_web/static/src/js/actions/stats_center_action.js`

## 调整内容

### 1. Hero 区

- 压低右上高光强度
- 加深主背景梯度
- 把页头改成更稳定的双栏 grid
- 右侧说明卡改成更深的半透明玻璃卡
- 提高标题与正文的可读性

### 2. 图表高度策略

- 统计图区 grid 改为 `align-items: start`
- 图表卡不再强制随同一行的最高卡片一起拉高
- 柱状图轨道高度整体收紧

### 3. 少数据场景紧凑态

- 给趋势图增加 `compact` 判断
- 给分布/排行卡增加 `compact` 判断
- 数据条目较少时，切到更紧凑的 bar/list 布局，减少大片空白

### 4. 标题观感

- 分区标题显式去掉 text-shadow / text-stroke
- 避免出现截图里像黑边或描边的观感

## 当前结论

这轮之后，`统计图表` 更接近可以复制到其他三期页面的样板页质量。

如果后续继续推进，下一步最适合把同一套“hero + panel shell + compact state”铺到 `物流工作台`。
