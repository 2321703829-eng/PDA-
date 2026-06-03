# 2026-04-18 统计图表模板修复

## Objective

修复 `统计图表中心` 无法打开的问题。

## Root Cause

- `custom_addons/logistics_web/static/src/xml/stats_center_templates.xml` 模板文件损坏
- `StatsCenterAction` 的 Owl 模板没有被前端模板系统成功注册
- 页面打开时触发 `Missing template: "logistics_web.StatsCenterAction"`

## Outcome

- 重写了 `stats_center_templates.xml`
- 保留了原有统计图表页面的四大分区、空态、下钻和筛选交互
- 模板已通过 Python `xml.etree.ElementTree` 的 UTF-8 解析校验

## Changed Files

- `custom_addons/logistics_web/static/src/xml/stats_center_templates.xml`

## Verify

- 访问 `/odoo/action-540`
- 页面不再出现 `Missing template: "logistics_web.StatsCenterAction"`
- 能正常进入 `统计图表中心`

## Boundary

- 本次只修模板文件，不改统计接口和服务层口径
