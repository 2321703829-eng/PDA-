# 2026-04-17 enterprise isolation p0 p1 skill added

## What Changed

- 新增本地 skill：`ai-code/.agents/skills/enterprise-isolation-p0-p1/SKILL.md`

## Why

- 企业分离主题已经有一份较完整的可行性与分期文档，但新对话接手时很容易把 `P0/P1` 与 `P2/P3` 混在一起
- 增加一个只服务 `P0/P1` 的本地 skill，可以把企业隔离口径、分期边界和默认检查项固定下来，避免过早跳到平台控制面和商用能力

## Scope

- 本次仅新增本地 skill，不改业务代码
- 本次不补企业分离目录下的新设计正文
- 本次不扩展平台控制面或套餐系统实现

## Follow-up

- 如后续正式进入 `P2`，可再新增一个面向平台控制基础版的本地 skill
- 如企业分离目录继续补接口、权限、实施和验收细稿，可同步回写本 skill 的必读列表
