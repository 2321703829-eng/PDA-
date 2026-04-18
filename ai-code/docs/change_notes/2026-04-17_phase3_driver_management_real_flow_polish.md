# 2026-04-17 三期司机管理真实链路收口与细修

## 本次变更

- 司机管理画像页改为“概览失败才整页失败，其余区块允许局部失败”的加载方式。
- KPI 卡片与趋势图点击下钻改为调用真实 drilldown 接口，再按精确记录集合打开运单/异常列表。
- drilldown 接口补充返回 `record_ids`，便于前端按准确结果集打开列表而不是只做粗粒度筛选。
- 画像页补充展示司机备注、最近使用车辆。
- 最近记录区补充“查看全部运单 / 查看全部异常”动作。
- 最近运单补充 `超时 / 缺少凭证` 风险标签。
- 最近异常补充从异常卡片内直接打开对应运单的入口。
- 本地 mock 数据同步补齐 `remark`、`recent_vehicle`、`recent exception -> waybill_id` 等字段，和真实结构保持一致。

## 影响文件

- `custom_addons/logistics_web/models/logistics_driver_service.py`
- `custom_addons/logistics_web/static/src/js/actions/driver_management_action_v2.js`
- `custom_addons/logistics_web/static/src/xml/driver_management_templates_safe.xml`
- `custom_addons/logistics_web/static/src/scss/driver_management.scss`

## 验证

- 已执行：`python .\\odoo-bin -c .\\odoo_local.conf -d odoo_logistics_dev -u logistics_web --stop-after-init`
- 已执行：临时联调数据下的服务侧自测，验证列表、画像聚合、最近记录和 drilldown 记录集返回。

## 备注

- 当前仍存在旧 `logistics_web_dashboard.py` 的 Odoo 19 `json` 路由弃用告警，但不属于本次司机管理新增代码。
