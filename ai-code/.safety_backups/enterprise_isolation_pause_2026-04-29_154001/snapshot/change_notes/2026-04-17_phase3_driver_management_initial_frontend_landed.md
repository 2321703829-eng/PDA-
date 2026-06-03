# 2026-04-17 三期司机管理首批代码落地

## 本次变更

- 在 `custom_addons/logistics_web` 中新增司机管理首批实现
- 新增司机管理入口 action 和菜单
- 新增司机管理前端 client action、模板和样式
- 新增司机列表 RPC 和司机画像相关 JSON 接口
- 为 `hr.employee` 补充 `logistics_has_own_vehicle` 字段，供司机管理页展示和筛选使用

## 主要文件

- `custom_addons/logistics_web/models/logistics_driver_service.py`
- `custom_addons/logistics_web/controllers/logistics_web_driver.py`
- `custom_addons/logistics_web/static/src/js/actions/driver_management_action.js`
- `custom_addons/logistics_web/static/src/xml/driver_management_templates.xml`
- `custom_addons/logistics_web/static/src/scss/driver_management.scss`
- `custom_addons/logistics_web/views/logistics_web_actions.xml`
- `custom_addons/logistics_web/views/logistics_web_menus.xml`

## 当前范围

- 司机列表页
- 司机画像页首屏
- KPI 卡片
- 趋势图区
- 执行概览区
- 风险摘要区
- 最近运单 / 最近异常记录区
- 从画像页下钻到运单 / 异常列表

## 说明

- 本次先复用 `hr.employee + logistics.dispatch.batch + logistics.dispatch.waybill + logistics.trace.exception` 现有数据底座
- 司机画像页中的部分经营指标按当前仓库可用字段做第一版聚合口径
- `logistics_has_own_vehicle` 已落字段，但后续仍需要结合实际业务维护数据，才能稳定体现筛选价值

## 验证

- 使用 `python -c "compile(...)"` 对新增 Python 文件做了语法检查
- 使用 `python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_dev -u logistics_web --stop-after-init` 完成模块升级验证
- 使用 Odoo shell 对司机列表、画像概览、KPI、风险摘要、趋势、最近运单、最近异常做了 ORM 级联调
- 当前真实开发库中暂无 `logistics_role = driver` 的员工，因此空态链路已验证；另通过临时创建并回滚测试数据验证了非空聚合链路

## 细修

- 司机列表搜索补充支持通过车辆信息命中司机
- 新增司机 drilldown POST 接口改为 `type="http"`，避免三期新代码继续引入 Odoo 19 `json` route 弃用告警
