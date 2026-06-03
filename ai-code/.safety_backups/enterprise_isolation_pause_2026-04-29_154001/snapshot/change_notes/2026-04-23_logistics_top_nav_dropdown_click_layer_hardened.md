# 2026-04-23 物流顶栏下拉菜单点击层加固

## 背景

物流模块顶栏 `运单 -> 配送节点明细` 在界面上能展开下拉菜单，但点击后浏览器仍停留在当前 `物流工作台` 动作页，没有真正切换到 `配送节点明细`。

排查结论：

- 菜单记录正确
- 绑定动作正确
- 前端菜单 JSON 里也带有正确的 `action_id`
- 浏览器地址仍停留在原动作号，说明不是服务端返回错动作，而是前端点击层没有稳定命中 submenu item

因此本次按“最小止血”处理，只加固导航点击层，不改业务动作和菜单结构。

## 改动

在 `custom_addons/logistics_web/static/src/scss/logistics_web.scss` 中：

- 给 `.o_main_navbar` 增加明确的 `position/z-index/overflow`
- 给顶栏下拉菜单容器增加 `overflow: visible`
- 给 `.dropdown-menu` / `.o-dropdown--menu` 提升 `z-index`
- 强制 submenu item 和链接节点开启 `pointer-events`

## 目标

确保物流顶栏下拉菜单：

- 视觉上可见
- 交互上也能真正吃到点击
- 不再出现“看起来点了配送节点明细，实际上仍停留在物流工作台”的情况
