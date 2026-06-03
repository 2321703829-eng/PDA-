# Odoo 社区版商用合规检查结果

检查日期：2026-04-10

检查依据：
- `ai-code/docs/context/compliance/Odoo社区版商用合规检查清单.md`
- 当前仓库静态代码、配置与许可证文件

检查方式：
- 只读静态检查
- 未执行编译、安装依赖、启动服务、模块升级或数据库操作

## 1. 结论摘要

当前仓库可以视为“基于 Odoo Community 的商业开发基线”，但还不能直接下结论为“所有商业交付场景都已完全合规”。

原因如下：
- 主仓库来源是 `odoo/odoo` 社区仓库。
- 根许可证文件显示 Odoo Community 基线为 `LGPLv3`。
- 当前自定义模块 `custom_addons/logistics_base` 的许可证为 `LGPL-3`，且未发现对 Enterprise / OPL / OEEL 模块的依赖。
- 但仓库内确实存在少量 `OEEL-1` 模块；若这些模块被安装、依赖或随交付物一起分发，则不能再按“纯 Community / 纯 LGPL 基线”理解。
- 当前无法仅从代码仓库判断项目最终属于“内部自用 / SaaS / 对外交付副本”中的哪一种场景，而这会直接影响分发义务判断。

## 2. 仓库级检查

### 2.1 主仓库来源

- Git 远程仓库为 `https://github.com/odoo/odoo.git`
- 未发现顶层 `enterprise` 私有仓目录

结论：
- 当前代码基线来源符合 “Odoo Community 主仓库” 口径

### 2.2 根许可证

根目录 [`LICENSE`](d:/Desktop/Odoo/LICENSE) 明确说明：
- Odoo 以 `GNU LGPL v3` 发布
- 某些随仓库打包的外部库和贡献代码可能使用其他 GPL 兼容许可证

结论：
- 不能只看根 `LICENSE` 就认定仓库内所有目录都完全同口径
- 对前端库、字体、图片、第三方资源仍需单独核查

### 2.3 当前工作区改动边界

`git status --short` 仅看到以下未跟踪内容：
- `ai-code/`
- `custom_addons/`
- `odoo_local.conf.example`

结论：
- 当前没有证据表明你们已经直接修改官方源码树中的现有文件
- 现阶段自定义内容基本隔离在 `custom_addons/` 和文档目录中

## 3. 模块级许可证检查

### 3.1 当前自定义模块

已发现自定义模块：
- [`custom_addons/logistics_base/__manifest__.py`](d:/Desktop/Odoo/custom_addons/logistics_base/__manifest__.py)

检查结果：
- `license`: `LGPL-3`
- `depends`: `contacts`, `hr`, `stock`
- 未发现依赖 Enterprise / OPL / OEEL 模块

初步结论：
- `logistics_base` 当前许可口径与 Community 基线兼容

### 3.2 仓库内发现的专有许可模块

在官方 `addons/` 中发现以下 manifest 明确声明为 `OEEL-1`：

| 模块 | 路径 | license | 风险说明 |
|---|---|---|---|
| certificate | `addons/certificate/__manifest__.py` | `OEEL-1` | 若安装或交付，不能再按纯 Community 基线处理 |
| l10n_hr_edi | `addons/l10n_hr_edi/__manifest__.py` | `OEEL-1` | 同上 |
| l10n_jo_edi_pos | `addons/l10n_jo_edi_pos/__manifest__.py` | `OEEL-1` | 同上 |
| project_hr_skills | `addons/project_hr_skills/__manifest__.py` | `OEEL-1` | 同上 |

说明：
- 这些模块存在于当前代码树中
- 但当前未发现你们的 `custom_addons` 对它们产生依赖
- “存在于仓库中” 与 “已用于实际生产 / 已随项目对外交付” 不是一回事，后者仍需结合部署与安装清单确认

### 3.3 Odoo 模块许可证枚举能力

在以下文件中可以看到 Odoo 自身对模块许可证的枚举支持：
- [`odoo/addons/base/models/ir_module.py`](d:/Desktop/Odoo/odoo/addons/base/models/ir_module.py)
- [`odoo/addons/base/data/ir_module_module.xml`](d:/Desktop/Odoo/odoo/addons/base/data/ir_module_module.xml)

其中明确出现：
- `OEEL-1`
- `OPL-1`
- `Other proprietary`

这说明：
- Odoo 框架本身支持识别专有许可模块
- 但这些枚举值的存在本身，不等于当前项目已经合规或不合规
- 真正需要关注的是：你们是否实际安装、依赖、复制、分发了这些模块

## 4. 第三方资源与 bundled 代码检查

