# Phase4 First-Round Scope Alignment Upgrade Runbook

## 1. 目标

将当前开发环境同步到四期首轮收口后的正式口径：

- 只保留司机画像、车辆画像
- 不启用调度状态表、历史表
- 商品单位改为单销售单位结构
- 地址改为“完整地址 + 经纬度 + 结构化地址 JSON”

## 2. 推荐路径

当前项目还在开发阶段，且你已确认没有历史数据需要保留。

推荐路径：

1. 停止当前 Odoo 服务
2. 新建一个开发数据库
3. 重新安装 `logistics_base`、`logistics_dispatch`、`logistics_web`
4. 回归关键页面和关键接口

原因：

- 本轮既有删表，也有删字段，还有字段类型调整
- Odoo 模块升级不会自动帮你清理所有废弃表和废弃列
- 新建开发库最干净，最适合当前阶段

## 3. 环境前提

当前本地已确认存在：

- `D:\Desktop\Odoo\odoo-bin`
- `D:\Desktop\Odoo\odoo_local.conf`

建议使用的 addons 路径仍为：

```ini
addons_path = d:\Desktop\Odoo\addons,d:\Desktop\Odoo\custom_addons
```

## 4. 方案 A：推荐的新开发库重建

### 步骤 1：停止 Odoo

先关闭当前本地 Odoo 进程，避免升级期间模型缓存和数据库占用干扰。

### 步骤 2：新建数据库

推荐数据库名示例：

- `odoo_logistics_phase4_v1`

可以通过 PostgreSQL 工具手工建库，也可以在具备建库权限时直接执行：

```powershell
createdb -U odoo odoo_logistics_phase4_v1
```

### 步骤 3：安装模块

在 `D:\Desktop\Odoo` 下执行：

```powershell
python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1 -i logistics_base,logistics_dispatch,logistics_web --stop-after-init
```

说明：

- `logistics_web` 会自动带上它依赖的物流前端相关模块
- 使用 `--stop-after-init` 可以把这一步当成一次性安装动作

### 步骤 4：启动服务

```powershell
python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_phase4_v1
```

### 步骤 5：执行验证

至少验证以下内容：

1. 司机画像页面可打开，筛选项包含状态、仓库、车辆
2. 车辆画像页面可打开，筛选项包含状态、仓库、司机
3. 门店画像可查看 `longitude`、`latitude`、`address_region_json`
4. 商品单位页面只显示单值价格字段，不再显示小/中/大三组字段
5. `调度状态` 菜单不再出现

## 5. 方案 B：原开发库原地升级

如果你们暂时还想继续用原数据库，可以走这条路径，但它不是首推。

### 步骤 1：停止 Odoo

停止当前服务。

### 步骤 2：执行模块升级

```powershell
python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_dev -u logistics_base,logistics_dispatch,logistics_web --stop-after-init
```

### 步骤 3：处理旧表和旧列

注意：

- Odoo 升级不会自动删除废弃表
- 旧的商品单位字段列也不会自动从数据库物理删除

如果确认原库没有保留价值，可以手工清理这些对象。

建议清理的旧表：

- `logistics_driver_dispatch_state`
- `logistics_vehicle_dispatch_state`
- `logistics_driver_assignment_history`
- `logistics_vehicle_assignment_history`
- `logistics_dispatch_state_change_log`

建议关注的旧列：

- `logistics_product_unit.small_barcode`
- `logistics_product_unit.middle_barcode`
- `logistics_product_unit.large_barcode`
- `logistics_product_unit.small_standard_price`
- `logistics_product_unit.middle_standard_price`
- `logistics_product_unit.large_standard_price`
- `logistics_product_unit.small_purchase_price`
- `logistics_product_unit.middle_purchase_price`
- `logistics_product_unit.large_purchase_price`
- `logistics_product_unit.small_suggest_retail_price`
- `logistics_product_unit.middle_suggest_retail_price`
- `logistics_product_unit.large_suggest_retail_price`

### 步骤 4：启动并验证

```powershell
python .\odoo-bin -c .\odoo_local.conf -d odoo_logistics_dev
```

然后执行和方案 A 相同的页面与接口验证。

## 6. 升级顺序建议

无论是新库还是原地升级，都建议按以下依赖顺序理解问题：

1. `logistics_base`
2. `logistics_dispatch`
3. `logistics_web`

原因：

- `logistics_base` 先决定画像模型和主数据字段
- `logistics_dispatch` 再决定执行链和快照字段
- `logistics_web` 最后消费前两层的字段和运行态

## 7. 本轮特别注意项

### 1. 地址经纬度类型变更

`longitude` / `latitude` 已从字符串改成浮点。

如果原数据库里存在非数字内容，原地升级可能在字段类型转换时报错。

这也是推荐新建开发库的原因之一。

### 2. 删除模型不等于自动删物理表

代码里删除模型后：

- Odoo 不会自动删除旧表
- 旧数据不会自动清理

所以如果继续用旧开发库，最终仍然要人工做一次数据库清理。

### 3. 前端页面已切换到新运行态来源

司机/车辆管理页当前运行态已经改为：

- 画像模型
- 当前活跃 batch
- 记录 `active` 状态

因此升级后如果页面报错，优先排查：

1. 模块是否完整升级
2. 资产是否重新加载
3. 浏览器是否还缓存旧 JS/XML

## 8. 建议的验证顺序

1. 先看模块升级日志是否成功结束
2. 再看后台菜单是否完整打开
3. 再看司机/车辆页面接口是否正常返回
4. 最后再做导入和主数据页面检查

## 9. 结果判定标准

满足以下条件即可认为本轮升级完成：

1. 司机画像、车辆画像页面能正常打开
2. 商品单位已是单销售单位结构
3. 门店地址已支持结构化地址 JSON
4. 调度状态菜单与对应页面不再出现
5. 没有接口仍在请求旧的 `dispatch_state` 或旧商品单位字段
