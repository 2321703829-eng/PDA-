# 2026-04-15 天枢企业导航与蓝色壳层第二阶段落地

## Objective

按最新确认后的品牌化方案，开始把系统结构从“物流内部并列导航”切换为“天枢科技首页 -> 企业一级模块”，并同步清理全局蓝色壳层中的紫色残留。

## Boundary

本次落地聚焦：

- 菜单结构与动作名称
- 首页入口信息架构
- 顶栏、下拉、页签、主按钮的蓝色主题覆盖
- 升级时数据库菜单名与父子关系同步

本次不包含：

- 全站所有页面的完整品牌化重绘
- 发票 / 车队 / 员工 / 库存模块的深度页面改造
- 模块升级与浏览器人工验收

## Change Notes

本次主要改动如下：

1. 一级结构改为企业模块
   - 将根菜单调整为 `天枢科技首页`
   - 物流菜单调整为一级企业模块 `物流`
   - 将 `运单 / 留痕 / 证据 / 异常` 下沉到 `物流` 下

2. 物流内部菜单收口
   - `调度中心 / 运单中心 / 留痕中心 / 证据中心 / 异常中心` 收成 `物流 / 批次 / 波次 / 运单 / 留痕 / 证据 / 异常`
   - 对应 act_window / client action 名称同步改名

3. 升级时动态重挂官方模块
   - 在 `ui_label_sync.py` 中补充菜单同步逻辑
   - 若模块存在，则将 `发票 / 车队 / 员工 / 库存 / 设置` 重挂到 `天枢科技首页` 下
   - 继续隐藏 `讨论 / 联系人`

4. 首页改为企业首页口径
   - 首页 hero 改为企业系统入口表达
   - 新增系统模块卡片：`发票 / 物流 / 车队 / 员工 / 库存 / 数据看板 / 设置`
   - 物流卡片和快捷入口继续承接当前物流日常工作

5. 蓝色主题继续收口
   - 增加顶栏一级菜单 hover / active 蓝色态
   - 增加下拉菜单 active / hover 蓝色态
   - 增加页签、主按钮蓝色态
   - 目标是减少默认紫色 hover / active / 弹层高亮残留

## Files

核心改动文件：

- `custom_addons/logistics_dispatch/views/logistics_dispatch_menus.xml`
- `custom_addons/logistics_dispatch/views/logistics_dispatch_batch_views.xml`
- `custom_addons/logistics_dispatch/views/logistics_dispatch_wave_views.xml`
- `custom_addons/logistics_dispatch/views/logistics_dispatch_waybill_views.xml`
- `custom_addons/logistics_trace_core/views/logistics_trace_event_views.xml`
- `custom_addons/logistics_trace_evidence/views/logistics_trace_evidence_views.xml`
- `custom_addons/logistics_trace_exception/views/logistics_trace_exception_views.xml`
- `custom_addons/logistics_web/views/logistics_web_actions.xml`
- `custom_addons/logistics_web/views/logistics_web_menus.xml`
- `custom_addons/logistics_web/models/ui_label_sync.py`
- `custom_addons/logistics_web/static/src/js/actions/home_action.js`
- `custom_addons/logistics_web/static/src/js/actions/dashboard_action_v2.js`
- `custom_addons/logistics_web/static/src/js/actions/boss_trace_action_v2.js`
- `custom_addons/logistics_web/static/src/xml/dashboard_templates.xml`
- `custom_addons/logistics_web/static/src/scss/logistics_web.scss`

## Verify

已完成的静态校验：

- `home_action.js` / `dashboard_action_v2.js` / `boss_trace_action_v2.js` 通过 `node --check`
- 相关 XML 文件通过 `xml.etree.ElementTree` 解析
- `ui_label_sync.py` 通过 Python AST 语法检查
- 关键源码路径中已无 `天枢物流 / 调度中心 / 运单中心 / 留痕中心 / 证据中心 / 异常中心 / 运营工作台 / 管理层总览` 这些旧一级结构词残留

待完成：

- 模块升级
- 浏览器强刷
- 人工确认顶栏是否已按 `首页 / 发票 / 物流 / 车队 / 员工 / 库存 / 数据看板 / 设置` 呈现
- 人工确认紫色 hover / active 残留是否已清干净
