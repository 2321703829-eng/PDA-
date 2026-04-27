# Custom Addons Blueprint

适用范围：
- `d:\Desktop\Odoo\custom_addons` 的目标拆分蓝图
- 当前系统从旧阶段模块命名过渡到新阶段模块体系时的设计参考

优先基准：
- `ai-code/docs/context/Odoo19物流留痕系统运单主对象与留痕主流程设计.md`
- `ai-code/docs/dev/project_coordination/Odoo19物流留痕系统五人分工与前端改造安排.md`
- `ai-code/docs/architecture/ARCHITECTURE.md`

---

## 1. 文档目的

本文档用于回答两个经常混在一起的问题：

1. 当前仓库里 `custom_addons` 目录实际上已经有什么
2. 按照当前有效业务主线，目标上应该拆成哪些模块

因此，这份文档既描述：
- 当前实际目录现状

也描述：
- 目标模块蓝图

它的作用不是替当前实现下最后结论，而是给后续设计和重构提供过渡地图。

---

## 2. 当前设计前提

当前最重要的业务前提已经明确为：

```text
波次记录 -> 批次 -> 运单号 -> 运单下订单列表 -> 留痕事件 -> 证据图片/备注
```

由此带来 3 个直接要求：

1. 自定义模块不能再围绕“订单是留痕主对象”来拆
2. 执行组织对象和事实对象必须分层
3. 证据、异常、规则、看板不能直接和旧的 `logistics_order` 语义绑死

---

## 3. 当前 custom_addons 目录现状

当前仓库内实际存在：

```text
custom_addons\
├─ logistics_base\
├─ logistics_dispatch\
├─ logistics_trace_core\
├─ logistics_trace_evidence\
├─ logistics_trace_exception\
├─ logistics_web\
├─ logistics_order\
├─ logistics_trace\
└─ logistics_exception\
```

对这几个目录的当前解释应为：

### 3.1 logistics_base

状态：
- 实际已有基础骨架

当前价值：
- 承接共用基础扩展入口
- 承接对官方模型的轻量扩展

### 3.2 logistics_dispatch

状态：
- 实际已有模块骨架
- 已开始承接波次 / 批次 / 运单主线的真实代码

当前价值：
- 是当前执行主线最明确的真实实现起点
- 已开始承接运单追溯列表页、详情页基础视图和菜单结构

### 3.3 logistics_order

状态：
- 旧阶段命名下的过渡目录 / 历史占位目录

当前问题：
- 名称容易误导为“订单主对象模块”
- 与现行运单主对象基线不一致

### 3.4 logistics_trace

状态：
- 旧阶段命名下的过渡目录 / 历史占位目录

当前问题：
- 边界过粗，未区分留痕核心与证据能力

### 3.5 logistics_exception

状态：
- 旧阶段命名下的过渡目录 / 历史占位目录

当前问题：
- 与旧的 `logistics_order` 语义耦合较深

### 3.6 logistics_trace_core

状态：
- 实际已有模块骨架

当前价值：
- 当前追溯事实层的真实承载入口之一
- 说明 `trace_core` 已经从设计名进入仓库现实

### 3.7 logistics_trace_evidence

状态：
- 实际已有模块骨架

当前价值：
- 当前证据层的真实承载入口之一
- 说明证据层已经不再只是未来规划

### 3.8 logistics_trace_exception

状态：
- 实际已有模块骨架

当前价值：
- 当前异常层的真实承载入口之一
- 说明异常层已经按新主线命名进入目录现实

### 3.9 logistics_web

状态：
- 实际已有模块骨架

当前价值：
- 当前物流后台页面、控制器和前后端交互承载层之一
- 是执行主线和追溯主线在 Odoo Web 上的重要落点

---

## 4. 目标模块蓝图

推荐将目标模块体系理解成下面 8 组。

## 4.1 基础扩展层

### logistics_base

职责：
- 共用基础扩展
- 官方模型轻量扩展
- 公共 mixin / 字典 / 基础能力

