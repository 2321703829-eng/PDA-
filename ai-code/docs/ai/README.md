# docs/ai

`docs/ai/` 用于维护 AI 协作的正式规则、提示词和路由说明。

## 当前入口规则

- `prompt_engineering/` 是当前正式正文目录
- `skill_router.md` 是 AI 路由入口说明
- `docs/ai/` 顶层与 `prompt_engineering/` 同名的旧文件，当前主要作为兼容入口保留

## 建议阅读顺序

1. [skill_router.md](./skill_router.md)
2. [prompt_engineering/AI总控提示词.md](./prompt_engineering/AI总控提示词.md)
3. [prompt_engineering/AI开发协作规范.md](./prompt_engineering/AI开发协作规范.md)
4. [prompt_engineering/AI验证与回归规则.md](./prompt_engineering/AI验证与回归规则.md)
5. [prompt_engineering/AI开发守门员补充提示词.md](./prompt_engineering/AI开发守门员补充提示词.md)
6. [prompt_engineering/AI外部资产接入与治理说明.md](./prompt_engineering/AI外部资产接入与治理说明.md)

## 使用边界

- 需要现行正文时，优先进入 `prompt_engineering/`
- 需要确认顶层旧文件是否仍可用时，只把它们视为跳转入口，不作为长期双份正文维护
- 如果后续新增 AI 专题，优先按子目录归类，而不是继续增加大量平级顶层文件