仓库中发现多个单独许可证文件，典型包括：
- [`addons/auth_passkey/_vendor/webauthn/LICENSE`](d:/Desktop/Odoo/addons/auth_passkey/_vendor/webauthn/LICENSE)
- [`addons/html_editor/static/lib/cropperjs/LICENSE`](d:/Desktop/Odoo/addons/html_editor/static/lib/cropperjs/LICENSE)
- [`addons/html_editor/static/lib/diff2html/LICENSE`](d:/Desktop/Odoo/addons/html_editor/static/lib/diff2html/LICENSE)
- [`addons/web/static/fonts/google/Open_Sans/LICENSE.txt`](d:/Desktop/Odoo/addons/web/static/fonts/google/Open_Sans/LICENSE.txt)
- [`addons/web/static/fonts/google/Roboto/LICENSE.txt`](d:/Desktop/Odoo/addons/web/static/fonts/google/Roboto/LICENSE.txt)
- [`addons/web/static/lib/bootstrap/LICENSE`](d:/Desktop/Odoo/addons/web/static/lib/bootstrap/LICENSE)
- [`addons/web/static/lib/fullcalendar/LICENSE.md`](d:/Desktop/Odoo/addons/web/static/lib/fullcalendar/LICENSE.md)
- [`addons/web/static/lib/pdfjs/LICENSE`](d:/Desktop/Odoo/addons/web/static/lib/pdfjs/LICENSE)

结论：
- 若只是内部开发或自建运行，这部分通常不是当前最急迫阻塞点
- 若后续要做安装包、镜像、客户私有化部署包、源码包或其他对外分发，建议整理第三方资源许可证清单和随附材料

## 5. 结合清单后的风险分级

## 高风险项

### 高风险 1：仓库内存在 `OEEL-1` 模块

这并不自动等于当前项目违规，但意味着：
- 这些模块不能被默认视为 Community/LGPL 模块
- 若未来安装、依赖、复制其源码、或把其随交付物一起提供给客户，需要按 Enterprise / 专有许可单独审查

### 高风险 2：商业使用场景尚未在仓库中被明确

清单要求先区分以下三类：
- 内部自用
- SaaS
- 对外交付副本

当前代码仓库无法单独证明你们属于哪一类。

这意味着：
- 我可以确认“代码基线是否干净”
- 但不能仅凭代码替你确认“最终对外分发义务已经满足”

## 中风险项

### 中风险 1：第三方前端资源需要在分发前补齐清单

若后续对外提供：
- Docker 镜像
- 安装包
- 源码压缩包
- 客户私有化部署副本

则建议补做：
- 第三方资源许可证盘点
- 随附 LICENSE / NOTICE 材料
- 交付包中保留必要版权声明

### 中风险 2：自定义模块版权说明仍可继续加强

当前 [`custom_addons/logistics_base/__manifest__.py`](d:/Desktop/Odoo/custom_addons/logistics_base/__manifest__.py) 已声明 `LGPL-3`，目录中也已有 [`README.md`](d:/Desktop/Odoo/custom_addons/logistics_base/README.md)。

但从长期合规角度，仍建议后续继续补充：
- 作者 / 公司归属
- 模块来源说明
- 是否仅为项目私有扩展

## 低风险项 / 正向项

### 低风险 1：当前未发现 Enterprise 仓目录混入

未发现：
- 顶层 `enterprise/` 目录
- 自定义模块显式依赖 `web_enterprise`、`pos_enterprise` 等情况

### 低风险 2：当前未发现直接修改官方源码的证据

从 Git 当前状态看：
- 官方源码目录没有已修改跟踪文件
- 自定义开发边界基本保持在 `custom_addons/`

这符合清单中“优先继承扩展、避免硬改官方源码”的建议。

## 6. 当前可下的结论

基于 2026-04-10 这次静态检查，可以下的结论是：

1. 当前仓库可以继续作为 Odoo Community 物流项目的开发基线使用。
2. 当前你们自己的自定义模块没有表现出明显的专有依赖问题。
3. 不能把“仓库里出现少量 OEEL 模块”忽略掉；它们必须被视为需排除或单独审查的对象。
4. 如果你们目前属于“内部自用”或“自建 SaaS”，现阶段主要风险仍是混入专有模块，而不是立即发生的对外分发问题。
5. 如果你们后续要“向客户交付可部署副本”，则在正式交付前还需要补做一次分发合规检查。

## 7. 建议的下一步动作

### 必做

- 明确当前项目商业场景到底是：
  - 内部自用
  - SaaS
  - 对外交付副本
- 输出一份“生产安装模块清单”
- 明确排除所有 `OEEL-1 / OPL-1 / Other proprietary` 模块进入交付方案

### 建议尽快做

- 为 `custom_addons` 下每个模块补充统一版权说明模板
- 整理第三方字体、JS、图片资源的许可证台账
- 在 `ai-code` 中固化一份模块许可扫描结果表

### 到交付前必须做

- 若交付 Docker / 安装包 / 客户私有化部署包，补齐 LICENSE / NOTICE / 版权说明材料
- 人工复核交付物中是否实际包含 OEEL / OPL / proprietary 模块代码
- 必要时让专业律师对最终交付结构做复核

## 8. 本次检查的边界

本次检查没有覆盖：
- 实际数据库中“已安装模块”清单
- 线上服务器实际部署内容
- 未来客户交付包的具体组成
- 商标、宣传用语、品牌授权合规

因此，本文件是“开发阶段的静态合规检查结果”，不是正式法律意见。

## 9. 参考口径

- Odoo 官方许可证说明：https://www.odoo.com/documentation/19.0/ro/legal/licenses.html
- GNU GPL FAQ：https://www.gnu.org/licenses/gpl-faq.en.html

