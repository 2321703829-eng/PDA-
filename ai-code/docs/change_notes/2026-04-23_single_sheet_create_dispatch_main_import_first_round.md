# 2026-04-23 single sheet create dispatch main import first round

## Summary

- 标准主数据导入首轮已经从默认三 Sheet 模板切到默认单表模板。
- 预校验从“已有主数据存在性校验”改成“可建档校验”。
- 正式导入支持 `find-or-create wave / batch`，并在 `create_only` 模式下创建新 `waybill / customer_line / goods_line`。

## Code

- 更新 `custom_addons/logistics_web/services/waybill_standard_import_service_v2.py`
  - 默认模板升级为 `TSL-IMPORT-WAYBILL-V3`
  - 新增单表解析
  - 兼容旧三 Sheet 解析
  - 预校验改造为主链新建校验
  - 正式导入支持新建 `wave / batch / waybill`
- 更新 `custom_addons/logistics_web/static/src/js/actions/import_center_action.js`
  - 导入中心文案改成单表新建主链口径
  - 默认模板版本改成 `V3`
- 更新 `custom_addons/logistics_dispatch/models/`
  - 模板下载链接统一切到 `V3`

## Docs

- 更新《四期导入接口返回样例》
- 更新《四期导入结果页字段说明》
- 更新《四期导入错误码清单》

## Verify

- `waybill_standard_import_service_v2.py` 通过 Python AST 解析
- `import_center_action.js` 通过 `node --check`
- 导入相关模型文件通过 Python AST 解析

## Risks

- 本轮结果页统计已经补到 `wave / batch / waybill / customer_line / goods_line` 口径，但还没有做真实页面联调。
- 旧 `precheck_token + logistics.import.batch` 兼容链仍保留，尚未做彻底清理。
