# 2026-04-15 Tianshu Phase 1 Brand Home And Waybill Structure

## What Changed

- 开始按 `2026-04-15_天枢科技物流后台品牌化重构与首页及订单导入重设计方案.md` 落第一批代码
- 本轮落地范围聚焦：
  - 天枢品牌首页
  - 蓝色品牌壳层与导航收口
  - 隐藏 `讨论 / 联系人` 主入口
  - 运单 `客户明细 / 货物明细` 基础数据结构

## Main Changes

### 1. 首页与品牌壳层

- 新增 `logistics_web.home` client action
- 新增首页菜单 `首页`
- 首页提供：
  - 今日工作卡片
  - 物流核心指标
  - 趋势看板摘要
  - 快捷入口
  - 角色化系统指引
  - 最近动态
- 后台顶栏收口为蓝色品牌风格

### 2. 导航重构

- 根应用名从 `物流` 调整为 `天枢物流`
- 导航命名收口为：
  - `首页`
  - `调度中心`
  - `运单中心`
  - `留痕中心`
  - `证据中心`
  - `异常中心`
  - `数据看板`
- `运营工作台 / 管理层总览` 继续保留在 `数据看板` 下

### 3. 模块显隐

- 在升级同步逻辑中将下面两个根菜单设置为隐藏：
  - `mail.menu_root_discuss`
  - `contacts.menu_contacts`
- 仅隐藏入口，不影响 `mail` / `res.partner` 作为底层能力继续使用

### 4. 运单三层结构地基

- 新增模型：
  - `logistics.dispatch.waybill.customer.line`
  - `logistics.dispatch.waybill.customer.goods.line`
- 在运单模型中新增：
  - `customer_line_ids`
  - `goods_line_ids`
  - `customer_line_count`
  - `goods_line_count`
  - `total_goods_qty`
  - `total_package_count`
  - `total_goods_weight`
  - `total_goods_volume`
- 运单详情页新增页签：
  - `客户明细`
  - `货物明细`

## Why

- 让系统先具备“品牌化首页 + 物流中心导航 + 运单客户货物结构”这三个最能感知的落地结果
- 为后续标准导入模板和三层导入写入逻辑提供数据结构基础

## Verification

- Python 语法校验通过：
  - `logistics_dispatch_waybill_customer_line.py`
  - `logistics_dispatch_waybill_customer_goods_line.py`
  - `ui_label_sync.py`
- XML 结构校验通过：
  - 菜单、动作、运单视图、首页模板和标签同步数据文件
- `home_action.js` 已通过 `node --check`

## Next

- 下一轮优先继续接：
  - 标准导入模板入口与预校验路径
  - 首页快捷入口与数据看板的更深联动
  - 运单客户/货物结构与导入写入逻辑
