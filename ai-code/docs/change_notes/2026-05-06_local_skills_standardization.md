# 2026-05-06 本地 Skills 标准化与新增发布同步 Skill

## 背景

在完成物流联调排查、小程序接口回归后，已经沉淀出两类高复用方法：

- 联调环境缓存、资产、隧道、实例混淆排查
- 小程序 `stops -> traces -> evidences -> images -> preview` 全链回归

为了让这些方法后续能稳定复用，需要把已有 skills 进一步标准化，并补一个“联调发布与服务器同步”专用 skill。

## 本次处理

### 1. 标准化现有 skills 结构

对以下两个本地 skill 统一补齐标准结构：

- `odoo-logistics-integration-troubleshooting`
- `odoo-logistics-mini-api-regression`

标准化结果：

- 目录中保留 `SKILL.md`
- 新增 `agents/openai.yaml`
- 统一描述口径、默认提示语、标题风格

### 2. 新增发布同步 skill

新增：

- `odoo-logistics-release-sync`

用途：

- 同步代码到目标环境
- 升级 Odoo 模块
- 清理前端资产
- 重启服务/容器
- 做最小 smoke test

### 3. 标准化后的本地 skill 列表

- `C:\Users\lenovo1\.codex\skills\odoo-logistics-integration-troubleshooting`
- `C:\Users\lenovo1\.codex\skills\odoo-logistics-mini-api-regression`
- `C:\Users\lenovo1\.codex\skills\odoo-logistics-release-sync`

## 结果

本地 skills 现在已经具备更统一的命名和结构：

- skill 目录命名统一为 `odoo-logistics-*`
- 每个 skill 至少包含：
  - `SKILL.md`
  - `agents/openai.yaml`
- 可以分别覆盖：
  - 联调环境排查
  - 小程序接口链回归
  - 联调发布与服务器同步

## 影响

- 不影响项目代码运行
- 仅影响本地 Codex 复用能力与后续协作效率
- 后续再次处理联调问题、mini 接口问题、服务器同步问题时，可直接复用 skill
