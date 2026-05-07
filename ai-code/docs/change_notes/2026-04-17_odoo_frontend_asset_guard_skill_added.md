# 2026-04-17 odoo_frontend_asset_guard skill added

## 本次新增

在 `ai-code/.agents/skills/` 下新增本地 skill：

- `odoo-frontend-asset-guard`

技能文件：

- `ai-code/.agents/skills/odoo-frontend-asset-guard/SKILL.md`

## 技能目的

将本轮关于 Odoo 前端 assets / registry / OWL template / manifest / bundle 验证的经验沉淀为可复用技能，用于后续：

- client action 报错排查
- `Missing template` 排查
- `actions registry` 缺 key 排查
- `__manifest__.py` 资产声明复核
- 联调前预防性检查

## 技能收口内容

skill 中统一整理了以下要点：

1. Odoo 前端链路必须按整条链检查：
   - `ir.actions.client.tag`
   - JS registry key
   - component `static template`
   - XML `t-name`
   - manifest asset 声明
   - 升级后的真实 bundle

2. 前端问题不能只看源码，还要核真实 bundle。

3. 规避建议优先采用更稳的资产组织方式：
   - 独立 action registry bootstrap
   - 关键模板拆分为独立 XML
   - manifest 显式声明关键 JS/XML

4. 固定化最小验证命令与联调验收清单。

## 影响范围

- 仅新增 `ai-code` 本地 skill 与 change note
- 不改业务代码
- 不改数据库结构