说明：
- 这是长期保留模块

## 4.2 执行组织层

### logistics_dispatch

职责：
- 承接波次、批次、运单主对象
- 承接车辆、司机、装车位、仓侧执行上下文
- 承接运单与订单归并关系

说明：
- 这是当前最核心的模块之一
- 已经开始作为真实代码模块落地

## 4.3 留痕核心层

### logistics_trace_core

职责：
- 承接批次级和运单级留痕事件
- 承接留痕时间线能力
- 承接留痕查询和基础事件类型

## 4.4 证据层

### logistics_trace_evidence

职责：
- 承接图片、备注、签名、元数据等证据对象
- 承接访问 key、预览信息、证据挂接关系

## 4.5 异常层

### logistics_trace_exception

职责：
- 承接异常对象
- 承接异常状态流转
- 承接处理记录与责任跟进

## 4.6 规则层

### logistics_trace_rule

职责：
- 留痕类型配置
- 异常类型配置
- 规则配置
- 编号与校验口径

## 4.7 展示层

### logistics_trace_dashboard

职责：
- 工作台聚合
- 老板页聚合
- 统计与看板能力

## 4.8 外围支撑层

### logistics_trace_mobile

职责：
- 司机端相关能力承接

### logistics_trace_integration

职责：
- 对外系统集成

### logistics_trace_cn

职责：
- 中国本地化或业务区域扩展

---

## 5. 推荐依赖关系

## 5.1 基础关系

```text
logistics_base
  -> 官方底座

logistics_dispatch
  -> logistics_base

logistics_trace_core
  -> logistics_dispatch
  -> logistics_base

logistics_trace_evidence
  -> logistics_trace_core

logistics_trace_exception
  -> logistics_trace_core
  -> logistics_dispatch

logistics_trace_rule
  -> logistics_base

logistics_trace_dashboard
  -> logistics_dispatch
  -> logistics_trace_core
  -> logistics_trace_evidence
  -> logistics_trace_exception
```

## 5.2 这样拆分的原因

- 执行组织对象和事实对象分层
- 证据层不再和留痕核心层强耦合在一个粗模块里
- 异常层建立在执行主线和事实层之上
- 展示层只做聚合，不反过来污染主模型

---

## 6. 当前实现状态与目标蓝图的关系

当前应这样理解：

### 已开始落地的模块

- `logistics_base`
- `logistics_dispatch`
- `logistics_trace_core`
- `logistics_trace_exception`
- `logistics_trace_evidence`
- `logistics_web`

### 已有正式设计稿但当前仓库未见真实模块目录的模块

- `logistics_trace_dashboard`

### 仅保留历史占位或桥接价值的目录

- `logistics_order`
- `logistics_trace`
- `logistics_exception`

因此当前最合理的推进方式不是再围绕旧目录继续深化，而是：

1. 保留旧目录作为历史过渡
2. 继续以 `dispatch / trace_core / trace_exception / evidence` 为真实实现方向

---

## 7. 当前建议

如果后续继续推进 `custom_addons`，建议按下面顺序理解和实施：

1. 先把 `logistics_dispatch` 继续补完整
2. 再起 `logistics_trace_core`
3. 再起 `logistics_trace_exception`
4. 再起 `logistics_trace_evidence`
5. 最后再做 `dashboard / rule / integration`

---

## 8. 当前结论

当前 `custom_addons` 的正确理解方式不是：

```text
logistics_base + logistics_order + logistics_trace + logistics_exception
```

而应该是：

```text
已存在现实：
  logistics_base
  + logistics_dispatch
  + logistics_trace_core
  + logistics_trace_evidence
  + logistics_trace_exception
  + logistics_web
  + 旧占位目录

目标蓝图：
  logistics_base
  + logistics_dispatch
  + logistics_trace_core
  + logistics_trace_evidence
  + logistics_trace_exception
  + logistics_trace_dashboard
  + logistics_trace_rule
```
