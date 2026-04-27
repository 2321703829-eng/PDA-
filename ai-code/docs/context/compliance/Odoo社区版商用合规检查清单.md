# Odoo 社区版商用合规检查清单（给 Codex / VSCode 使用）

## 文件用途

本文件用于在基于 **Odoo Community（GitHub 社区主仓库）** 进行二次开发时，检查当前代码、模块依赖、交付方式与许可证口径是否存在明显的商业合规风险。

本文件重点服务于以下场景：

- 基于 `odoo/odoo` 社区仓库自研物流系统
- 使用 VSCode + Codex 检查 Odoo 源码与自定义模块
- 判断当前项目是否混入 Enterprise / OPL / 其他专有模块
- 判断当前项目属于“内部自用 / SaaS / 对外交付安装包”中的哪一种
- 在开发前期就把许可证风险从技术设计中剥离出来

> 说明：本文件是开发检查清单，不是正式法律意见。若后续存在“向客户交付部署包、出售安装包、提供源码给外部客户、与第三方联合分发”的计划，建议再由专业律师复核。

---

## 一、先给结论

### 1. 当前可作为开发基线的对象
- 仅将 **Odoo GitHub 社区主仓库 `odoo/odoo`** 作为一期开发基线。
- 该社区主仓库整体口径为 **LGPLv3**。
- 单看 Community 主仓库口径，没有看到“禁止商业用途”的总限制。

### 2. 当前最需要避免的对象
- 不要把 **Odoo Enterprise** 代码混入社区版项目。
- 不要默认把 **Odoo Apps 商店模块** 都视为可自由商用。
- 不要默认仓库内所有文件都与主 LICENSE 完全一致；某些外部库或贡献代码可能有单独许可证。

### 3. 当前最需要区分的三种使用方式
- **内部自用**：公司自己部署、自己运行、不给外部交付副本
- **在线提供服务 / SaaS**：自己部署服务器，用户通过网页访问
- **对外交付副本**：把程序、安装包、镜像、源码、部署包直接交给客户或合作方

这三种场景的合规关注点不同，后续检查时必须明确当前项目属于哪一种。

---

## 二、Codex 首先要判断的基础问题

### [检查项 1] 当前代码基线是否来自 `odoo/odoo` 社区主仓库
**目标**：确认项目基础代码来自 Community，而不是 Enterprise 或混合版本。

**检查方式**：
- 检查 Git 远程仓库地址
- 检查项目目录是否以 `odoo/odoo` 官方社区仓库为来源
- 检查当前项目是否存在 `enterprise` 私有仓、专有模块目录或不明来源的付费模块

**判定原则**：
- 若仅基于 `odoo/odoo`，继续检查
- 若混入 Enterprise 或无法识别来源，标记为高风险

---

### [检查项 2] 当前项目中是否混入 Enterprise 模块
**目标**：避免把 Community 项目误做成 Enterprise 依赖项目。

**重点检查**：
- 是否存在 Enterprise 仓库目录
- 是否存在引用 Enterprise 模块的 `depends`
- 是否存在官方 Enterprise License 文件
- 是否在 README、部署脚本、配置文件中引用 Enterprise 路径

**判定原则**：
- 只要有 Enterprise 代码或依赖，不能再按“纯社区版可自由开发”理解
- 一旦依赖 Enterprise，就应改按 Enterprise 许可口径单独核查

---

### [检查项 3] 当前项目中是否混入 Odoo Apps 专有模块
**目标**：避免从 Apps 商店安装付费或专有模块后，却误以为整个项目都能自由分发。

**重点检查**：
- 检查 `addons`、`custom_addons` 中是否包含来自 Odoo Apps 的模块
- 检查这些模块的 `__manifest__.py` 中 `license` 字段
- 检查模块说明文档、LICENSE 文件、购买记录、来源链接

**高风险口径**：
- `OPL-1`
- `Other proprietary`
- 无法识别来源且无清晰许可证说明的第三方模块

