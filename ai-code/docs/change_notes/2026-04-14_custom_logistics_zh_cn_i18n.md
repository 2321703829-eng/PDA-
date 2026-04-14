# 2026-04-14 自定义物流模块中文语言适配

## 变更目标

让 `logistics_dispatch`、`logistics_trace_core`、`logistics_trace_evidence`、`logistics_trace_exception`、`logistics_web` 在 Odoo 中文环境下跟随系统语言一起切换，不再出现官方界面是中文、自定义物流模块仍然是英文的情况。

## 本次修改

- 重写并替换了以下模块的 `i18n/zh_CN.po`
  - `custom_addons/logistics_dispatch/i18n/zh_CN.po`
  - `custom_addons/logistics_trace_core/i18n/zh_CN.po`
  - `custom_addons/logistics_trace_evidence/i18n/zh_CN.po`
  - `custom_addons/logistics_trace_exception/i18n/zh_CN.po`
  - `custom_addons/logistics_web/i18n/zh_CN.po`
- 修正了之前自动生成语言包里的问题
  - 中文内容损坏为 `????`
  - `Language: zh_CN` 头信息位置错误
  - 翻译条目覆盖范围不足
- 将 `logistics_web` 中未走翻译函数的动态文案接入翻译链
  - `controllers/logistics_web_dashboard.py`
  - `static/src/js/actions/dashboard_action.js`
  - `static/src/js/actions/boss_trace_action.js`
  - `static/src/js/views/logistics_waybill_form_view.js`

## 当前覆盖范围

已优先覆盖当前联调路径里最容易被用户看到的内容：

- 顶部应用与菜单
- 运单 / 批次 / 波次列表与详情页
- 留痕事件 / 证据 / 异常队列
- 运单详情页 `Trace & Evidence`
- 工作台与老板页的标题、卡片、按钮、提示语
- 关键状态、枚举、按钮动作、空态文案

## 验证方式

执行模块升级：

```powershell
cd d:\Desktop\Odoo
python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_dev -u logistics_dispatch,logistics_trace_core,logistics_trace_evidence,logistics_trace_exception,logistics_web --stop-after-init
```

然后重新启动 Odoo，并在浏览器中强制刷新页面：

```powershell
cd d:\Desktop\Odoo
python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_dev
```

浏览器中使用 `Ctrl + F5` 强制刷新。

## 后续建议

- 下一轮可以继续补齐更深层的后台提示语、JS 动作名、异常处理流程文案。
- 若后续新增字段、按钮、组件模板，应同步补进对应模块的 `zh_CN.po`。
