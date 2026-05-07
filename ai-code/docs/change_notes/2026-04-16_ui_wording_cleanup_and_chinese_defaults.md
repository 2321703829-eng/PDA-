# 2026-04-16 残余文案清理与新建默认名中文化

## Objective

继续收口二期后台中的残余英文和不统一文案，减少页面、面包屑、字段标签和异常日志中的英文泄漏。

## Scope

- [logistics_dispatch_waybill.py](/d:/Desktop/Odoo/custom_addons/logistics_dispatch/models/logistics_dispatch_waybill.py)
- [logistics_dispatch_batch.py](/d:/Desktop/Odoo/custom_addons/logistics_dispatch/models/logistics_dispatch_batch.py)
- [logistics_dispatch_wave.py](/d:/Desktop/Odoo/custom_addons/logistics_dispatch/models/logistics_dispatch_wave.py)
- [logistics_trace_event.py](/d:/Desktop/Odoo/custom_addons/logistics_trace_core/models/logistics_trace_event.py)
- [logistics_trace_event.py](/d:/Desktop/Odoo/custom_addons/logistics_trace_evidence/models/logistics_trace_event.py)
- [logistics_trace_evidence.py](/d:/Desktop/Odoo/custom_addons/logistics_trace_evidence/models/logistics_trace_evidence.py)
- [logistics_trace_event.py](/d:/Desktop/Odoo/custom_addons/logistics_trace_exception/models/logistics_trace_event.py)
- [logistics_trace_exception.py](/d:/Desktop/Odoo/custom_addons/logistics_trace_exception/models/logistics_trace_exception.py)
- [logistics_trace_exception_process_log.py](/d:/Desktop/Odoo/custom_addons/logistics_trace_exception/models/logistics_trace_exception_process_log.py)
- [logistics_web_dashboard.py](/d:/Desktop/Odoo/custom_addons/logistics_web/controllers/logistics_web_dashboard.py)

## Changes

1. 将波次、批次、运单、留痕事件、证据、异常单的新建默认占位名从 `New` 收口为 `新建`，并兼容旧逻辑里传入的 `New`。
2. 将留痕事件自动生成名称从英文事件标题改为中文业务标题，例如 `开始装车 - 时间`。
3. 将证据相关残余字段标签从 `Evidence Items / Evidence Count` 收口为 `证据记录 / 证据数`。
4. 将异常相关残余字段标签从 `Exceptions / Open Exception Count / Exception Event` 收口为 `异常记录 / 待处理异常数 / 异常事件`。
5. 将异常处理日志中的英文标签和选项收口为中文：
   - `Action Type` -> `操作类型`
   - `Action Time` -> `操作时间`
   - `From State` -> `原状态`
   - `To State` -> `新状态`
   - `Note` -> `备注`
6. 将证据自动命名从 `Evidence - 时间` 收口为 `证据 - 时间`。
7. 将工作台和看板接口里的英文兜底文案改为中文，避免在未命中翻译时回落到英文。

## Verify

计划验证以下结果：

- 新建波次、批次、运单、留痕、证据、异常时，不再出现 `New`
- 留痕事件和证据记录生成名不再出现英文
- 异常处理日志字段标题全部为中文
- 工作台/看板接口返回的摘要标签和兜底文案不再依赖英文源串

## Notes

本次未调整异常编号 `EXC-...` 规则，避免影响现有业务识别、导入兼容和历史记录引用。
