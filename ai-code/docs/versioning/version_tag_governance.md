# version_tag_governance

## 1. 目的

为 `d:\Desktop\Odoo` 当前物流项目建立统一的 Git 版本与 tag 治理口径，解决下面 4 个问题：

1. 哪个提交可以作为当前稳定基线
2. 哪个阶段可以给测试、演示、验收或上线使用
3. 文档里写的“当前版本”对应哪一段代码
4. 出问题时应该回看哪个版本锚点

这份文档不负责替代分支开发流程，也不要求每次提交都打 tag。

它负责规定：

- 什么情况下需要打 tag
- tag 怎么命名
- tag 前后要检查什么
- tag 和文档、change notes 如何联动

---

## 2. 当前项目特征

当前项目不是单 addon 的小改动仓库，而是：

- Odoo 官方源码 + 自定义物流 addon 的单仓
- 设计、代码、前端、联调文档都在同一仓库里
- 新旧模块命名并存，仍处于治理和收口阶段

因此当前 tag 的核心作用不是“发版装饰”，而是：

**给阶段成果建立稳定锚点，避免代码口径、文档口径和团队口径长期漂移。**

---

## 3. 什么时候必须考虑打 tag

满足下面任一场景时，应评估是否创建新 tag：

1. 要把一版代码交给测试
2. 要给主管、业务、客户或合作方演示
3. 完成一轮明确里程碑，例如：
   - `dispatch` 主线可跑通
   - `trace + evidence` 首轮闭环可跑通
   - `exception` 页面和状态流转可验收
4. 要冻结一轮文档基线，避免后续继续边改边漂
5. 要进入上线前联调或正式发布准备

如果只是日常小修、临时试验、个人分支探索，不要求打 tag。

---

## 4. tag 分层

当前项目建议只保留 3 类 tag。

### 4.1 baseline

用途：
- 记录团队认可的阶段基线
- 给后续设计、开发、测试、回归提供共同起点

推荐命名：

```text
baseline/YYYY-MM-DD
baseline/YYYY-MM-DD-brief-topic
```

示例：

```text
baseline/2026-04-27
baseline/2026-04-27-dispatch-trace-aligned
```

适用场景：
- 当前阶段已经能代表“接下来大家默认基于这一版继续干”

当前项目首个正式基线建议命名：

```text
baseline/2026-04-27-v0.1.0-tianshu
```

说明：

- `2026-04-27` 表示基线日期
- `v0.1.0` 表示首个项目级稳定版本号
- `tianshu` 表示本轮团队约定的基线标识

如果后续继续沿用同类命名，推荐保持：

```text
baseline/YYYY-MM-DD-vX.Y.Z-tianshu
```

### 4.2 milestone

用途：
- 记录明显的业务里程碑
- 用于主管汇报、阶段验收、跨人协作对齐

推荐命名：

```text
milestone/<domain>-v<major>
milestone/<domain>-<brief-topic>
```

示例：

```text
milestone/dispatch-v1
milestone/waybill-trace-v1
milestone/logistics-web-p0
```

适用场景：
- 某条主线达到可演示、可评审、可验收状态

### 4.3 release

用途：
- 记录正式发布、正式验收或准上线版本

推荐命名：

```text
release/vX.Y.Z
release/vX.Y.Z-brief-topic
```

示例：

```text
release/v0.1.0
release/v0.2.0-dispatch-waybill
```

适用场景：
- 明确对外或对内正式冻结版本

---

## 5. 当前不建议使用的 tag 方式

- 纯日期但没有类别前缀，例如：`20260427`
- 临时描述过长，例如：`this-is-my-current-test-snapshot`
- 个人化命名，例如：`xiaoming-final-final`
- 混用中文空格、特殊符号、版本口径不一致的命名

原则是：

**tag 需要让不看聊天记录的人也能马上知道它属于哪一层。**

---

## 6. 打 tag 前置检查

准备打 tag 前，至少检查下面内容：

### 6.1 代码基线

