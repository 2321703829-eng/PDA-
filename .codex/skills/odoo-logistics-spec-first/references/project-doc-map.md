# Project Doc Map

Use this file to decide what to read before changing anything substantial in `odoo-reconstruct`.

## 1. Always Start Here

1. `README.md`
2. `odoo-19.0/README.md`
3. `odoo-19.0/00-总览/系统重构核心设计摘要.md`

These three files define the overall direction.

## 2. Read by Task Type

### Overall architecture or scope changes

- `odoo-19.0/00-总览/Odoo19物流留痕系统总体设计与边界说明.md`
- `odoo-19.0/02-业务与模块/Odoo19物流留痕系统模块重设方案.md`

### Dispatch, wave, batch, vehicle, dock flow

- `odoo-19.0/02-业务与模块/Odoo19物流留痕系统调度主流程设计.md`
- `odoo-19.0/03-数据与规范/Odoo19原生SQL结构梳理-订单车辆批次仓库调度.md`

### Waybill, trace, evidence, image flow

- `odoo-19.0/02-业务与模块/Odoo19物流留痕系统运单主对象与留痕主流程设计.md`
- `odoo-19.0/03-数据与规范/Odoo19运单留痕证据表与事件设计.md`
- `odoo-19.0/03-数据与规范/Odoo19物流留痕图片存储架构建议.md`

### API, module boundary, naming, enum, status, event

- `odoo-19.0/03-数据与规范/Odoo19物流留痕系统跨模块接口与数据约束总规范.md`
- `odoo-19.0/03-数据与规范/Odoo19物流留痕系统统一命名状态机与编号规则.md`

### Query, list pages, search, performance, indexes

- `odoo-19.0/03-数据与规范/Odoo19订单批次店铺查询性能与索引能力评估.md`
- `odoo-19.0/03-数据与规范/Odoo19运单留痕证据表与事件设计.md`

### Admin UI, driver mini/H5, workflow UX

- `odoo-19.0/04-页面与体验/Odoo19参考界面对比与后台功能改造建议.md`
- `odoo-19.0/04-页面与体验/司机端前端改造方案.md`

### Team ownership and collaboration boundaries

- `odoo-19.0/05-协作与实施/Odoo19物流留痕系统五人分工与前端改造安排.md`
- `odoo-19.0/05-协作与实施/图片模块协作边界说明.md`

### Commercial compliance and scope exclusion

- `odoo-19.0/01-治理与范围/Odoo19物流留痕系统商用合规影响评估.md`
- `odoo-19.0/01-治理与范围/明确暂不需要的模块和功能.md`

## 3. Reading Minimum by Role

### Backend module developer

Read at least:

1. `系统重构核心设计摘要.md`
2. `Odoo19物流留痕系统总体设计与边界说明.md`
3. the relevant module flow doc in `02-业务与模块`
4. `Odoo19物流留痕系统跨模块接口与数据约束总规范.md`
5. `Odoo19物流留痕系统统一命名状态机与编号规则.md`

### Frontend developer

Read at least:

1. `系统重构核心设计摘要.md`
2. `Odoo19物流留痕系统运单主对象与留痕主流程设计.md`
3. `Odoo19参考界面对比与后台功能改造建议.md`
4. `司机端前端改造方案.md`
5. API and naming specs in `03-数据与规范`

### Data/API designer

Read at least:

1. `Odoo19物流留痕系统跨模块接口与数据约束总规范.md`
2. `Odoo19物流留痕系统统一命名状态机与编号规则.md`
3. `Odoo19运单留痕证据表与事件设计.md`
4. `Odoo19订单批次店铺查询性能与索引能力评估.md`

## 4. Conflict Rule

If docs seem inconsistent:

1. prefer the more specific document over the broad summary
2. prefer the newer task-specific design over older generic assumptions
3. if the conflict changes implementation behavior, update the docs before coding
