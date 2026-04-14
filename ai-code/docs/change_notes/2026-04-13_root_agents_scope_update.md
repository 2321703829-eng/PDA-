# 2026-04-13 根目录 AGENTS 作用范围调整

## 背景

此前项目的 `AGENTS.md` 只放在 `ai-code/` 目录下，导致规则作用范围主要局限于该子目录。

为了让同一套协作规则能够覆盖整个 `Odoo` 仓库，需要把仓库级 guide 放到根目录。

## 本次调整

- 新增仓库根目录文件：`AGENTS.md`
- 将根目录版本设为整个 `Odoo` 工作区的 canonical guide
- 保留 `ai-code/AGENTS.md`，但改成根目录版本的镜像入口说明

## 当前结果

现在以下路径都能继承同一套仓库级规则：

- `addons/`
- `odoo/`
- `custom_addons/`
- `ai-code/`

## 额外同步

根目录版本同时同步了当前有效项目口径：

- 执行主线：`wave -> batch -> waybill -> waybill order lines`
- 追溯主线：`waybill -> trace -> evidence -> exception`
- `stock_delivery_trip` 不属于当前仓库可直接复用模块
