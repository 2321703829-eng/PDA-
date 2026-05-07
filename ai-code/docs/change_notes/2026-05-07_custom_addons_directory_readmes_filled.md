# custom_addons 目录级 README 覆盖

## 本轮目标

为 `custom_addons/` 下的高频子目录补一轮目录级 `README.md`，让进入模块内部后也能快速知道该目录承接什么。

## 本轮变更

1. 为现行模块的高频目录补齐 `README.md`，重点覆盖：
   - `models/`
   - `controllers/`
   - `services/`
   - `views/`
   - `security/`
   - `data/`
   - `i18n/`
   - `migrations/`
   - `static/`
2. 继续向深层补齐高频目录：
   - `logistics_dispatch/static/src/import_templates/`
   - `logistics_web/static/src/`
   - `logistics_web/static/src/js/`
   - `logistics_web/static/src/js/actions/`
   - `logistics_web/static/src/js/components/`
   - `logistics_web/static/src/js/services/`
   - `logistics_web/static/src/js/views/`
   - `logistics_web/static/src/js/widgets/`
   - `logistics_web/static/src/scss/`
   - `logistics_web/static/src/xml/`
3. 明确跳过 `__pycache__` 这类运行产物目录，不将其纳入治理入口。

## 本轮结论

- `custom_addons/` 现在不只模块级入口清楚，进入模块内部常用目录后也有本地说明可读。
- 这轮仍然只做目录治理，没有修改业务代码。