---

### [检查项 4] 每个模块 manifest 中声明的 license 是什么
**目标**：不要只看总仓库 LICENSE，要逐模块确认许可证。

**Codex 应执行的动作**：
- 遍历所有自定义模块和第三方模块的 `__manifest__.py`
- 提取 `license` 字段
- 汇总模块名、来源、license、是否用于生产

**建议输出表头**：
- 模块名
- 来源（官方社区 / 第三方 / 自研）
- 目录路径
- manifest 中 license
- 是否安装
- 是否参与生产
- 风险备注

---

## 三、如何判断当前商业使用场景

### [检查项 5] 当前是否仅限公司内部自用
**判断问题**：
- 软件是否只部署在本公司控制的服务器或电脑上
- 是否只供本公司员工使用
- 是否不会把安装包、镜像、源码、完整部署副本交给外部客户

**若答案为是**：
- 当前更偏向“内部自用”场景
- 风险重点从“对外分发”转移到“是否混入专有模块”

---

### [检查项 6] 当前是否为纯在线服务 / SaaS
**判断问题**：
- 是否由你方自己部署服务器
- 外部用户是否只是通过网页、浏览器、接口访问系统
- 是否不会向用户直接交付程序副本

**若答案为是**：
- 当前更偏向“在线服务”场景
- 重点仍应检查是否混入 Enterprise / OPL / 其他专有模块
- 同时保留对未来“客户私有化部署”转型的合规预案

---

### [检查项 7] 当前是否会向外部交付软件副本
**判断问题**：
- 是否会向客户交付源码
- 是否会向客户交付 Docker 镜像、安装包、压缩包、虚拟机镜像
- 是否会由客户自己在其服务器安装运行
- 是否会出售或分发带有 Odoo 社区代码的可部署程序

**若答案为是**：
- 当前进入“对外分发 / 交付副本”场景
- 必须单独核查 LGPL 分发义务与第三方模块许可证
- 该场景风险明显高于纯内部使用或纯 SaaS

---

## 四、对 Community / Enterprise / Apps 的判断口径

### A. Odoo Community
**当前可接受口径**：
- 可作为自研物流系统底座
- 可商用，但必须遵守相应开源许可证条件
- 不应再自行添加“禁止商业用途”这类与 GPL/LGPL 冲突的限制语

### B. Odoo Enterprise
**当前项目原则**：
- 一期不纳入基线
- 不混入代码
- 不在依赖中引用
- 不让 Codex 基于 Enterprise 目录写代码

### C. Odoo Apps / 第三方模块
**当前项目原则**：
- 每个模块单独核查 license
- 未核清前，不视为可安全商用或可自由分发
- 如果是 OPL / proprietary 模块，不应默认纳入可自由交付方案

---

## 五、对自定义模块的合规建议

### [检查项 8] 自定义业务模块应尽量放在独立目录
**建议目录**：
- `custom_addons/`
- `private_addons/`

**目的**：
- 将官方社区代码与自研物流模块分层
- 降低误改官方源码带来的许可证与升级风险
- 便于单独扫描自定义代码、许可证声明与交付边界

---

### [检查项 9] 尽量避免直接改官方源码，优先继承扩展
**目标**：
- 降低合规和升级复杂度
- 把你们的物流系统设计成“基于 Community 的扩展”，而不是难以拆分的混合体

**Codex 检查点**：
- 是否直接修改了 `odoo/addons/...` 官方源码
- 是否本可用继承、扩展字段、视图覆盖，却采取了硬改官方文件
- 是否有修改记录和补丁说明

---

### [检查项 10] 给自定义模块补充清晰版权与来源说明
**建议**：
- 自研模块统一在源码头部或 README 中注明版权所有方
- 说明该模块是自研物流扩展，不冒充 Odoo 官方模块
- 保留与官方代码边界清晰的目录结构和说明文档

---

