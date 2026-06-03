## 2026-05-08 feat-text 推送前检查清单

### 使用场景

- 当前分支并不是单一功能上传。
- 分支上同时存在：
  - 小程序原始单表导入相关改动
  - 用户并行开发中的其他代码
  - 运行过程产生的噪音文件或历史未清理改动
- 因此本次推送应按“合并分支联调”来处理，而不是按“单功能提交”处理。

---

### 一、先确认当前分支口径

- 当前工作分支是否就是准备推送的目标分支：
  - 目标远端分支：`feat-text`
  - 当前本地分支若不是 `feat-text`，先确认是：
    - 直接推 `HEAD:feat-text`
    - 还是先切到本地 `feat-text` 再整理

- 先明确这次推送目标：
  - 是“把当前联调可用状态整体推到 `feat-text`”
  - 还是“只推小程序导入能力，不带并行改动”

建议：
- 如果这次是联调整体推进，允许多功能一起进 `feat-text`
- 但提交记录仍然要分组，避免后续无法定位责任边界

---

### 二、先看工作区噪音，禁止一把全提

当前仓库状态里已经能确认有大量非业务文件风险：

- 存在大量 `__pycache__/`
- 存在 `.worktrees/`
- 存在 Odoo 原生 addons 下的大量运行时缓存目录

执行前检查：

- 先看 `git status --short`
- 不要使用：
  - `git add .`
  - `git commit -a`

只允许：
- 按文件清单精确 `git add`

建议先排除：

- `__pycache__/`
- `.worktrees/`
- 运行日志
- 临时测试文件
- 非本次联调目标的自动生成文件

---

### 三、按功能分组梳理改动

这次至少应拆成 3 组来看：

#### A. 小程序导入主功能

重点文件包括：

- `custom_addons/logistics_dispatch/models/selection_options.py`
- `custom_addons/logistics_web/controllers/__init__.py`
- `custom_addons/logistics_web/controllers/logistics_web_import_v3.py`
- `custom_addons/logistics_web/controllers/logistics_web_admin_import.py`
- `custom_addons/logistics_web/controllers/logistics_web_mini_import.py`
- `custom_addons/logistics_web/services/__init__.py`
- `custom_addons/logistics_web/services/mini_program_raw_sheet_import_service.py`
- `custom_addons/logistics_web/static/src/js/actions/import_center_action.js`
- `custom_addons/logistics_web/static/src/xml/import_center_templates.xml`

检查点：

- 新导入类型是否完整注册
- admin / mini controller 是否都已接通
- import center 页面是否仍可正常打开
- 不要再把白屏修复、结构扁平化修复遗漏掉

#### B. 联调辅助变更

主要是这次为联调稳定性做的修补：

- 客户种子数据准备相关说明
- 导入中心白屏热修说明
- 预校验前端汇总取值修正说明
- 当前任务内人工指定客户说明

检查点：

- 这些文档是否与当前实际代码一致
- 是否存在“文档记录了，但代码没带上”的情况

#### C. 你的并行开发改动

这一组要你自己最后确认：

- 是否和小程序导入直接相关
- 是否已经联调验证过
- 是否应该跟本次一起推

建议：

- 如果无直接耦合，尽量单独提交
- 如果存在耦合，至少在提交信息里说明“联调合并带入”

---

### 四、重点检查会互相打架的文件

当前最需要人工复查最终内容的文件：

- `custom_addons/logistics_web/static/src/js/actions/import_center_action.js`
- `custom_addons/logistics_web/static/src/xml/import_center_templates.xml`
- `custom_addons/logistics_web/controllers/logistics_web_import_v3.py`
- `custom_addons/logistics_web/controllers/logistics_web_admin_import.py`
- `custom_addons/logistics_web/controllers/logistics_web_mini_import.py`
- `custom_addons/logistics_web/services/mini_program_raw_sheet_import_service.py`

检查点：

- 前端字段取值是否和后端返回结构一致
- admin 路由是否仍然注册正确
- 小程序原始单表预校验页是否包含：
  - 候选客户提示
  - 当前任务内人工指定客户按钮
- 指定客户后是否只作用于当前任务

---

### 五、确认数据库与模块升级影响

本次不是纯前端改动，推送后联调环境至少要考虑：

- `logistics_web` 模块升级

如果本次同时带入其他模型层改动，还要追加检查：

- 是否涉及新字段
- 是否涉及 schema 升级
- 是否需要同步升级其他自定义模块

上线前必须回答清楚：

- 只重启容器够不够
- 还是必须执行 `-u logistics_web`
- 是否还有其他模块需要一起 `-u`

---

### 六、确认联调数据前提

这次已经验证过，小程序导入功能是否成功，不只取决于代码，还取决于客户主数据是否存在。

推送前要确认：

- 当前联调环境是否已有足够客户主数据
- 若没有，是否已经准备：
  - 导入模板种子数据
  - 人工指定客户流程

检查点：

- 不能把“代码已支持”误判成“联调环境一定可用”
- 要区分：
  - 代码问题
  - 环境数据问题

---

### 七、提交前实际执行清单

建议按这个顺序执行：

1. `git status --short`
2. 按功能列出准备提交的文件清单
3. 确认不带入噪音目录和运行缓存
4. `git add <精确文件列表>`
5. `git diff --cached --name-only`
6. `git diff --cached`
7. 按功能拆 1 到 3 个提交
8. 推送到 `feat-text`

---

### 八、提交建议

建议不要压成一个“万能提交”。

推荐至少拆成：

#### 提交 1：小程序导入主链路

- 导入类型注册
- controller
- service
- import center 页面入口与预校验/confirm 交互

建议提交信息：

- `feat: add mini raw sheet import flow`

#### 提交 2：人工复核增强

- 未命中候选客户
- 当前任务内人工指定客户

建议提交信息：

- `feat: support manual partner assignment for mini raw import`

#### 提交 3：联调修复与说明

- 白屏热修
- 预校验结构取值修复
- 相关 change notes

建议提交信息：

- `fix: stabilize mini raw import review flow`

---

### 九、推送后联调验证清单

推送到 `feat-text` 后，联调环境至少再验证：

- 导入中心可打开
- 小程序原始单表入口可见
- 预校验结果卡片显示正常
- 未命中客户能显示前 5 个候选
- 可以“选择此客户”
- 指定后当前任务可继续 confirm
- 指定结果不会影响新任务

---

### 十、当前建议

基于当前仓库状态，最稳的做法是：

- 先冻结这次准备推送的文件范围
- 再按功能拆提交
- 最后再推 `feat-text`

不要直接在当前混合工作区上做“一把提交、一把推送”。
