# 2026-04-18 三期司机管理验收收口补强

## 本次变更

- 司机列表页补充 `月均异常率 + 风险标签` 展示，并增加 `近 7 天无执行` 提示，贴近三期验收稿中的列表表现要求。
- 司机画像页页头副标题收口为 `概览`，避免继续沿用泛化的“司机画像”命名。
- 司机趋势区补充签收率 / 超时率图例开关，减少双指标图区的阅读干扰。
- 风险区的 4 张摘要卡改为可点击下钻，并补充“高频异常类型 -> 异常列表”的下钻闭环。
- `严重异常数` 下钻进一步收口为只打开 `high + critical` 严重级别异常，避免继续落到泛异常列表。
- 风险区新增“最近异常记录”轻量块，和最近记录区形成“风险先看问题、记录区再看全量最近对象”的分层。
- 执行概览区补充 `运单总数 / 近 30 天运单数` 的直接下钻入口。
- 司机管理的“缺证据”口径统一改为 `missing + partial`，同步修正 KPI、风险摘要、最近运单标签和 drilldown 过滤逻辑。
- 司机状态筛选首版收口为 `在用 / 停用`，不再继续在筛选项中暴露未冻结状态项。
- 双指标趋势图调整为“第一行两张图，第二行一张宽图”的版式，并把 `签收率 / 超时率` 做成可分别点击的点位下钻。
- 列表页与详情页补充统一的无权限文案映射，权限错误不再和普通加载失败混成同一提示。
- 司机管理补充后端查看权限闭环：新增专用查看组 / 管理组，菜单、action、ORM 列表接口和画像 HTTP 接口统一收口到同一条查看权限。

## 影响文件

- `custom_addons/logistics_web/models/logistics_driver_service.py`
- `custom_addons/logistics_web/controllers/logistics_web_driver.py`
- `custom_addons/logistics_web/security/logistics_web_security.xml`
- `custom_addons/logistics_web/views/logistics_web_actions.xml`
- `custom_addons/logistics_web/views/logistics_web_menus.xml`
- `custom_addons/logistics_web/static/src/js/actions/driver_management_action_v2.js`
- `custom_addons/logistics_web/static/src/xml/driver_management_templates_safe.xml`
- `custom_addons/logistics_web/static/src/scss/driver_management.scss`
- `ai-code/前端设计/三期前端优化设计/02_跨模块规范/03_权限与状态/三期司机管理权限与状态说明.md`

## 验证

- 已执行：用 Python `compile(...)` 对 `logistics_driver_service.py`、`logistics_web_driver.py` 做不落盘语法检查。
- 已执行：用 XML 解析器检查 `driver_management_templates_safe.xml` 可正常解析。
- 已执行：对 `driver_management_action_v2.js` 做静态语法检查。
- 已执行：对司机管理控制器中的 drilldown 路由做语法检查，确认新增过滤参数接线正常。
- 待执行：升级 `logistics_web` 模块后回扫司机管理入口可见性和低权限账号访问结果。

## 备注

- 这次主要收口司机管理第一版的验收缺口，没有扩到车队台账、后台工作人员管理细化或企业分离权限层。
- 当前仍未做浏览器实机联调；后续建议按三期司机管理联调与验收清单走一轮人工回扫。