## 六、对外部依赖和 bundled 代码的检查

### [检查项 11] 检查仓库内是否存在单独许可证文件
**Codex 应检查**：
- `LICENSE`
- `COPYRIGHT`
- `NOTICE`
- 单个目录下的 `license.txt`、`COPYING`、`README`

**目标**：
- 识别是否存在“主仓库 LGPLv3，但某些目录另有许可证”的情况

---

### [检查项 12] 检查前端库、JS 库、图片、字体、图标资源的许可证
**重点原因**：
- 很多项目的版权风险并不来自 Python 主体，而来自前端资源包、商用字体、图标、模板、图片素材

**Codex 应检查**：
- `static/` 目录
- 第三方 JS / CSS 依赖
- 前端模板、图标包、字体文件
- 图片或设计素材来源

---

## 七、分发场景下的高风险问题

### [检查项 13] 若计划对外交付副本，是否已准备许可证随附材料
**检查内容**：
- 是否准备附带 LICENSE 文本
- 是否保留原版权声明
- 是否说明使用了 Odoo Community / LGPLv3 组件
- 是否整理好需要提供的对应源码范围

---

### [检查项 14] 是否试图对社区版附加额外限制
**高风险行为示例**：
- 声称“不得商业使用”
- 声称“不得逆向”且覆盖掉开源许可证已赋予的权利
- 对社区版代码部分加上与 LGPL 冲突的进一步限制

**判定原则**：
- 不要对 Odoo Community 覆盖部分擅自加与 LGPL/GPL 冲突的限制
- 自研模块的约束也要与整体分发结构协调处理

---

### [检查项 15] 是否把商标权问题与代码许可问题混为一谈
**说明**：
- 代码许可允许的事情，不等于商标使用当然允许
- 即使代码可合法使用，也不代表可以任意使用 “Odoo” 品牌作宣传包装

**建议**：
- 对外材料中避免制造“官方授权代理”或“官方联合产品”的误解
- 单独核查品牌、商标、宣传语使用方式

---

## 八、给当前物流系统项目的建议结论

### 当前适合的安全策略
1. 仅以 `odoo/odoo` 社区主仓库为底座
2. 一期只做自研物流模块，不混入 Enterprise
3. 自定义模块统一放在 `custom_addons/`
4. 所有第三方模块先查 `__manifest__.py` 中 `license`
5. 不从 Odoo Apps 随意下载模块直接进生产
6. 若当前仅内部使用或自建在线服务，先把重点放在代码分层与来源清晰
7. 若未来准备交付客户私有化部署，再专项补做分发合规检查

### 当前不建议的做法
- 混装 Community 与 Enterprise 后再试图按社区版口径整体商用
- 直接复制 Apps 商店付费模块源码进项目
- 让 Codex 基于来源不明的模块继续扩写代码
- 把 Community 代码打包对外卖出，却不核查分发义务
- 对开源部分自行增加“禁止商用”“禁止修改”等冲突条款

---

## 九、建议 Codex 输出的检查结果格式

Codex 检查完后，建议输出以下结果：

### 1. 仓库级检查
- 当前主仓库来源
- 是否为 Odoo Community
- 是否发现 Enterprise 目录或依赖
- 是否发现不明来源代码

### 2. 模块级检查
| 模块名 | 来源 | 目录 | license | 是否安装 | 风险等级 | 备注 |
|---|---|---|---|---|---|---|

### 3. 使用场景判断
- 当前属于：内部自用 / 在线服务 / 对外交付副本
- 当前场景下最需要注意的问题

### 4. 高风险项清单
- 未识别许可证模块
- Enterprise 依赖
- OPL / proprietary 模块
- 外部素材许可证不清
- 直接修改官方源码且无边界记录

### 5. 处理建议
- 保留
- 替换
- 移除
- 延后接入
- 需人工法律复核

---

## 十、参考口径（供人工核对）

