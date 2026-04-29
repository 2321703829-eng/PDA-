# 2026-04-15 首页白条、首页仪表盘与全局表单壳层修复

## Objective

- 修复天枢科技首页顶部出现的白色空白区域
- 把首页下半区从摘要卡片补强为更像“物流仪表盘”的驾驶舱区
- 统一运单、车队、员工等表单页的视觉壳层，进一步弱化 Odoo 默认风格

## Boundary

- 本次仅调整 `logistics_web` 前端 action/template/scss
- 不改业务模型、不改官方模块 XML 结构
- 通过全局品牌样式覆盖官方表单页，不做逐模块重写

## Change Notes

### 1. 首页顶部白色空白区域修复

- 在 `home_action.js` 为首页 action 补充 `display.controlPanel = false`
- 在 `logistics_web.scss` 增加空 control panel 隐藏规则，避免首页和空白 action 再出现无内容白条

### 2. 首页仪表盘补强

- 首页 state 新增 `boardPanels`
- 首页模板新增 `物流仪表盘` 区块
- 仪表盘拆为：
  - 执行概览
  - 风险概览
  - 证据概览
- 每个面板包含主数值、摘要说明、三项子指标，提升首页的“驾驶舱”感

### 3. 全局表单页品牌壳层增强

- 统一控制栏为浅蓝渐变壳层
- 统一表单页背景、sheet、阴影、边框圆角
- 统一按钮盒 `oe_button_box` 与统计按钮 `oe_stat_button`
- 统一 notebook 页签蓝系激活态
- 统一状态条 `o_field_statusbar / o_arrow_button` 的蓝系风格
- 统一表单输入框焦点态

## Verify

- `node --check custom_addons/logistics_web/static/src/js/actions/home_action.js`
- XML 解析通过：
  - `custom_addons/logistics_web/static/src/xml/dashboard_templates.xml`

## Upgrade

```powershell
python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_dev -u logistics_web --stop-after-init
python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_dev
```

浏览器建议使用：

```text
http://127.0.0.1:8069/web?debug=assets
```

然后执行 `Ctrl + F5` 强刷。
