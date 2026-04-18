# 2026-04-15 Menu Label And Write Date Translation Fix

## What Changed

- 修复 `logistics_web` 顶部导航与下拉菜单仍显示旧中文的问题
- 修复物流相关导出里 `Last Updated on` 仍显示英文的问题

## Why

- 已经更新过 XML 菜单和动作名称，但历史 `zh_CN` 翻译值仍保留在数据库中，导致页面继续显示 `前端 / 管理工作台 / 老板追溯总览`
- 自定义模块的 `Last Updated on`、`Last Updated by` 翻译条目为空，导出时仍会显示英文

## Changes

- 新增 `custom_addons/logistics_web/models/ui_label_sync.py`
  - 在升级时同步收口菜单和 client action 的 `name` 与 `zh_CN` 本地化值
- 新增 `custom_addons/logistics_web/data/logistics_web_label_sync.xml`
  - 通过数据函数在模块升级时执行标签同步
- 更新 `custom_addons/logistics_web/i18n/zh_CN.po`
  - 将历史 `Frontend / Management Dashboard / Boss Trace Overview` 翻译收口到最新命名
  - 补充 `运营与追溯 / 运营工作台 / 管理层总览` 的同文翻译
- 更新以下模块的 `zh_CN.po`
  - `logistics_dispatch`
  - `logistics_trace_core`
  - `logistics_trace_evidence`
  - 将 `Last Updated on` 翻译为 `更新时间`
  - 将 `Last Updated by` 翻译为 `更新人`

## Verification

- 升级 `logistics_dispatch, logistics_trace_core, logistics_trace_evidence, logistics_web` 后：
  - 顶部不再显示 `前端`
  - 下拉菜单不再显示 `管理工作台 / 老板追溯总览`
  - 导出中的更新时间字段应显示为 `更新时间`