### Odoo 官方
- Odoo Licenses 文档：Community 为 LGPLv3，Enterprise 为专有许可；Odoo Apps 默认为 OPL-1
- Odoo 开发文档：模块 manifest 可声明不同 license

### GNU 官方
- GPL FAQ：不能额外加“禁止商业使用”类限制
- GPL FAQ：商业销售本身是允许的，但须遵守许可证条件
- GPL FAQ：公司内部使用通常不构成向外部分发
- GPL FAQ：普通 GPL/LGPL 与 AGPL 在网络交互义务上口径不同

---

## 十一、当前项目的一句话判断

如果当前项目：
- 基线是 `odoo/odoo` 社区仓库
- 不混入 Enterprise
- 不使用 OPL / proprietary 模块
- 当前主要为内部使用或自建在线服务

那么当前阶段可以继续推进基于 Odoo Community 的物流系统开发。

真正需要在下一阶段重点补核的，是：
- 第三方模块来源
- 对外交付方式
- 分发场景下的源码与许可证义务
- 商标与宣传口径

---

## 十二、当前项目实查结果（2026-04-10）

本节用于把上面的检查清单，落到当前仓库 `d:\Desktop\Odoo` 的实际代码结果上。

检查范围：
- 仓库来源
- 根许可证
- 官方模块 manifest license
- `custom_addons` 自定义模块
- 第三方资源许可证文件
- 当前工作区改动边界

检查方式：
- 只读静态检查
- 未执行编译、安装依赖、启动服务、模块升级或数据库操作

### 1. 当前仓库基线判断

当前仓库的 Git 远程地址为：
- `https://github.com/odoo/odoo.git`

结合根目录 [`LICENSE`](d:/Desktop/Odoo/LICENSE) 的内容，可以确认：
- 当前基线来自 Odoo Community 主仓库
- 根许可证口径为 `LGPLv3`

当前未发现：
- 顶层 `enterprise` 私有仓目录
- 自定义模块显式依赖 `web_enterprise`、`pos_enterprise` 等 Enterprise 模块

初步结论：
- 当前仓库可以作为 Odoo Community 商业开发基线继续使用

### 2. 当前自定义模块检查结果

已发现的自定义模块为：
- [`custom_addons/logistics_base/__manifest__.py`](d:/Desktop/Odoo/custom_addons/logistics_base/__manifest__.py)

检查结果：
- `license`: `LGPL-3`
- `depends`: `contacts`, `hr`, `stock`
- 当前未发现对 `OEEL-1`、`OPL-1`、`Other proprietary` 模块的直接依赖

结论：
- 目前 `logistics_base` 的许可证口径与 Community 基线兼容

### 3. 当前仓库中发现的专有许可模块

虽然主仓库基线是 Community，但在当前 `addons/` 中，仍发现少量模块在 manifest 中明确声明为 `OEEL-1`：

