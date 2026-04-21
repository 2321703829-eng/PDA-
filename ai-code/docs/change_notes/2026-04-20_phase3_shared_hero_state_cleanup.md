# 2026-04-20 三期前端共享 Hero 与状态层收口

## 本次目标

在进入全页面统一回扫前，先修复共享层里会反复污染页面观感的问题，并补一层可复用的状态面板与窄屏规则。

## 本次调整

### 1. 切开普通页头与 Hero 页头职责

- 将 `logistics_web.scss` 中的 `.o_logistics_web_page_header` 调整为仅作用于非 Hero 场景：
  - `.o_logistics_web_page_header:not(.o_logistics_web_page_hero)`
- 避免普通白底页头样式把 `管理看板 / 导入中心 / 导入结果页` 等 Hero 页面重新洗成灰白头图。

### 2. 补强导入页与管理看板的最终 Hero 覆盖

- 在共享层里追加最终覆盖：
  - `o_logistics_import_page_hero`
  - `o_logistics_import_center_page_hero`
  - `o_logistics_import_result_page_hero`
  - `o_logistics_boss_page_hero`
- 目标是即使页面专属 SCSS 的加载顺序出现波动，也不会再退回灰头图。

### 3. 修复首页 Hero 与共享 Hero 版式回归

- 首页模板 `home_action_templates.xml` 接回统一 Hero 体系：
  - 为首页头图补上 `o_logistics_web_page_hero`
  - 将首页右侧说明块切回共享 `o_logistics_web_page_note`
  - 修正首页头图中的坏编码说明文案
- 在 `00_design_system.scss` 中补回 Hero 共享布局：
  - `padding`
  - `margin-bottom`
  - `border-radius`
- 避免出现：
  - 首页主标题发虚
  - 系统名 / badge 颜色异常
  - 统计图表 / 工作台 / 导入页 / 司机页头图变成无圆角大方块

### 4. 统一共享状态面板与反馈条

- 强化：
  - `.o_logistics_web_feedback_strip`
  - `.o_logistics_web_placeholder_panel`
- 新增共享状态容器样式：
  - `.o_logistics_web_state_panel`
  - `.o_logistics_boss_state_panel`
- 统一空态 / 错误态 / 无数据但可操作态的边框、圆角、背景渐变与阴影层级。

### 5. 补共享响应式规则

- 在 `00_design_system.scss` 中补：
  - `1180px` 断点下 Hero 间距和 note 宽度收缩
  - `760px` 断点下 Hero padding、圆角和 badge 密度收紧
- 在 `logistics_web.scss` 中补：
  - `1180px` 下共享摘要卡改为两列
  - `900px` 下共享摘要卡改为一列
  - 状态面板 / placeholder panel 的窄屏 padding 与圆角统一压缩
- 在页面级样式中补：
  - `import_pages.scss`：导入动作栏、结果信息卡、模板卡的窄屏堆叠
  - `dashboard.scss`：工作台摘要卡和目标卡的小屏密度收紧
  - `boss_trace.scss`：管理看板摘要卡和判断卡的小屏密度收紧

### 6. 修复首页字体与标题版式回归

- 首页头图模板重新接入统一 Hero 结构：
  - `o_logistics_web_page_hero`
  - `o_logistics_web_page_hero_main`
  - `o_logistics_web_page_hero_aside`
  - `o_logistics_web_page_note`
- 修复了首页中：
  - 系统名 / badge / 主标题颜色异常
  - 头图标题区域无圆角、无 padding 的版式问题
  - 说明块中的坏编码文案

## 影响页面

- 统计图表
- 物流工作台
- 司机管理
- 导入中心
- 导入结果页
- 管理看板

## 验证

- `python ai-code/scripts/check_odoo_frontend_assets.py custom_addons/logistics_web`
  - `Errors: 0`
  - `Warnings: 0`

## 后续建议

- 继续做三期统一回扫的第二段：
  - 页面级按钮尺寸统一
  - 空态 / 无权限态文案统一
  - 窄屏下筛选区、双列区块、表格溢出统一收口