- 目标分支已明确
- 本轮目标提交范围已明确
- 没有把明显不应纳入版本的临时文件一起带入
- 关键 addon 能正常安装、升级或最少完成静态检查

### 6.2 文档基线

- `docs/context/`
- `docs/architecture/ARCHITECTURE.md`
- `docs/dev/upgrade_and_verify.md`
- `docs/review/doc_sync.md`

这些入口文档如被本轮改动影响，必须先同步。

### 6.3 变更记录

- 已补 `docs/change_notes/`
- change note 能说明：
  - 为什么打这个 tag
  - 本轮包含什么
  - 哪些内容明确不在本轮内

---

## 7. 打 tag 的最小发布包

每次正式创建 `baseline / milestone / release` tag，建议同时具备：

1. 一个明确提交点
2. 一份对应的 change note
3. 一份可复述的版本说明

最少要回答清楚：

- 这是哪个版本层级
- 当前主线做到哪一步
- 相关模块是哪几个
- 本版不包含什么

此外，版本说明默认建议至少包含下面 3 类信息：

1. 当前项目或当前阶段的简要介绍
2. 当前模块关系或业务主线关系的图式说明
3. 本次 tag 相比上一个 tag 的优化结果

说明：

- 如果是项目首个正式 tag，没有上一个 tag，可先用“历期优化结果汇总”替代
- 从第二个正式 tag 开始，默认应补“本次 tag 相比上一个 tag 的优化结果”

---

## 8. tag 与分支的关系

默认约定：

- 分支回答“正在做什么”
- tag 回答“哪一版已经被承认”

因此不要用 tag 替代分支，也不要把分支名直接当 tag 名。

建议关系如下：

- 功能开发：`feat-*`
- 治理收口：`chore-*` 或团队约定分支
- 阶段冻结：在集成后提交点创建 `baseline / milestone / release` tag

---

## 9. 推荐执行流程

### 9.1 baseline 流程

1. 先选定当前团队认可的集成提交
2. 检查核心文档是否同步
3. 补 change note
4. 编写 baseline 说明，至少补齐项目介绍、模块关系图式和本轮成果
5. 创建 `baseline/...` tag
6. 在后续沟通里默认引用这个 tag

### 9.2 milestone 流程

1. 先明确里程碑 Outcome
2. 验证关键链路是否可跑通
3. 补 change note 和版本说明
4. 明确“相对上一个 tag 增加了什么”
5. 创建 `milestone/...` tag
6. 用于演示、评审、验收

### 9.3 release 流程

1. 先冻结范围
2. 做安装/升级/联调验证
3. 明确相对上一个 tag 的上线变化
4. 明确上线风险和回退点
5. 创建 `release/...` tag

---

## 10. 当前项目建议的第一轮落地方式

如果当前仓库还没有稳定的项目 tag 体系，建议不要一开始就追求复杂版本号体系。

第一轮按下面顺序落地即可：

1. 先建立 `baseline/...` 体系
2. 主管和团队开始用 baseline 版本对齐讨论
3. 再为真正阶段成果增加 `milestone/...`
4. 最后在需要发布或正式验收时再启用 `release/...`

这样最省阻力。

---

## 11. 与文档治理的联动要求

打 tag 不是独立动作，必须同步检查：

- 文件夹命名是否仍和主线一致
- 新旧模块边界是否说明清楚
- 当前有效文档、桥接文档、历史文档是否区分清楚

相关规则见：

- [document_directory_governance.md](/d:/Desktop/Odoo/ai-code/docs/review/document_directory_governance.md:1)
- [doc_sync.md](/d:/Desktop/Odoo/ai-code/docs/review/doc_sync.md:1)

---

## 12. 当前结论

对这个项目来说，tag 的意义不是“Git 操作完成了”，而是：

**从某个提交开始，团队对代码、文档和阶段结果有了共同承认的版本锚点。**

先把 `baseline` 建起来，再逐步增加 `milestone` 和 `release`，是当前最稳妥的推进方式。