- [`addons/certificate/__manifest__.py:17`](d:/Desktop/Odoo/addons/certificate/__manifest__.py#L17)
- [`addons/l10n_hr_edi/__manifest__.py:35`](d:/Desktop/Odoo/addons/l10n_hr_edi/__manifest__.py#L35)
- [`addons/l10n_jo_edi_pos/__manifest__.py:12`](d:/Desktop/Odoo/addons/l10n_jo_edi_pos/__manifest__.py#L12)
- [`addons/project_hr_skills/__manifest__.py:17`](d:/Desktop/Odoo/addons/project_hr_skills/__manifest__.py#L17)

这意味着：
- 不能把当前整个代码树简单理解成“所有模块都自动等于纯 LGPL”
- 上述模块若被安装、依赖、复制源码、或随交付物一起提供给客户，需要按专有许可单独审查

当前额外确认到：
- 你们的 `custom_addons` 中暂未发现对这些模块的依赖

### 4. Odoo 框架对模块许可证的支持情况

以下文件中可以看到 Odoo 自身对模块许可证的枚举支持：
- [`odoo/addons/base/models/ir_module.py`](d:/Desktop/Odoo/odoo/addons/base/models/ir_module.py)
- [`odoo/addons/base/data/ir_module_module.xml`](d:/Desktop/Odoo/odoo/addons/base/data/ir_module_module.xml)

其中包含：
- `OEEL-1`
- `OPL-1`
- `Other proprietary`

说明：
- Odoo 框架本身允许模块声明不同许可证
- 因此必须按模块级别做 license 检查，不能只看仓库根 `LICENSE`

### 5. 第三方资源与 bundled 代码检查结果

仓库内发现多处单独许可证文件，例如：
- [`addons/auth_passkey/_vendor/webauthn/LICENSE`](d:/Desktop/Odoo/addons/auth_passkey/_vendor/webauthn/LICENSE)
- [`addons/html_editor/static/lib/cropperjs/LICENSE`](d:/Desktop/Odoo/addons/html_editor/static/lib/cropperjs/LICENSE)
- [`addons/html_editor/static/lib/diff2html/LICENSE`](d:/Desktop/Odoo/addons/html_editor/static/lib/diff2html/LICENSE)
- [`addons/web/static/fonts/google/Open_Sans/LICENSE.txt`](d:/Desktop/Odoo/addons/web/static/fonts/google/Open_Sans/LICENSE.txt)
- [`addons/web/static/fonts/google/Roboto/LICENSE.txt`](d:/Desktop/Odoo/addons/web/static/fonts/google/Roboto/LICENSE.txt)
- [`addons/web/static/lib/bootstrap/LICENSE`](d:/Desktop/Odoo/addons/web/static/lib/bootstrap/LICENSE)
- [`addons/web/static/lib/fullcalendar/LICENSE.md`](d:/Desktop/Odoo/addons/web/static/lib/fullcalendar/LICENSE.md)
- [`addons/web/static/lib/pdfjs/LICENSE`](d:/Desktop/Odoo/addons/web/static/lib/pdfjs/LICENSE)

结论：
- 对“内部开发 / 自建运行”场景，这些通常不是当前第一阻塞项
- 对“对外交付源码包、安装包、镜像、客户私有化部署包”场景，这部分必须补做许可证随附材料整理

### 6. 当前工作区边界检查结果

从 `git status --short` 可见，当前未跟踪内容主要为：
- `ai-code/`
- `custom_addons/`
- `odoo_local.conf.example`

当前未看到：
- 官方源码树内已有跟踪文件被直接修改的证据

结论：
- 目前你们的自定义内容基本隔离在独立目录中
- 这符合本清单中“优先继承扩展、避免硬改官方源码”的建议

### 7. 当前项目的合规判断

基于本次静态检查，可以得出以下判断：

1. 当前项目可以继续作为基于 Odoo Community 的物流系统开发基线。
2. 当前自定义模块没有表现出明显的专有依赖问题。
3. 当前仓库中存在 `OEEL-1` 模块，这些模块必须被视为需要排除或单独审查的对象。
4. 仅凭当前代码仓库，还不能最终确认你们属于“内部自用 / SaaS / 对外交付副本”中的哪一种商业场景，因此还不能直接下“所有商用场景都已合规”的最终结论。

### 8. 当前项目的下一步合规动作

- 明确当前商业场景到底是：
  - 内部自用
  - SaaS
  - 对外交付副本
- 输出一份生产环境的实际安装模块清单
- 明确排除 `OEEL-1 / OPL-1 / Other proprietary` 模块进入交付方案
- 若后续对外提供安装包、源码包、镜像或客户私有化部署包，再专项补做一次分发合规检查

### 9. 详细结果文档

本次检查的完整结果已另存为：
- [`docs/context/compliance/Odoo社区版商用合规检查结果.md`](d:/Desktop/Odoo/ai-code/docs/context/compliance/Odoo社区版商用合规检查结果.md)
