---
name: character-assets
description: "角色资产主控：从剧本依据到可复用角色资产包"
---

# 角色资产主控

先读 [知识索引](../../knowledge/index.md)，按情景只加载本轮需要的 reference。

使用 [工作流](../../references/workflow.md) 与 [接口](../../references/interfaces.md)。先用 [需求路由与整合](../../references/routing-and-integration.md) 标定单张或批量范围、当前状态与前置门槛。先定位用户项目和当前阶段；没有项目时用内置 scripts/character_project.py 导入标准剧本与资产表，场记可选。从角色清单做第 -1 阶段视觉基准和全员轻规划；用群像差异化总控建立比较组与五轴矩阵，由人物设计总控先阅读全文，建立按来源版本复用的 ScriptContextV1，再形成 DesignDirectionBriefV1：人物定位、言行与关系、目标矛盾、人物弧线、观众信息、设计意图和专项任务。按 [人物理解与设计统筹](../../references/director-understanding.md) 从人物需要路由 Skill 或 knowledge/reference；未写外观不等于不需设计。常规问题同轮执行专项规范，复杂冲突独立会诊，保存真实参与方式和可见成果。新项目的常规独立人物默认按 [分阶段设计](../../references/phased-design.md) 提交身份、身体、穿衣风格圣经与各状态服饰文字快照。服饰设计师 Skill 对常规独立人物服饰阶段必经，接收人物总控理解与方向，协调五个服饰专项；有台词群演与无台词群像都由群演单图设计师处理。当前画幅做实后再推进。身体阶段仍须有五组比例锚点；全部完成后机械合成完整卡。默认一套连贯推荐，关键分歧给备选；先集中确认人物方向，再审当前阶段设计，不为微参数反复采访。用户要求先看一版时使用 preview 候选流程，实际审图和明确确认后同图转正。普通角色分层处理；已批准角色不因新方法自动重做。每轮只推进一个已授权且依赖已批准的阶段；及时提交结构化 JSON 并通过 CLI 记录批准、图片、审查和来源。本插件只写 GPT Image 2.5 提示词，不调用生图工具。用户回图后必须实际查看图片，通过审查与操作者确认后才进入下一阶段。新细节先提议，获批后修改设计卡。头像默认 3:4 竖版，全身图默认 9:16 竖版，只有操作者明确要求才更改。人形头像与表情以脸为主体，可取完整头部、双肩及上胸，不固定裁到锁骨以上；服装不入画用 face_only，上胸入画用对应白色背心，整组模式一致；全身图用白色背心、短裤、赤脚作模卡参考，执行资产表恢复已批准正式服装。新项目的常规独立人物依次完成头像、九宫格、全身模卡、每状态一张 9:16 竖版四格服饰执行图。有指定台词的群演跳过前三张与穿衣圣经，每状态独立产一张 9:16 四格执行资产；无台词群演群像只产每状态一张完整全身群像执行图。先用 CLI plan 判定 asset_mode，不给群像套人形四格。文字设计先批准，图像每张审查批准一次，按资产名命名后打包。旧项目沿用原链路；仅显式 upgrade-pipeline 可迁移合格旧项目。运行中报告实际文件路径、未解决疑点与下一步；不虚报成图质量。项目最终交付除逐角色包外，按 [有设定图资产表](../../references/final-asset-table.md) 把已批准图片放入资产表的角色/状态对应单元格；必须是真正嵌入单元格的图片，浮动锚点不合格。测试预览须标未批准，不能冒充定稿。

## Packaged references

- [knowledge/index.md](../../knowledge/index.md)
- [references/workflow.md](../../references/workflow.md)
- [references/interfaces.md](../../references/interfaces.md)
- [references/routing-and-integration.md](../../references/routing-and-integration.md)
- [references/director-understanding.md](../../references/director-understanding.md)
- [references/phased-design.md](../../references/phased-design.md)
- [references/costume-design-stage.md](../../references/costume-design-stage.md)
- [references/costume-designer.md](../../references/costume-designer.md)
- [references/model-card-baseline.md](../../references/model-card-baseline.md)
- [references/evidence.md](../../references/evidence.md)
- [references/source-notes.md](../../references/source-notes.md)
- [references/differentiation-framework.md](../../references/differentiation-framework.md)
- [references/specialist-contract.md](../../references/specialist-contract.md)
- [references/design-detail-standard.md](../../references/design-detail-standard.md)
- [references/render-texture-standard.md](../../references/render-texture-standard.md)
- [references/feature-focus-and-body-form.md](../../references/feature-focus-and-body-form.md)
- [references/group-ensemble.md](../../references/group-ensemble.md)
- [references/final-asset-table.md](../../references/final-asset-table.md)
