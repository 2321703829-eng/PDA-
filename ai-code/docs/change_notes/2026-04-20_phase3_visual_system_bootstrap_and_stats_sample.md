# 2026-04-20 三期界面系统化美化首轮落码与统计图表样板页

## 本次调整

围绕三期“界面系统化美化”启动第一轮基础层落码，先不大范围改动所有页面，而是按“全局样式变量与通用页面骨架 -> 统计图表样板页”的顺序推进。

本次新增 / 更新：

1. 新增 `custom_addons/logistics_web/static/src/scss/00_design_system.scss`
2. 重写 `custom_addons/logistics_web/static/src/scss/stats_center.scss`
3. 更新 `custom_addons/logistics_web/static/src/xml/stats_center_templates.xml`
4. 更新 `custom_addons/logistics_web/static/src/js/actions/stats_center_action.js`
5. 同步更新三期进度文档口径：
   - `前端设计/三期前端优化设计/README.md`
   - `前端设计/三期前端优化设计/00_导航与总纲/2026-04-18_三期优化进度总览.md`
   - `前端设计/三期前端优化设计/02_验收与联调/当前已验证通过项与待修项.md`

## 落地内容

### 1. 全局样式变量与通用页面骨架

- 补充页面级设计令牌：
  - 间距
  - 圆角
  - surface / border / shadow
  - success 色系
- 补充可复用骨架类：
  - `o_logistics_web_panel_shell`
  - `o_logistics_web_page_hero`
  - `o_logistics_web_page_kicker`
  - `o_logistics_web_page_note`
- 目标是让三期后续页面可以在同一套骨架上继续扩展，而不是继续逐页散改

### 2. 统计图表样板页

- 页头改成更明确的 hero 结构
- 过滤区改成统一工具栏面板
- 摘要卡补充 tone 和说明文案
- 执行 / 风险 / 司机 / 区域四个分区全部套入统一 panel shell
- 图表卡、排行卡、空态卡的视觉层级与交互悬浮态统一

### 3. 文档口径同步

- 三期不再把“界面系统化美化”写成“尚未启动编码”
- 当前更准确的状态是：
  - 已启动第一轮基础层落码
  - 已完成全局样式变量、通用页面骨架、统计图表样板页
  - 尚未覆盖其余三期页面

## 校验

- `python ai-code/scripts/check_odoo_frontend_assets.py custom_addons/logistics_web`
- `node --check custom_addons/logistics_web/static/src/js/actions/stats_center_action.js`
- `stats_center_templates.xml` XML 解析通过

## 当前结论

三期“界面系统化美化”已经不再是纯方案阶段。

当前最合适的继续推进方式是：

1. 用这轮全局样式骨架继续覆盖 `物流工作台`
2. 再收 `司机管理`
3. 最后统一 `导入中心 / 导入结果页`
